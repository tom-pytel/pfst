#!/usr/bin/env python

import os
import sys
import unittest
from ast import parse as ast_parse, unparse as ast_unparse

from fst import *
from fst.astutil import (
    OPCLS2STR, TemplateStr, type_param, TypeVar, ParamSpec, TypeVarTuple, WalkFail, copy_ast, compare_asts,
)

from fst.misc import PYVER, PYLT11, PYLT12, PYLT13, PYLT14, PYGE11, PYGE12, PYGE13, PYGE14

from data_other import PARS_DATA

PYFNMS = sum((
    [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
    for top in ('src', 'tests')),
    start=[]
)

# ASTEXPR = lambda src: ast_parse(src).body[0].value
# ASTSTMT = lambda src: ast_parse(src).body[0]
# ASTEXPR = lambda src: parse(src).body[0].value.f.copy(pars=False)
ASTSTMT = lambda src: parse(src).body[0].f.copy()
ASTEXPR = lambda src: parse(src).f

PRECEDENCE_DST_STMTS = [
    (ASTSTMT('x'), 'value'),  # when able to replace in non-mod roots then can use this
    (ASTSTMT('x = y'), 'targets[0]'),
    (ASTSTMT('for x in y:\n    pass'), 'target'),
    (ASTSTMT('async for x in y:\n    pass'), 'target'),
]

PRECEDENCE_DST_EXPRS = [
    (ASTEXPR('(x,)'), 'elts[0]'),
    (ASTEXPR('[x]'), 'elts[0]'),
    (ASTEXPR('[*x]'), 'elts[0].value'),
    (ASTEXPR('{k: v}'), 'keys[0]'),
    (ASTEXPR('{k: v}'), 'values[0]'),
    (ASTEXPR('{**x}'), 'values[0]'),
    (ASTEXPR("f'{x}'"), 'values[0].value'),
    (ASTEXPR('x.y'), 'value'),
    (ASTEXPR('x[y]'), 'value'),
    (ASTEXPR('x[y]'), 'slice'),
    (ASTEXPR('call(a)'), 'args[0]'),
    (ASTEXPR('call(**a)'), 'keywords[0].value'),
]

PRECEDENCE_SRC_EXPRS = [
    (ASTEXPR('z'),),
    (ASTEXPR('x, y'), 'elts[0]'),
    (ASTEXPR('[x, y]'), 'elts[0]'),
    (ASTEXPR('(x := y)'), 'target', 'value'),
    (ASTEXPR('lambda: x'), 'body'),
    (ASTEXPR('x if y else z'), 'body', 'test', 'orelse'),
    (ASTEXPR('await x'), 'value'),
    (ASTEXPR('yield x'), 'value'),
    (ASTEXPR('yield from x'), 'value'),
    (ASTEXPR('x < y'), 'left', 'comparators[0]'),
    (ASTEXPR('x and y'), 'values[0]'),
    (ASTEXPR('x or y'), 'values[0]'),
    (ASTEXPR('~x'), 'operand'),
    (ASTEXPR('not x'), 'operand'),
    (ASTEXPR('+x'), 'operand'),
    (ASTEXPR('-x'), 'operand'),
    (ASTEXPR('x + y'), 'left', 'right'),
    (ASTEXPR('x - y'), 'left', 'right'),
    (ASTEXPR('x * y'), 'left', 'right'),
    (ASTEXPR('x @ y'), 'left', 'right'),
    (ASTEXPR('x / y'), 'left', 'right'),
    (ASTEXPR('x % y'), 'left', 'right'),
    (ASTEXPR('x << y'), 'left', 'right'),
    (ASTEXPR('x >> y'), 'left', 'right'),
    (ASTEXPR('x | y'), 'left', 'right'),
    (ASTEXPR('x ^ y'), 'left', 'right'),
    (ASTEXPR('x & y'), 'left', 'right'),
    (ASTEXPR('x // y'), 'left', 'right'),
    (ASTEXPR('x ** y'), 'left', 'right'),
]

PARSE_TESTS = [
    ('all',               FST._parse_stmtishs,          Module,         'i: int = 1\nj'),
    ('all',               FST._parse_stmtishs,          Module,         'except Exception: pass\nexcept: pass'),
    ('all',               FST._parse_stmtishs,          Module,         'case None: pass\ncase 1: pass'),
    ('all',               FST._parse_stmtish,           AnnAssign,      'i: int = 1'),
    ('all',               FST._parse_stmtish,           ExceptHandler,  'except: pass'),
    ('all',               FST._parse_stmtish,           match_case,     'case None: pass'),
    ('all',               FST._parse_stmts,             Module,         'i: int = 1\nj'),
    ('all',               FST._parse_stmt,              AnnAssign,      'i: int = 1'),
    ('all',               FST._parse_ExceptHandlers,    Module,         'except Exception: pass\nexcept: pass'),
    ('all',               FST._parse_ExceptHandler,     ExceptHandler,  'except: pass'),
    ('all',               FST._parse_match_cases,       Module,         'case None: pass\ncase 1: pass'),
    ('all',               FST._parse_match_case,        match_case,     'case None: pass'),
    ('all',               FST._parse_expr,              Name,           'j'),
    ('all',               FST._parse_expr,              Starred,        '*s'),
    ('all',               FST._parse_all,               Starred,        '*not a'),
    ('all',               FST._parse_stmt,              AnnAssign,      'a:b'),
    ('all',               FST._parse_all,               Slice,          'a:b:c'),
    ('all',               FST._parse_all,               MatchAs,        '1 as a'),
    ('all',               FST._parse_all,               arguments,      'a: list[str], /, b: int = 1, *c, d=100, **e'),
    ('all',               FST._parse_all,               arguments,      'a, /, b, *c, d=100, **e'),
    ('all',               FST._parse_all,               Starred,        '*not a'),
    ('all',               FST._parse_all,               comprehension,  'for i in range(5) if i'),
    ('all',               FST._parse_all,               withitem,       'f(**a) as b'),
    ('all',               FST._parse_all,               Mult,           '*'),
    ('all',               FST._parse_all,               Mult,           '*='),
    ('all',               FST._parse_all,               Gt,             '>'),
    ('all',               FST._parse_all,               And,            'and'),
    ('all',               FST._parse_all,               Invert,         '~'),

    ('most',              FST._parse_stmtishs,          Module,         'i: int = 1\nj'),
    ('most',              FST._parse_stmtishs,          Module,         'except Exception: pass\nexcept: pass'),
    ('most',              FST._parse_stmtishs,          Module,         'case None: pass\ncase 1: pass'),
    ('most',              FST._parse_stmtish,           AnnAssign,      'i: int = 1'),
    ('most',              FST._parse_stmtish,           ExceptHandler,  'except: pass'),
    ('most',              FST._parse_stmtish,           match_case,     'case None: pass'),
    ('most',              FST._parse_stmts,             Module,         'i: int = 1\nj'),
    ('most',              FST._parse_stmt,              AnnAssign,      'i: int = 1'),
    ('most',              FST._parse_ExceptHandlers,    Module,         'except Exception: pass\nexcept: pass'),
    ('most',              FST._parse_ExceptHandler,     ExceptHandler,  'except: pass'),
    ('most',              FST._parse_match_cases,       Module,         'case None: pass\ncase 1: pass'),
    ('most',              FST._parse_match_case,        match_case,     'case None: pass'),
    ('most',              FST._parse_expr,              Name,           'j'),
    ('most',              FST._parse_expr,              Starred,        '*s'),
    ('most',              FST._parse_all,               SyntaxError,    '*not a'),
    ('most',              FST._parse_stmt,              AnnAssign,      'a:b'),
    ('most',              FST._parse_all,               SyntaxError,    'a:b:c'),
    ('most',              FST._parse_all,               SyntaxError,    '1 as a'),
    ('most',              FST._parse_all,               SyntaxError,    'a: list[str], /, b: int = 1, *c, d=100, **e'),
    ('most',              FST._parse_all,               SyntaxError,    'a, /, b, *c, d=100, **e'),
    ('most',              FST._parse_all,               SyntaxError,    '*not a'),
    ('most',              FST._parse_all,               SyntaxError,    'for i in range(5) if i'),
    ('most',              FST._parse_all,               SyntaxError,    'f(**a) as b'),
    ('most',              FST._parse_all,               SyntaxError,    '*'),
    ('most',              FST._parse_all,               SyntaxError,    '*='),
    ('most',              FST._parse_all,               SyntaxError,    '>'),
    ('most',              FST._parse_all,               SyntaxError,    'and'),
    ('most',              FST._parse_all,               SyntaxError,    '~'),

    ('min',               FST._parse_stmtishs,          Module,         'i: int = 1\nj'),
    ('min',               FST._parse_stmtishs,          SyntaxError,    'except Exception: pass\nexcept: pass'),
    ('min',               FST._parse_stmtishs,          SyntaxError,    'case None: pass\ncase 1: pass'),
    ('min',               FST._parse_stmtish,           AnnAssign,      'i: int = 1'),
    ('min',               FST._parse_stmtish,           SyntaxError,    'except: pass'),
    ('min',               FST._parse_stmtish,           SyntaxError,    'case None: pass'),
    ('min',               FST._parse_stmts,             Module,         'i: int = 1\nj'),
    ('min',               FST._parse_stmt,              AnnAssign,      'i: int = 1'),
    ('min',               FST._parse_ExceptHandlers,    SyntaxError,    'except Exception: pass\nexcept: pass'),
    ('min',               FST._parse_ExceptHandler,     SyntaxError,    'except: pass'),
    ('min',               FST._parse_match_cases,       SyntaxError,    'case None: pass\ncase 1: pass'),
    ('min',               FST._parse_match_case,        SyntaxError,    'case None: pass'),
    ('min',               FST._parse_expr,              Name,           'j'),
    ('min',               FST._parse_expr,              Starred,        '*s'),
    ('min',               FST._parse_all,               SyntaxError,    '*not a'),
    ('min',               FST._parse_stmt,              AnnAssign,      'a:b'),
    ('min',               FST._parse_all,               SyntaxError,    'a:b:c'),
    ('min',               FST._parse_all,               SyntaxError,    '1 as a'),
    ('min',               FST._parse_all,               SyntaxError,    'a: list[str], /, b: int = 1, *c, d=100, **e'),
    ('min',               FST._parse_all,               SyntaxError,    'a, /, b, *c, d=100, **e'),
    ('min',               FST._parse_all,               SyntaxError,    '*not a'),
    ('min',               FST._parse_all,               SyntaxError,    'for i in range(5) if i'),
    ('min',               FST._parse_all,               SyntaxError,    'f(**a) as b'),
    ('min',               FST._parse_all,               SyntaxError,    '*'),
    ('min',               FST._parse_all,               SyntaxError,    '*='),
    ('min',               FST._parse_all,               SyntaxError,    '>'),
    ('min',               FST._parse_all,               SyntaxError,    'and'),
    ('min',               FST._parse_all,               SyntaxError,    '~'),

    ('exec',              FST._parse_Module,            Module,         'i: int = 1'),
    ('eval',              FST._parse_Expression,        Expression,     'None'),
    ('single',            FST._parse_Interactive,       Interactive,    'i: int = 1'),

    ('stmtishs',          FST._parse_stmtishs,          Module,         'i: int = 1\nj'),
    ('stmtishs',          FST._parse_stmtishs,          Module,         'except Exception: pass\nexcept: pass'),
    ('stmtishs',          FST._parse_stmtishs,          Module,         'case None: pass\ncase 1: pass'),
    ('stmtish',           FST._parse_stmtish,           AnnAssign,      'i: int = 1'),
    ('stmtish',           FST._parse_stmtish,           ExceptHandler,  'except: pass'),
    ('stmtish',           FST._parse_stmtish,           match_case,     'case None: pass'),
    ('stmtish',           FST._parse_stmtishs,          NodeError,      'except Exception: pass\nexcept: pass'),
    ('stmtish',           FST._parse_stmtishs,          NodeError,      'case None: pass\ncase 1: pass'),
    ('stmtish',           FST._parse_stmtish,           NodeError,      'i: int = 1\nj'),

    ('stmts',             FST._parse_stmts,             Module,         'i: int = 1\nj'),
    ('stmts',             FST._parse_stmts,             SyntaxError,    'except Exception: pass\nexcept: pass'),
    ('stmt',              FST._parse_stmt,              AnnAssign,      'i: int = 1'),
    ('stmt',              FST._parse_stmt,              Expr,           'j'),
    ('stmt',              FST._parse_stmt,              NodeError,      'i: int = 1\nj'),
    ('stmt',              FST._parse_stmt,              SyntaxError,    'except: pass'),

    ('ExceptHandlers',    FST._parse_ExceptHandlers,    Module,         'except Exception: pass\nexcept: pass'),
    ('ExceptHandlers',    FST._parse_ExceptHandlers,    NodeError,      'except Exception: pass\nexcept: pass\nelse: pass'),
    ('ExceptHandlers',    FST._parse_ExceptHandlers,    NodeError,      'except Exception: pass\nexcept: pass\nfinally: pass'),
    ('ExceptHandlers',    FST._parse_ExceptHandlers,    SyntaxError,    'i: int = 1\nj'),
    ('ExceptHandler',     FST._parse_ExceptHandler,     ExceptHandler,  'except: pass'),
    ('ExceptHandler',     FST._parse_ExceptHandler,     NodeError,      'except Exception: pass\nexcept: pass'),
    ('ExceptHandler',     FST._parse_ExceptHandler,     SyntaxError,    'i: int = 1'),

    ('match_cases',       FST._parse_match_cases,       Module,         'case None: pass\ncase 1: pass'),
    ('match_cases',       FST._parse_match_cases,       SyntaxError,    'i: int = 1'),
    ('match_case',        FST._parse_match_case,        match_case,     'case None: pass'),
    ('match_case',        FST._parse_match_case,        NodeError,      'case None: pass\ncase 1: pass'),
    ('match_case',        FST._parse_match_case,        SyntaxError,    'i: int = 1'),

    ('expr',              FST._parse_expr,              Name,           'j'),
    ('expr',              FST._parse_expr,              Starred,        '*s'),
    ('expr',              FST._parse_expr,              Starred,        '*\ns'),
    ('expr',              FST._parse_expr,              Tuple,          '*\ns,'),
    ('expr',              FST._parse_expr,              Tuple,          '1\n,\n2\n,'),
    ('expr',              FST._parse_expr,              SyntaxError,    '*not a'),
    ('expr',              FST._parse_expr,              SyntaxError,    'a:b'),
    ('expr',              FST._parse_expr,              SyntaxError,    'a:b:c'),

    ('expr_callarg',      FST._parse_expr_callarg,      Name,           'j'),
    ('expr_callarg',      FST._parse_expr_callarg,      Starred,        '*s'),
    ('expr_callarg',      FST._parse_expr_callarg,      Starred,        '*not a'),
    ('expr_callarg',      FST._parse_expr_callarg,      Tuple,          'j, k'),
    ('expr_callarg',      FST._parse_expr_callarg,      NodeError,      'i=1'),
    ('expr_callarg',      FST._parse_expr_callarg,      SyntaxError,    'a:b'),
    ('expr_callarg',      FST._parse_expr_callarg,      SyntaxError,    'a:b:c'),

    ('expr_slice',        FST._parse_expr_slice,        Name,           'j'),
    ('expr_slice',        FST._parse_expr_slice,        Slice,          'a:b'),
    ('expr_slice',        FST._parse_expr_slice,        Tuple,          'j, k'),
    ('expr_slice',        FST._parse_expr_slice,        Tuple,          'a:b:c, x:y:z'),

    ('expr_sliceelt',     FST._parse_expr_sliceelt,     Name,           'j'),
    ('expr_sliceelt',     FST._parse_expr_sliceelt,     Slice,          'a:b'),
    ('expr_sliceelt',     FST._parse_expr_sliceelt,     Tuple,          'j, k'),
    ('expr_sliceelt',     FST._parse_expr_sliceelt,     SyntaxError,    'a:b:c, x:y:z'),

    ('boolop',            FST._parse_boolop,            And,            'and'),
    ('boolop',            FST._parse_boolop,            NodeError,      '*'),
    ('operator',          FST._parse_operator,          Mult,           '*'),
    ('operator',          FST._parse_operator,          Mult,           '*='),
    ('operator',          FST._parse_operator,          NodeError,      'and'),
    ('binop',             FST._parse_binop,             Mult,           '*'),
    ('binop',             FST._parse_binop,             SyntaxError,    '*='),
    ('augop',             FST._parse_augop,             NodeError,      '*'),
    ('augop',             FST._parse_augop,             Mult,           '*='),
    ('unaryop',           FST._parse_unaryop,           UAdd,           '+'),
    ('unaryop',           FST._parse_unaryop,           SyntaxError,    'and'),
    ('cmpop',             FST._parse_cmpop,             GtE,            '>='),
    ('cmpop',             FST._parse_cmpop,             IsNot,          'is\nnot'),
    ('cmpop',             FST._parse_cmpop,             NodeError,      '>= a >='),
    ('cmpop',             FST._parse_cmpop,             NodeError,      'and'),

    ('comprehension',     FST._parse_comprehension,     comprehension,  'for u in v'),
    ('comprehension',     FST._parse_comprehension,     comprehension,  'for u in v if w'),
    ('comprehension',     FST._parse_comprehension,     NodeError,      'for u in v for s in t'),

    ('arguments',         FST._parse_arguments,         arguments,      ''),
    ('arguments',         FST._parse_arguments,         arguments,      'a: list[str], /, b: int = 1, *c, d=100, **e'),

    ('arguments_lambda',  FST._parse_arguments_lambda,  arguments,      ''),
    ('arguments_lambda',  FST._parse_arguments_lambda,  arguments,      'a, /, b, *c, d=100, **e'),
    ('arguments_lambda',  FST._parse_arguments_lambda,  arguments,      'a,\n/,\nb,\n*c,\nd=100,\n**e'),
    ('arguments_lambda',  FST._parse_arguments_lambda,  SyntaxError,    'a: list[str], /, b: int = 1, *c, d=100, **e'),

    ('arg',               FST._parse_arg,               arg,            'a: b'),
    ('arg',               FST._parse_arg,               NodeError,      'a: b = c'),
    ('arg',               FST._parse_arg,               NodeError,      'a, b'),
    ('arg',               FST._parse_arg,               NodeError,      'a, /'),
    ('arg',               FST._parse_arg,               NodeError,      '*, a'),
    ('arg',               FST._parse_arg,               NodeError,      '*a'),
    ('arg',               FST._parse_arg,               NodeError,      '**a'),

    ('keyword',           FST._parse_keyword,           keyword,        'a=1'),
    ('keyword',           FST._parse_keyword,           keyword,        '**a'),
    ('keyword',           FST._parse_keyword,           NodeError,      '1'),
    ('keyword',           FST._parse_keyword,           NodeError,      'a'),
    ('keyword',           FST._parse_keyword,           NodeError,      'a=1, b=2'),

    ('alias',             FST._parse_alias,             alias,          'a'),
    ('alias',             FST._parse_alias,             alias,          'a.b'),
    ('alias',             FST._parse_alias,             alias,          '*'),
    ('alias',             FST._parse_alias,             NodeError,      'a, b'),
    ('alias',             FST._parse_alias,             alias,          'a as c'),
    ('alias',             FST._parse_alias,             alias,          'a.b as c'),
    ('alias',             FST._parse_alias,             SyntaxError,    '* as c'),

    ('alias_dotted',      FST._parse_alias_dotted,      alias,          'a'),
    ('alias_dotted',      FST._parse_alias_dotted,      alias,          'a.b'),
    ('alias_dotted',      FST._parse_alias_dotted,      SyntaxError,    '*'),
    ('alias_dotted',      FST._parse_alias_dotted,      NodeError,      'a, b'),
    ('alias_dotted',      FST._parse_alias_dotted,      alias,          'a as c'),
    ('alias_dotted',      FST._parse_alias_dotted,      alias,          'a.b as c'),
    ('alias_dotted',      FST._parse_alias_dotted,      SyntaxError,    '* as c'),

    ('alias_star',        FST._parse_alias_star,        alias,          'a'),
    ('alias_star',        FST._parse_alias_star,        SyntaxError,    'a.b'),
    ('alias_star',        FST._parse_alias_star,        alias,          '*'),
    ('alias_star',        FST._parse_alias_star,        NodeError,      'a, b'),
    ('alias_star',        FST._parse_alias_star,        alias,          'a as c'),
    ('alias_star',        FST._parse_alias_star,        SyntaxError,    'a.b as c'),
    ('alias_star',        FST._parse_alias_star,        SyntaxError,    '* as c'),

    ('withitem',          FST._parse_withitem,          withitem,       'a'),
    ('withitem',          FST._parse_withitem,          withitem,       'a, b'),
    ('withitem',          FST._parse_withitem,          withitem,       '(a, b)'),
    ('withitem',          FST._parse_withitem,          withitem,       'a as b'),
    ('withitem',          FST._parse_withitem,          NodeError,      'a, b as c'),
    ('withitem',          FST._parse_withitem,          NodeError,      'a as b, x as y'),
    ('withitem',          FST._parse_withitem,          withitem,       '(a)'),
    ('withitem',          FST._parse_withitem,          SyntaxError,    '(a as b)'),
    ('withitem',          FST._parse_withitem,          SyntaxError,    '(a as b, x as y)'),

    ('pattern',           FST._parse_pattern,           MatchValue,     '42'),
    ('pattern',           FST._parse_pattern,           MatchSingleton, 'None'),
    ('pattern',           FST._parse_pattern,           MatchSequence,  '[a, *_]'),
    ('pattern',           FST._parse_pattern,           MatchSequence,  '[]'),
    ('pattern',           FST._parse_pattern,           MatchMapping,   '{"key": _}'),
    ('pattern',           FST._parse_pattern,           MatchMapping,   '{}'),
    ('pattern',           FST._parse_pattern,           MatchClass,     'SomeClass()'),
    ('pattern',           FST._parse_pattern,           MatchClass,     'SomeClass(attr=val)'),
    ('pattern',           FST._parse_pattern,           MatchAs,        'as_var'),
    ('pattern',           FST._parse_pattern,           MatchAs,        '1 as as_var'),
    ('pattern',           FST._parse_pattern,           MatchOr,        '1 | 2 | 3'),
    ('pattern',           FST._parse_pattern,           MatchAs,        '_'),
    ('pattern',           FST._parse_pattern,           MatchStar,      '*a'),
    ('pattern',           FST._parse_pattern,           SyntaxError,    ''),

    ('expr',              FST._parse_expr,              BoolOp,         '\na\nor\nb\n'),
    ('expr',              FST._parse_expr,              NamedExpr,      '\na\n:=\nb\n'),
    ('expr',              FST._parse_expr,              BinOp,          '\na\n|\nb\n'),
    ('expr',              FST._parse_expr,              BinOp,          '\na\n**\nb\n'),
    ('expr',              FST._parse_expr,              UnaryOp,        '\nnot\na\n'),
    ('expr',              FST._parse_expr,              UnaryOp,        '\n~\na\n'),
    ('expr',              FST._parse_expr,              Lambda,         '\nlambda\n:\nNone\n'),
    ('expr',              FST._parse_expr,              IfExp,          '\na\nif\nb\nelse\nc\n'),
    ('expr',              FST._parse_expr,              Dict,           '\n{\na\n:\nb\n}\n'),
    ('expr',              FST._parse_expr,              Set,            '\n{\na\n,\nb\n}\n'),
    ('expr',              FST._parse_expr,              ListComp,       '\n[\na\nfor\na\nin\nb\n]\n'),
    ('expr',              FST._parse_expr,              SetComp,        '\n{\na\nfor\na\nin\nb\n}\n'),
    ('expr',              FST._parse_expr,              DictComp,       '\n{\na\n:\nc\nfor\na\n,\nc\nin\nb\n}\n'),
    ('expr',              FST._parse_expr,              GeneratorExp,   '\n(\na\nfor\na\nin\nb\n)\n'),
    ('expr',              FST._parse_expr,              Await,          '\nawait\na\n'),
    ('expr',              FST._parse_expr,              Yield,          '\nyield\n'),
    ('expr',              FST._parse_expr,              Yield,          '\nyield\na\n'),
    ('expr',              FST._parse_expr,              YieldFrom,      '\nyield\nfrom\na\n'),
    ('expr',              FST._parse_expr,              Compare,        '\na\n<\nb\n'),
    ('expr',              FST._parse_expr,              Call,           '\nf\n(\na\n)\n'),
    ('expr',              FST._parse_expr,              JoinedStr,      "\nf'{a}'\n"),
    ('expr',              FST._parse_expr,              JoinedStr,      '\nf"{a}"\n'),
    ('expr',              FST._parse_expr,              JoinedStr,      "\nf'''\n{\na\n}\n'''\n"),
    ('expr',              FST._parse_expr,              JoinedStr,      '\nf"""\n{\na\n}\n"""\n'),
    ('expr',              FST._parse_expr,              Constant,       '\n...\n'),
    ('expr',              FST._parse_expr,              Constant,       '\nNone\n'),
    ('expr',              FST._parse_expr,              Constant,       '\nTrue\n'),
    ('expr',              FST._parse_expr,              Constant,       '\nFalse\n'),
    ('expr',              FST._parse_expr,              Constant,       '\n1\n'),
    ('expr',              FST._parse_expr,              Constant,       '\n1.0\n'),
    ('expr',              FST._parse_expr,              Constant,       '\n1j\n'),
    ('expr',              FST._parse_expr,              Constant,       "\n'a'\n"),
    ('expr',              FST._parse_expr,              Constant,       '\n"a"\n'),
    ('expr',              FST._parse_expr,              Constant,       "\n'''\na\n'''\n"),
    ('expr',              FST._parse_expr,              Constant,       '\n"""\na\n"""\n'),
    ('expr',              FST._parse_expr,              Constant,       "\nb'a'\n"),
    ('expr',              FST._parse_expr,              Constant,       '\nb"a"\n'),
    ('expr',              FST._parse_expr,              Constant,       "\nb'''\na\n'''\n"),
    ('expr',              FST._parse_expr,              Constant,       '\nb"""\na\n"""\n'),
    ('expr',              FST._parse_expr,              Attribute,      '\na\n.\nb\n'),
    ('expr',              FST._parse_expr,              Subscript,      '\na\n[\nb\n]\n'),
    ('expr',              FST._parse_expr,              Starred,        '\n*\na\n'),
    ('expr',              FST._parse_expr,              List,           '\n[\na\n,\nb\n]\n'),
    ('expr',              FST._parse_expr,              Tuple,          '\n(\na\n,\nb\n)\n'),
    ('expr',              FST._parse_expr,              Tuple,          '\na\n,\n'),
    ('expr',              FST._parse_expr,              Tuple,          '\na\n,\nb\n'),

    ('pattern',           FST._parse_pattern,           MatchValue,     '\n42\n'),
    ('pattern',           FST._parse_pattern,           MatchSingleton, '\nNone\n'),
    ('pattern',           FST._parse_pattern,           MatchSequence,  '\n[\na\n,\n*\nb\n]\n'),
    ('pattern',           FST._parse_pattern,           MatchSequence,  '\n\na\n,\n*\nb\n\n'),
    ('pattern',           FST._parse_pattern,           MatchMapping,   '\n{\n"key"\n:\n_\n}\n'),
    ('pattern',           FST._parse_pattern,           MatchClass,     '\nSomeClass\n(\nattr\n=\nval\n)\n'),
    ('pattern',           FST._parse_pattern,           MatchAs,        '\nas_var\n'),
    ('pattern',           FST._parse_pattern,           MatchAs,        '\n1\nas\nas_var\n'),
    ('pattern',           FST._parse_pattern,           MatchOr,        '\n1\n|\n2\n'),

    ('expr',              FST._parse_expr,              BoolOp,         '\n a\n or\n b\n '),
    ('expr',              FST._parse_expr,              NamedExpr,      '\n a\n :=\n b\n '),
    ('expr',              FST._parse_expr,              BinOp,          '\n a\n |\n b\n '),
    ('expr',              FST._parse_expr,              BinOp,          '\n a\n **\n b\n '),
    ('expr',              FST._parse_expr,              UnaryOp,        '\n not\n a\n '),
    ('expr',              FST._parse_expr,              UnaryOp,        '\n ~\n a\n '),
    ('expr',              FST._parse_expr,              Lambda,         '\n lambda\n :\n None\n '),
    ('expr',              FST._parse_expr,              IfExp,          '\n a\n if\n b\n else\n c\n '),
    ('expr',              FST._parse_expr,              Dict,           '\n {\n a\n :\n b\n }\n '),
    ('expr',              FST._parse_expr,              Set,            '\n {\n a\n ,\n b\n }\n '),
    ('expr',              FST._parse_expr,              ListComp,       '\n [\n a\n for\n a\n in\n b\n ]\n '),
    ('expr',              FST._parse_expr,              SetComp,        '\n {\n a\n for\n a\n in\n b\n }\n '),
    ('expr',              FST._parse_expr,              DictComp,       '\n {\n a\n :\n c\n for\n a\n ,\n c\n in\n b\n }\n '),
    ('expr',              FST._parse_expr,              GeneratorExp,   '\n (\n a\n for\n a\n in\n b\n )\n '),
    ('expr',              FST._parse_expr,              Await,          '\n await\n a\n '),
    ('expr',              FST._parse_expr,              Yield,          '\n yield\n '),
    ('expr',              FST._parse_expr,              Yield,          '\n yield\n a\n '),
    ('expr',              FST._parse_expr,              YieldFrom,      '\n yield\n from\n a\n '),
    ('expr',              FST._parse_expr,              Compare,        '\n a\n <\n b\n '),
    ('expr',              FST._parse_expr,              Call,           '\n f\n (\n a\n )\n '),
    ('expr',              FST._parse_expr,              JoinedStr,      "\n f'{a}'\n "),
    ('expr',              FST._parse_expr,              JoinedStr,      '\n f"{a}"\n '),
    ('expr',              FST._parse_expr,              JoinedStr,      "\n f'''\n {\n a\n }\n '''\n "),
    ('expr',              FST._parse_expr,              JoinedStr,      '\n f"""\n {\n a\n }\n """\n '),
    ('expr',              FST._parse_expr,              Constant,       '\n ...\n '),
    ('expr',              FST._parse_expr,              Constant,       '\n None\n '),
    ('expr',              FST._parse_expr,              Constant,       '\n True\n '),
    ('expr',              FST._parse_expr,              Constant,       '\n False\n '),
    ('expr',              FST._parse_expr,              Constant,       '\n 1\n '),
    ('expr',              FST._parse_expr,              Constant,       '\n 1.0\n '),
    ('expr',              FST._parse_expr,              Constant,       '\n 1j\n '),
    ('expr',              FST._parse_expr,              Constant,       "\n 'a'\n "),
    ('expr',              FST._parse_expr,              Constant,       '\n "a"\n '),
    ('expr',              FST._parse_expr,              Constant,       "\n '''\n a\n '''\n "),
    ('expr',              FST._parse_expr,              Constant,       '\n """\n a\n """\n '),
    ('expr',              FST._parse_expr,              Constant,       "\n b'a'\n "),
    ('expr',              FST._parse_expr,              Constant,       '\n b"a"\n '),
    ('expr',              FST._parse_expr,              Constant,       "\n b'''\n a\n '''\n "),
    ('expr',              FST._parse_expr,              Constant,       '\n b"""\n a\n """\n '),
    ('expr',              FST._parse_expr,              Attribute,      '\n a\n .\n b\n '),
    ('expr',              FST._parse_expr,              Subscript,      '\n a\n [\n b\n ]\n '),
    ('expr',              FST._parse_expr,              Starred,        '\n *\n a\n '),
    ('expr',              FST._parse_expr,              List,           '\n [\n a\n ,\n b\n ]\n '),
    ('expr',              FST._parse_expr,              Tuple,          '\n (\n a\n ,\n b\n )\n '),
    ('expr',              FST._parse_expr,              Tuple,          '\n a\n ,\n '),
    ('expr',              FST._parse_expr,              Tuple,          '\n a\n ,\n b\n '),

    ('pattern',           FST._parse_pattern,           MatchValue,     '\n 42\n '),
    ('pattern',           FST._parse_pattern,           MatchSingleton, '\n None\n '),
    ('pattern',           FST._parse_pattern,           MatchSequence,  '\n [\n a\n ,\n *\n b\n ]\n '),
    ('pattern',           FST._parse_pattern,           MatchSequence,  '\n \n a\n ,\n *\n b\n \n '),
    ('pattern',           FST._parse_pattern,           MatchMapping,   '\n {\n "key"\n :\n _\n }\n '),
    ('pattern',           FST._parse_pattern,           MatchClass,     '\n SomeClass\n (\n attr\n =\n val\n )\n '),
    ('pattern',           FST._parse_pattern,           MatchAs,        '\n as_var\n '),
    ('pattern',           FST._parse_pattern,           MatchAs,        '\n 1\n as\n as_var\n '),
    ('pattern',           FST._parse_pattern,           MatchOr,        '\n 1\n |\n 2\n '),

    (mod,                 FST._parse_Module,            Module,         'j'),
    (Module,              FST._parse_Module,            Module,         'j'),
    (Expression,          FST._parse_Expression,        Expression,     'None'),
    (Interactive,         FST._parse_Interactive,       Interactive,    'j'),

    (stmt,                FST._parse_stmt,              AnnAssign,      'i: int = 1'),
    (stmt,                FST._parse_stmt,              Expr,           'j'),
    (stmt,                FST._parse_stmt,              NodeError,      'i: int = 1\nj'),
    (stmt,                FST._parse_stmt,              SyntaxError,    'except: pass'),
    (AnnAssign,           FST._parse_stmt,              AnnAssign,      'i: int = 1'),
    (Expr,                FST._parse_stmt,              Expr,           'j'),

    (ExceptHandler,       FST._parse_ExceptHandler,     ExceptHandler,  'except: pass'),
    (ExceptHandler,       FST._parse_ExceptHandler,     NodeError,      'except Exception: pass\nexcept: pass'),
    (ExceptHandler,       FST._parse_ExceptHandler,     SyntaxError,    'i: int = 1'),

    (match_case,          FST._parse_match_case,        match_case,     'case None: pass'),
    (match_case,          FST._parse_match_case,        NodeError,      'case None: pass\ncase 1: pass'),
    (match_case,          FST._parse_match_case,        SyntaxError,    'i: int = 1'),

    (expr,                FST._parse_expr,              Name,           'j'),
    (expr,                FST._parse_expr,              Starred,        '*s'),
    (expr,                FST._parse_expr,              Starred,        '*\ns'),
    (expr,                FST._parse_expr,              Tuple,          '*\ns,'),
    (expr,                FST._parse_expr,              Tuple,          '1\n,\n2\n,'),
    (expr,                FST._parse_expr,              SyntaxError,    '*not a'),
    (expr,                FST._parse_expr,              SyntaxError,    'a:b'),
    (expr,                FST._parse_expr,              SyntaxError,    'a:b:c'),
    (Name,                FST._parse_expr,              Name,           'j'),
    (Starred,             FST._parse_expr,              Starred,        '*s'),

    (Starred,             FST._parse_expr_callarg,      Starred,        '*not a'),

    (Slice,               FST._parse_expr_slice,        Slice,          'a:b'),

    (boolop,              FST._parse_boolop,            And,            'and'),
    (boolop,              FST._parse_boolop,            NodeError,      '*'),
    (operator,            FST._parse_operator,          Mult,           '*'),
    (operator,            FST._parse_operator,          Mult,           '*='),
    (operator,            FST._parse_operator,          NodeError,      'and'),
    (unaryop,             FST._parse_unaryop,           UAdd,           '+'),
    (unaryop,             FST._parse_unaryop,           SyntaxError,    'and'),
    (cmpop,               FST._parse_cmpop,             GtE,            '>='),
    (cmpop,               FST._parse_cmpop,             IsNot,          'is\nnot'),
    (cmpop,               FST._parse_cmpop,             NodeError,      '>= a >='),
    (cmpop,               FST._parse_cmpop,             NodeError,      'and'),

    (comprehension,       FST._parse_comprehension,     comprehension,  'for u in v'),
    (comprehension,       FST._parse_comprehension,     comprehension,  'for u in v if w'),
    (comprehension,       FST._parse_comprehension,     NodeError,      '()'),

    (arguments,           FST._parse_arguments,         arguments,      ''),
    (arguments,           FST._parse_arguments,         arguments,      'a: list[str], /, b: int = 1, *c, d=100, **e'),
    (arguments,           FST._parse_arguments_lambda,  arguments,      'a, /, b, *c, d=100, **e'),

    (arg,                 FST._parse_arg,               arg,            'a: b'),
    (arg,                 FST._parse_arg,               NodeError,      'a: b = c'),
    (arg,                 FST._parse_arg,               NodeError,      'a, b'),
    (arg,                 FST._parse_arg,               NodeError,      'a, /'),
    (arg,                 FST._parse_arg,               NodeError,      '*, a'),
    (arg,                 FST._parse_arg,               NodeError,      '*a'),
    (arg,                 FST._parse_arg,               NodeError,      '**a'),

    (keyword,             FST._parse_keyword,           keyword,        'a=1'),
    (keyword,             FST._parse_keyword,           keyword,        '**a'),
    (keyword,             FST._parse_keyword,           NodeError,      '1'),
    (keyword,             FST._parse_keyword,           NodeError,      'a'),
    (keyword,             FST._parse_keyword,           NodeError,      'a=1, b=2'),

    (alias,               FST._parse_alias,             alias,          'a'),
    (alias,               FST._parse_alias,             alias,          'a.b'),
    (alias,               FST._parse_alias,             alias,          '*'),
    (alias,               FST._parse_alias,             NodeError,      'a, b'),
    (alias,               FST._parse_alias,             alias,          'a as c'),
    (alias,               FST._parse_alias,             alias,          'a.b as c'),
    (alias,               FST._parse_alias,             SyntaxError,    '* as c'),

    (withitem,            FST._parse_withitem,          withitem,       'a'),
    (withitem,            FST._parse_withitem,          withitem,       'a, b'),
    (withitem,            FST._parse_withitem,          withitem,       '(a, b)'),
    (withitem,            FST._parse_withitem,          withitem,       'a as b'),
    (withitem,            FST._parse_withitem,          NodeError,      'a as b, x as y'),
    (withitem,            FST._parse_withitem,          withitem,       '(a)'),
    (withitem,            FST._parse_withitem,          SyntaxError,    '(a as b)'),
    (withitem,            FST._parse_withitem,          SyntaxError,    '(a as b, x as y)'),

    (pattern,             FST._parse_pattern,           MatchValue,     '42'),
    (pattern,             FST._parse_pattern,           MatchSingleton, 'None'),
    (pattern,             FST._parse_pattern,           MatchSequence,  '[a, *_]'),
    (pattern,             FST._parse_pattern,           MatchSequence,  '[]'),
    (pattern,             FST._parse_pattern,           MatchMapping,   '{"key": _}'),
    (pattern,             FST._parse_pattern,           MatchMapping,   '{}'),
    (pattern,             FST._parse_pattern,           MatchClass,     'SomeClass()'),
    (pattern,             FST._parse_pattern,           MatchClass,     'SomeClass(attr=val)'),
    (pattern,             FST._parse_pattern,           MatchAs,        'as_var'),
    (pattern,             FST._parse_pattern,           MatchAs,        '1 as as_var'),
    (pattern,             FST._parse_pattern,           MatchOr,        '1 | 2 | 3'),
    (pattern,             FST._parse_pattern,           MatchAs,        '_'),
    (pattern,             FST._parse_pattern,           MatchStar,      '*a'),
    (pattern,             FST._parse_pattern,           SyntaxError,    ''),

    (MatchValue,          FST._parse_pattern,           MatchValue,     '42'),
    (MatchSingleton,      FST._parse_pattern,           MatchSingleton, 'None'),
    (MatchSequence,       FST._parse_pattern,           MatchSequence,  '[a, *_]'),
    (MatchSequence,       FST._parse_pattern,           MatchSequence,  '[]'),
    (MatchMapping,        FST._parse_pattern,           MatchMapping,   '{"key": _}'),
    (MatchMapping,        FST._parse_pattern,           MatchMapping,   '{}'),
    (MatchClass,          FST._parse_pattern,           MatchClass,     'SomeClass()'),
    (MatchClass,          FST._parse_pattern,           MatchClass,     'SomeClass(attr=val)'),
    (MatchAs,             FST._parse_pattern,           MatchAs,        'as_var'),
    (MatchAs,             FST._parse_pattern,           MatchAs,        '1 as as_var'),
    (MatchOr,             FST._parse_pattern,           MatchOr,        '1 | 2 | 3'),
    (MatchAs,             FST._parse_pattern,           MatchAs,        '_'),
    (MatchStar,           FST._parse_pattern,           MatchStar,      '*a'),

    ('expr',              FST._parse_expr,              Tuple,          ' *a,  # tail'),
    ('expr_callarg',      FST._parse_expr_callarg,      Starred,        ' *not a  # tail'),
    ('expr_slice',        FST._parse_expr_slice,        Slice,          ' a:b:c  # tail'),
    ('expr_slice',        FST._parse_expr_slice,        Yield,          ' yield  # tail'),
    ('boolop',            FST._parse_boolop,            And,            ' and  # tail'),
    ('binop',             FST._parse_binop,             RShift,         ' >>  # tail'),
    ('augop',             FST._parse_augop,             SyntaxError,    ' >>=  # tail'),  # this can never be as a statement can never be enclosed and a line continuation cannot follow a comment
    ('unaryop',           FST._parse_unaryop,           Invert,         ' ~  # tail'),
    ('cmpop',             FST._parse_cmpop,             GtE,            ' >=  # tail'),
    ('comprehension',     FST._parse_comprehension,     comprehension,  ' for i in j  # tail'),
    ('arguments',         FST._parse_arguments,         arguments,      ' a: list[str], /, b: int = 1, *c, d=100, **e  # tail'),
    ('arguments_lambda',  FST._parse_arguments_lambda,  arguments,      ' a, /, b, *c, d=100, **e  # tail'),
    ('arg',               FST._parse_arg,               arg,            ' a: b  # tail'),
    ('keyword',           FST._parse_keyword,           keyword,        ' a=1  # tail'),
    ('alias_dotted',      FST._parse_alias_dotted,      alias,          ' a.b  # tail'),
    ('alias_star',        FST._parse_alias_star,        alias,          ' *  # tail'),
    ('withitem',          FST._parse_withitem,          withitem,       ' a as b,  # tail'),
    ('pattern',           FST._parse_pattern,           MatchOr,        ' 1 | 2 | 3  # tail'),
    ('pattern',           FST._parse_pattern,           MatchStar,      ' *a  # tail'),
]

if PYGE11:
    PARSE_TESTS.extend([
        ('ExceptHandler',     FST._parse_ExceptHandler,     ExceptHandler,  'except* Exception: pass'),

        ('expr_slice',        FST._parse_expr_slice,        Tuple,          '*s'),
        ('expr_slice',        FST._parse_expr_slice,        Tuple,          '*not a'),
        ('expr_sliceelt',     FST._parse_expr_sliceelt,     Starred,        '*not a'),

        (ExceptHandler,       FST._parse_ExceptHandler,     ExceptHandler,  'except* Exception: pass'),

        ('arg',               FST._parse_arg,               arg,            ' a: *b  # tail'),
    ])

if PYGE12:
    PARSE_TESTS.extend([
        ('type_param',        FST._parse_type_param,        TypeVar,        'a: int'),
        ('type_param',        FST._parse_type_param,        ParamSpec,      '**a'),
        ('type_param',        FST._parse_type_param,        TypeVarTuple,   '*a'),

        (type_param,          FST._parse_type_param,        TypeVar,        'a: int'),
        (TypeVar,             FST._parse_type_param,        TypeVar,        'a: int'),
        (type_param,          FST._parse_type_param,        ParamSpec,      '**a'),
        (ParamSpec,           FST._parse_type_param,        ParamSpec,      '**a'),
        (type_param,          FST._parse_type_param,        TypeVarTuple,   '*a'),
        (TypeVarTuple,        FST._parse_type_param,        TypeVarTuple,   '*a'),

        ('type_param',        FST._parse_type_param,        TypeVar,        ' a: int  # tail'),
    ])

if PYGE13:
    PARSE_TESTS.extend([
        ('type_param',        FST._parse_type_param,        TypeVar,        'a: int = int'),
        ('type_param',        FST._parse_type_param,        ParamSpec,      '**a = {T: int, U: str}'),
        ('type_param',        FST._parse_type_param,        TypeVarTuple,   '*a = (int, str)'),

        (type_param,          FST._parse_type_param,        TypeVar,        'a: int = int'),
        (TypeVar,             FST._parse_type_param,        TypeVar,        'a: int = int'),
        (type_param,          FST._parse_type_param,        ParamSpec,      '**a = {T: int, U: str}'),
        (ParamSpec,           FST._parse_type_param,        ParamSpec,      '**a = {T: int, U: str}'),
        (type_param,          FST._parse_type_param,        TypeVarTuple,   '*a = (int, str)'),
        (TypeVarTuple,        FST._parse_type_param,        TypeVarTuple,   '*a = (int, str)'),
    ])


def read(fnm):
    with open(fnm) as f:
        return f.read()


def regen_pars_data():
    newlines = []

    for src, elt, *_ in PARS_DATA:
        src   = src.strip()
        t     = parse(src)
        f     = eval(f't.{elt}', {'t': t}).f
        l     = f.pars()
        ssrc  = f.get_src(*l)

        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        newlines.append('(r"""')
        newlines.extend(f'''{src}\n""", {elt!r}, r"""\n{ssrc}\n"""),\n'''.split('\n'))

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PARS_DATA = [')
    stop  = lines.index(']  # END OF PARS_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_precedence_data():
    newlines = []

    for dst, *attrs in PRECEDENCE_DST_STMTS + PRECEDENCE_DST_EXPRS + PRECEDENCE_SRC_EXPRS:
        for src, *_ in PRECEDENCE_SRC_EXPRS:
            for attr in attrs:
                d            = dst.copy()
                s            = src.body[0].value.copy()
                is_stmt      = isinstance(d.a, stmt)
                f            = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})
                is_unpar_tup = False if is_stmt else (d.body[0].value.is_parenthesized_tuple() is False)

                f.pfield.set(f.parent.a, s.a)

                truth = ast_unparse(f.root.a)

                if is_unpar_tup:
                    truth = truth[1:-1]

                newlines.append(f'    {truth!r},')

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PRECEDENCE_DATA = [')
    stop  = lines.index(']  # END OF PRECEDENCE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


class TestFST(unittest.TestCase):
    def test__unparse(self):
        self.assertEqual('for i in j', FST._unparse(FST('[i for i in j]').generators[0].a))

        for op in (Add, Sub, Mult, Div, Mod, Pow, LShift, RShift, BitOr, BitXor, BitAnd, FloorDiv, And, Or):
            self.assertIs(OPCLS2STR[op], FST._unparse(FST(f'a {OPCLS2STR[op]} b').op.a))

        for op in (Add, Sub, Mult, Div, Mod, Pow, LShift, RShift, BitOr, BitXor, BitAnd, FloorDiv):
            self.assertIs(OPCLS2STR[op], FST._unparse(FST(f'a {OPCLS2STR[op]}= b').op.a))

        for op in (Invert, Not, UAdd, USub):
            self.assertIs(OPCLS2STR[op], FST._unparse(FST(f'{OPCLS2STR[op]} a').op.a))

        for op in (Eq, NotEq, Lt, LtE, Gt, GtE, Is, IsNot, In, NotIn):
            self.assertIs(OPCLS2STR[op], FST._unparse(FST(f'a {OPCLS2STR[op]} b').ops[0].a))

    def test__parse(self):
        for mode, func, res, src in PARSE_TESTS:
            try:
                test = 'parse'

                try:
                    ast = FST._parse(src, mode)

                except (SyntaxError, NodeError) as exc:
                    if res is not exc.__class__:
                        raise

                else:
                    if issubclass(res, Exception):
                        raise RuntimeError(f'expected {res.__name__}')

                    ref = func(src)

                    self.assertEqual(ast.__class__, res)
                    self.assertTrue(compare_asts(ast, ref, locs=True))

                if issubclass(res, Exception):
                    continue

                # reparse

                if src != '*=':  # augassign is ambiguous and syntactically impossible
                    test = 'reparse'
                    unp  = ((s := FST._unparse(ast)) and s.lstrip()) or src  # 'lstrip' because comprehension has leading space, 'or src' because unparse of operators gives nothing
                    ast2 = FST._parse(unp, mode)

                    compare_asts(ast, ast2, raise_=True)

                # trailing newline

                if src != '*=':  # augassign is ambiguous and syntactically impossible
                    test = 'newline'
                    srcn = src + '\n'
                    ast  = FST._parse(srcn, mode)

                # # IndentationError

                # test = 'indent'

                # if not src.startswith('\n') and src.strip():  # won't get IndentationError on stuff that starts with newlines or empty arguments
                #     src = ' ' + src

                #     self.assertRaises(IndentationError, FST._parse, src, mode)
                #     self.assertRaises(IndentationError, func, src)

            except Exception:
                print()
                print(test, mode, src, res, func)

                raise

    def test__parse_special(self):
        self.assertRaises(SyntaxError, FST._parse_expr, 'i for i in j')
        self.assertRaises(SyntaxError, FST._parse_expr_slice, 'i for i in j')
        self.assertRaises(SyntaxError, FST._parse_expr_callarg, 'i for i in j')

        self.assertRaises(SyntaxError, FST._parse_withitem, 'i for i in j')
        self.assertRaises(SyntaxError, FST._parse_withitem, '')

    # def test__parse_trailing_comment_without_newline(self):
    #     a = FST._parse_expr(' *a, # line')
    #     self.assertEqual()

    def test___new__(self):
        f = FST(None, 'exec')
        self.assertEqual('', f.src)
        self.assertIsInstance(f.a, Module)
        self.assertEqual([], f.a.body)

        f = FST(None, 'single')
        self.assertEqual('', f.src)
        self.assertIsInstance(f.a, Interactive)
        self.assertEqual([], f.a.body)

        f = FST(None, 'eval')
        self.assertEqual('None', f.src)
        self.assertIsInstance(f.a, Expression)
        self.assertIsInstance(f.a.body, expr)

        f = FST('i = 1', 'exec')
        self.assertEqual('i = 1', f.src)
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Assign)

        f = FST('i = 1', 'single')
        self.assertEqual('i = 1', f.src)
        self.assertIsInstance(f.a, Interactive)
        self.assertIsInstance(f.a.body[0], Assign)

        f = FST('i', 'eval')
        self.assertEqual('i', f.src)
        self.assertIsInstance(f.a, Expression)
        self.assertIsInstance(f.a.body, Name)

        v = PYVER
        f = FST.fromsrc('i', 'exec', filename='fnm', type_comments=True, feature_version=v)

        g = FST('j', 'exec', from_=f)
        self.assertEqual('fnm', g.parse_params['filename'])
        self.assertIs(True, g.parse_params['type_comments'])
        self.assertEqual(v, g.parse_params['feature_version'])

        g = FST('j', 'exec', from_=f, filename='blah', type_comments=False, feature_version=None)
        self.assertEqual('blah', g.parse_params['filename'])
        self.assertIs(False, g.parse_params['type_comments'])
        self.assertIs(None, g.parse_params['feature_version'])

        # full parse tests

        for mode, func, res, src in PARSE_TESTS:
            try:
                try:
                    fst = FST(src, mode)

                except (SyntaxError, NodeError) as exc:
                    if res is not exc.__class__:
                        raise

                else:
                    if issubclass(res, Exception):
                        raise RuntimeError(f'expected {res.__name__}')

                    ref = func(src)

                    self.assertEqual(src, fst.src)
                    self.assertEqual(fst.a.__class__, res)
                    self.assertTrue(compare_asts(fst.a, ref, locs=True))

            except Exception:
                print()
                print(mode, src, res, func)

                raise

    def test_infer_indent(self):
        self.assertEqual('    ', FST.fromsrc('def f(): pass').indent)
        self.assertEqual('  ', FST.fromsrc('def f():\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('async def f():\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('class cls:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('with a:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('async with a:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('for a in b:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('for a in b: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('for a in b:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST.fromsrc('async for a in b:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('async for a in b: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('async for a in b:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST.fromsrc('while a:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('while a: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('while a:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST.fromsrc('if 1:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('if 1: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('if 1:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST.fromsrc('try:\n  pass\nexcept: pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept: pass\nelse: pass\nfinally:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept: pass\nelse:\n  pass\nfinally: pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept:\n  pass\nelse: pass\nfinally: pass').indent)
        self.assertEqual('  ', FST.fromsrc('try:\n  pass\nexcept: pass\nelse: pass\nfinally: pass').indent)

        if PYGE12:
            self.assertEqual('  ', FST.fromsrc('try:\n  pass\nexcept* Exception: pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception:\n  pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception: pass\nelse:\n  pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception: pass\nelse: pass\nfinally:\n  pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception: pass\nelse:\n  pass\nfinally: pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception:\n  pass\nelse: pass\nfinally: pass').indent)
            self.assertEqual('  ', FST.fromsrc('try:\n  pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').indent)

    def test_unmake_fst_in_operations(self):
        f = parse('(1, 2, 3)').f
        g = parse('(4, 5)').f
        i = f.body[0].value.elts[1]
        h = g.body[0]
        f.body[0].value.put_slice(g, 1, 2)
        self.assertEqual('(1, 4, 5, 3)', f.src)
        self.assertIsNone(i.a)
        self.assertIsNone(h.a)
        self.assertIsNone(g.a)

        f = parse('[1, 2, 3]').f
        g = parse('[4, 5]').f
        i = f.body[0].value.elts[1]
        h = g.body[0]
        f.body[0].value.put_slice(g, 1, 2)
        self.assertEqual('[1, 4, 5, 3]', f.src)
        self.assertIsNone(i.a)
        self.assertIsNone(h.a)
        self.assertIsNone(g.a)

        f = parse('{1, 2, 3}').f
        g = parse('{4, 5}').f
        i = f.body[0].value.elts[1]
        h = g.body[0]
        f.body[0].value.put_slice(g, 1, 2)
        self.assertEqual('{1, 4, 5, 3}', f.src)
        self.assertIsNone(i.a)
        self.assertIsNone(h.a)
        self.assertIsNone(g.a)

        f = parse('{1:1, 1:1, 3:3}').f
        g = parse('{4:4, 5:5}').f
        ik = f.body[0].value.keys[1]
        iv = f.body[0].value.values[1]
        h = g.body[0]
        f.body[0].value.put_slice(g, 1, 2)
        self.assertEqual('{1:1, 4:4, 5:5, 3:3}', f.src)
        self.assertIsNone(ik.a)
        self.assertIsNone(iv.a)
        self.assertIsNone(h.a)
        self.assertIsNone(g.a)

    def test_src(self):
        self.assertEqual('and', FST('a and b').op.src)
        self.assertEqual('or', FST('a or b').op.src)
        self.assertEqual(['and'], FST('a and b').op.lines)
        self.assertEqual(['or'], FST('a or b').op.lines)

    def test_loc(self):
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.loc)  # arguments
        self.assertEqual((0, 5, 0, 8), parse('with f(): pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((1, 2, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.loc)  # match_case
        self.assertEqual((0, 3, 0, 25), parse('[i for i in range(5) if i]').body[0].value.generators[0].f.loc)  # comprehension
        self.assertEqual((0, 3, 0, 25), parse('(i for i in range(5) if i)').body[0].value.generators[0].f.loc)  # comprehension

        self.assertEqual((0, 5, 0, 12), parse('with ( f() ): pass').body[0].items[0].f.loc)  # withitem only context_expr w/ parens
        self.assertEqual((0, 5, 0, 21), parse('with ( f() ) as ( f ): pass').body[0].items[0].f.loc)  # withitem w/ parens
        self.assertEqual((1, 2, 1, 28), parse('match a:\n  case ( 2 ) if a == 1: pass').body[0].cases[0].f.loc)  # match_case w/ parens
        self.assertEqual((0, 3, 0, 33), parse('[i for ( i ) in range(5) if ( i ) ]').body[0].value.generators[0].f.loc)  # comprehension w/ parens
        self.assertEqual((0, 3, 0, 33), parse('(i for ( i ) in range(5) if ( i ) )').body[0].value.generators[0].f.loc)  # comprehension w/ parens

        self.assertEqual('f() as ( f )', parse('with f() as ( f ): pass').body[0].items[0].f.src)
        self.assertEqual('( f() ) as f', parse('with ( f() ) as f: pass').body[0].items[0].f.src)
        self.assertEqual('( f() ) as ( f )', parse('with ( f() ) as ( f ): pass').body[0].items[0].f.src)
        self.assertEqual('( f() ) as ( f )', parse('with ( f() ) as ( f ), ( g() ) as ( g ): pass').body[0].items[0].f.src)
        self.assertEqual('( g() ) as ( g )', parse('with ( f() ) as ( f ), ( g() ) as ( g ): pass').body[0].items[1].f.src)
        self.assertEqual('( f() )', parse('with ( f() ): pass').body[0].items[0].f.src)
        self.assertEqual('a as b', parse('with (a as b): pass').body[0].items[0].f.src)
        self.assertEqual('a as b', parse('with (a as b, c as d): pass').body[0].items[0].f.src)
        self.assertEqual('c as d', parse('with (a as b, c as d): pass').body[0].items[1].f.src)
        self.assertEqual('c as d', parse('with (a as b, c as d, e as f): pass').body[0].items[1].f.src)
        self.assertEqual('e as f', parse('with (a as b, c as d, e as f): pass').body[0].items[2].f.src)

        self.assertEqual('case 1: pass', parse('match a:\n  case 1: pass').body[0].cases[0].f.src)
        self.assertEqual('case (1 | 2): pass', parse('match a:\n  case (1 | 2): pass').body[0].cases[0].f.src)
        self.assertEqual('case ( 2 ) if a == 1: pass', parse('match a:\n  case ( 2 ) if a == 1: pass').body[0].cases[0].f.src)

        self.assertEqual('for ( i ) in range(5) if ( i )', parse('[ ( i ) for ( i ) in range(5) if ( i ) ]').body[0].value.generators[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('( ( i ) for ( i ) in range(5) if ( i ) )').body[0].value.generators[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('[ ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) ]').body[0].value.generators[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('( ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) )').body[0].value.generators[0].f.src)
        self.assertEqual('for ( j ) in range(6) if ( j )', parse('[ ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) ]').body[0].value.generators[1].f.src)
        self.assertEqual('for ( j ) in range(6) if ( j )', parse('( ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) )').body[0].value.generators[1].f.src)

        self.assertEqual('', parse('def f(): pass').body[0].args.f.src)
        self.assertEqual('a', parse('def f(a): pass').body[0].args.f.src)
        self.assertEqual('a', parse('def f( a ): pass').body[0].args.f.src)
        self.assertEqual('', parse('lambda: None').body[0].value.args.f.src)
        self.assertEqual('a = ( 1 )', parse('lambda a = ( 1 ) : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = 2', parse('lambda *, z, a, b = 2: None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = 2', parse('lambda *, z, a, b = 2 : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 )', parse('lambda *, z, a, b = ( 2 ): None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 )', parse('lambda *, z, a, b = ( 2 ) : None').body[0].value.args.f.src)
        self.assertEqual('*s, a, b = ( 2 )', parse('lambda *s, a, b = ( 2 ) : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 ),', parse('lambda *, z, a, b = ( 2 ),: None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 ),', parse('lambda *, z, a, b = ( 2 ), : None').body[0].value.args.f.src)
        self.assertEqual('**ss', parse('lambda **ss : None').body[0].value.args.f.src)
        self.assertEqual('a, /', parse('lambda a, /: None').body[0].value.args.f.src)
        self.assertEqual('a, /', parse('lambda  a, / : None').body[0].value.args.f.src)
        self.assertEqual('a, /,', parse('lambda a, /, : None').body[0].value.args.f.src)
        self.assertEqual('a, / ,', parse('lambda  a, / , : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = 2', parse('def f(*, z, a, b = 2): pass').body[0].args.f.src)
        self.assertEqual('*, z, a, b = ( 2 )', parse('def f(*, z, a, b = ( 2 )): pass').body[0].args.f.src)
        self.assertEqual('*, z, a, b = ( 2 )', parse('def f( *, z, a, b = ( 2 ) ): pass').body[0].args.f.src)
        self.assertEqual('*s, a, b = ( 2 )', parse('def f( *s, a, b = ( 2 ) ): pass').body[0].args.f.src)
        self.assertEqual('*, z, a, b = ( 2 ),', parse('def f( *, z, a, b = ( 2 ), ): pass').body[0].args.f.src)
        self.assertEqual('**ss', parse('def f( **ss ): pass').body[0].args.f.src)
        self.assertEqual('a, /', parse('def f(a, /): pass').body[0].args.f.src)
        self.assertEqual('a, /', parse('def f( a, / ): pass').body[0].args.f.src)
        self.assertEqual('a, /,', parse('def f(a, /,): pass').body[0].args.f.src)
        self.assertEqual('a, / ,', parse('def f(a, / , ): pass').body[0].args.f.src)

        # loc calculated from children at root

        self.assertEqual((0, 0, 0, 12), parse('match a:\n case 1: pass').body[0].cases[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 6), parse('with a as b: pass').body[0].items[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 1), parse('def f(a): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 1), parse('lambda a: None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 10), parse('[i for i in j]').body[0].value.generators[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 15), parse('[i for i in j if k]').body[0].value.generators[0].f.copy().loc)

        self.assertEqual((0, 0, 0, 9), parse('lambda a = ( 1 ) : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 14), parse('lambda *, z, a, b = 2: None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 14), parse('lambda *, z, a, b = 2 : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 18), parse('lambda *, z, a, b = ( 2 ): None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 18), parse('lambda *, z, a, b = ( 2 ) : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 16), parse('lambda *s, a, b = ( 2 ) : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 19), parse('lambda *, z, a, b = ( 2 ),: None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 19), parse('lambda *, z, a, b = ( 2 ), : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 4), parse('lambda **ss : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 14), parse('def f(*, z, a, b = 2): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 18), parse('def f(*, z, a, b = ( 2 )): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 18), parse('def f( *, z, a, b = ( 2 ) ): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 16), parse('def f( *s, a, b = ( 2 ) ): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 19), parse('def f( *, z, a, b = ( 2 ), ): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 4), parse('def f( **ss ): pass').body[0].args.f.copy().loc)

        # special cases

        self.assertEqual((0, 12, 0, 14), FST('f"a{(lambda *a: b)}"', 'exec').body[0].value.values[1].value.args.loc)

    def test_bloc(self):
        ast = parse('@deco\nclass cls:\n @deco\n def meth():\n  @deco\n  class fcls: pass')

        self.assertEqual((0, 0, 5, 18), ast.f.loc)
        self.assertEqual((0, 0, 5, 18), ast.f.bloc)
        self.assertEqual((1, 0, 5, 18), ast.body[0].f.loc)
        self.assertEqual((0, 0, 5, 18), ast.body[0].f.bloc)
        self.assertEqual((3, 1, 5, 18), ast.body[0].body[0].f.loc)
        self.assertEqual((2, 1, 5, 18), ast.body[0].body[0].f.bloc)
        self.assertEqual((5, 2, 5, 18), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((4, 2, 5, 18), ast.body[0].body[0].body[0].f.bloc)

    def test_fromsrc_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromsrc(read(fnm))

            for ast in walk(fst.a):
                ast.f.loc

            fst.verify(raise_=True)

    def test_fromast_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_parse(read(fnm)))

            for ast in walk(fst.a):
                ast.f.loc

            fst.verify(raise_=True)

    def test_fromast_special(self):
        f = FST.fromast(ast_parse('*t').body[0].value)
        self.assertEqual('*t', f.src)
        self.assertIsInstance(f.a, Starred)

    def test_verify(self):
        ast = parse('i = 1')
        ast.f.verify(raise_=True)

        ast.body[0].lineno = 100

        self.assertRaises(WalkFail, ast.f.verify, raise_=True)
        self.assertEqual(None, ast.f.verify(raise_=False))

        for mode, func, res, src in PARSE_TESTS:
            try:
                if issubclass(res, Exception):
                    continue

                fst = FST(src, mode)

                fst.verify(mode)
                fst.verify()

                if isinstance(a := fst.a, Expression):
                    a = a.body
                elif isinstance(a, (Module, Interactive)):
                    a = a.body[0]

                if end_col_offset := getattr(a, 'end_col_offset', None):
                    a.end_col_offset = end_col_offset + 1

                    self.assertFalse(fst.verify(mode, raise_=False))

            except Exception:
                print()
                print(mode, src, res, func)

                raise

    def test_walk(self):
        a = parse("""
def f(a, b=1, *c, d=2, **e): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.args[0].f)
        self.assertIs(l[2], a.args[1].f)
        self.assertIs(l[3], a.defaults[0].f)
        self.assertIs(l[4], a.vararg.f)
        self.assertIs(l[5], a.kwonlyargs[0].f)
        self.assertIs(l[6], a.kw_defaults[0].f)
        self.assertIs(l[7], a.kwarg.f)

        a = parse("""
def f(*, a, b, c=1, d=2, **e): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.kwonlyargs[0].f)
        self.assertIs(l[2], a.kwonlyargs[1].f)
        self.assertIs(l[3], a.kwonlyargs[2].f)
        self.assertIs(None, a.kw_defaults[0])
        self.assertIs(None, a.kw_defaults[1])
        self.assertIs(l[4], a.kw_defaults[2].f)
        self.assertIs(l[5], a.kwonlyargs[3].f)
        self.assertIs(l[6], a.kw_defaults[3].f)
        self.assertIs(l[7], a.kwarg.f)

        a = parse("""
def f(a, b=1, /, c=2, d=3, *e, f=4, **g): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.posonlyargs[0].f)
        self.assertIs(l[2], a.posonlyargs[1].f)
        self.assertIs(l[3], a.defaults[0].f)
        self.assertIs(l[4], a.args[0].f)
        self.assertIs(l[5], a.defaults[1].f)
        self.assertIs(l[6], a.args[1].f)
        self.assertIs(l[7], a.defaults[2].f)
        self.assertIs(l[8], a.vararg.f)
        self.assertIs(l[9], a.kwonlyargs[0].f)
        self.assertIs(l[10], a.kw_defaults[0].f)
        self.assertIs(l[11], a.kwarg.f)

        a = parse("""
def f(a=1, /, b=2): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.posonlyargs[0].f)
        self.assertIs(l[2], a.defaults[0].f)
        self.assertIs(l[3], a.args[0].f)
        self.assertIs(l[4], a.defaults[1].f)

        a = parse("""
call(a, b=1, *c, d=2, **e)
            """.strip()).body[0].value
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.func.f)
        self.assertIs(l[2], a.args[0].f)
        self.assertIs(l[3], a.keywords[0].f)
        self.assertIs(l[4], a.keywords[0].value.f)
        self.assertIs(l[5], a.args[1].f)
        self.assertIs(l[6], a.args[1].value.f)
        self.assertIs(l[7], a.keywords[1].f)
        self.assertIs(l[8], a.keywords[1].value.f)
        self.assertIs(l[9], a.keywords[2].f)
        self.assertIs(l[10], a.keywords[2].value.f)

        a = parse("""
i = 1
self.save_reduce(obj=obj, *rv)
            """.strip()).body[1].value
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.func.f)
        self.assertIs(l[2], a.func.value.f)
        self.assertIs(l[3], a.keywords[0].f)
        self.assertIs(l[4], a.keywords[0].value.f)
        self.assertIs(l[5], a.args[0].f)
        self.assertIs(l[6], a.args[0].value.f)

        f = parse('[] + [i for i in l]').body[0].value.f
        self.assertEqual(12, len(list(f.walk(False))))
        self.assertEqual(8, len(list(f.walk('all'))))
        self.assertEqual(7, len(list(f.walk(True))))
        # self.assertEqual(1, len(list(f.walk('allown'))))  # doesn't support
        self.assertEqual(4, len(list(f.walk('own'))))

    def test_walk_scope(self):
        fst = FST.fromsrc("""
def f(a, /, b, *c, d, **e):
    f = 1
    [i for i in g if i]
    {k: v for k, v in h if k and v}
    @deco1
    def func(l=m): hidden
    @deco2
    class sup(cls, meta=moto): hidden
    lambda n=o, **kw: hidden
            """.strip()).a.body[0].f
        self.assertEqual(['f', 'g', 'h', 'deco1', 'm', 'deco2', 'cls', 'moto', 'o'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])
        self.assertEqual(['a', 'b', 'c', 'd', 'e'],
                         [f.a.arg for f in fst.walk(scope=True) if isinstance(f.a, arg)])

        l = []
        for f in (gen := fst.walk(True, scope=True)):
            if isinstance(f.a, Name):
                l.append(f.a.id)
            elif isinstance(f.a, ClassDef):
                gen.send(True)
        self.assertEqual(['f', 'g', 'h', 'deco1', 'm', 'deco2', 'cls', 'moto', 'hidden', 'o'], l)

        fst = FST.fromsrc("""[z for a in b if (c := a)]""".strip()).a.body[0].value.f
        self.assertEqual(['z', 'a', 'c', 'a'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

        fst = FST.fromsrc("""[z for a in b if (c := a)]""".strip()).a.body[0].f
        self.assertEqual(['b', 'c'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

        fst = FST.fromsrc("""[z for a in b if b in [c := i for i in j if i in {d := k for k in l}]]""".strip()).a.body[0].value.f
        self.assertEqual(['z', 'a', 'b', 'c', 'j', 'd'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

    def test_walk_bulk(self):
        for fnm in PYFNMS:
            ast       = FST.fromsrc(read(fnm)).a
            bln, bcol = 0, 0

            for f in (gen := ast.f.walk(True)):
                if isinstance(f.a, (JoinedStr, TemplateStr)):  # these are borked
                    gen.send(False)

                    continue

                self.assertTrue(f.bln > bln or (f.bln == bln and f.bcol >= bcol))

                lof = list(f.walk(True, self_=False, recurse=False))
                lob = list(f.walk(True, self_=False, recurse=False, back=True))

                self.assertEqual(lof, lob[::-1])

                lf, c = [], None
                while c := f.next_child(c, True): lf.append(c)
                self.assertEqual(lf, lof)

                lb, c = [], None
                while c := f.prev_child(c, True): lb.append(c)
                self.assertEqual(lb, lob)

                bln, bcol = f.bln, f.bcol

    def test_walk_modify(self):
        fst = parse('if 1:\n a\n b\n c\nelse:\n d\n e').body[0].f
        i   = 0

        for f in fst.walk(self_=False):
            if f.pfield.name in ('body', 'orelse'):
                f.replace(str(i := i + 1), raw=False)

        self.assertEqual(fst.src, 'if 1:\n 1\n 2\n 3\nelse:\n 4\n 5')

        fst = parse('[a, b, c]').body[0].f
        i   = 0

        for f in fst.walk(self_=False):
            if f.pfield.name == 'elts':
                f.replace(str(i := i + 1), raw=False)

        self.assertEqual(fst.src, '[1, 2, 3]')

    def test_next_prev(self):
        fst = parse('a and b and c and d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.op.f)
        self.assertIs((f := fst.next_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.op.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        if PYGE12:
            fst = parse('@deco\ndef f[T, U](a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
            a = fst.a
            f = None
            self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, True)), a.args.f)
            self.assertIs((f := fst.next_child(f, True)), a.returns.f)
            self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, True)), None)
            f = None
            self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, False)), a.args.f)
            self.assertIs((f := fst.next_child(f, False)), a.returns.f)
            self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, False)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, True)), a.args.f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, True)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, False)), a.args.f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('@deco\ndef f(a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.args.f)
        self.assertIs((f := fst.next_child(f, True)), a.returns.f)
        self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.args.f)
        self.assertIs((f := fst.next_child(f, False)), a.returns.f)
        self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, True)), a.args.f)
        self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, False)), a.args.f)
        self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('a <= b == c >= d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.left.f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.left.f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.left.f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.left.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('match a:\n case {1: a, 2: b, **rest}: pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('match a:\n case cls(1, 2, a=3, b=4): pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.cls.f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.cls.f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

    def test_next_prev_vs_walk(self):
        def test1(src):
            f = FST.fromsrc(src).a.body[0].args.f
            m = list(f.walk(True, self_=False, recurse=False))

            l, c = [], None
            while c := f.next_child(c): l.append(c)
            self.assertEqual(l, m)

            l, c = [], None
            while c := f.prev_child(c): l.append(c)
            self.assertEqual(l, m[::-1])

        test1('def f(**a): apass')
        test1('def f(*, e, d, c=3, b=2, **a): pass')
        test1('def f(*f, e, d, c=3, b=2, **a): pass')
        test1('def f(g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(h, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(i, /, h, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j, i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, e, d, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, **a): pass')
        test1('def f(j, i, /, h, g, **a): pass')
        test1('def f(j, i, /, **a): pass')
        test1('def f(j, i, /, *f, **a): pass')
        test1('def f(j=7, i=6, /, **a): pass')
        test1('def f(**a): pass')
        test1('def f(b=1, **a): pass')
        test1('def f(a, /): pass')
        test1('def f(a, /, b): pass')
        test1('def f(a, /, b, c=1): pass')
        test1('def f(a, /, b, c=1, *d): pass')
        test1('def f(a, /, b, c=1, *d, e): pass')
        test1('def f(a, /, b, c=1, *d, e, f=2): pass')
        test1('def f(a, /, b, c=1, *d, e, f=2, **g): pass')
        test1('def f(a=1, b=2, *e): pass')
        test1('def f(a, b, /, c, d, *e): pass')
        test1('def f(a, b, /, c, d=1, *e): pass')
        test1('def f(a, b, /, c=2, d=1, *e): pass')
        test1('def f(a, b=3, /, c=2, d=1, *e): pass')
        test1('def f(a=4, b=3, /, c=2, d=1, *e): pass')
        test1('def f(a, b=1, /, c=2, d=3, *e, f=4, **g): pass')
        test1('def __init__(self, max_size=0, *, ctx, pending_work_items, shutdown_lock, thread_wakeup): pass')

        def test2(src):
            f = FST.fromsrc(src).a.body[0].value.f
            m = list(f.walk(True, self_=False, recurse=False))

            l, c = [], None
            while c := f.next_child(c): l.append(c)
            self.assertEqual(l, m)

            l, c = [], None
            while c := f.prev_child(c): l.append(c)
            self.assertEqual(l, m[::-1])

        test2('call(a=1, *b)')
        test2('call()')
        test2('call(a, b)')
        test2('call(c=1, d=1)')
        test2('call(a, b, c=1, d=1)')
        test2('call(a, b, *c, d)')
        test2('call(a, b, *c, d=2)')
        test2('call(a, b=1, *c, d=2)')
        test2('call(a, b=1, *c, d=2, **e)')
        test2('system_message(message, level=level, type=type,*children, **kwargs)')

    def test_next_prev_step_vs_walk(self):
        def test(src):
            fst = FST.fromsrc(src.strip())

            f, l = fst, []
            while f := f.step_fwd(True): l.append(f)
            self.assertEqual(l, list(fst.walk(True, self_=False)))

            f, l = fst, []
            while f := f.step_fwd(False): l.append(f)
            self.assertEqual(l, list(fst.walk(False, self_=False)))

            f, l = fst, []
            while f := f.step_fwd('own'): l.append(f)
            self.assertEqual(l, list(fst.walk('own', self_=False)))

            f, l = fst, []
            while f := f.step_fwd('allown'): l.append(f)
            self.assertEqual(l, [g for g in fst.walk(True, self_=False) if g.has_own_loc])

            f, l = fst, []
            while f := f.step_back(True): l.append(f)
            self.assertEqual(l, list(fst.walk(True, self_=False, back=True)))

            f, l = fst, []
            while f := f.step_back(False): l.append(f)
            self.assertEqual(l, list(fst.walk(False, self_=False, back=True)))

            f, l = fst, []
            while f := f.step_back('own'): l.append(f)
            self.assertEqual(l, list(fst.walk('own', self_=False, back=True)))

            f, l = fst, []
            while f := f.step_back('allown'): l.append(f)
            self.assertEqual(l, [g for g in fst.walk(True, self_=False, back=True) if g.has_own_loc])

        test('''
def f(a=1, b=2) -> int:
    i = [[k for k in range(j)] for i in range(5) if i for j in range(i) if j]
            ''')

        test('''
match a:
    case 1 | 2:
          pass
            ''')

        test('''
with a as b, c as d:
    pass
            ''')

    def test_child_path(self):
        f = parse('if 1: a = (1, 2, {1: 2})').f
        p = f.child_path(f.body[0].body[0].value.elts[2].keys[0], True)

        self.assertEqual(p, 'body[0].body[0].value.elts[2].keys[0]')
        self.assertIs(f.child_from_path(p), f.body[0].body[0].value.elts[2].keys[0])

        p = f.child_path(f.body[0].body[0].value.elts[2].keys[0], False)

        self.assertEqual(p, [astfield(name='body', idx=0), astfield(name='body', idx=0),
                             astfield(name='value', idx=None), astfield(name='elts', idx=2),
                             astfield(name='keys', idx=0)])
        self.assertIs(f.child_from_path(p), f.body[0].body[0].value.elts[2].keys[0])

        self.assertRaises(ValueError, f.child_path, parse('1').f)

    def test_is_atom(self):
        self.assertIs(False, parse('1 + 2').body[0].value.f.is_atom())
        self.assertEqual('unenclosable', parse('f()').body[0].value.f.is_atom())
        self.assertEqual('pars', parse('(1 + 2)').body[0].value.f.is_atom())
        self.assertIs(False, parse('(1 + 2)').body[0].value.f.is_atom(pars=False))

        self.assertIs(False, parse('1, 2').body[0].value.f.is_atom())
        self.assertIs(True, parse('(1, 2)').body[0].value.f.is_atom())
        self.assertIs(True, parse('[1, 2]').body[0].value.f.is_atom())

        self.assertIs(False, parse('match a:\n case 1, 2: pass').body[0].cases[0].pattern.f.is_atom())
        self.assertIs(True, parse('match a:\n case (1, 2): pass').body[0].cases[0].pattern.f.is_atom())
        self.assertIs(True, parse('match a:\n case [1, 2]: pass').body[0].cases[0].pattern.f.is_atom())

    def test_is_enclosed_special(self):
        # Call
        # JoinedStr
        # TemplateStr
        # Constant - str
        # Attribute
        # Subscript
        # MatchClass
        # MatchStar
        # MatchAs
        # cmpop
        # comprehension
        # arguments
        # arg
        # alias
        # withitem

        self.assertTrue(FST('f(a, b=1)', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('f\\\n(a, b=1)', 'exec').body[0].copy(pars=False).value.is_enclosed_or_line())
        self.assertTrue(FST('(f\\\n(a, b=1))', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(f\n(a, b=1))', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(f(\na\n,\nb\n=\n1))', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(f(\na\n,\nb\n=\n"()"))', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

        if PYGE12:
            self.assertTrue(FST(r'''
(f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
            self.assertFalse(FST(r'''
(f"a{(1,

2)}b" f"""{3}

{4}
{5}"""
f"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

            self.assertTrue(FST(r'''
(f"a" f"""c
b""" f"d\
\
e")
                '''.strip(), 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

            self.assertFalse(FST(r'''
(f"a" f"""c
b"""

f"d\
\
e")
                '''.strip(), 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('a.b', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(a\n.\nb)', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n.\\\nb)', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('a[b]', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(a\n[\nb\n])', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(a\n[(\nb\n)])', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n[(\nb\n)])', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n[\\\nb\\\n])', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case f(a, b=1): pass', 'exec').body[0].cases[0].pattern.is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case f\\\n(a, b=1): pass', 'exec').body[0].cases[0].pattern.is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f\\\n(a, b=1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (f\n(a, b=1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f(\na\n,\nb\n=\n1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f(\na\n,\nb\n=\n"()")): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case *s,: pass', 'exec').body[0].cases[0].pattern.patterns[0].is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (*\ns,): pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case *\\\ns,: pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (*\\\ns,): pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case a as b: pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a as b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\nas b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a\\\nas b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\\\nas\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a\\\nas\\\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\\\nas\n\\\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('a not in b', 'exec').body[0].value.ops[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(a not in b)', 'exec').body[0].value.ops[0].copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(a not\nin b)', 'exec').body[0].value.ops[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(a not\\\nin b)', 'exec').body[0].value.ops[0].copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(a is\nnot b)', 'exec').body[0].value.ops[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(a is\\\nnot b)', 'exec').body[0].value.ops[0].copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.generators[0].copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('[i for\n i in j]', 'exec').body[0].value.generators[0].copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('[i for i\n in j]', 'exec').body[0].value.generators[0].copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('[i for i in\n j]', 'exec').body[0].value.generators[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('[i for\\\n i in j]', 'exec').body[0].value.generators[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('[i for i\\\n in j]', 'exec').body[0].value.generators[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('[i for i in\\\n j]', 'exec').body[0].value.generators[0].copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('def f(a, b=1): pass', 'exec').body[0].args.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('def f(a,\n b=1): pass', 'exec').body[0].args.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('def f(a,\\\n b=1): pass', 'exec').body[0].args.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('def f(a, b=(1,\n2)): pass', 'exec').body[0].args.copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('def f(a:\n int): pass', 'exec').body[0].args.args[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('def f(a:\\\n int): pass', 'exec').body[0].args.args[0].copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('from a import (b as c)', 'exec').body[0].names[0].copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('from a import (b\n as c)', 'exec').body[0].names[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('from a import (b\\\n as c)', 'exec').body[0].names[0].copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('with (b as c): pass', 'exec').body[0].items[0].copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('with (b\n as c): pass', 'exec').body[0].items[0].copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('with (b\\\n as c): pass', 'exec').body[0].items[0].copy(pars=False).is_enclosed_or_line())

        if PYGE14:
            self.assertTrue(FST(r'''
(t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
            self.assertFalse(FST(r'''
(t"a{(1,

2)}b" t"""{3}

{4}
{5}"""
t"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

    def test_is_enclosed_general(self):
        self.assertTrue(FST('a < b', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(a\n< b)', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n< b)', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(a\\\n<\nb)', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n<\\\nb)', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertFalse(FST('(a\\\n<\n\\\nb)', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('a, b, c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, b\\\n, c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, [\nb\n], c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

        self.assertTrue(FST('a, {\nx: y\n}, c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, {\nb\n}, c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, [\ni for i in j\n], c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, {\ni for i in j\n}, c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, {\ni: j for i, j in k\n}, c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, (\ni for i in j\n), c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, [i,\nj], c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())
        self.assertTrue(FST('a, b[\ni:j:k\n], c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

        if PYGE12:
            self.assertTrue(FST('a, f"{(1,\n2)}", c', 'exec').body[0].value.copy(pars=False).is_enclosed_or_line())

    def test_is_enclosed_in_parents(self):
        self.assertFalse(FST('i', 'exec').body[0].is_enclosed_in_parents())
        self.assertFalse(FST('i', 'single').body[0].is_enclosed_in_parents())
        self.assertFalse(FST('i', 'eval').body.is_enclosed_in_parents())

        self.assertFalse(FST('@d\ndef f(): pass', 'exec').body[0].decorator_list[0].is_enclosed_in_parents())
        self.assertTrue(FST('def f(): pass', 'exec').body[0].args.is_enclosed_in_parents())
        self.assertTrue(FST('def f(a) -> int: pass', 'exec').body[0].args.is_enclosed_in_parents())
        self.assertFalse(FST('def f(a) -> int: pass', 'exec').body[0].returns.is_enclosed_in_parents())

        self.assertFalse(FST('@d\nasync def f(): pass', 'exec').body[0].decorator_list[0].is_enclosed_in_parents())
        self.assertTrue(FST('async def f(): pass', 'exec').body[0].args.is_enclosed_in_parents())
        self.assertTrue(FST('async def f(a) -> int: pass', 'exec').body[0].args.is_enclosed_in_parents())
        self.assertFalse(FST('async def f(a) -> int: pass', 'exec').body[0].returns.is_enclosed_in_parents())

        self.assertFalse(FST('@d\nclass c: pass', 'exec').body[0].decorator_list[0].is_enclosed_in_parents())
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0].bases[0].is_enclosed_in_parents())
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0].keywords[0].is_enclosed_in_parents())

        self.assertFalse(FST('return v', 'exec').body[0].value.is_enclosed_in_parents())
        self.assertFalse(FST('del v', 'exec').body[0].targets[0].is_enclosed_in_parents())
        self.assertFalse(FST('t = v', 'exec').body[0].targets[0].is_enclosed_in_parents())
        self.assertFalse(FST('t = v', 'exec').body[0].value.is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].target.is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].op.is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].value.is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].target.is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].annotation.is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].value.is_enclosed_in_parents())

        self.assertFalse(FST('for a in b: pass', 'exec').body[0].target.is_enclosed_in_parents())
        self.assertFalse(FST('for a in b: pass', 'exec').body[0].iter.is_enclosed_in_parents())
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0].target.is_enclosed_in_parents())
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0].iter.is_enclosed_in_parents())
        self.assertFalse(FST('while a: pass', 'exec').body[0].test.is_enclosed_in_parents())
        self.assertFalse(FST('if a: pass', 'exec').body[0].test.is_enclosed_in_parents())

        self.assertFalse(FST('with a: pass', 'exec').body[0].items[0].is_enclosed_in_parents())
        self.assertFalse(FST('with (a): pass', 'exec').body[0].items[0].is_enclosed_in_parents())  # pars belong to `a`
        self.assertFalse(FST('with ((a)): pass', 'exec').body[0].items[0].is_enclosed_in_parents())  # pars belong to `a`
        self.assertTrue(FST('with (a as b): pass', 'exec').body[0].items[0].is_enclosed_in_parents())  # pars belong to `with`
        self.assertTrue(FST('with ((a) as b): pass', 'exec').body[0].items[0].is_enclosed_in_parents())  # outer pars belong to `with`
        self.assertFalse(FST('async with a: pass', 'exec').body[0].items[0].is_enclosed_in_parents())
        self.assertFalse(FST('async with (a): pass', 'exec').body[0].items[0].is_enclosed_in_parents())
        self.assertFalse(FST('async with ((a)): pass', 'exec').body[0].items[0].is_enclosed_in_parents())
        self.assertTrue(FST('async with (a as b): pass', 'exec').body[0].items[0].is_enclosed_in_parents())
        self.assertTrue(FST('async with ((a) as b): pass', 'exec').body[0].items[0].is_enclosed_in_parents())

        self.assertFalse(FST('match (a):\n case 1: pass', 'exec').body[0].subject.is_enclosed_in_parents())
        self.assertFalse(FST('raise exc from cause', 'exec').body[0].exc.is_enclosed_in_parents())
        self.assertFalse(FST('raise exc from cause', 'exec').body[0].cause.is_enclosed_in_parents())
        self.assertFalse(FST('try: pass\nexcept Exception as exc: pass', 'exec').body[0].handlers[0].type.is_enclosed_in_parents())
        self.assertFalse(FST('try: pass\nexcept (Exception) as exc: pass', 'exec').body[0].handlers[0].type.is_enclosed_in_parents())  # because pars belong to `type`
        self.assertFalse(FST('try: pass\nexcept ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0].type.is_enclosed_in_parents())  # same
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0].test.is_enclosed_in_parents())
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0].msg.is_enclosed_in_parents())
        self.assertFalse(FST('import a as b', 'exec').body[0].names[0].is_enclosed_in_parents())
        self.assertFalse(FST('from a import b', 'exec').body[0].names[0].is_enclosed_in_parents())
        self.assertFalse(FST('from a import b as c', 'exec').body[0].names[0].is_enclosed_in_parents())
        self.assertTrue(FST('from a import (b)', 'exec').body[0].names[0].is_enclosed_in_parents())
        self.assertTrue(FST('from a import (b as c)', 'exec').body[0].names[0].is_enclosed_in_parents())

        self.assertFalse(FST('(a)', 'exec').body[0].value.is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.op.is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[0].is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[1].is_enclosed_in_parents())
        self.assertFalse(FST('(a := b)', 'exec').body[0].value.is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.left.is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.op.is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.right.is_enclosed_in_parents())
        self.assertFalse(FST('-(a)', 'exec').body[0].value.op.is_enclosed_in_parents())
        self.assertFalse(FST('-(a)', 'exec').body[0].value.operand.is_enclosed_in_parents())
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value.args.is_enclosed_in_parents())
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value.body.is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.body.is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.test.is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.orelse.is_enclosed_in_parents())
        self.assertTrue(FST('{k: v}', 'exec').body[0].value.keys[0].is_enclosed_in_parents())
        self.assertTrue(FST('{k: v}', 'exec').body[0].value.values[0].is_enclosed_in_parents())
        self.assertTrue(FST('{a}', 'exec').body[0].value.elts[0].is_enclosed_in_parents())
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.elt.is_enclosed_in_parents())
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.generators[0].is_enclosed_in_parents())
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value.elt.is_enclosed_in_parents())
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value.generators[0].is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.key.is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.value.is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.generators[0].is_enclosed_in_parents())
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value.elt.is_enclosed_in_parents())
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value.generators[0].is_enclosed_in_parents())
        self.assertFalse(FST('await (a)', 'exec').body[0].value.is_enclosed_in_parents())
        self.assertFalse(FST('yield (a)', 'exec').body[0].value.is_enclosed_in_parents())
        self.assertFalse(FST('yield from (a)', 'exec').body[0].value.is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.left.is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.ops[0].is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.comparators[0].is_enclosed_in_parents())
        self.assertFalse(FST('call(a, b=c)', 'exec').body[0].value.func.is_enclosed_in_parents())
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value.args[0].is_enclosed_in_parents())
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value.keywords[0].is_enclosed_in_parents())
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[0].is_enclosed_in_parents())
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[1].value.is_enclosed_in_parents())

        self.assertFalse(FST('(a).b', 'exec').body[0].value.value.is_enclosed_in_parents())
        self.assertFalse(FST('(a).b', 'exec').body[0].value.ctx.is_enclosed_in_parents())
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value.value.is_enclosed_in_parents())
        self.assertTrue(FST('(a)[b]', 'exec').body[0].value.slice.is_enclosed_in_parents())
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value.ctx.is_enclosed_in_parents())
        self.assertFalse(FST('*(a)', 'exec').body[0].value.value.is_enclosed_in_parents())
        self.assertFalse(FST('*(a)', 'exec').body[0].value.ctx.is_enclosed_in_parents())
        self.assertFalse(FST('a', 'exec').body[0].value.ctx.is_enclosed_in_parents())
        self.assertFalse(FST('(a)', 'exec').body[0].value.ctx.is_enclosed_in_parents())

        self.assertTrue(FST('[a]', 'exec').body[0].value.elts[0].is_enclosed_in_parents())
        self.assertFalse(FST('[a]', 'exec').body[0].value.ctx.is_enclosed_in_parents())
        self.assertTrue(FST('(a,)', 'exec').body[0].value.elts[0].is_enclosed_in_parents())
        self.assertFalse(FST('(a,)', 'exec').body[0].value.ctx.is_enclosed_in_parents())
        self.assertFalse(FST('a,', 'exec').body[0].value.elts[0].is_enclosed_in_parents())
        self.assertFalse(FST('a,', 'exec').body[0].value.ctx.is_enclosed_in_parents())

        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).lower.is_enclosed_in_parents())
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).upper.is_enclosed_in_parents())
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).step.is_enclosed_in_parents())

        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).target.is_enclosed_in_parents())
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).iter.is_enclosed_in_parents())
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).ifs[0].is_enclosed_in_parents())

        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).posonlyargs[0].is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).args[0].is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).defaults[0].is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).vararg.is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kwonlyargs[0].is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kw_defaults[0].is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kwarg.is_enclosed_in_parents())
        self.assertFalse(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=True).annotation.is_enclosed_in_parents())

        self.assertFalse(FST('call(k=v)', 'exec').body[0].value.keywords[0].copy(pars=True).value.is_enclosed_in_parents())

        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True).context_expr.is_enclosed_in_parents())
        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True).optional_vars.is_enclosed_in_parents())

        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True).pattern.is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True).guard.is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).value.is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).value.is_enclosed_in_parents())  # inconsistent case, MatchValue owns the pars
        self.assertFalse(FST('match a:\n case 1, 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0].is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1, 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0].is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case [1, 2]: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0].is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).keys[0].is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0].is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).cls.is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0].is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).kwd_patterns[0].is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1 as a: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).pattern.is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1 as a): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).pattern.is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1 | 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0].is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1 | 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0].is_enclosed_in_parents())

        if PYGE12:
            self.assertTrue(FST('def f[T]() -> int: pass', 'exec').body[0].type_params[0].is_enclosed_in_parents())
            self.assertTrue(FST('async def f[T]() -> int: pass', 'exec').body[0].type_params[0].is_enclosed_in_parents())
            self.assertTrue(FST('class c[T]: pass', 'exec').body[0].type_params[0].is_enclosed_in_parents())

            self.assertFalse(FST('type t[T] = v', 'exec').body[0].name.is_enclosed_in_parents())
            self.assertTrue(FST('type t[T] = v', 'exec').body[0].type_params[0].is_enclosed_in_parents())
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].value.is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* Exception as exc: pass', 'exec').body[0].handlers[0].type.is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* (Exception) as exc: pass', 'exec').body[0].handlers[0].type.is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0].type.is_enclosed_in_parents())
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].type_params[0].copy().is_enclosed_in_parents())
            self.assertFalse(FST('type t[*T] = v', 'exec').body[0].type_params[0].copy().is_enclosed_in_parents())
            self.assertFalse(FST('type t[**T] = v', 'exec').body[0].type_params[0].copy().is_enclosed_in_parents())

        if PYGE14:
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[0].is_enclosed_in_parents())
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[1].value.is_enclosed_in_parents())

        # with field

        self.assertFalse(FST('i', 'exec').is_enclosed_in_parents('body'))
        self.assertFalse(FST('i', 'single').is_enclosed_in_parents('body'))
        self.assertFalse(FST('i', 'eval').is_enclosed_in_parents('body'))

        self.assertFalse(FST('@d\ndef f(): pass', 'exec').body[0].is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('def f(): pass', 'exec').body[0].is_enclosed_in_parents('args'))
        self.assertTrue(FST('def f(a) -> int: pass', 'exec').body[0].is_enclosed_in_parents('args'))
        self.assertFalse(FST('def f(a) -> int: pass', 'exec').body[0].is_enclosed_in_parents('returns'))

        self.assertFalse(FST('@d\nasync def f(): pass', 'exec').body[0].is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('async def f(): pass', 'exec').body[0].is_enclosed_in_parents('args'))
        self.assertTrue(FST('async def f(a) -> int: pass', 'exec').body[0].is_enclosed_in_parents('args'))
        self.assertFalse(FST('async def f(a) -> int: pass', 'exec').body[0].is_enclosed_in_parents('returns'))

        self.assertFalse(FST('@d\nclass c: pass', 'exec').body[0].is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0].is_enclosed_in_parents('bases'))
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0].is_enclosed_in_parents('keywords'))

        self.assertFalse(FST('return v', 'exec').body[0].is_enclosed_in_parents('value'))
        self.assertFalse(FST('del v', 'exec').body[0].is_enclosed_in_parents('targets'))
        self.assertFalse(FST('t = v', 'exec').body[0].is_enclosed_in_parents('targets'))
        self.assertFalse(FST('t = v', 'exec').body[0].is_enclosed_in_parents('value'))
        self.assertFalse(FST('t += v', 'exec').body[0].is_enclosed_in_parents('target'))
        self.assertFalse(FST('t += v', 'exec').body[0].is_enclosed_in_parents('op'))
        self.assertFalse(FST('t += v', 'exec').body[0].is_enclosed_in_parents('value'))
        self.assertFalse(FST('t: int = v', 'exec').body[0].is_enclosed_in_parents('target'))
        self.assertFalse(FST('t: int = v', 'exec').body[0].is_enclosed_in_parents('annotation'))
        self.assertFalse(FST('t: int = v', 'exec').body[0].is_enclosed_in_parents('value'))

        self.assertFalse(FST('for a in b: pass', 'exec').body[0].is_enclosed_in_parents('target'))
        self.assertFalse(FST('for a in b: pass', 'exec').body[0].is_enclosed_in_parents('iter'))
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0].is_enclosed_in_parents('target'))
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0].is_enclosed_in_parents('iter'))
        self.assertFalse(FST('while a: pass', 'exec').body[0].is_enclosed_in_parents('test'))
        self.assertFalse(FST('if a: pass', 'exec').body[0].is_enclosed_in_parents('test'))

        self.assertFalse(FST('with a: pass', 'exec').body[0].is_enclosed_in_parents('items'))
        self.assertFalse(FST('with (a): pass', 'exec').body[0].is_enclosed_in_parents('items'))  # pars belong to `a`
        self.assertFalse(FST('with ((a)): pass', 'exec').body[0].is_enclosed_in_parents('items'))  # pars belong to `a`
        self.assertTrue(FST('with (a as b): pass', 'exec').body[0].is_enclosed_in_parents('items'))  # pars belong to `with`
        self.assertTrue(FST('with ((a) as b): pass', 'exec').body[0].is_enclosed_in_parents('items'))  # outer pars belong to `with`
        self.assertFalse(FST('async with a: pass', 'exec').body[0].is_enclosed_in_parents('items'))
        self.assertFalse(FST('async with (a): pass', 'exec').body[0].is_enclosed_in_parents('items'))
        self.assertFalse(FST('async with ((a)): pass', 'exec').body[0].is_enclosed_in_parents('items'))
        self.assertTrue(FST('async with (a as b): pass', 'exec').body[0].is_enclosed_in_parents('items'))
        self.assertTrue(FST('async with ((a) as b): pass', 'exec').body[0].is_enclosed_in_parents('items'))

        self.assertFalse(FST('match (a):\n case 1: pass', 'exec').body[0].is_enclosed_in_parents('subject'))
        self.assertFalse(FST('raise exc from cause', 'exec').body[0].is_enclosed_in_parents('exc'))
        self.assertFalse(FST('raise exc from cause', 'exec').body[0].is_enclosed_in_parents('cause'))
        self.assertFalse(FST('try: pass\nexcept Exception as exc: pass', 'exec').body[0].handlers[0].is_enclosed_in_parents('type'))
        self.assertFalse(FST('try: pass\nexcept (Exception) as exc: pass', 'exec').body[0].handlers[0].is_enclosed_in_parents('type'))  # because pars belong to `type`
        self.assertFalse(FST('try: pass\nexcept ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0].is_enclosed_in_parents('type'))  # same
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0].is_enclosed_in_parents('test'))
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0].is_enclosed_in_parents('msg'))
        self.assertFalse(FST('import a as b', 'exec').body[0].is_enclosed_in_parents('names'))
        self.assertFalse(FST('from a import b', 'exec').body[0].is_enclosed_in_parents('names'))
        self.assertFalse(FST('from a import b as c', 'exec').body[0].is_enclosed_in_parents('names'))
        self.assertTrue(FST('from a import (b)', 'exec').body[0].is_enclosed_in_parents('names'))
        self.assertTrue(FST('from a import (b as c)', 'exec').body[0].is_enclosed_in_parents('names'))

        self.assertFalse(FST('(a)', 'exec').body[0].is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.is_enclosed_in_parents('op'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.is_enclosed_in_parents('values'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[1].is_enclosed_in_parents())
        self.assertFalse(FST('(a := b)', 'exec').body[0].is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.is_enclosed_in_parents('left'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.is_enclosed_in_parents('op'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.is_enclosed_in_parents('right'))
        self.assertFalse(FST('-(a)', 'exec').body[0].value.is_enclosed_in_parents('op'))
        self.assertFalse(FST('-(a)', 'exec').body[0].value.is_enclosed_in_parents('operand'))
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value.is_enclosed_in_parents('args'))
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value.is_enclosed_in_parents('body'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.is_enclosed_in_parents('body'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.is_enclosed_in_parents('test'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.is_enclosed_in_parents('orelse'))
        self.assertTrue(FST('{k: v}', 'exec').body[0].value.is_enclosed_in_parents('keys'))
        self.assertTrue(FST('{k: v}', 'exec').body[0].value.is_enclosed_in_parents('values'))
        self.assertTrue(FST('{a}', 'exec').body[0].value.is_enclosed_in_parents('elts'))
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.is_enclosed_in_parents('elt'))
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.is_enclosed_in_parents('generators'))
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value.is_enclosed_in_parents('elt'))
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value.is_enclosed_in_parents('generators'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.is_enclosed_in_parents('key'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.is_enclosed_in_parents('value'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.is_enclosed_in_parents('generators'))
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value.is_enclosed_in_parents('elt'))
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value.is_enclosed_in_parents('generators'))
        self.assertFalse(FST('await (a)', 'exec').body[0].is_enclosed_in_parents('value'))
        self.assertFalse(FST('yield (a)', 'exec').body[0].is_enclosed_in_parents('value'))
        self.assertFalse(FST('yield from (a)', 'exec').body[0].is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.is_enclosed_in_parents('left'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.is_enclosed_in_parents('ops'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.is_enclosed_in_parents('comparators'))
        self.assertFalse(FST('call(a, b=c)', 'exec').body[0].value.is_enclosed_in_parents('func'))
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value.is_enclosed_in_parents('args'))
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value.is_enclosed_in_parents('keywords'))
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.is_enclosed_in_parents('values'))
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[1].is_enclosed_in_parents('value'))

        self.assertFalse(FST('(a).b', 'exec').body[0].value.is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a).b', 'exec').body[0].value.is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value.is_enclosed_in_parents('value'))
        self.assertTrue(FST('(a)[b]', 'exec').body[0].value.is_enclosed_in_parents('slice'))
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value.is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('*(a)', 'exec').body[0].value.is_enclosed_in_parents('value'))
        self.assertFalse(FST('*(a)', 'exec').body[0].value.is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('a', 'exec').body[0].value.is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('(a)', 'exec').body[0].value.is_enclosed_in_parents('ctx'))

        self.assertTrue(FST('[a]', 'exec').body[0].value.is_enclosed_in_parents('elts'))
        self.assertFalse(FST('[a]', 'exec').body[0].value.is_enclosed_in_parents('ctx'))
        self.assertTrue(FST('(a,)', 'exec').body[0].value.is_enclosed_in_parents('elts'))
        self.assertFalse(FST('(a,)', 'exec').body[0].value.is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('a,', 'exec').body[0].value.is_enclosed_in_parents('elts'))
        self.assertFalse(FST('a,', 'exec').body[0].value.is_enclosed_in_parents('ctx'))

        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).is_enclosed_in_parents('lower'))
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).is_enclosed_in_parents('upper'))
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).is_enclosed_in_parents('step'))

        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).is_enclosed_in_parents('target'))
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).is_enclosed_in_parents('iter'))
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).is_enclosed_in_parents('ifs'))

        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).is_enclosed_in_parents('posonlyargs'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).is_enclosed_in_parents('args'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).is_enclosed_in_parents('defaults'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).is_enclosed_in_parents('vararg'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).is_enclosed_in_parents('kwonlyargs'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).is_enclosed_in_parents('kw_defaults'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).is_enclosed_in_parents('kwarg'))
        self.assertFalse(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=True).is_enclosed_in_parents('annotation'))

        self.assertFalse(FST('call(k=v)', 'exec').body[0].value.keywords[0].copy(pars=True).is_enclosed_in_parents('value'))

        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True).is_enclosed_in_parents('context_expr'))
        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True).is_enclosed_in_parents('optional_vars'))

        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True).is_enclosed_in_parents('pattern'))
        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True).is_enclosed_in_parents('guard'))
        self.assertFalse(FST('match a:\n case 1: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('value'))
        self.assertTrue(FST('match a:\n case (1): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('value'))  # inconsistent case, MatchValue owns the pars
        self.assertFalse(FST('match a:\n case 1, 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case (1, 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case [1, 2]: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('keys'))
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('patterns'))
        self.assertFalse(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('cls'))
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('kwd_patterns'))
        self.assertFalse(FST('match a:\n case 1 as a: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('pattern'))
        self.assertTrue(FST('match a:\n case (1 as a): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('pattern'))
        self.assertFalse(FST('match a:\n case 1 | 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case (1 | 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).is_enclosed_in_parents('patterns'))

        if PYGE12:
            self.assertTrue(FST('def f[T]() -> int: pass', 'exec').body[0].is_enclosed_in_parents('type_params'))
            self.assertTrue(FST('async def f[T]() -> int: pass', 'exec').body[0].is_enclosed_in_parents('type_params'))
            self.assertTrue(FST('class c[T]: pass', 'exec').body[0].is_enclosed_in_parents('type_params'))

            self.assertFalse(FST('type t[T] = v', 'exec').body[0].is_enclosed_in_parents('name'))
            self.assertTrue(FST('type t[T] = v', 'exec').body[0].is_enclosed_in_parents('type_params'))
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].is_enclosed_in_parents('value'))
            self.assertFalse(FST('try: pass\nexcept* Exception as exc: pass', 'exec').body[0].handlers[0].is_enclosed_in_parents('type'))
            self.assertFalse(FST('try: pass\nexcept* (Exception) as exc: pass', 'exec').body[0].handlers[0].is_enclosed_in_parents('type'))
            self.assertFalse(FST('try: pass\nexcept* ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0].is_enclosed_in_parents('type'))
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].type_params[0].copy().is_enclosed_in_parents())
            self.assertFalse(FST('type t[*T] = v', 'exec').body[0].type_params[0].copy().is_enclosed_in_parents())
            self.assertFalse(FST('type t[**T] = v', 'exec').body[0].type_params[0].copy().is_enclosed_in_parents())

        if PYGE14:
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.is_enclosed_in_parents('values'))
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[1].is_enclosed_in_parents('value'))

    def test_is_parenthesized_tuple(self):
        self.assertTrue(parse('(1, 2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,),)').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('((a), b)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(a, (b))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((a), (b))').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('(\n1,2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1\n,2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,\n2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,2\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1)\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1),\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,\n))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,)\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,\n),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,)\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,),\n)').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('((a), b)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(a, (b))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((a), (b))').body[0].value.f.is_parenthesized_tuple())

        self.assertFalse(parse('(1,),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('(1),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((1)),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((1,),),').body[0].value.f.is_parenthesized_tuple())

        self.assertFalse(parse('(a), b').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((a)), b').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('a, (b)').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('a, ((b))').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('(a), (b)').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((a)), ((b))').body[0].value.f.is_parenthesized_tuple())

        self.assertIsNone(parse('[(a), (b)]').body[0].value.f.is_parenthesized_tuple())

    def test_get_indent(self):
        ast = parse('i = 1; j = 2')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual('', ast.body[1].f.get_indent())

        ast = parse('def f(): \\\n i = 1')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())

        ast = parse('class cls: i = 1')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())

        ast = parse('class cls: i = 1; \\\n    j = 2')

        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[1].f.get_indent())

        ast = parse('class cls:\n  i = 1; \\\n    j = 2')

        self.assertEqual('  ', ast.body[0].body[0].f.get_indent())
        self.assertEqual('  ', ast.body[0].body[1].f.get_indent())

        ast = parse('class cls:\n   def f(): i = 1')

        self.assertEqual('   ', ast.body[0].body[0].f.get_indent())
        self.assertEqual('   ' + ast.f.root.indent, ast.body[0].body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   1').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): 1').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1').body[0].body[0].f.get_indent())

        self.assertEqual('    ', parse('class cls:\n def f():\n    1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('class cls:\n def f(): 1').body[0].body[0].body[0].f.get_indent())  # indentation inferred otherwise would be '     '
        self.assertEqual('  ', parse('class cls:\n def f(): \\\n   1').body[0].body[0].body[0].f.get_indent())  # indentation inferred otherwise would be '     '
        self.assertEqual('   ', parse('class cls:\n def f(): # \\\n   1').body[0].body[0].body[0].f.get_indent())

        self.assertEqual('  ', parse('if 1:\n  2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('if 1: 2\nelse:\n   3').body[0].body[0].f.get_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('   ', parse('if 1: \\\n 2\nelse:\n   3').body[0].body[0].f.get_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('  ', parse('if 1: # \\\n  2\nelse:\n   3').body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('if 1:\n  2\nelse:\n   3').body[0].orelse[0].f.get_indent())
        self.assertEqual('  ', parse('if 1:\n  2\nelse: 3').body[0].orelse[0].f.get_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('  ', parse('if 1:\n  2\nelse: \\\n 3').body[0].orelse[0].f.get_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('   ', parse('if 1:\n  2\nelse: # \\\n   3').body[0].orelse[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): 1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1; 2').body[0].body[1].f.get_indent())

        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[1].f.get_indent())

        self.assertEqual('', parse('\\\ni').body[0].f.get_indent())
        self.assertEqual('    ', parse('try: i\nexcept: pass').body[0].body[0].f.get_indent())

        self.assertEqual('', parse('if 1: i\nelif 2: j').body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j').body[0].body[0].f.get_indent())
        self.assertEqual('', parse('if 1: i\nelif 2: j').body[0].orelse[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j').body[0].orelse[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j\nelse: k').body[0].orelse[0].orelse[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j\nelif 3: k').body[0].orelse[0].orelse[0].body[0].f.get_indent())

        # self.assertEqual('  ', parse('if 1: i\nelse:\n  j').body[0].body[0].f.get_indent())  # candidate for sibling indentation, nope, not doing this

        self.assertEqual('  ', parse('if 1:\n\\\n  \\\n i').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('if 1:\n  \\\n\\\n i').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('if 1:\n  \\\n   \\\n\\\n i').body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('if 1:\n   \\\n  \\\n\\\n i').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: \\\n\\\n  \\\n   \\\n\\\n i').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('if 1:\n\\\n  \\\n   \\\n\\\n i').body[0].body[0].f.get_indent())
        self.assertEqual('     ', parse('if 1:\n\\\n\\\n     \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].f.get_indent())

        self.assertEqual('          ', parse('if 2:\n     if 1:\\\n\\\n\\\n  \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].body[0].f.get_indent())  # indentation inferred otherwise would be '         '
        self.assertEqual('      ', parse('if 2:\n     if 1:\n\\\n      \\\n  \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].body[0].f.get_indent())

    def test_dedent_multiline_strings(self):
        f = parse('''
class cls:
    def func():
        i = """This is a
        normal
        multiline string"""

        j = ("This is a "
        "split "
        "multiline string")

        k = f"""This is a
        normal
        multiline f-string"""

        l = (f"This is a "
        "split "
        f"multiline f-string")
            '''.strip()).body[0].body[0].f
        self.assertEqual('''
def func():
    i = """This is a
        normal
        multiline string"""

    j = ("This is a "
    "split "
    "multiline string")

    k = f"""This is a
        normal
        multiline f-string"""

    l = (f"This is a "
    "split "
    f"multiline f-string")
            '''.strip(), f.copy().src)

        f = parse('''
class cls:
    def func():
        l = (f"This is a "
        f"split " """
        super
        special
        """
        f"multiline f-string")
            '''.strip()).body[0].body[0].f
        self.assertEqual('''
def func():
    l = (f"This is a "
    f"split " """
        super
        special
        """
    f"multiline f-string")
            '''.strip(), f.copy().src)

    def test_copy_lines(self):
        src = 'class cls:\n if True:\n  i = 1\n else:\n  j = 2'
        ast = parse(src)

        self.assertEqual(src.split('\n'), ast.f.get_src(*ast.f.loc, True))
        self.assertEqual(src.split('\n'), ast.body[0].f.get_src(*ast.body[0].f.loc, True))
        self.assertEqual('if True:\n  i = 1\n else:\n  j = 2'.split('\n'), ast.body[0].body[0].f.get_src(*ast.body[0].body[0].f.loc, True))
        self.assertEqual(['i = 1'], ast.body[0].body[0].body[0].f.get_src(*ast.body[0].body[0].body[0].f.loc, True))
        self.assertEqual(['j = 2'], ast.body[0].body[0].orelse[0].f.get_src(*ast.body[0].body[0].orelse[0].f.loc, True))

        self.assertEqual(['True:', '  i'], ast.f.root.get_src(1, 4, 2, 3, True))

    def test_code_as_simple(self):
        # stmts

        f = FST(r'''
if 1:
    pass

call(a)
'''.strip(), 'exec')

        h = f._code_as_stmts(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_stmts(f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_stmts(f.a)
        self.assertTrue(compare_asts(h.a, f.a, locs=False, raise_=True))

        f0 = f.body[0].copy()
        h = f._code_as_stmts(f0.a)
        self.assertEqual(ast_unparse(f0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f0.a, locs=False, raise_=True))

        f1 = f.body[1].copy()
        h = f._code_as_stmts(f1.a)
        self.assertEqual(ast_unparse(f1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f1.a, locs=False, raise_=True))

        g = FST('from a import b', 'exec').body[0].names[0]
        self.assertRaises(ValueError, f._code_as_stmts, f.body[0].test)
        self.assertRaises(NodeError, f._code_as_stmts, g.copy())
        self.assertRaises(NodeError, f._code_as_stmts, g.a)
        self.assertRaises(SyntaxError, f._code_as_stmts, 'except Exception: pass')

        f = FST('f(a)', 'exec')
        h = f._code_as_stmts(f.body[0].value.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_stmts(f.src)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_stmts(f.a)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        # expr

        f = FST('a if b else {"c": f()}', 'eval')

        h = f._code_as_expr(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body.a, locs=True, raise_=True))

        f = FST('a if b else {"c": f()}', 'single')

        h = f._code_as_expr(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        f = FST('a if b else {"c": f()}', 'exec')

        h = f._code_as_expr(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        h = f._code_as_expr(f.body[0].copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        h = f._code_as_expr(f.body[0].value.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        h = f._code_as_expr(f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        g = f.body[0].value.copy()
        h = f._code_as_expr(g.a)
        self.assertEqual(ast_unparse(g.a), h.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=False, raise_=True))

        self.assertRaises(ValueError, f._code_as_expr, FST('i = 1', 'exec').body[0])
        self.assertRaises(NodeError, f._code_as_expr, FST('i = 1', 'exec').body[0].copy())
        self.assertRaises(NodeError, f._code_as_expr, f.body[0].a)
        self.assertRaises(SyntaxError, f._code_as_expr, 'pass')

        # ExceptHandlers

        f = FST(r'''
try: pass
except (ValueError, RuntimeError) as exc:
    def f():
        """doc
  string"""

        pass

    i = f"""a
  {test}
        b"""

except Exception:
    ("a"
"b")
    k = \
("c"
    "d")
'''.strip(), 'exec')

        g = f.body[0].get_slice(field='handlers')

        h = f._code_as_ExceptHandlers(g.copy())
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = f._code_as_ExceptHandlers(g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.body[0].copy()
        h = f._code_as_ExceptHandlers(g0.a)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = f._code_as_ExceptHandlers(g1.a)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, f._code_as_ExceptHandlers, f.body[0].handlers[0])

        self.assertEqual(0, len(FST._code_as_ExceptHandlers('').body))  # make sure we can parse zero ExceptHandlers

        # match_cases

        f = FST(r'''
match a:
    case 1:
        def f():
            """doc
  string"""

            pass

        i = f"""a
  {test}
        b"""

    case 2:
        ("a"
"b")
        k = \
("c"
    "d")
'''.strip(), 'exec')

        g = f.body[0].get_slice(field='cases')

        h = f._code_as_match_cases(g.copy())
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = f._code_as_match_cases(g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.body[0].copy()
        h = f._code_as_match_cases(g0.a)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = f._code_as_match_cases(g1.a)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, f._code_as_match_cases, f.body[0].cases[0])

        self.assertEqual(0, len(FST._code_as_match_cases('').body))  # make sure we can parse zero match_cases

        # boolop

        f = FST(And(), ['and'])

        h = f._code_as_boolop(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_boolop(f.a)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=False, raise_=True))

        h = f._code_as_boolop(f.src)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        # rest of AST ones

        CODE_ASES = [
            (FST._code_as_expr_slice, 'body[0].value.slice', 'a[1]'),
            (FST._code_as_expr_slice, 'body[0].value.slice', 'a[b:c:d]'),
            (FST._code_as_expr_slice, 'body[0].value.slice', 'a[b:c:d, e:f]'),
            (FST._code_as_binop, 'body[0].value.op', 'a + b'),
            (FST._code_as_augop, 'body[0].op', 'a += b'),
            (FST._code_as_unaryop, 'body[0].value.op', '~a'),
            (FST._code_as_cmpop, 'body[0].value.ops[0]', 'a < b'),
            (FST._code_as_comprehension, 'body[0].value.generators[0]', '[i for i in j if i < 0]'),
            (FST._code_as_arguments, 'body[0].args', 'def f(a: str, /, b: int = 1, *c: tuple[bool], d: float = 2.0, **e: dict): pass'),
            (FST._code_as_arguments_lambda, 'body[0].value.args', 'lambda a, /, b=1, *c, d=2, **e: None'),
            (FST._code_as_arg, 'body[0].args.args[0]', 'def f(a: str = "test"): pass'),
            (FST._code_as_keyword, 'body[0].keywords[0]', 'class cls(meta=something): pass'),
            (FST._code_as_keyword, 'body[0].value.keywords[0]', 'call(key = word)'),
            (FST._code_as_alias, 'body[0].names[0]', 'from a import b'),
            (FST._code_as_alias, 'body[0].names[0]', 'from a import *'),
            (FST._code_as_alias, 'body[0].names[0]', 'import a.b'),
            (FST._code_as_alias_dotted, 'body[0].names[0]', 'import a'),
            (FST._code_as_alias_dotted, 'body[0].names[0]', 'import a.b'),
            (FST._code_as_alias_star, 'body[0].names[0]', 'from a import b'),
            (FST._code_as_alias_star, 'body[0].names[0]', 'from a import *'),
            (FST._code_as_withitem, 'body[0].items[0]', 'with a: pass'),
            (FST._code_as_withitem, 'body[0].items[0]', 'with (a): pass'),
            (FST._code_as_withitem, 'body[0].items[0]', 'with a as b: pass'),
            (FST._code_as_withitem, 'body[0].items[0]', 'with (a as b): pass'),
            (FST._code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case 42: pass'),
            (FST._code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case None: pass'),
            (FST._code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case [_, *_]: pass'),
            (FST._code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case {"key": _}: pass'),
            (FST._code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case SomeClass(attr=val): pass'),
            (FST._code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case as_var: pass'),
            (FST._code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case 1 | 2 | 3: pass'),
            (FST._code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case _: pass'),
        ]

        if PYGE12:
            CODE_ASES.extend([
                (FST._code_as_type_param, 'body[0].type_params[0]', 'type t[T: int] = ...'),
                (FST._code_as_type_param, 'body[0].type_params[0]', 'class c[T: int]: pass'),
                (FST._code_as_type_param, 'body[0].type_params[0]', 'def f[T: int](): pass'),
            ])

        for code_as, attr, src in CODE_ASES:
            m = FST(src, 'exec')
            f = eval(f'm.{attr}', {'m': m}).copy()

            g = code_as(f.copy())
            self.assertEqual(g.src, f.src)
            self.assertTrue(compare_asts(g.a, f.a, locs=True, raise_=True))

            g = code_as(f.copy().a)
            self.assertEqual(ast_unparse(g.a), ast_unparse(f.a))
            self.assertTrue(compare_asts(g.a, f.a, locs=False, raise_=True))

            self.assertRaises(ValueError, code_as, eval(f'm.{attr}', {'m': m}))

        # identifiers

        f = FST('name', 'exec').body[0].value.copy()

        self.assertEqual('name', FST._code_as_identifier(f.copy()))
        self.assertEqual('name', FST._code_as_identifier(f.a))
        self.assertEqual('name', FST._code_as_identifier(f.src))

        self.assertEqual('name', FST._code_as_identifier_alias(f.copy()))
        self.assertEqual('name', FST._code_as_identifier_alias(f.a))
        self.assertEqual('name', FST._code_as_identifier_alias(f.src))

        f = FST('name.attr', 'exec').body[0].value.copy()

        self.assertEqual('name.attr', FST._code_as_identifier_dotted(f.copy()))
        self.assertEqual('name.attr', FST._code_as_identifier_dotted(f.a))
        self.assertEqual('name.attr', FST._code_as_identifier_dotted(f.src))

        self.assertEqual('name.attr', FST._code_as_identifier_alias(f.copy()))
        self.assertEqual('name.attr', FST._code_as_identifier_alias(f.a))
        self.assertEqual('name.attr', FST._code_as_identifier_alias(f.src))

        f = FST('from a import *', 'exec').body[0].names[0].copy()

        self.assertEqual('*', FST._code_as_identifier_star(f.copy()))
        self.assertEqual('*', FST._code_as_identifier_star(f.a))
        self.assertEqual('*', FST._code_as_identifier_star(f.src))

        self.assertEqual('*', FST._code_as_identifier_alias(f.copy()))
        self.assertEqual('*', FST._code_as_identifier_alias(f.a))
        self.assertEqual('*', FST._code_as_identifier_alias(f.src))

    def test_code_as_stmtishs(self):
        f = FST(r'''
if 1:
    pass

call(a)
'''.strip(), 'exec')

        h = f._code_as_stmtishs(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_stmtishs(f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_stmtishs(f.a)
        self.assertTrue(compare_asts(h.a, f.a, locs=False, raise_=True))

        f0 = f.body[0].copy()
        h = f._code_as_stmtishs(f0.a)
        self.assertEqual(ast_unparse(f0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f0.a, locs=False, raise_=True))

        f1 = f.body[1].copy()
        h = f._code_as_stmtishs(f1.a)
        self.assertEqual(ast_unparse(f1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f1.a, locs=False, raise_=True))

        g = FST('from a import b', 'exec').body[0].names[0]
        self.assertRaises(ValueError, f._code_as_stmtishs, f.body[0].test)
        self.assertRaises(NodeError, f._code_as_stmtishs, g.copy())
        self.assertRaises(NodeError, f._code_as_stmtishs, g.a)

        f = FST('f(a)', 'exec')
        h = f._code_as_stmtishs(f.body[0].value.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_stmtishs(f.src)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = f._code_as_stmtishs(f.a)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        f = FST(r'''
try: pass
except (ValueError, RuntimeError) as exc:
    def f():
        """doc
  string"""

        pass

    i = f"""a
  {test}
        b"""

except Exception:
    ("a"
"b")
    k = \
("c"
    "d")
'''.strip(), 'exec')

        g = f.body[0].get_slice(field='handlers')

        h = f._code_as_stmtishs(g.copy())
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = f._code_as_stmtishs(g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.body[0].copy()
        h = f._code_as_stmtishs(g0.a)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = f._code_as_stmtishs(g1.a)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, f._code_as_stmtishs, f.body[0].handlers[0])

        f = FST(r'''
match a:
    case 1:
        def f():
            """doc
  string"""

            pass

        i = f"""a
  {test}
        b"""

    case 2:
        ("a"
"b")
        k = \
("c"
    "d")
'''.strip(), 'exec')

        g = f.body[0].get_slice(field='cases')

        h = f._code_as_stmtishs(g.copy())
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = f._code_as_stmtishs(g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.body[0].copy()
        h = f._code_as_stmtishs(g0.a)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = f._code_as_stmtishs(g1.a)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, f._code_as_stmtishs, f.body[0].cases[0])

        # special 'case' non-keyword

        self.assertIsInstance(FST._code_as_stmtishs('case 1: pass').body[0].a, match_case)
        self.assertIsInstance(FST._code_as_stmtishs('case = 1').body[0].a, Assign)
        self.assertIsInstance(FST._code_as_stmtishs('case.b = 1').body[0].a, Assign)

    def test_code_as_sanitize(self):
        CODE_ASES = [
            (FST._code_as_expr, 'f(a)'),
            (FST._code_as_expr_slice, 'b:c:d'),
            (FST._code_as_expr_slice, 'b:c:d, e:f'),
            (FST._code_as_binop, '+'),
            (FST._code_as_augop, '+='),
            (FST._code_as_unaryop, '~'),
            (FST._code_as_cmpop, '<'),
            (FST._code_as_comprehension, 'for i in j if i < 0'),
            (FST._code_as_arguments, 'a: str, /, b: int = 1, *c: tuple[bool], d: float = 2.0, **e: dict'),
            (FST._code_as_arguments_lambda, 'a, /, b=1, *c, d=2, **e'),
            (FST._code_as_arg, 'a: str'),
            (FST._code_as_keyword, 'meta=something'),
            (FST._code_as_keyword, 'key = word'),
            (FST._code_as_alias_dotted, 'a'),
            (FST._code_as_alias_dotted, 'a.b'),
            (FST._code_as_alias_star, 'b'),
            (FST._code_as_alias_star, '*'),
            (FST._code_as_withitem, 'a'),
            (FST._code_as_withitem, 'a as b'),
            (FST._code_as_pattern, '42'),
            (FST._code_as_pattern, 'None'),
            (FST._code_as_pattern, '[_, *_]'),
            (FST._code_as_pattern, '{"key": _}'),
            (FST._code_as_pattern, 'SomeClass(attr=val)'),
            (FST._code_as_pattern, 'as_var'),
            (FST._code_as_pattern, '1 | 2 | 3'),
            (FST._code_as_pattern, '_'),
        ]

        if PYGE12:
            CODE_ASES.extend([
                (FST._code_as_type_param, 'T: int'),
            ])

        for code_as, src in CODE_ASES:
            self.assertEqual(src, code_as(src).src)
            self.assertEqual(src, code_as(f'{src}  ').src)

            if code_as in (FST._code_as_expr, FST._code_as_pattern):  # parenthesizable things so lets abuse
                srcp = f'(\n# pre\n{src} # post\n# post2\n)'

                self.assertEqual(srcp, code_as(srcp).src)

                if code_as is FST._code_as_expr:
                    self.assertEqual(src, code_as(srcp[1:-1]).src)

    def test_code_as_from_ast(self):
        for mode, func, res, src in PARSE_TESTS:
            if issubclass(res, Exception):
                continue

            ast = None

            try:
                if func in (FST._parse_stmtishs, FST._parse_stmtish,
                            FST._parse_ExceptHandlers, FST._parse_ExceptHandler,
                            FST._parse_match_cases, FST._parse_match_case):
                    continue

                ast  = FST._parse(src, mode)
                astc = copy_ast(ast)
                fst  = FST._code_as_all(ast)

                for a in walk(ast):
                    self.assertIs(False, getattr(a, 'f', False))

                self.assertIsNot(fst.a, ast)

                compare_asts(ast, fst.a, locs=False, raise_=True)
                compare_asts(ast, astc, locs=True, raise_=True)

            except Exception:
                print()
                print(f'{mode=}')
                print(f'{src=}')
                print(f'{res=}')
                print(f'{func=}')
                print(ast)

                raise

    def test_par(self):
        f = parse('1,').body[0].value.f.copy()
        f.par()  # self.assertTrue(f.par())
        self.assertEqual('(1,)', f.src)
        f.par()  # self.assertFalse(f.par())
        self.assertEqual('(1,)', f.src)
        f.par(force=True)  # self.assertTrue(f.par(force=True))
        self.assertEqual('((1,))', f.src)
        f.par()  # self.assertFalse(f.par())
        self.assertEqual('((1,))', f.src)

        # self.assertFalse(parse('()').body[0].value.f.copy().par())
        # self.assertFalse(parse('[]').body[0].value.f.copy().par())
        # self.assertFalse(parse('{}').body[0].value.f.copy().par())
        self.assertEqual('()', parse('()').body[0].value.f.copy().par().src)
        self.assertEqual('[]', parse('[]').body[0].value.f.copy().par().src)
        self.assertEqual('{}', parse('{}').body[0].value.f.copy().par().src)

        f = parse('i = 1').body[0].f.copy()
        f._put_src(['# comment', ''], 0, 0, 0, 0)
        f.par()  # self.assertFalse(f.par())
        self.assertEqual('# comment\ni = 1', f.src)
        f.par(force=True)  # self.assertTrue(f.par(force=True))
        self.assertEqual('(# comment\ni = 1)', f.src)

        if PYGE14:  # make sure parent Interpolation.str gets modified
            f = FST('t"{a}"', 'exec').body[0].value.copy()
            f.values[0].value.par(force=True)
            self.assertEqual('t"{(a)}"', f.src)
            self.assertEqual('(a)', f.values[0].str)

            f = FST('t"{a,}"', 'exec').body[0].value.copy()
            f.values[0].value.par(force=True)
            self.assertEqual('t"{(a,)}"', f.src)
            self.assertEqual('(a,)', f.values[0].str)

            f = FST('t"{a+b}"', 'exec').body[0].value.copy()
            f.values[0].value.par()
            self.assertEqual('t"{(a+b)}"', f.src)
            self.assertEqual('(a+b)', f.values[0].str)

        # grouping

        f = parse('[i]').f
        f.body[0].value.elts[0].par(force=True)
        self.assertEqual('[(i)]', f.src)
        self.assertEqual((0, 0, 0, 5), f.loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].value.loc)
        self.assertEqual((0, 2, 0, 3), f.body[0].value.elts[0].loc)

        f = parse('a + b').f
        f.body[0].value.left.par(force=True)
        f.body[0].value.right.par(force=True)
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)

        f = parse('a + b').f
        f.body[0].value.right.par(force=True)
        f.body[0].value.left.par(force=True)
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)
        f.body[0].value.par(force=True)
        self.assertEqual('((a) + (b))', f.src)
        f.body[0].value.left.par(force=True)
        self.assertEqual('(((a)) + (b))', f.src)
        f.body[0].value.right.par(force=True)
        self.assertEqual('(((a)) + ((b)))', f.src)

        f = parse('call(i for i in j)').f
        f.body[0].value.args[0].par(force=True)
        self.assertEqual(f.src, 'call((i for i in j))')
        f.body[0].value.args[0].par(force=True)
        self.assertEqual(f.src, 'call(((i for i in j)))')

        f = parse('i').body[0].value.f.copy()
        f._put_src('\n# post', 0, 1, 0, 1, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(True, whole=True)
        self.assertEqual((1, 0, 1, 1), f.loc)
        self.assertEqual(f.root.src, '(# pre\ni\n# post)')

        f = parse('i').body[0].value.f.copy()
        f._put_src('\n# post', 0, 1, 0, 1, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(True, whole=False)
        self.assertEqual((1, 1, 1, 2), f.loc)
        self.assertEqual(f.root.src, '# pre\n(i)\n# post')

        # Tuple

        f = parse('i,').f
        f.body[0].value.par()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('a, b').f
        f.body[0].value.par()
        self.assertEqual('(a, b)', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.elts[1].loc)

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(whole=True)
        self.assertEqual((0, 0, 2, 7), f.loc)
        self.assertEqual(f.src, '(# pre\ni,\n# post)')

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n(i,)\n# post')

        # MatchSequence

        f = FST('i,', pattern)
        f.par()
        self.assertEqual('[i,]', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 1, 0, 2), f.patterns[0].loc)

        f = FST('a, b', pattern)
        f.par()
        self.assertEqual('[a, b]', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 1, 0, 2), f.patterns[0].loc)
        self.assertEqual((0, 4, 0, 5), f.patterns[1].loc)

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(whole=True)
        self.assertEqual((0, 0, 2, 7), f.loc)
        self.assertEqual(f.src, '[# pre\ni,\n# post]')

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n[i,]\n# post')

        # special rules for Starred

        f = FST('*\na')
        f.par()
        self.assertEqual('*(\na)', f.src)
        f.verify()

        # unparenthesizable

        self.assertEqual('a:b:c', FST('a:b:c').par().src)
        self.assertEqual('for i in j', FST('for i in j').par().src)
        self.assertEqual('a: int, b=2', FST('a: int, b=2').par().src)
        self.assertEqual('a: int', FST('a: int', arg).par().src)
        self.assertEqual('key="word"', FST('key="word"', keyword).par().src)
        self.assertEqual('a as b', FST('a as b', alias).par().src)
        self.assertEqual('a as b', FST('a as b', withitem).par().src)

        if not PYLT13:
            self.assertEqual('t: int = int', FST('t: int = int', type_param).par().src)
            self.assertEqual('*t = (int,)', FST('*t = (int,)', type_param).par().src)
            self.assertEqual('**t = {T: int}', FST('**t = {T: int}', type_param).par().src)

        elif not PYLT12:
            self.assertEqual('t: int', FST('t: int', type_param).par().src)
            self.assertEqual('*t', FST('*t', type_param).par().src)
            self.assertEqual('**t', FST('**t', type_param).par().src)

    def test_unpar(self):
        f = parse('((1,))').body[0].value.f.copy(pars=True)
        self.assertEqual('((1,))', f.src)
        f.unpar()  # self.assertTrue()
        self.assertEqual('(1,)', f.src)
        f.unpar()  # self.assertFalse()
        self.assertEqual('(1,)', f.src)
        f.unpar(node=True)  # self.assertTrue()
        self.assertEqual('1,', f.src)
        f.unpar()  # self.assertFalse()

        # self.assertFalse(parse('()').body[0].value.f.copy().unpar())
        # self.assertFalse(parse('[]').body[0].value.f.copy().unpar())
        # self.assertFalse(parse('{}').body[0].value.f.copy().unpar())
        self.assertEqual('()', parse('()').body[0].value.f.copy().unpar().src)
        self.assertEqual('[]', parse('[]').body[0].value.f.copy().unpar().src)
        self.assertEqual('{}', parse('{}').body[0].value.f.copy().unpar().src)

        f = parse('( # pre1\n( # pre2\n1,\n # post1\n) # post2\n)').body[0].value.f.copy(pars=True)
        self.assertEqual('( # pre1\n( # pre2\n1,\n # post1\n) # post2\n)', f.src)
        f.unpar()  # self.assertTrue()
        self.assertEqual('( # pre2\n1,\n # post1\n)', f.src)
        f.unpar()  # self.assertFalse()
        self.assertEqual('( # pre2\n1,\n # post1\n)', f.src)
        f.unpar(node=True)  # self.assertTrue()
        self.assertEqual('1,', f.src)

        if PYGE14:  # make sure parent Interpolation.str gets modified
            f = FST('t"{(a)}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar()
            self.assertEqual('t"{a}"', f.src)
            self.assertEqual('a', f.values[0].str)

            f = FST('t"{((a,))}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar()
            self.assertEqual('t"{(a,)}"', f.src)
            self.assertEqual('(a,)', f.values[0].str)

            f = FST('t"{((a,))}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar(node=True)
            self.assertEqual('t"{a,}"', f.src)
            self.assertEqual('a,', f.values[0].str)

        # f = FST('a:b:c', 'expr_slice')  # no way to do this currenly, would need unpar(force) which would need lots of code just for this stupid unnatural case
        # f.par(True)
        # self.assertEqual('(a:b:c)', f.src)
        # f.unpar()
        # self.assertEqual('a:b:c', f.src)

        # grouping

        f = parse('a').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(a)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((a))').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(\n ( (a) )  \n)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((i,))').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('(\n ( (i,) ) \n)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0].unpar(shared=False)
        self.assertEqual(f.src, 'call((i for i in j))')
        self.assertEqual((0, 0, 0, 20), f.loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0].unpar(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call( ( ( (i for i in j) ) ) )').f
        f.body[0].value.args[0].unpar(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0].unpar(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0].unpar(shared=False)
        self.assertEqual(f.src, 'call((i for i in j),)')
        self.assertEqual((0, 0, 0, 21), f.loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('( # pre\ni\n# post\n)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('( # pre\ni\n# post\n)').body[0].value.f.copy(pars=True)
        f.unpar(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        f = parse('( # pre\n(i,)\n# post\n)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)

        f = parse('( # pre\n(i)\n# post\n)').body[0].value.f.copy(pars=True)
        f.unpar(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a)if(a)]', 'exec')
        f.body[0].value.generators[0].ifs[0].unpar(shared=False)
        f.body[0].value.generators[0].ifs[1].unpar(shared=False)
        self.assertEqual('[a for a in b if a if a]', f.src)

        f = FST('for(a)in b: pass', 'exec')
        f.body[0].target.unpar(shared=False)
        self.assertEqual('for a in b: pass', f.src)

        f = FST('assert(test)', 'exec')
        f.body[0].test.unpar(shared=False)
        self.assertEqual('assert test', f.src)

        f = FST('assert({test})', 'exec')
        f.body[0].test.unpar(shared=False)
        self.assertEqual('assert{test}', f.src)

        # tuple

        f = parse('()').f
        f.body[0].value.unpar()
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)

        f = parse('(i,)').f
        f.body[0].value.unpar(node=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('(a, b)').f
        f.body[0].value.unpar(node=True)
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.body[0].value.elts[1].loc)

        f = parse('( # pre\ni,\n# post\n)').f
        f.body[0].value.unpar(node=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('( # pre\ni,\n# post\n)').body[0].value.f.copy()
        f.unpar(node=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a,b)if(a,)if(a,b)]', 'exec')
        f.body[0].value.generators[0].ifs[0].unpar(node=True)
        f.body[0].value.generators[0].ifs[1].unpar(node=True)
        f.body[0].value.generators[0].ifs[2].unpar(node=True)
        self.assertEqual('[a for a in b if a,b if a,if a,b]', f.src)
        f.body[0].value.generators[0].ifs[0].par()  # so that it will verify
        f.body[0].value.generators[0].ifs[1].par()
        f.body[0].value.generators[0].ifs[2].par()
        self.assertEqual('[a for a in b if (a,b) if (a,)if (a,b)]', f.src)
        f.verify()

        f = FST('for(a,b)in b: pass', 'exec')
        f.body[0].target.unpar(node=True)
        self.assertEqual('for a,b in b: pass', f.src)
        f.verify()

        f = FST('for(a,)in b: pass', 'exec')
        f.body[0].target.unpar(node=True)
        self.assertEqual('for a,in b: pass', f.src)
        f.verify()

        # special rules for Starred

        f = FST('*(\na)')
        self.assertEqual('*(\na)', f.src)
        f.unpar()
        self.assertEqual('*a', f.src)
        f.verify()

        f = FST('*\na')
        f._parenthesize_grouping(star_child=False)
        self.assertEqual('(*\na)', f.src)
        f.unpar()
        self.assertEqual('(*\na)', f.src)

        # unowned pars

        f = FST('a:b:c')
        f.par(True)
        self.assertEqual('(a:b:c)', f.src)
        f.unpar(shared=None)
        self.assertEqual('a:b:c', f.src)

        f = FST('f(a)')
        f.args[0].unpar(shared=None)
        self.assertEqual('f a', f.src)

        f = FST('class c(a): pass')
        f.bases[0].unpar(shared=None)
        self.assertEqual('class c a: pass', f.src)

        f = FST('case c(a): pass')
        f.pattern.patterns[0].unpar(shared=None)
        self.assertEqual('case c a: pass', f.src)

        f = FST('from a import (b)')
        f.names[0].unpar(shared=None)
        self.assertEqual('from a import b', f.src)

    def test_pars(self):
        for src, elt, slice_copy in PARS_DATA:
            src  = src.strip()
            t    = parse(src)
            f    = eval(f't.{elt}', {'t': t}).f
            l    = f.pars()
            ssrc = f.get_src(*l)

            try:
                self.assertEqual(ssrc, slice_copy.strip())

            except Exception:
                print(elt)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_pars_special(self):
        f = parse('''
( (
 (
   a
  ) )
)
        '''.strip()).body[0].value.f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 0, 4, 1))

        f = parse('''
( (
 (
   a
  ) )
,)
        '''.strip()).body[0].value.elts[0].f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 2, 3, 5))

        f = parse('''
(

   a

,)
        '''.strip()).body[0].value.elts[0].f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (2, 3, 2, 4))

        self.assertEqual((0, 1, 0, 15), parse('f(i for i in j)').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 16), parse('f((i for i in j))').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 18), parse('f(((i for i in j)))').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 14), parse('f(i for i in j)').body[0].value.args[0].f.pars(shared=False))
        self.assertEqual((0, 2, 0, 16), parse('f((i for i in j))').body[0].value.args[0].f.pars(shared=False))
        self.assertEqual((0, 2, 0, 18), parse('f(((i for i in j)))').body[0].value.args[0].f.pars(shared=False))

        f = parse('((1), ( (2) ))').body[0].value.f
        self.assertEqual(1, f.elts[0].pars().n)
        self.assertEqual(2, f.elts[1].pars().n)
        self.assertEqual(0, f.pars().n)

        self.assertEqual(1, parse('call(((i for i in j)))').body[0].value.args[0].f.pars().n)
        self.assertEqual(0, parse('call((i for i in j))').body[0].value.args[0].f.pars().n)
        self.assertEqual(0, parse('call(i for i in j)').body[0].value.args[0].f.pars().n)
        self.assertEqual(-1, parse('call(i for i in j)').body[0].value.args[0].f.pars(shared=False).n)

        self.assertEqual((0, 8, 0, 9), parse('class c(b): pass').body[0].bases[0].f.pars())
        self.assertEqual((0, 8, 0, 9), parse('class c(b,): pass').body[0].bases[0].f.pars())
        self.assertEqual((0, 8, 0, 11), parse('class c((b)): pass').body[0].bases[0].f.pars())
        self.assertEqual((0, 8, 0, 11), parse('class c((b),): pass').body[0].bases[0].f.pars())

        self.assertEqual((0, 5, 0, 8), parse('with (a): pass').body[0].items[0].context_expr.f.pars())
        self.assertEqual((0, 5, 0, 8), parse('with (a): pass').body[0].items[0].f.pars())
        self.assertEqual((0, 5, 0, 10), parse('with ((a)): pass').body[0].items[0].context_expr.f.pars())
        self.assertEqual((0, 5, 0, 10), parse('with ((a)): pass').body[0].items[0].f.pars())
        self.assertEqual((0, 6, 0, 7), parse('with (a as b): pass').body[0].items[0].context_expr.f.pars())
        self.assertEqual((0, 6, 0, 12), parse('with (a as b): pass').body[0].items[0].f.pars())
        self.assertEqual((0, 6, 0, 9), parse('with ((a) as b): pass').body[0].items[0].context_expr.f.pars())
        self.assertEqual((0, 6, 0, 14), parse('with ((a) as b): pass').body[0].items[0].f.pars())
        self.assertRaises(SyntaxError, parse, 'with ((a as b)): pass')

        self.assertEqual((0, 15, 0, 16), parse('from a import (b)').body[0].names[0].f.pars())
        self.assertRaises(SyntaxError, parse, 'from a import ((b))')
        self.assertEqual((0, 15, 0, 21), parse('from a import (b as c)').body[0].names[0].f.pars())
        self.assertRaises(SyntaxError, parse, 'from a import ((b as c))')

        # tricky cases, large pars delta

        self.assertEqual('for i in (j)', FST('((i for i in (j)))', 'exec').body[0].value.generators[0].src)
        self.assertEqual((0, 2, 0, 5), FST('(((a), b))', 'exec').body[0].value.elts[0].pars())
        self.assertEqual((0, 5, 0, 8), FST('call((i),)', 'exec').body[0].value.args[0].pars())
        self.assertEqual((0, 5, 0, 10), FST('call(((i)),)', 'exec').body[0].value.args[0].pars())
        self.assertEqual((0, 8, 0, 13), FST('class c(((b))): pass', 'exec').body[0].bases[0].pars())
        self.assertEqual((0, 8, 0, 13), FST('class c(((b)),): pass', 'exec').body[0].bases[0].pars())
        self.assertEqual((0, 22, 0, 25), FST('call(i for i in range(256))', 'exec').body[0].value.args[0].generators[0].iter.args[0].pars())

        f = parse('bytes((x ^ 0x5C) for x in range(256))').body[0].value.f
        f.args[0].generators[0].iter.put('256', 0, field='args', raw=False)
        self.assertEqual('bytes((x ^ 0x5C) for x in range(256))', f.root.src)

        # unowned pars

        f = FST('a:b:c')
        f.par(True)
        self.assertEqual((0, 1, 0, 6), f.pars())
        self.assertEqual((0, 0, 0, 7), f.pars(None))

        f = FST('f(a)')
        self.assertEqual((0, 2, 0, 3), f.args[0].pars())
        self.assertEqual((0, 1, 0, 4), f.args[0].pars(None))

        f = FST('class c(a): pass')
        self.assertEqual((0, 8, 0, 9), f.bases[0].pars())
        self.assertEqual((0, 7, 0, 10), f.bases[0].pars(None))

        f = FST('case f(a): pass')
        self.assertEqual((0, 7, 0, 8), f.pattern.patterns[0].pars())
        self.assertEqual((0, 6, 0, 9), f.pattern.patterns[0].pars(None))

        f = FST('from a import (b)')
        self.assertEqual((0, 15, 0, 16), f.names[0].pars())
        self.assertEqual((0, 14, 0, 17), f.names[0].pars(None))

        # walruses

        self.assertEqual('b := c', FST('a, b := c, d').elts[1].copy(pars_walrus=False).src)
        self.assertEqual('b := c', FST('a = (b := c)').value.copy(pars_walrus=False).src)

        self.assertEqual('(b := c)', FST('a, b := c, d').elts[1].copy(pars_walrus=True).src)
        self.assertEqual('(b := c)', FST('a = (b := c)').value.copy(pars_walrus=True).src)

    def test_pars_n(self):
        self.assertEqual(1, FST('(a)', 'exec').body[0].value.pars().n)
        self.assertEqual(0, FST('(a, b)', 'exec').body[0].value.elts[0].pars().n)
        self.assertEqual(0, FST('(a, b)', 'exec').body[0].value.elts[1].pars().n)
        self.assertEqual(1, FST('((a), b)', 'exec').body[0].value.elts[0].pars().n)
        self.assertEqual(1, FST('(a, (b))', 'exec').body[0].value.elts[1].pars().n)

        self.assertEqual(0, FST('(a, b)', 'exec').body[0].value.pars().n)
        self.assertEqual(1, FST('((a, b))', 'exec').body[0].value.pars().n)

        self.assertEqual(0, FST('f(i for i in j)', 'exec').body[0].value.args[0].pars().n)
        self.assertEqual(-1, FST('f(i for i in j)', 'exec').body[0].value.args[0].pars(shared=False).n)
        self.assertTrue((f := FST('f(i for i in j)', 'exec').body[0].value.args[0]).pars(shared=False) > f.bloc)
        self.assertEqual(0, FST('f((i for i in j))', 'exec').body[0].value.args[0].pars(shared=False).n)
        self.assertTrue((f := FST('f((i for i in j))', 'exec').body[0].value.args[0]).pars(shared=False) == f.bloc)
        self.assertEqual(1, FST('f(((i for i in j)))', 'exec').body[0].value.args[0].pars(shared=False).n)
        self.assertTrue((f := FST('f(((i for i in j)))', 'exec').body[0].value.args[0]).pars(shared=False) < f.bloc)

    def test_copy_pars(self):
        self.assertEqual('a', parse('(a)').body[0].value.f.copy(pars=False).root.src)
        self.assertEqual('a', parse('(a)').body[0].value.f.copy(pars='auto').root.src)
        self.assertEqual('(a)', parse('(a)').body[0].value.f.copy(pars=True).root.src)
        self.assertEqual('a', parse('( # pre\na\n # post\n)').body[0].value.f.copy(pars=False).root.src)
        self.assertEqual('( # pre\na\n # post\n)', parse('( # pre\na\n # post\n)').body[0].value.f.copy(pars=True).root.src)

        self.assertEqual('b as c', parse('from a import (b as c)').body[0].names[0].f.copy(pars=False).root.src)
        self.assertEqual('b as c', parse('from a import (b as c)').body[0].names[0].f.copy(pars='auto').root.src)
        self.assertEqual('b as c', parse('from a import (b as c)').body[0].names[0].f.copy(pars=True).root.src)  # cannot be individually parenthesized
        self.assertEqual('b as c', parse('from a import (b as c, d as e)').body[0].names[0].f.copy(pars=False).root.src)
        self.assertEqual('b as c', parse('from a import ( # pre\nb as c\n# post\n)').body[0].names[0].f.copy(pars=False).root.src)
        self.assertEqual('b as c', parse('from a import ( # pre\nb as c\n# post\n)').body[0].names[0].f.copy(pars=True).root.src)  # cannot be individually parenthesized

        self.assertEqual('a as b', parse('with (a as b): pass').body[0].items[0].f.copy(pars=False).root.src)
        self.assertEqual('a as b', parse('with (a as b): pass').body[0].items[0].f.copy(pars='auto').root.src)
        self.assertEqual('a as b', parse('with (a as b): pass').body[0].items[0].f.copy(pars=True).root.src)  # cannot be individually parenthesized
        self.assertEqual('a as b', parse('with (a as b, c as d): pass').body[0].items[0].f.copy(pars=True).root.src)
        self.assertEqual('a as b', parse('with ( # pre\na as b\n# post\n): pass').body[0].items[0].f.copy(pars=False).root.src)
        self.assertEqual('a as b', parse('with ( # pre\na as b\n# post\n): pass').body[0].items[0].f.copy(pars=True).root.src)  # cannot be individually parenthesized

        self.assertEqual('1|2', parse('match a:\n case (1|2): pass').body[0].cases[0].pattern.f.copy(pars=False).root.src)
        self.assertEqual('1|2', parse('match a:\n case (1|2): pass').body[0].cases[0].pattern.f.copy(pars='auto').root.src)
        self.assertEqual('(1|2)', parse('match a:\n case (1|2): pass').body[0].cases[0].pattern.f.copy(pars=True).root.src)
        self.assertEqual('1|2', parse('match a:\n case ( # pre\n1|2\n# post\n): pass').body[0].cases[0].pattern.f.copy(pars=False).root.src)
        self.assertEqual('( # pre\n1|2\n# post\n)', parse('match a:\n case ( # pre\n1|2\n# post\n): pass').body[0].cases[0].pattern.f.copy(pars=True).root.src)

    def test_copy_special(self):
        f = FST.fromsrc('@decorator\nclass cls:\n  pass')
        self.assertEqual(f.a.body[0].f.copy().src, '@decorator\nclass cls:\n  pass')
        # self.assertEqual(f.a.body[0].f.copy(decos=False).src, 'class cls:\n  pass')

        l = FST.fromsrc("['\\u007f', '\\u0080', 'ʁ', 'ᛇ', '時', '🐍', '\\ud800', 'Źdźbło']").a.body[0].value.elts
        self.assertEqual("'\\u007f'", l[0].f.copy().src)
        self.assertEqual("'\\u0080'", l[1].f.copy().src)
        self.assertEqual("'ʁ'", l[2].f.copy().src)
        self.assertEqual("'ᛇ'", l[3].f.copy().src)
        self.assertEqual("'時'", l[4].f.copy().src)
        self.assertEqual("'🐍'", l[5].f.copy().src)
        self.assertEqual("'\\ud800'", l[6].f.copy().src)
        self.assertEqual("'Źdźbło'", l[7].f.copy().src)

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy()
        self.assertEqual('(w := x,)', f.src)

        # f = FST.fromsrc('a[1:2, 3:4]').a.body[0].value.slice.f.copy()
        # self.assertIs(f._fix(inplace=False), f)
        # self.assertRaises(SyntaxError, f.fix)
        # self.assertIs(None, f._fix(raise_=False))

        f = FST.fromsrc('''
if 1:
    def f():
        """
        strict docstring
        """
        """
        loose docstring
        """
            '''.strip())
        self.assertEqual('''
def f():
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    async def f():
        """
        strict docstring
        """
        """
        loose docstring
        """
            '''.strip())
        self.assertEqual('''
async def f():
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())
        self.assertEqual('''
class cls:
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())

        self.assertEqual('''
class cls:
    """
        strict docstring
        """
    """
        loose docstring
        """
            '''.strip(), f.a.body[0].body[0].f.copy(docstr=False).src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())

        self.assertEqual('''
class cls:
    """
    strict docstring
    """
    """
        loose docstring
        """
            '''.strip(), f.a.body[0].body[0].f.copy(docstr='strict').src)


        f = FST.fromsrc('''
# start

"""docstring"""

i = 1

# end
            '''.strip())
        self.assertEqual((g := f.copy()).get_src(*g.loc), f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            ''')
        self.assertEqual('i', a.body[0].f.copy(precomms=False, postcomms=False).src)
        self.assertEqual('# pre\ni', a.body[0].f.copy(precomms=True, postcomms=False).src)
        self.assertEqual('# pre\ni # post\n', a.body[0].f.copy(precomms=True, postcomms=True).src)
        self.assertEqual('# prepre\n\n# pre\ni', a.body[0].f.copy(precomms='all', postcomms=False).src)

        a = parse('( i )')
        self.assertEqual('i', a.body[0].value.f.copy(precomms=False, postcomms=False).src)
        self.assertEqual('( i )', a.body[0].value.f.copy(precomms=False, postcomms=False, pars=True).src)

        if PYGE12:
            f = FST.fromsrc('a[*b]').a.body[0].value.slice.f.copy()
            self.assertEqual('*b,', f.src)

            f = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy()
            self.assertEqual('*tuple[int, ...],', f.src)

        # misc

        self.assertEqual('opts.ignore_module', FST('''
opts.ignore_module = [mod.strip()
                      for i in opts.ignore_module for mod in i.split(',')]
            '''.strip(), 'exec').body[0].value.generators[0].iter.copy().src)

    def test_copy_bulk(self):
        for fnm in PYFNMS:
            ast = FST.fromsrc(read(fnm)).a

            for a in walk(ast):
                if a.f.is_parsable():
                    f = a.f.copy()

                    f.verify(raise_=True)

    def test_find_loc(self):
        f    = parse('abc += xyz').f
        fass = f.body[0]
        fabc = fass.target
        fpeq = fass.op
        fxyz = fass.value

        self.assertIs(fass, f.find_loc(0, 0, 0, 10))
        self.assertIs(None, f.find_loc(0, 0, 0, 10, False))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 3))
        self.assertIs(fass, f.find_loc(0, 0, 0, 3, False))
        self.assertIs(fass, f.find_loc(0, 0, 0, 4))
        self.assertIs(fass, f.find_loc(0, 0, 0, 4, False))
        self.assertIs(fass, f.find_loc(0, 3, 0, 4, False))
        self.assertIs(fpeq, f.find_loc(0, 4, 0, 6))
        self.assertIs(fass, f.find_loc(0, 4, 0, 6, False))
        self.assertIs(fxyz, f.find_loc(0, 7, 0, 10))
        self.assertIs(fass, f.find_loc(0, 7, 0, 10, False))
        self.assertIs(fass, f.find_loc(0, 6, 0, 10))
        self.assertIs(fass, f.find_loc(0, 6, 0, 10, False))

        f  = parse('a+b').f
        fx = f.body[0]
        fo = fx.value
        fa = fo.left
        fp = fo.op
        fb = fo.right

        self.assertIs(fa, f.find_loc(0, 0, 0, 0))
        self.assertIs(fp, f.find_loc(0, 1, 0, 1))
        self.assertIs(fb, f.find_loc(0, 2, 0, 2))
        self.assertIs(f, f.find_loc(0, 3, 0, 3))
        self.assertIs(fa, f.find_loc(0, 0, 0, 1))
        self.assertIs(fo, f.find_loc(0, 0, 0, 2))
        self.assertIs(fo, f.find_loc(0, 0, 0, 3))
        self.assertIs(fp, f.find_loc(0, 1, 0, 2))
        self.assertIs(fo, f.find_loc(0, 1, 0, 3))
        self.assertIs(fb, f.find_loc(0, 2, 0, 3))

    def test_find_in_loc(self):
        f    = parse('abc += xyz').body[0].f
        fabc = f.target
        fpeq = f.op
        fxyz = f.value

        self.assertIs(f, f.find_in_loc(0, 0, 0, 10))
        self.assertIs(f, f.find_in_loc(-1, -1, 1, 11))
        self.assertIs(fabc, f.find_in_loc(0, 0, 0, 3))
        self.assertIs(fpeq, f.find_in_loc(0, 1, 0, 10))
        self.assertIs(fxyz, f.find_in_loc(0, 5, 0, 10))
        self.assertIs(None, f.find_in_loc(0, 5, 0, 6))

    def test_fstview(self):
        self.assertEqual('a', parse('if 1: a').f.body[0].body[0].src)
        self.assertEqual('b', parse('if 1: a\nelse: b').f.body[0].orelse[0].src)
        self.assertEqual('a\nb\nc', parse('a\nb\nc').f.body.copy().src)

        f = parse('a\nb\nc').f
        g = f.body.cut()
        self.assertEqual('', f.src)
        self.assertEqual('a\nb\nc', g.src)

        f = parse('a\nb\nc\nd\ne').f
        g = f.body[1:4].cut()
        self.assertEqual('a\ne', f.src)
        self.assertEqual('b\nc\nd', g.src)

        f = parse('a\nb\nc\nd\ne').f
        g = f.body[1:4]
        g.replace('f')
        self.assertEqual(1, len(g))
        self.assertEqual('f', g[0].src)
        self.assertEqual('a\nf\ne', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.append('d')
        self.assertEqual(2, len(g))
        self.assertEqual('b', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('a\nb\nd\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.extend('d\ne')
        self.assertEqual(3, len(g))
        self.assertEqual('b', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('a\nb\nd\ne\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prepend('d')
        self.assertEqual(2, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('b', g[1].src)
        self.assertEqual('a\nd\nb\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prextend('d\ne')
        self.assertEqual(3, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('e', g[1].src)
        self.assertEqual('b', g[2].src)
        self.assertEqual('a\nd\ne\nb\nc', f.src)

        f = parse('a\nb\nc').f
        f.body[1:2] = 'd\ne'
        self.assertEqual('a\nd\ne\nc', f.src)

        f = parse('a\nb\nc').f
        f.body[1] = 'd'
        self.assertEqual('a\nd\nc', f.src)

        f = parse('a\nb\nc\nd\ne').f
        f.body[1:4] = 'f'
        self.assertEqual('a\nf\ne', f.src)

        f = parse('a\nb\nc\nd\ne').f
        f.body[1:4] = 'f\ng'
        self.assertEqual('a\nf\ng\ne', f.src)

        f = parse('a\nb\nc').f
        def test():
            f.body[1] = 'd\ne'
        self.assertRaises(ValueError, test)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prextend('d\ne')

        f = parse('a\nb\nc').f
        g = f.body
        g.cut()
        self.assertEqual(0, len(g))
        self.assertEqual('', f.src)
        g.append('d')
        self.assertEqual(1, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('d\n', f.src)
        g.prepend('e')
        self.assertEqual(2, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('e\nd\n', f.src)
        g.extend('f\ng')
        self.assertEqual(4, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('f', g[2].src)
        self.assertEqual('g', g[3].src)
        self.assertEqual('e\nd\nf\ng\n', f.src)
        g.prextend('h\ni')
        self.assertEqual(6, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('i', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('d', g[3].src)
        self.assertEqual('f', g[4].src)
        self.assertEqual('g', g[5].src)
        self.assertEqual('h\ni\ne\nd\nf\ng\n', f.src)
        g.replace('h')
        self.assertEqual(1, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('h\n', f.src)
        g.insert('i')
        self.assertEqual(2, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('h', g[1].src)
        self.assertEqual('i\nh\n', f.src)
        g.insert('j', 1)
        self.assertEqual(3, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('h', g[2].src)
        self.assertEqual('i\nj\nh\n', f.src)
        g.insert('k', -1)
        self.assertEqual(4, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('i\nj\nk\nh\n', f.src)
        g.insert('l', 'end')
        self.assertEqual(5, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('l', g[4].src)
        self.assertEqual('i\nj\nk\nh\nl\n', f.src)

        f = parse('x\na\nb\nc\ny').f
        g = f.body[1:-1]
        g.cut()
        self.assertEqual(0, len(g))
        self.assertEqual('x\ny', f.src)
        g.append('d')
        self.assertEqual(1, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('x\nd\ny', f.src)
        g.prepend('e')
        self.assertEqual(2, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('x\ne\nd\ny', f.src)
        g.extend('f\ng')
        self.assertEqual(4, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('f', g[2].src)
        self.assertEqual('g', g[3].src)
        self.assertEqual('x\ne\nd\nf\ng\ny', f.src)
        g.prextend('h\ni')
        self.assertEqual(6, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('i', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('d', g[3].src)
        self.assertEqual('f', g[4].src)
        self.assertEqual('g', g[5].src)
        self.assertEqual('x\nh\ni\ne\nd\nf\ng\ny', f.src)
        g.replace('h')
        self.assertEqual(1, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('x\nh\ny', f.src)
        g.insert('i')
        self.assertEqual(2, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('h', g[1].src)
        self.assertEqual('x\ni\nh\ny', f.src)
        g.insert('j', 1)
        self.assertEqual(3, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('h', g[2].src)
        self.assertEqual('x\ni\nj\nh\ny', f.src)
        g.insert('k', -1)
        self.assertEqual(4, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('x\ni\nj\nk\nh\ny', f.src)
        g.insert('l', 'end')
        self.assertEqual(5, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('l', g[4].src)
        self.assertEqual('x\ni\nj\nk\nh\nl\ny', f.src)

        a = parse('''
class cls:
    def prefunc(): pass
    def postfunc(): pass
            '''.strip())
        self.assertIsInstance(a.f.body, fstview)
        self.assertIsInstance(a.body[0].f.body, fstview)
        a.body[0].f.body.cut()
        self.assertIsInstance(a.body[0].f.body, fstview)

        a = parse('a\nb\nc\nd\ne')
        p = a.f.body[1:4]
        g = p[1]
        f = p.replace('f')
        self.assertEqual('a\nf\ne', a.f.src)
        self.assertEqual(1, len(f))
        self.assertEqual('f', f[0].src)
        self.assertIsNone(g.a)

        c = FST('a\nb').body
        c[0] = None
        self.assertEqual('b', c.fst.src)
        self.assertEqual(1, c.stop)

        c = FST.new().body
        c[0:0] = 'a\nb'
        self.assertEqual('a\nb\n', c.fst.src)
        self.assertEqual(2, c.stop)

    def test_is_node_type_properties_and_parents(self):
        fst = parse('''
match a:
    case 1:
        try:
            pass
        except Exception:
            class cls:
                def f():
                    return [lambda: None for i in ()]
            '''.strip())

        f = fst.body[0].cases[0].body[0].handlers[0].body[0].body[0].body[0].value.elt.body.f
        self.assertEqual(f.src, 'None')

        self.assertIsInstance((f := f.parent_scope()).a, Lambda)
        self.assertTrue(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertTrue(f.is_scope)
        self.assertFalse(f.is_block)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmtish)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_scope()).a, ListComp)
        self.assertTrue(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertTrue(f.is_scope)
        self.assertFalse(f.is_block)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmtish)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_named_scope()).a, FunctionDef)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmtish)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_named_scope()).a, ClassDef)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmtish)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmtish()).a, ExceptHandler)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_scope)
        self.assertTrue(f.is_block)
        self.assertFalse(f.is_stmt)
        self.assertTrue(f.is_stmtish)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmt()).a, Try)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_scope)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmtish)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmtish()).a, match_case)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_scope)
        self.assertTrue(f.is_block)
        self.assertFalse(f.is_stmt)
        self.assertTrue(f.is_stmtish)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_block()).a, Match)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_scope)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmtish)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_scope()).a, Module)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_block)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmtish)
        self.assertTrue(f.is_mod)

    def test_options(self):
        new = dict(
            docstr    = 'test_docstr',
            precomms  = 'test_precomms',
            postcomms = 'test_postcomms',
            prespace  = 'test_prespace',
            postspace = 'test_postspace',
            pep8space = 'test_pep8space',
            pars      = 'test_pars',
            elif_     = 'test_elif_',
            raw       = 'test_raw',
        )

        old    = FST.set_options(**new)
        newset = FST.set_options(**old)
        oldset = FST.set_options(**old)

        self.assertEqual(newset, new)
        self.assertEqual(oldset, old)

        with FST.options(**new) as opts:
            self.assertEqual(opts, old)
            self.assertEqual(new, FST.set_options(**new))

        self.assertEqual(old, FST.set_options(**old))

        try:
            with FST.options(**new) as opts:
                self.assertEqual(opts, old)
                self.assertEqual(new, FST.set_options(**new))

                raise NodeError

        except NodeError:
            pass

        self.assertEqual(old, FST.set_options(**old))

    def test_reconcile(self):
        # basic replacements

        m = (o := FST('i = 1')).mark()

        o.a.value = Name(id='test')
        f = o.reconcile(m)
        self.assertEqual('i = test', f.src)
        f.verify()

        o.a.targets[0].id = 'blah'
        f = o.reconcile(m)
        self.assertEqual('blah = test', f.src)
        f.verify()

        o.a.value = copy_ast(o.a.targets[0])
        f = o.reconcile(m)
        self.assertEqual('blah = blah', f.src)
        f.verify()

        o.a.value.ctx = Load()
        o.a.targets[0].ctx = Store()
        f = o.reconcile(m)
        self.assertEqual('blah = blah', f.src)
        f.verify()

        # error causing parent replacement

        m = (o := FST("f'{a}'")).mark()

        o.a.values[0].conversion = 97
        f = o.reconcile(m)
        self.assertEqual("f'{a!a}'", f.src)
        f.verify()

        o.a.values[0].conversion = 115
        f = o.reconcile(m)
        self.assertEqual("f'{a!s}'", f.src)
        f.verify()

        o.a.values[0].conversion = 114
        f = o.reconcile(m)
        self.assertEqual("f'{a!r}'", f.src)
        f.verify()

        o.a.values[0].conversion = -1
        f = o.reconcile(m)
        self.assertEqual("f'{a}'", f.src)
        f.verify()

        # misc change ctx

        m = (o := FST('i')).mark()
        o.a.ctx = Load()
        f = o.reconcile(m)
        self.assertEqual('i', f.src)
        self.assertIsInstance(f.a.ctx.f, FST)
        f.verify()

        # AST from same tree moved around

        m = (o := FST('i = a')).mark()
        o.a.value = Starred(value=o.a.value)
        f = o.reconcile(m)
        self.assertEqual('i = *a', f.src)
        f.verify()

        # FST from another tree

        m = (o := FST('i = 1')).mark()
        o.a.value = FST('(x,\n # comment\ny)').a
        f = o.reconcile(m)
        self.assertEqual('i = (x,\n # comment\ny)', f.src)
        f.verify()

        # delete one from non-slice

        m = (o := FST('def f() -> int: pass')).mark()
        o.a.returns = None
        f = o.reconcile(m)
        self.assertEqual('def f(): pass', f.src)
        f.verify()

        # add nonexistent node from pure AST

        m = (o := FST('def f(): int')).mark()
        o.a.returns = Name(id='str')
        f = o.reconcile(m)
        self.assertEqual('def f() -> str: int', f.src)
        f.verify()

        # add nonexistent node from same tree

        m = (o := FST('def f(): int')).mark()
        o.a.returns = o.a.body[0].value
        f = o.reconcile(m)
        self.assertEqual('def f() -> int: int', f.src)
        f.verify()

        # replace root from same tree

        m = (o := FST('def f(): int')).mark()
        o.a = o.a.body[0].value
        f = o.reconcile(m)
        self.assertIsInstance(f.a, Name)
        self.assertEqual('int', f.src)
        f.verify()

        # replace root from different tree

        m = (o := FST('def f(): int')).mark()
        o.a = FST('call()').a
        f = o.reconcile(m)
        self.assertIsInstance(f.a, Call)
        self.assertEqual('call()', f.src)
        f.verify()

        # replace root from pure AST

        m = (o := FST('def f(): int')).mark()
        o.a = Name(id='hello')
        f = o.reconcile(m)
        self.assertIsInstance(f.a, Name)
        self.assertEqual('hello', f.src)
        f.verify()

        # simple slice replace

        m = (o := FST('[\n1,  # one\n2,  # two\n3   # three\n]')).mark()
        o.a.elts[0] = Constant(value=-1)
        o.a.elts[1] = Constant(value=-2)
        o.a.elts[2] = Constant(value=-3)
        f = o.reconcile(m)
        self.assertEqual('[\n-1,  # one\n-2,  # two\n-3   # three\n]', f.src)
        f.verify()

        # 2 level pure AST

        m = (o := FST('i = 1')).mark()
        o.a.value = List(elts=[Name(id='a')])
        f = o.reconcile(m)
        self.assertEqual('i = [a]', f.src)
        f.verify()

        # level 1 pure AST, level 2 from another tree

        m = (o := FST('i = 1')).mark()
        o.a.value = List(elts=[FST('(a, # yay!\n)').a])
        f = o.reconcile(m)
        self.assertEqual('i = [(a, # yay!\n)]', f.src)
        f.verify()

        # level 1 pure AST, level 2 from same tree

        m = (o := FST('i = (a, # yay!\n)')).mark()
        o.a.value = List(elts=[o.value.a])
        f = o.reconcile(m)
        self.assertEqual('i = [(a, # yay!\n)]', f.src)
        f.verify()

        # slice, don't do first because src is at end and don't do second because dst is at end

        m = (o := FST('[\n1, # 1\n2, # 2\n]')).mark()
        a = o.a.elts[0]
        o.a.elts[0] = o.a.elts[1]
        o.a.elts[1] = a
        f = o.reconcile(m)
        self.assertEqual('[\n2, # 2\n1, # 1\n]', f.src)
        f.verify()

        # slice, delete tail

        m = (o := FST('[1, 2, 3, 4]')).mark()
        del o.a.elts[2:]
        f = o.reconcile(m)
        self.assertEqual('[1, 2]', f.src)
        f.verify()

        m = (o := FST('[1, 2, 3, 4]')).mark()
        del o.a.elts[:]
        f = o.reconcile(m)
        self.assertEqual('[]', f.src)
        f.verify()

        # slice, swap two from same tree

        m = (o := FST('[1, 2, 3, 4]')).mark()
        e0 = o.a.elts[0]
        e1 = o.a.elts[1]
        o.a.elts[0] = o.a.elts[2]
        o.a.elts[1] = o.a.elts[3]
        o.a.elts[2] = e0
        o.a.elts[3] = e1
        f = o.reconcile(m)
        self.assertEqual('[3, 4, 1, 2]', f.src)
        f.verify()

        # slice, extend from same tree

        m = (o := FST('[1, 2, 3]')).mark()
        o.a.elts.extend(o.a.elts[:2])
        f = o.reconcile(m)
        self.assertEqual('[1, 2, 3, 1, 2]', f.src)
        f.verify()

        # slice, extend from different tree

        m = (o := FST('[1, 2, 3]')).mark()
        o.a.elts.extend(FST('[4, 5]').a.elts)
        f = o.reconcile(m)
        self.assertEqual('[1, 2, 3, 4, 5]', f.src)
        f.verify()

        # slice, extend from pure ASTs

        m = (o := FST('[1, 2, 3]')).mark()
        o.a.elts.extend([Name(id='x'), Name(id='y')])
        f = o.reconcile(m)
        self.assertEqual('[1, 2, 3, x, y]', f.src)
        f.verify()

        m = (o := FST('i = 1\nj = 2\nk = 3')).mark()
        o.a.body.append(Assign(targets=[Name(id='x')], value=Constant(value=4)))
        o.a.body.append(Assign(targets=[Name(id='y')], value=Constant(value=5)))
        f = o.reconcile(m)
        self.assertEqual('i = 1\nj = 2\nk = 3\nx = 4\ny = 5\n', f.src)
        f.verify()

        # other recurse slice FST

        m = (o := FST('[1]')).mark()
        o.a.elts.extend(FST('[2,#2\n3,#3\n4,#4\n]').a.elts)
        f = o.reconcile(m)
        self.assertEqual('[1, 2,#2\n3,#3\n4,#4\n]', f.src)
        f.verify()

        m = (o := FST('{a: b, **c}')).mark()
        o.a.keys[1] = o.a.keys[0]
        o.a.keys[0] = None
        f = o.reconcile(m)
        self.assertEqual('{**b, a: c}', f.src)
        f.verify()

        m = (o := FST('if 1:\n  i = 1\n  j = 2\n  k = 3\nelse:\n  a = 4\n  b = 5\n  c = 6')).mark()
        body = o.a.body[:]
        o.a.body[:] = o.a.orelse[1:]
        o.a.orelse = body * 2
        f = o.reconcile(m)
        self.assertEqual('if 1:\n  b = 5\n  c = 6\nelse:\n  i = 1\n  j = 2\n  k = 3\n  i = 1\n  j = 2\n  k = 3\n', f.src)
        f.verify()

        m = (o := FST('def f(*, a=1, b=2): pass')).mark()
        o.a.args.kw_defaults[0] = None
        f = o.reconcile(m)
        self.assertEqual('def f(*, a, b=2): pass', f.src)
        f.verify()

        m = (o := FST('{1: a, **b}', MatchMapping)).mark()
        o.a.rest = None
        f = o.reconcile(m)
        self.assertEqual('{1: a}', f.src)
        f.verify()

        m = (o := FST('{1: a, **b}', MatchMapping)).mark()
        o.a.rest = 'rest'
        f = o.reconcile(m)
        self.assertEqual('{1: a, **rest}', f.src)
        f.verify()

        m = (o := FST('{1: a}', MatchMapping)).mark()
        o.a.rest = 'rest'
        f = o.reconcile(m)
        self.assertEqual('{1: a, **rest}', f.src)
        f.verify()

        # recurse slice in pure AST that has FSTs

        m = (o := FST('[\n1, # 1\n2, # 2\n]')).mark()
        o.a = List(elts=[o.a.elts[1], o.a.elts[0]])
        f = o.reconcile(m)
        self.assertEqual('[\n2, # 2\n1, # 1\n]', f.src)
        f.verify()

        m = (o := FST('[1,\n# 1and2\n2, 3,\n# 3and4\n4]')).mark()
        o.a = List(elts=[o.a.elts[2], o.a.elts[3], o.a.elts[0], o.a.elts[1]])
        f = o.reconcile(m)
        self.assertEqual('[3,\n# 3and4\n4, 1,\n# 1and2\n2]', f.src)
        f.verify()

        m = (o := FST('[1,#1\n]')).mark()
        o.a = List(elts=[o.a.elts[0]])
        o.a.elts.extend(FST('[2,#2\n3,#3\n4,#4\n]').a.elts)
        f = o.reconcile(m)
        self.assertEqual('[1, #1\n 2,#2\n3,#3\n4,#4\n]', f.src)
        f.verify()

        m = (o := FST('{a: b, **c}')).mark()
        o.a = Dict(keys=[None, o.a.keys[0]], values=[o.a.values[0], o.a.values[1]])
        f = o.reconcile(m)
        self.assertEqual('{**b, a: c}', f.src)
        f.verify()

        m = (o := FST('def f(*, a=1, b=2): pass')).mark()
        o.a.args = arguments(kwonlyargs=o.a.args.kwonlyargs, kw_defaults=[None, o.a.args.kw_defaults[1]], posonlyargs=[], args=[], defaults=[])
        f = o.reconcile(m)
        self.assertEqual('def f(*, a, b=2): pass', f.src)
        f.verify()

        m = (o := FST('{1: a, **b}', MatchMapping)).mark()
        o.a = MatchMapping(keys=[o.a.keys[0]], patterns=[o.a.patterns[0]], rest=None)
        f = o.reconcile(m)
        self.assertEqual('{1: a}', f.src)
        f.verify()

        m = (o := FST('{1: a, **b}', MatchMapping)).mark()
        o.a = MatchMapping(keys=[o.a.keys[0]], patterns=[o.a.patterns[0]], rest='rest')
        f = o.reconcile(m)
        self.assertEqual('{1: a, **rest}', f.src)
        f.verify()

        m = (o := FST('{1: a}', MatchMapping)).mark()
        o.a = MatchMapping(keys=[o.a.keys[0]], patterns=[o.a.patterns[0]], rest='rest')
        f = o.reconcile(m)
        self.assertEqual('{1: a, **rest}', f.src)
        f.verify()

        # Dict

        m = (o := FST('{a: b}')).mark()
        o.a.keys[0] = Name(id='x')
        o.a.values[0] = Name(id='y')
        f = o.reconcile(m)
        self.assertEqual('{x: y}', f.src)
        f.verify()

        m = (o := FST('{a: b}')).mark()
        o.a.keys[0] = None
        f = o.reconcile(m)
        self.assertEqual('{**b}', f.src)
        f.verify()

        m = (o := FST('{a : b, c : d}')).mark()
        a = o.a
        a.keys.append(Name(id='x'))
        a.values.append(Name(id='y'))
        a.keys.extend(a.keys[:2])
        a.values.extend(a.values[:2])
        b = FST('{s : t, u : v}').a
        a.keys.extend(b.keys)
        a.values.extend(b.values)
        f = o.reconcile(m)
        self.assertEqual('{a : b, c : d, x: y, a : b, c : d, s : t, u : v}', f.src)
        f.verify()

        m = (o := FST('{a : b, c : d}')).mark()
        a = o.a
        a.keys.append(Name(id='x'))
        a.values.append(Name(id='y'))
        a.keys.extend(a.keys[:2])
        a.values.extend(a.values[:2])
        b = FST('{s : t, u : v}').a
        a.keys.extend(b.keys)
        a.values.extend(b.values)
        o.a = Dict(keys=o.a.keys, values=o.a.values)
        f = o.reconcile(m)
        self.assertEqual('{a : b, c : d, x: y, a : b, c : d, s : t, u : v}', f.src)
        f.verify()

        # operators

        o = FST('a or b or c')
        m = o.mark()
        o.a.op = And()
        f = o.reconcile(m)
        self.assertEqual('a and b and c', f.src)
        f.verify()

        o = FST('a or b or c')
        m = o.mark()
        o.a.op = FST(And()).a
        f = o.reconcile(m)
        self.assertEqual('a and b and c', f.src)
        f.verify()

        o = FST('a or b or c\nd and e')
        m = o.mark()
        o.a.body[0].value.op = o.a.body[1].value.op
        f = o.reconcile(m)
        self.assertEqual('a and b and c\nd and e', f.src)
        f.verify()

        o = FST('a + b')
        m = o.mark()
        o.a.op = Mult()
        f = o.reconcile(m)
        self.assertEqual('a * b', f.src)
        f.verify()

        o = FST('a + b')
        m = o.mark()
        o.a.op = FST(Mult()).a
        f = o.reconcile(m)
        self.assertEqual('a * b', f.src)
        f.verify()

        o = FST('a + b')
        m = o.mark()
        o.a.op = FST('*=').a
        f = o.reconcile(m)
        self.assertEqual('a * b', f.src)
        f.verify()

        o = FST('a + b\nc * d')
        m = o.mark()
        o.a.body[0].value.op = o.a.body[1].value.op
        f = o.reconcile(m)
        self.assertEqual('a * b\nc * d', f.src)
        f.verify()

        o = FST('a + b\nc *= d')
        m = o.mark()
        o.a.body[0].value.op = o.a.body[1].op
        f = o.reconcile(m)
        self.assertEqual('a * b\nc *= d', f.src)
        f.verify()

        o = FST('a += b')
        m = o.mark()
        o.a.op = Mult()
        f = o.reconcile(m)
        self.assertEqual('a *= b', f.src)
        f.verify()

        o = FST('a += b')
        m = o.mark()
        o.a.op = FST(Mult()).a
        f = o.reconcile(m)
        self.assertEqual('a *= b', f.src)
        f.verify()

        o = FST('a += b')
        m = o.mark()
        o.a.op = FST('*=').a
        f = o.reconcile(m)
        self.assertEqual('a *= b', f.src)
        f.verify()

        o = FST('a += b\nc *= d')
        m = o.mark()
        o.a.body[0].op = o.a.body[1].op
        f = o.reconcile(m)
        self.assertEqual('a *= b\nc *= d', f.src)
        f.verify()

        o = FST('a += b\nc * d')
        m = o.mark()
        o.a.body[0].op = o.a.body[1].value.op
        f = o.reconcile(m)
        self.assertEqual('a *= b\nc * d', f.src)
        f.verify()

        o = FST('-a')
        m = o.mark()
        o.a.op = Not()
        f = o.reconcile(m)
        self.assertEqual('not a', f.src)
        f.verify()

        o = FST('-a')
        m = o.mark()
        o.a.op = FST(Not()).a
        f = o.reconcile(m)
        self.assertEqual('not a', f.src)
        f.verify()

        o = FST('-a\nnot b')
        m = o.mark()
        o.a.body[0].value.op = o.a.body[1].value.op
        f = o.reconcile(m)
        self.assertEqual('not a\nnot b', f.src)
        f.verify()

        o = FST('a<b')
        m = o.mark()
        o.a.ops[0] = IsNot()
        f = o.reconcile(m)
        self.assertEqual('a is not b', f.src)
        f.verify()

        o = FST('a<b')
        m = o.mark()
        o.a.ops[0] = FST(IsNot()).a
        f = o.reconcile(m)
        self.assertEqual('a is not b', f.src)
        f.verify()

        o = FST('a<b\nc is not d')
        m = o.mark()
        o.a.body[0].value.ops[0] = o.a.body[1].value.ops[0]
        f = o.reconcile(m)
        self.assertEqual('a is not b\nc is not d', f.src)
        f.verify()

        # misc

        if not PYLT12:
            m = (o := FST(r'''
if 1:
    "a\n"
    f"{f()}"
                '''.strip(), 'exec')).mark()
            o.a.body[0].body[1].value.values[0].value.func = o.a.body[0].body[0]
            f = o.reconcile(m)
            self.assertEqual(r'''
if 1:
    "a\n"
    f"{"a\n"()}"
                '''.strip(), f.src)
            f.verify()

        a = (o := FST('[\n[\n[\n[\n[\n[\n[\n[\nx,#0\n0\n],#1\n1\n],#2\n2\n],#3\n3\n],#4\n4\n],#5\n5\n],#6\n6\n],#7\n7\n]')).a
        m = o.mark()
        a.elts[0] = List(elts=[a.elts[0].elts[0]])
        a.elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0]])
        f = o.reconcile(m)
        self.assertEqual('[\n[\n[\n[\n[\n[\n[\n[\nx,#0\n],#1\n1\n],#2\n],#3\n3\n],#4\n],#5\n5\n],#6\n],#7\n7\n]', f.src)
        f.verify()

        a = (o := FST('[\n[\n[\n[\n[\n[\n[\n[\nx,#0\n0\n],#1\n1\n],#2\n2\n],#3\n3\n],#4\n4\n],#5\n5\n],#6\n6\n],#7\n7\n]')).a
        m = o.mark()
        o.a = List(elts=[a.elts[0]])
        a.elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0]])
        f = o.reconcile(m)
        self.assertEqual('[\n[\n[\n[\n[\n[\n[\n[\nx,#0\n0\n],#1\n],#2\n2\n],#3\n],#4\n4\n],#5\n],#6\n6\n],#7\n]', f.src)
        f.verify()

        a = (o := FST('f(#0\ng(#1\nh(#2\ni(#3\n))))')).a
        m = o.mark()
        a.args[0] = Call(func=Name('g'), args=[a.args[0].args[0]], keywords=[])
        a.args[0].args[0].args[0] = Call(func=Name('i'), args=[], keywords=[])
        f = o.reconcile(m)
        self.assertEqual('f(#0\ng(h(#2\ni())))', f.src)
        f.verify()

        # make sure modifications are detected

        m = (o := FST('i = 1')).mark()
        o.value.par(True)
        self.assertRaises(RuntimeError, o.reconcile, m)

    def test_reconcile_slices(self):
        m = (o := FST('a # a\nb # b\nc # c', 'exec')).mark()
        o.a.body[0] = o.a.body[1]
        o.a.body[1] = o.a.body[2]
        f = o.reconcile(m)
        self.assertEqual('b # b\nc # c\nc # c', f.src)
        f.verify()

        m = (o := FST('{\na, # a\nb, # b\nc, # c\n}', 'exec')).mark()
        o.a.body[0].value.elts[0] = o.a.body[0].value.elts[1]
        o.a.body[0].value.elts[1] = o.a.body[0].value.elts[2]
        f = o.reconcile(m)
        self.assertEqual('{\nb, # b\nc, # c\nc, # c\n}', f.src)
        f.verify()

        m = (o := FST('[\na, # a\nb, # b\nc, # c\n]', 'exec')).mark()
        o.a.body[0].value.elts[0] = o.a.body[0].value.elts[1]
        o.a.body[0].value.elts[1] = o.a.body[0].value.elts[2]
        f = o.reconcile(m)
        self.assertEqual('[\nb, # b\nc, # c\nc, # c\n]', f.src)
        f.verify()

        m = (o := FST('(\na, # a\nb, # b\nc, # c\n)', 'exec')).mark()
        o.a.body[0].value.elts[0] = o.a.body[0].value.elts[1]
        o.a.body[0].value.elts[1] = o.a.body[0].value.elts[2]
        f = o.reconcile(m)
        self.assertEqual('(\nb, # b\nc, # c\nc, # c\n)', f.src)
        f.verify()

        m = (o := FST('{\na:a, # a\nb:b, # b\nc:c, # c\n}', 'exec')).mark()
        o.a.body[0].value.keys[0] = o.a.body[0].value.keys[1]
        o.a.body[0].value.values[0] = o.a.body[0].value.values[1]
        o.a.body[0].value.keys[1] = o.a.body[0].value.keys[2]
        o.a.body[0].value.values[1] = o.a.body[0].value.values[2]
        f = o.reconcile(m)
        self.assertEqual('{\nb:b, # b\nc:c, # c\nc:c, # c\n}', f.src)
        f.verify()

        m = (o := FST('@a # a\n@b # b\n@c # c\ndef f(): pass', 'exec')).mark()
        o.a.body[0].decorator_list[0] = o.a.body[0].decorator_list[1]
        o.a.body[0].decorator_list[1] = o.a.body[0].decorator_list[2]
        f = o.reconcile(m)
        self.assertEqual('@b # a\n@c # b\n@c # c\ndef f(): pass', f.src)
        f.verify()

        m = (o := FST('@a # a\n@b # b\n@c # c\nasync def f(): pass', 'exec')).mark()
        o.a.body[0].decorator_list[0] = o.a.body[0].decorator_list[1]
        o.a.body[0].decorator_list[1] = o.a.body[0].decorator_list[2]
        f = o.reconcile(m)
        self.assertEqual('@b # a\n@c # b\n@c # c\nasync def f(): pass', f.src)
        f.verify()

        m = (o := FST('@a # a\n@b # b\n@c # c\nclass cls: pass', 'exec')).mark()
        o.a.body[0].decorator_list[0] = o.a.body[0].decorator_list[1]
        o.a.body[0].decorator_list[1] = o.a.body[0].decorator_list[2]
        f = o.reconcile(m)
        self.assertEqual('@b # a\n@c # b\n@c # c\nclass cls: pass', f.src)
        f.verify()

        m = (o := FST('class cls(a,b,c): pass', 'exec')).mark()
        o.a.body[0].bases[0] = o.a.body[0].bases[1]
        o.a.body[0].bases[1] = o.a.body[0].bases[2]
        f = o.reconcile(m)
        self.assertEqual('class cls(b,c,c): pass', f.src)
        f.verify()

        m = (o := FST('del a,b,c', 'exec')).mark()
        o.a.body[0].targets[0] = o.a.body[0].targets[1]
        o.a.body[0].targets[1] = o.a.body[0].targets[2]
        f = o.reconcile(m)
        self.assertEqual('del b,c,c', f.src)
        f.verify()

        m = (o := FST('a=b=c = d', 'exec')).mark()
        o.a.body[0].targets[0] = o.a.body[0].targets[1]
        o.a.body[0].targets[1] = o.a.body[0].targets[2]
        f = o.reconcile(m)
        self.assertEqual('b=c=c = d', f.src)
        f.verify()

        m = (o := FST('a  or  b  or  c', 'exec')).mark()
        o.a.body[0].value.values[0] = o.a.body[0].value.values[1]
        o.a.body[0].value.values[1] = o.a.body[0].value.values[2]
        f = o.reconcile(m)
        self.assertEqual('b  or  c  or  c', f.src)
        f.verify()

        m = (o := FST('call(a,b,c)', 'exec')).mark()
        o.a.body[0].value.args[0] = o.a.body[0].value.args[1]
        o.a.body[0].value.args[1] = o.a.body[0].value.args[2]
        f = o.reconcile(m)
        self.assertEqual('call(b,c,c)', f.src)
        f.verify()

        m = (o := FST('[i for i in j if a if b if c]', 'exec')).mark()
        o.a.body[0].value.generators[0].ifs[0] = o.a.body[0].value.generators[0].ifs[1]
        o.a.body[0].value.generators[0].ifs[1] = o.a.body[0].value.generators[0].ifs[2]
        f = o.reconcile(m)
        self.assertEqual('[i for i in j if b if c if c]', f.src)
        f.verify()

        m = (o := FST('[i for k in l if k for j in k if j for i in j if i]', 'exec')).mark()
        o.a.body[0].value.generators[0] = o.a.body[0].value.generators[1]
        o.a.body[0].value.generators[1] = o.a.body[0].value.generators[2]
        f = o.reconcile(m)
        self.assertEqual('[i for j in k if j for i in j if i for i in j if i]', f.src)
        f.verify()

        m = (o := FST('{i for k in l if k for j in k if j for i in j if i}', 'exec')).mark()
        o.a.body[0].value.generators[0] = o.a.body[0].value.generators[1]
        o.a.body[0].value.generators[1] = o.a.body[0].value.generators[2]
        f = o.reconcile(m)
        self.assertEqual('{i for j in k if j for i in j if i for i in j if i}', f.src)
        f.verify()

        m = (o := FST('{i: i for k in l if k for j in k if j for i in j if i}', 'exec')).mark()
        o.a.body[0].value.generators[0] = o.a.body[0].value.generators[1]
        o.a.body[0].value.generators[1] = o.a.body[0].value.generators[2]
        f = o.reconcile(m)
        self.assertEqual('{i: i for j in k if j for i in j if i for i in j if i}', f.src)
        f.verify()

        m = (o := FST('(i for k in l if k for j in k if j for i in j if i)', 'exec')).mark()
        o.a.body[0].value.generators[0] = o.a.body[0].value.generators[1]
        o.a.body[0].value.generators[1] = o.a.body[0].value.generators[2]
        f = o.reconcile(m)
        self.assertEqual('(i for j in k if j for i in j if i for i in j if i)', f.src)
        f.verify()

        m = (o := FST('class cls(a=1,b=2,c=3): pass', 'exec')).mark()
        o.a.body[0].keywords[0] = o.a.body[0].keywords[1]
        o.a.body[0].keywords[1] = o.a.body[0].keywords[2]
        f = o.reconcile(m)
        self.assertEqual('class cls(b=2,c=3,c=3): pass', f.src)
        f.verify()

        m = (o := FST('call(a=1,b=2,c=3)', 'exec')).mark()
        o.a.body[0].value.keywords[0] = o.a.body[0].value.keywords[1]
        o.a.body[0].value.keywords[1] = o.a.body[0].value.keywords[2]
        f = o.reconcile(m)
        self.assertEqual('call(b=2,c=3,c=3)', f.src)
        f.verify()

        m = (o := FST('import a,b,c', 'exec')).mark()
        o.a.body[0].names[0] = o.a.body[0].names[1]
        o.a.body[0].names[1] = o.a.body[0].names[2]
        f = o.reconcile(m)
        self.assertEqual('import b,c,c', f.src)
        f.verify()

        m = (o := FST('from z import a,b,c', 'exec')).mark()
        o.a.body[0].names[0] = o.a.body[0].names[1]
        o.a.body[0].names[1] = o.a.body[0].names[2]
        f = o.reconcile(m)
        self.assertEqual('from z import b,c,c', f.src)
        f.verify()

        m = (o := FST('with a  as  a, b  as  b, c  as  c: pass', 'exec')).mark()
        o.a.body[0].items[0] = o.a.body[0].items[1]
        o.a.body[0].items[1] = o.a.body[0].items[2]
        f = o.reconcile(m)
        self.assertEqual('with b  as  b, c  as  c, c  as  c: pass', f.src)
        f.verify()

        m = (o := FST('async with a  as  a, b  as  b, c  as  c: pass', 'exec')).mark()
        o.a.body[0].items[0] = o.a.body[0].items[1]
        o.a.body[0].items[1] = o.a.body[0].items[2]
        f = o.reconcile(m)
        self.assertEqual('async with b  as  b, c  as  c, c  as  c: pass', f.src)
        f.verify()

        m = (o := FST('case [a,b,c]: pass', 'match_case')).mark()
        o.a.pattern.patterns[0] = o.a.pattern.patterns[1]
        o.a.pattern.patterns[1] = o.a.pattern.patterns[2]
        f = o.reconcile(m)
        self.assertEqual('case [b,c,c]: pass', f.src)
        f.verify()

        m = (o := FST('case {1:a,2:b,3:c}: pass', 'match_case')).mark()
        o.a.pattern.keys[0] = o.a.pattern.keys[1]
        o.a.pattern.patterns[0] = o.a.pattern.patterns[1]
        o.a.pattern.keys[1] = o.a.pattern.keys[2]
        o.a.pattern.patterns[1] = o.a.pattern.patterns[2]
        f = o.reconcile(m)
        self.assertEqual('case {2:b,3:c,3:c}: pass', f.src)
        f.verify()

        m = (o := FST('case cls(a,b,c): pass', 'match_case')).mark()
        o.a.pattern.patterns[0] = o.a.pattern.patterns[1]
        o.a.pattern.patterns[1] = o.a.pattern.patterns[2]
        f = o.reconcile(m)
        self.assertEqual('case cls(b,c,c): pass', f.src)
        f.verify()

        m = (o := FST('case a|b|c: pass', 'match_case')).mark()
        o.a.pattern.patterns[0] = o.a.pattern.patterns[1]
        o.a.pattern.patterns[1] = o.a.pattern.patterns[2]
        f = o.reconcile(m)
        self.assertEqual('case b|c|c: pass', f.src)
        f.verify()

        m = (o := FST('global a,b,c', 'exec')).mark()
        o.a.body[0].names[0] = o.a.body[0].names[1]
        o.a.body[0].names[1] = o.a.body[0].names[2]
        f = o.reconcile(m)
        self.assertEqual('global b,c,c', f.src)
        f.verify()

        m = (o := FST('nonlocal a,b,c', 'exec')).mark()
        o.a.body[0].names[0] = o.a.body[0].names[1]
        o.a.body[0].names[1] = o.a.body[0].names[2]
        f = o.reconcile(m)
        self.assertEqual('nonlocal b,c,c', f.src)
        f.verify()

        m = (o := FST("f'a{a}b{b}c{c}'", 'exec')).mark()
        o.a.body[0].value.values[0] = o.a.body[0].value.values[2]
        o.a.body[0].value.values[1] = o.a.body[0].value.values[3]
        o.a.body[0].value.values[2] = o.a.body[0].value.values[4]
        o.a.body[0].value.values[3] = o.a.body[0].value.values[5]
        f = o.reconcile(m)
        self.assertEqual("f'b{b}c{c}c{c}'", f.src.rstrip())
        f.verify()

        if not PYLT12:
            m = (o := FST('def f[T,U,V](): pass', 'exec')).mark()
            o.a.body[0].type_params[0] = o.a.body[0].type_params[1]
            o.a.body[0].type_params[1] = o.a.body[0].type_params[2]
            f = o.reconcile(m)
            self.assertEqual('def f[U,V,V](): pass', f.src)
            f.verify()

            m = (o := FST('async def f[T,U,V](): pass', 'exec')).mark()
            o.a.body[0].type_params[0] = o.a.body[0].type_params[1]
            o.a.body[0].type_params[1] = o.a.body[0].type_params[2]
            f = o.reconcile(m)
            self.assertEqual('async def f[U,V,V](): pass', f.src)
            f.verify()

            m = (o := FST('class cls[T,U,V]: pass', 'exec')).mark()
            o.a.body[0].type_params[0] = o.a.body[0].type_params[1]
            o.a.body[0].type_params[1] = o.a.body[0].type_params[2]
            f = o.reconcile(m)
            self.assertEqual('class cls[U,V,V]: pass', f.src)
            f.verify()

            m = (o := FST('type t[T,U,V] = ...', 'exec')).mark()
            o.a.body[0].type_params[0] = o.a.body[0].type_params[1]
            o.a.body[0].type_params[1] = o.a.body[0].type_params[2]
            f = o.reconcile(m)
            self.assertEqual('type t[U,V,V] = ...', f.src)
            f.verify()

        if not PYLT14:
            m = (o := FST("t'a{a}b{b}c{c}'", 'exec')).mark()
            o.a.body[0].value.values[0] = o.a.body[0].value.values[2]
            o.a.body[0].value.values[1] = o.a.body[0].value.values[3]
            o.a.body[0].value.values[2] = o.a.body[0].value.values[4]
            o.a.body[0].value.values[3] = o.a.body[0].value.values[5]
            f = o.reconcile(m)
            self.assertEqual("t'b{b}c{c}c{c}'", f.src)
            f.verify()

        # non-slice lists

        m = (o := FST('def f(a=1,b=2,/,c=3,d=4,*,e=5,f=6): pass', 'exec')).mark()
        o.a.body[0].args.posonlyargs[0] = o.a.body[0].args.posonlyargs[1]
        o.a.body[0].args.defaults[0] = o.a.body[0].args.defaults[1]
        o.a.body[0].args.args[0] = o.a.body[0].args.args[1]
        o.a.body[0].args.defaults[2] = o.a.body[0].args.defaults[3]
        o.a.body[0].args.kwonlyargs[0] = o.a.body[0].args.kwonlyargs[1]
        o.a.body[0].args.kw_defaults[0] = o.a.body[0].args.kw_defaults[1]
        f = o.reconcile(m)
        self.assertEqual('def f(b=2,b=2,/,d=4,d=4,*,f=6,f=6): pass', f.src)
        f.verify()

        m = (o := FST('case cls(a=1,b=2,c=3): pass', 'match_case')).mark()
        o.a.pattern.kwd_attrs[0] = o.a.pattern.kwd_attrs[1]
        o.a.pattern.kwd_patterns[0] = o.a.pattern.kwd_patterns[1]
        o.a.pattern.kwd_attrs[1] = o.a.pattern.kwd_attrs[2]
        o.a.pattern.kwd_patterns[1] = o.a.pattern.kwd_patterns[2]
        f = o.reconcile(m)
        self.assertEqual('case cls(b=2,c=3,c=3): pass', f.src)
        f.verify()

    def test_ast_accessors(self):
        def test(f, field, put, expect, src=None):
            got = getattr(f, field)

            if expect is None:
                self.assertEqual(str(got) if isinstance(got, fstview) else got, src)  # fstview for kwd_attrs

            else:
                self.assertIsInstance(got, expect)

                if src is not None:
                    if expect is FST:
                        self.assertEqual(src, got.src)

                    else:
                        try:
                            self.assertEqual(src, got.copy().src)
                        except NotImplementedError:  # TODO: because not all slices are implemented prescribed
                            self.assertEqual(src, str(got))

                        except ValueError as exc:
                            if not str(exc).startswith('cannot get slice from'):
                                raise

                            self.assertEqual(src, got[0].copy().src)

            try:
                setattr(f, field, put)

            except NotImplementedError:
                with FST.options(raw=True):
                    try:
                        setattr(f, field, put)

                    except ValueError as exc:
                        if not str(exc).startswith('cannot specify a field'):
                            raise

                        getattr(f, field)[0] = put

            except ValueError as exc:
                if not str(exc).startswith('cannot put slice to'):
                    raise

                getattr(f, field)[0] = put

            f.verify()

            return f

        self.assertEqual('a\n', test(FST('i\nj', 'exec'), 'body', 'a', fstview, 'i\nj').src)
        self.assertEqual('a\n', test(FST('i;j', 'single'), 'body', 'a', fstview, 'i;j').src)
        self.assertEqual('a', test(FST('i', 'eval'), 'body', 'a', FST, 'i').src)

        f = FST('@deco\ndef func(args) -> ret: pass')
        self.assertEqual('@neco\ndef func(args) -> ret: pass', test(f, 'decorator_list', '@neco', fstview,
                                                                    '<<FunctionDef ROOT 1,0..1,27>.decorator_list[0:1] [<Name 0,1..0,5>]>').src)
        self.assertEqual('@neco\ndef new(args) -> ret: pass', test(f, 'name', 'new', None, 'func').src)
        self.assertEqual('@neco\ndef new(nargs) -> ret: pass', test(f, 'args', 'nargs', FST, 'args').src)
        self.assertEqual('@neco\ndef new(nargs) -> int: pass', test(f, 'returns', 'int', FST, 'ret').src)
        self.assertEqual('@neco\ndef new(nargs) -> int:\n    return\n', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('@deco\nasync def func(args) -> ret: pass')
        self.assertEqual('@neco\nasync def func(args) -> ret: pass', test(f, 'decorator_list', '@neco', fstview,
                                                                          '<<AsyncFunctionDef ROOT 1,0..1,33>.decorator_list[0:1] [<Name 0,1..0,5>]>').src)
        self.assertEqual('@neco\nasync def new(args) -> ret: pass', test(f, 'name', 'new', None, 'func').src)
        self.assertEqual('@neco\nasync def new(nargs) -> ret: pass', test(f, 'args', 'nargs', FST, 'args').src)
        self.assertEqual('@neco\nasync def new(nargs) -> int: pass', test(f, 'returns', 'int', FST, 'ret').src)
        self.assertEqual('@neco\nasync def new(nargs) -> int:\n    return\n', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('@deco\nclass cls(base, meta=other): pass')
        self.assertEqual('@neco\nclass cls(base, meta=other): pass', test(f, 'decorator_list', '@neco', fstview,
                                                                          '<<ClassDef ROOT 1,0..1,33>.decorator_list[0:1] [<Name 0,1..0,5>]>').src)
        self.assertEqual('@neco\nclass new(base, meta=other): pass', test(f, 'name', 'new', None, 'cls').src)
        self.assertEqual('@neco\nclass new(bass, meta=other): pass', test(f, 'bases', 'bass', fstview,
                                                                          '<<ClassDef ROOT 1,0..1,33>.bases[0:1] [<Name 1,10..1,14>]>').src)
        self.assertEqual('@neco\nclass new(bass, moto=some): pass', test(f, 'keywords', 'moto=some', fstview,
                                                                         '<<ClassDef ROOT 1,0..1,33>.keywords[0:1] [<keyword 1,16..1,26>]>').src)
        self.assertEqual('@neco\nclass new(bass, moto=some):\n    return\n', test(f, 'body', 'return', fstview, 'pass').src)

        self.assertEqual('return yup', test(FST('return yes'), 'value', 'yup', FST, 'yes').src)

        self.assertEqual('del zzz', test(FST('del a, b'), 'targets', 'zzz', fstview,
                                         '<<Delete ROOT 0,0..0,8>.targets[0:2] [<Name 0,4..0,5>, <Name 0,7..0,8>]>').src)

        self.assertEqual('zzz = c', test(FST('a, b = c'), 'targets', 'zzz', fstview,
                                         '<<Assign ROOT 0,0..0,8>.targets[0:1] [<Tuple 0,0..0,4>]>').src)
        self.assertEqual('a, b = zzz', test(FST('a, b = c'), 'value', 'zzz', FST, 'c').src)

        f = FST('a += b')
        self.assertEqual('new += b', test(f, 'target', 'new', FST, 'a').src)
        self.assertEqual('new >>= b', test(f, 'op', '>>=', FST, '+=').src)
        self.assertEqual('new >>= zzz', test(f, 'value', 'zzz', FST, 'b').src)

        f = FST('a: int = v')
        self.assertEqual('new: int = v', test(f, 'target', 'new', FST, 'a').src)
        self.assertEqual('new: int = zzz', test(f, 'value', 'zzz', FST, 'v').src)
        self.assertEqual('new: str = zzz', test(f, 'annotation', 'str', FST, 'int').src)
        self.assertEqual('(new): str = zzz', test(f, 'simple', 0, None, 1).src)

        f = FST('for a, b in c: pass\nelse: pass')
        self.assertEqual('for new in c: pass\nelse: pass', test(f, 'target', 'new', FST, 'a, b').src)
        self.assertEqual('for new in zzz: pass\nelse: pass', test(f, 'iter', 'zzz', FST, 'c').src)
        self.assertEqual('for new in zzz:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('for new in zzz:\n    return\nelse:\n    continue\n', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('async for a, b in c: pass\nelse: pass')
        self.assertEqual('async for new in c: pass\nelse: pass', test(f, 'target', 'new', FST, 'a, b').src)
        self.assertEqual('async for new in zzz: pass\nelse: pass', test(f, 'iter', 'zzz', FST, 'c').src)
        self.assertEqual('async for new in zzz:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('async for new in zzz:\n    return\nelse:\n    continue\n', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('while a: pass\nelse: pass')
        self.assertEqual('while new: pass\nelse: pass', test(f, 'test', 'new', FST, 'a').src)
        self.assertEqual('while new:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('while new:\n    return\nelse:\n    continue\n', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('if a: pass\nelse: pass')
        self.assertEqual('if new: pass\nelse: pass', test(f, 'test', 'new', FST, 'a').src)
        self.assertEqual('if new:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('if new:\n    return\nelse:\n    continue\n', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('with a as b: pass')
        self.assertEqual('with old as new: pass', test(f, 'items', 'old as new', fstview,
                                                       '<<With ROOT 0,0..0,17>.items[0:1] [<withitem 0,5..0,11>]>').src)
        self.assertEqual('with old as new:\n    return\n', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('async with a as b: pass')
        self.assertEqual('async with old as new: pass', test(f, 'items', 'old as new', fstview,
                                                       '<<AsyncWith ROOT 0,0..0,23>.items[0:1] [<withitem 0,11..0,17>]>').src)
        self.assertEqual('async with old as new:\n    return\n', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('match a:\n    case _: pass')
        self.assertEqual('match new:\n    case _: pass', test(f, 'subject', 'new', FST, 'a').src)
        self.assertEqual('match new:\n    case 1: return\n', test(f, 'cases', 'case 1: return', fstview, 'case _: pass').src)

        f = FST('raise exc from cause')
        self.assertEqual('raise e from cause', test(f, 'exc', 'e', FST, 'exc').src)
        self.assertEqual('raise e from c', test(f, 'cause', 'c', FST, 'cause').src)

        f = FST('try: pass\nexcept: pass\nelse: pass\nfinally: pass')
        self.assertEqual('try:\n    return\nexcept: pass\nelse: pass\nfinally: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse: pass\nfinally: pass', test(f, 'handlers', 'except Exception as e: continue', fstview, 'except: pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse:\n    break\nfinally: pass', test(f, 'orelse', 'break', fstview, 'pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse:\n    break\nfinally:\n    f()\n', test(f, 'finalbody', 'f()', fstview, 'pass').src)

        f = FST('assert test, "msg"')
        self.assertEqual('assert toast, "msg"', test(f, 'test', 'toast', FST, 'test').src)
        self.assertEqual('assert toast, "sheep"', test(f, 'msg', '"sheep"', FST, '"msg"').src)

        self.assertEqual('import a, b, c', test(FST('import x, y'), 'names', 'a, b, c', fstview,
                                                '<<Import ROOT 0,0..0,11>.names[0:2] [<alias 0,7..0,8>, <alias 0,10..0,11>]>').src)

        f = FST('from .module import x, y')
        self.assertEqual('from .new import x, y', test(f, 'module', 'new', None, 'module').src)
        self.assertEqual('from .new import a, b, c', test(f, 'names', 'a, b, c', fstview,
                                                          '<<ImportFrom ROOT 0,0..0,21>.names[0:2] [<alias 0,17..0,18>, <alias 0,20..0,21>]>').src)
        self.assertEqual('from ...new import a, b, c', test(f, 'level', 3, None, 1).src)

        self.assertEqual('global a, b, c', test(FST('global x, y'), 'names', 'a, b, c', fstview,
                                                "<<Global ROOT 0,0..0,11>.names[0:2] ['x', 'y']>").src)

        self.assertEqual('nonlocal a, b, c', test(FST('nonlocal x, y'), 'names', 'a, b, c', fstview,
                                                  "<<Nonlocal ROOT 0,0..0,13>.names[0:2] ['x', 'y']>").src)

        self.assertEqual('new', test(FST('v', Expr), 'value', 'new', FST, 'v').src)

        f = FST('a and b and c')
        self.assertEqual('<<BoolOp ROOT 0,0..0,13>.values[0:3] [<Name 0,0..0,1>, <Name 0,6..0,7>, <Name 0,12..0,13>]>', str(f.values))
        self.assertEqual('a or b or c', test(f, 'op', 'or', FST, 'and').src)

        f = FST('(a := b)')
        self.assertEqual('(new := b)', test(f, 'target', 'new', FST, 'a').src)
        self.assertEqual('(new := old)', test(f, 'value', 'old', FST, 'b').src)

        f = FST('a + b')
        self.assertEqual('new + b', test(f, 'left', 'new', FST, 'a').src)
        self.assertEqual('new >> b', test(f, 'op', '>>', FST, '+').src)
        self.assertEqual('new >> newtoo', test(f, 'right', 'newtoo', FST, 'b').src)

        f = FST('-a')
        self.assertEqual('not a', test(f, 'op', 'not', FST, '-').src)
        self.assertEqual('not new', test(f, 'operand', 'new', FST, 'a').src)

        f = FST('lambda a: None')
        self.assertEqual('lambda args: None', test(f, 'args', 'args', FST, 'a').src)
        self.assertEqual('lambda args: new', test(f, 'body', 'new', FST, 'None').src)

        f = FST('a if b else c')
        self.assertEqual('new if b else c', test(f, 'body', 'new', FST, 'a').src)
        self.assertEqual('new if test else c', test(f, 'test', 'test', FST, 'b').src)
        self.assertEqual('new if test else blah', test(f, 'orelse', 'blah', FST, 'c').src)

        f = FST('{a: b}')
        self.assertEqual('<<Dict ROOT 0,0..0,6>.keys[0:1] [<Name 0,1..0,2>]>', str(f.keys))
        self.assertEqual('<<Dict ROOT 0,0..0,6>.values[0:1] [<Name 0,4..0,5>]>', str(f.values))

        self.assertEqual('{a, b, c}', test(FST('{x, y}'), 'elts', '{a, b, c}', fstview, '{x, y}').src)

        f = FST('[i for i in j if i]')
        self.assertEqual('[new for i in j if i]', test(f, 'elt', 'new', FST, 'i').src)
        self.assertEqual('[new async for dog in dogs]', test(f, 'generators', 'async for dog in dogs', fstview,
                                                             '<<ListComp ROOT 0,0..0,21>.generators[0:1] [<comprehension 0,5..0,20>]>').src)

        f = FST('{i for i in j if i}')
        self.assertEqual('{new for i in j if i}', test(f, 'elt', 'new', FST, 'i').src)
        self.assertEqual('{new async for dog in dogs}', test(f, 'generators', 'async for dog in dogs', fstview,
                                                             '<<SetComp ROOT 0,0..0,21>.generators[0:1] [<comprehension 0,5..0,20>]>').src)

        f = FST('{i: i for i in j if i}')
        self.assertEqual('{new: i for i in j if i}', test(f, 'key', 'new', FST, 'i').src)
        self.assertEqual('{new: old for i in j if i}', test(f, 'value', 'old', FST, 'i').src)
        self.assertEqual('{new: old async for dog in dogs}', test(f, 'generators', 'async for dog in dogs', fstview,
                                                             '<<DictComp ROOT 0,0..0,26>.generators[0:1] [<comprehension 0,10..0,25>]>').src)

        f = FST('(i for i in j if i)')
        self.assertEqual('(new for i in j if i)', test(f, 'elt', 'new', FST, 'i').src)
        self.assertEqual('(new async for dog in dogs)', test(f, 'generators', 'async for dog in dogs', fstview,
                                                             '<<GeneratorExp ROOT 0,0..0,21>.generators[0:1] [<comprehension 0,5..0,20>]>').src)

        self.assertEqual('await yup', test(FST('await yes'), 'value', 'yup', FST, 'yes').src)

        self.assertEqual('yield yup', test(FST('yield yes'), 'value', 'yup', FST, 'yes').src)

        self.assertEqual('yield from yup', test(FST('yield from yes'), 'value', 'yup', FST, 'yes').src)

        f = FST('a < b < c')
        self.assertEqual('new < b < c', test(f, 'left', 'new', FST, 'a').src)
        self.assertEqual('<<Compare ROOT 0,0..0,11>.ops[0:2] [<Lt 0,4..0,5>, <Lt 0,8..0,9>]>', str(f.ops))
        self.assertEqual('<<Compare ROOT 0,0..0,11>.comparators[0:2] [<Name 0,6..0,7>, <Name 0,10..0,11>]>', str(f.comparators))

        f = FST('call(arg, kw=blah)')
        self.assertEqual('call(a, b, kw=blah)', test(f, 'args', 'a, b', fstview,
                                                     '<<Call ROOT 0,0..0,18>.args[0:1] [<Name 0,5..0,8>]>').src)
        self.assertEqual('call(a, b, kw1=bloh, kws=hmm)', test(f, 'keywords', 'kw1=bloh, kws=hmm', fstview,
                                                               '<<Call ROOT 0,0..0,19>.keywords[0:1] [<keyword 0,11..0,18>]>').src)

        f = FST('u"a"')
        self.assertEqual('u', f.kind)
        self.assertEqual("'new'", test(f, 'value', 'new', None, 'a').src)
        self.assertEqual("u'new'", test(f, 'kind', 'u', None, None).src)

        f = FST('a.b')
        self.assertEqual('new.b', test(f, 'value', 'new', FST, 'a').src)
        self.assertEqual('new.dog', test(f, 'attr', 'dog', None, 'b').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('a[b]')
        self.assertEqual('new[b]', test(f, 'value', 'new', FST, 'a').src)
        self.assertEqual('new[dog]', test(f, 'slice', 'dog', FST, 'b').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('*a')
        self.assertEqual('*new', test(f, 'value', 'new', FST, 'a').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('name')
        self.assertEqual('new', test(f, 'id', 'new', None, 'name').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('[a, b]')
        self.assertEqual('[x, y, z]', test(f, 'elts', '[x, y, z]', fstview, '[a, b]').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('(a, b)')
        self.assertEqual('(x, y, z)', test(f, 'elts', '(x, y, z)', fstview, '(a, b)').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('a:b:c')
        self.assertEqual('low:b:c', test(f, 'lower', 'low', FST, 'a').src)
        self.assertEqual('low:up:c', test(f, 'upper', 'up', FST, 'b').src)
        self.assertEqual('low:up:st', test(f, 'step', 'st', FST, 'c').src)

        f = FST('for i in j if i')
        self.assertEqual('for new in j if i', test(f, 'target', 'new', FST, 'i').src)
        self.assertEqual('for new in blah if i', test(f, 'iter', 'blah', FST, 'j').src)
        self.assertEqual('for new in blah if new', test(f, 'ifs', 'if new', fstview,
                                                        '<<comprehension ROOT 0,0..0,20>.ifs[0:1] [<Name 0,19..0,20>]>').src)
        self.assertEqual('async for new in blah if new', test(f, 'is_async', 1, None, 0).src)

        f = FST('except Exception as exc: pass')
        self.assertEqual('except ValueError as exc: pass', test(f, 'type', 'ValueError', FST, 'Exception').src)
        self.assertEqual('except ValueError as blah: pass', test(f, 'name', 'blah', None, 'exc').src)
        self.assertEqual('except ValueError as blah:\n    return\n', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('a, /, b=c, *d, e=f, **g')
        self.assertEqual('new, /, b=c, *d, e=f, **g', test(f, 'posonlyargs', 'new', fstview, 'a').src)
        self.assertEqual('new, /, blah=c, *d, e=f, **g', test(f, 'args', 'blah', fstview, 'b').src)
        self.assertEqual('new, /, blah=cat, *d, e=f, **g', test(f, 'defaults', 'cat', fstview, 'c').src)
        self.assertEqual('new, /, blah=cat, *va, e=f, **g', test(f, 'vararg', 'va', FST, 'd').src)
        self.assertEqual('new, /, blah=cat, *va, lemur=f, **g', test(f, 'kwonlyargs', 'lemur', fstview, 'e').src)
        self.assertEqual('new, /, blah=cat, *va, lemur=raisin, **g', test(f, 'kw_defaults', 'raisin', fstview, 'f').src)
        self.assertEqual('new, /, blah=cat, *va, lemur=raisin, **splat', test(f, 'kwarg', 'splat', FST, 'g').src)

        f = FST('a: int', arg)
        self.assertEqual('new: int', test(f, 'arg', 'new', None, 'a').src)
        self.assertEqual('new: list', test(f, 'annotation', 'list', FST, 'int').src)

        f = FST('a=blah', keyword)
        self.assertEqual('new=blah', test(f, 'arg', 'new', None, 'a').src)
        self.assertEqual('new=dog', test(f, 'value', 'dog', FST, 'blah').src)

        f = FST('a as b', alias)
        self.assertEqual('new as b', test(f, 'name', 'new', None, 'a').src)
        self.assertEqual('new as cat', test(f, 'asname', 'cat', None, 'b').src)

        f = FST('a as b', withitem)
        self.assertEqual('new as b', test(f, 'context_expr', 'new', FST, 'a').src)
        self.assertEqual('new as cat', test(f, 'optional_vars', 'cat', FST, 'b').src)

        f = FST('case a if b: pass')
        self.assertEqual('case new if b: pass', test(f, 'pattern', 'new', FST, 'a').src)
        self.assertEqual('case new if old: pass', test(f, 'guard', 'old', FST, 'b').src)
        self.assertEqual('case new if old:\n    return\n', test(f, 'body', 'return', fstview, 'pass').src)

        self.assertEqual('2', test(FST('1', MatchValue), 'value', '2', FST, '1').src)

        self.assertEqual('True', test(FST('False', MatchSingleton), 'value', True, None, False).src)

        self.assertEqual('[a, b, c]', test(FST('[x, y]', MatchSequence), 'patterns', 'a, b, c', fstview, '[x, y]').src)

        f = FST('{1: a, **b}', MatchMapping)
        self.assertEqual('{2: a, **b}', test(f, 'keys', '2', fstview, '1').src)
        # self.assertEqual('{2: new, **b}', test(f, None, 'new', fstview,
        #                                        '<<MatchMapping ROOT 0,0..0,11>.patterns[0:1] [<MatchAs 0,4..0,5>]>').src)
        self.assertEqual('{2: a, **rest}', test(f, 'rest', 'rest', None, 'b').src)

        f = FST('cls(a, b=c)', MatchClass)
        self.assertEqual('glob(a, b=c)', test(f, 'cls', 'glob', FST, 'cls').src)
        self.assertEqual('glob(new, b=c)', test(f, 'patterns', 'new', fstview,
                                               '<<MatchClass ROOT 0,0..0,12>.patterns[0:1] [<MatchAs 0,5..0,6>]>').src)
        self.assertEqual('glob(new, kw=c)', test(f, 'kwd_attrs', 'kw', None,
                                                "<<MatchClass ROOT 0,0..0,14>.kwd_attrs[0:1] ['b']>").src)
        self.assertEqual('glob(new, kw=blah)', test(f, 'kwd_patterns', 'blah', fstview, 'c').src)

        self.assertEqual('*new', test(FST('*star', MatchStar), 'name', 'new', None, 'star').src)

        f = FST('a as b', MatchAs)
        self.assertEqual('new as b', test(f, 'pattern', 'new', FST, 'a').src)
        self.assertEqual('new as grog', test(f, 'name', 'grog', None, 'b').src)

        self.assertEqual('1 | 2 | 3', test(FST('a.b | c.d', MatchOr), 'patterns', '1 | 2 | 3', fstview, 'a.b | c.d').src)

        if not PYLT11:
            f = FST('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass')
            self.assertEqual('try:\n    return\nexcept* Exception: pass\nelse: pass\nfinally: pass', test(f, 'body', 'return', fstview, 'pass').src)
            self.assertEqual('try:\n    return\nexcept* Exception as e: continue\nelse: pass\nfinally: pass', test(f, 'handlers', 'except* Exception as e: continue', fstview, 'except* Exception: pass').src)
            self.assertEqual('try:\n    return\nexcept* Exception as e: continue\nelse:\n    break\nfinally: pass', test(f, 'orelse', 'break', fstview, 'pass').src)
            self.assertEqual('try:\n    return\nexcept* Exception as e: continue\nelse:\n    break\nfinally:\n    f()\n', test(f, 'finalbody', 'f()', fstview, 'pass').src)

        if not PYLT12:
            self.assertEqual('def func[U](): pass', test(FST('def func[T](): pass'), 'type_params', 'U', fstview,
                                                         '<<FunctionDef ROOT 0,0..0,19>.type_params[0:1] [<TypeVar 0,9..0,10>]>').src)

            self.assertEqual('async def func[U](): pass', test(FST('async def func[T](): pass'), 'type_params', 'U', fstview,
                                                               '<<AsyncFunctionDef ROOT 0,0..0,25>.type_params[0:1] [<TypeVar 0,15..0,16>]>').src)

            self.assertEqual('class cls[U]: pass', test(FST('class cls[T]: pass'), 'type_params', 'U', fstview,
                                                        '<<ClassDef ROOT 0,0..0,18>.type_params[0:1] [<TypeVar 0,10..0,11>]>').src)

            f = FST('type t[T] = v')
            self.assertEqual('type new[T] = v', test(f, 'name', 'new', FST, 't').src)
            self.assertEqual('type new[U] = v', test(f, 'type_params', 'U', fstview,
                                                        '<<TypeAlias ROOT 0,0..0,15>.type_params[0:1] [<TypeVar 0,9..0,10>]>').src)
            self.assertEqual('type new[U] = zzz', test(f, 'value', 'zzz', FST, 'v').src)

            # these are complicated...

            # (FormattedValue, 'value'):            _get_one_FormattedValue_value, # expr
            # (FormattedValue, 'conversion'):       _get_one_conversion, # int
            # (FormattedValue, 'format_spec'):      _get_one_format_spec, # expr?  - no location on py < 3.12

            self.assertEqual('f"new"', test(FST('f"{a}"'), 'values', 'new', fstview,
                                            '<<JoinedStr ROOT 0,0..0,6>.values[0:1] [<FormattedValue 0,2..0,5>]>').src)  # TODO: the result of this put is incorrect because it is not implemented yet

            self.assertEqual('new', test(FST('T', TypeVar), 'name', 'new', None, 'T').src)
            self.assertEqual('T: str', test(FST('T: int', TypeVar), 'bound', 'str', FST, 'int').src)

            self.assertEqual('*new', test(FST('*T', TypeVarTuple), 'name', 'new', None, 'T').src)

            self.assertEqual('**new', test(FST('**T', ParamSpec), 'name', 'new', None, 'T').src)

        else:
            pass

            # (FormattedValue, 'value'):            _get_one_FormattedValue_value, # expr
            # (FormattedValue, 'conversion'):       _get_one_conversion, # int
            # (FormattedValue, 'format_spec'):      _get_one_format_spec, # expr?  - no location on py < 3.12

            self.assertEqual('new', test(FST('f"{a}"'), 'values', 'new', fstview,
                                         '<<JoinedStr ROOT 0,0..0,6>.values[0:1] [<FormattedValue 0,0..0,6>]>').src)  # TODO: the result of this put is incorrect because it is not implemented yet, and will probably not be implemented for py < 3.12

        if not PYLT13:
            self.assertEqual('T = str', test(FST('T = int', TypeVar), 'default_value', 'str', FST, 'int').src)
            self.assertEqual('*T = str', test(FST('*T = int', TypeVarTuple), 'default_value', 'str', FST, 'int').src)
            self.assertEqual('**T = str', test(FST('**T = int', ParamSpec), 'default_value', 'str', FST, 'int').src)

        if not PYLT14:
            # (Interpolation, 'value'):             _get_one_default, # expr
            # (Interpolation, 'str'):               _get_one_constant, # constant
            # (Interpolation, 'conversion'):        _get_one_conversion, # int
            # (Interpolation, 'format_spec'):       _get_one_format_spec, # expr?  - no location on py < 3.12

            self.assertEqual('t"new"', test(FST('t"{a}"'), 'values', 'new', fstview,
                                            '<<TemplateStr ROOT 0,0..0,6>.values[0:1] [<Interpolation 0,2..0,5>]>').src)  # TODO: the result of this put is incorrect because it is not implemented yet

    @unittest.skipUnless(PYLT12, 'only valid for py < 3.12')
    def test_disallow_put_JoinedStr_pylt12(self):
        self.assertRaises(NotImplementedError, FST('i = f"a{b}c"', 'exec').body[0].value.values[1].value.replace, 'z')
        self.assertRaises(NotImplementedError, FST('i = f"a{b}c"').value.values[1].value.replace, 'z')
        self.assertRaises(NotImplementedError, FST('f"a{b}c"').values[1].value.replace, 'z')
        self.assertRaises(NotImplementedError, FST('f"{a}"').values[0].value.replace, 'z')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-pars', default=False, action='store_true', help="regenerate parentheses test data")
    parser.add_argument('--regen-precedence', default=False, action='store_true', help="regenerate precedence test data")

    args, _ = parser.parse_known_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT12:
            raise RuntimeError('cannot regenerate on python version < 3.12')

    if args.regen_pars or args.regen_all:
        print('Regenerating parentheses test data...')
        regen_pars_data()

    if args.regen_precedence or args.regen_all:
        print('Regenerating precedence test data...')
        regen_precedence_data()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
