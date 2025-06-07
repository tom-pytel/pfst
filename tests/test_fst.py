#!/usr/bin/env python

import os
import re
import sys
import unittest
import ast as ast_
from random import randint, seed, shuffle

from fst import *
from fst import fst
from fst.astutil import TemplateStr, type_param, TypeVar, ParamSpec, TypeVarTuple
fst_ = fst

from data_put_one import PUT_ONE_DATA
from data_other import (PARS_DATA, COPY_DATA, GET_SLICE_SEQ_DATA, GET_SLICE_STMT_DATA, GET_SLICE_STMT_NOVERIFY_DATA,
                        PUT_SLICE_SEQ_DATA, PUT_SLICE_STMT_DATA, PUT_SLICE_DATA, PUT_SRC_DATA, PRECEDENCE_DATA,
                        REPLACE_EXISTING_ONE_DATA)

_PY_VERSION = sys.version_info[:2]

PYFNMS = sum((
    [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
    for top in ('src', 'tests')),
    start=[]
)

# ASTEXPR = lambda src: ast_.parse(src).body[0].value
# ASTSTMT = lambda src: ast_.parse(src).body[0]
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
    ('expr',              FST._parse_expr,              SyntaxError,    '*not a'),
    ('expr',              FST._parse_expr,              NodeError,      'a:b'),
    ('expr',              FST._parse_expr,              SyntaxError,    'a:b:c'),

    ('slice',             FST._parse_slice,             Name,           'j'),
    ('slice',             FST._parse_slice,             Slice,          'a:b'),
    ('slice',             FST._parse_slice,             Tuple,          'j, k'),

    ('sliceelt',          FST._parse_sliceelt,          Name,           'j'),
    ('sliceelt',          FST._parse_sliceelt,          Slice,          'a:b'),
    ('sliceelt',          FST._parse_sliceelt,          Starred,        '*s'),
    ('sliceelt',          FST._parse_sliceelt,          Tuple,          'j, k'),

    ('callarg',           FST._parse_callarg,           Name,           'j'),
    ('callarg',           FST._parse_callarg,           Starred,        '*s'),
    ('callarg',           FST._parse_callarg,           Starred,        '*not a'),
    ('callarg',           FST._parse_callarg,           Tuple,          'j, k'),
    ('callarg',           FST._parse_callarg,           NodeError,      'i=1'),
    ('callarg',           FST._parse_callarg,           NodeError,      'a:b'),
    ('callarg',           FST._parse_callarg,           SyntaxError,    'a:b:c'),

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
    ('unaryop',           FST._parse_unaryop,           NodeError,      'and'),
    ('cmpop',             FST._parse_cmpop,             GtE,            '>='),
    ('cmpop',             FST._parse_cmpop,             IsNot,          'is\nnot'),
    ('cmpop',             FST._parse_cmpop,             NodeError,      '>= a >='),
    ('cmpop',             FST._parse_cmpop,             NodeError,      'and'),

    ('comprehension',     FST._parse_comprehension,     comprehension,  'for u in v'),
    ('comprehension',     FST._parse_comprehension,     comprehension,  'for u in v if w'),

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
    (expr,                FST._parse_expr,              SyntaxError,    '*not a'),
    (expr,                FST._parse_expr,              NodeError,      'a:b'),
    (expr,                FST._parse_expr,              SyntaxError,    'a:b:c'),
    (Name,                FST._parse_expr,              Name,           'j'),
    (Starred,             FST._parse_expr,              Starred,        '*s'),

    (Slice,               FST._parse_slice,             Slice,          'a:b'),

    (boolop,              FST._parse_boolop,            And,            'and'),
    (boolop,              FST._parse_boolop,            NodeError,      '*'),
    (operator,            FST._parse_operator,          Mult,           '*'),
    (operator,            FST._parse_operator,          Mult,           '*='),
    (operator,            FST._parse_operator,          NodeError,      'and'),
    (unaryop,             FST._parse_unaryop,           UAdd,           '+'),
    (unaryop,             FST._parse_unaryop,           NodeError,      'and'),
    (cmpop,               FST._parse_cmpop,             GtE,            '>='),
    (cmpop,               FST._parse_cmpop,             IsNot,          'is\nnot'),
    (cmpop,               FST._parse_cmpop,             NodeError,      '>= a >='),
    (cmpop,               FST._parse_cmpop,             NodeError,      'and'),

    (comprehension,       FST._parse_comprehension,     comprehension,  'for u in v'),
    (comprehension,       FST._parse_comprehension,     comprehension,  'for u in v if w'),

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
]

if _PY_VERSION >= (3, 11):
    PARSE_TESTS.extend([
        ('ExceptHandler',     FST._parse_ExceptHandler,     ExceptHandler,  'except* Exception: pass'),

        ('slice',             FST._parse_slice,             Tuple,          '*s'),
        ('slice',             FST._parse_slice,             Tuple,          '*not a'),
        ('sliceelt',          FST._parse_sliceelt,          Starred,        '*not a'),

        (ExceptHandler,       FST._parse_ExceptHandler,     ExceptHandler,  'except* Exception: pass'),
    ])

if _PY_VERSION >= (3, 12):
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
    ])

if _PY_VERSION >= (3, 13):
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


def regen_copy_data():
    newlines = []

    for src, elt, *_ in COPY_DATA:
        src   = src.strip()
        t     = parse(src)
        f     = eval(f't.{elt}', {'t': t}).f
        s     = f.copy(fix=True)
        ssrc  = s.src
        sdump = s.dump(out=list, compact=True)

        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        s.verify(raise_=True)

        newlines.append('(r"""')
        newlines.extend(f'''{src}\n""", {elt!r}, r"""\n{ssrc}\n""", r"""'''.split('\n'))
        newlines.extend(sdump)
        newlines.append('"""),\n')

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('COPY_DATA = [')
    stop  = lines.index(']  # END OF COPY_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_get_slice_seq():
    newlines = []

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    for name in ('GET_SLICE_SEQ_DATA',):
        for src, elt, start, stop, options, *_ in globals()[name]:
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.get_slice(start, stop, cut=True, **options)
            tsrc  = t.f.src
            ssrc  = s.src
            tdump = t.f.dump(out=list, compact=True)
            sdump = s.dump(out=list, compact=True)

            assert not tsrc.startswith('\n') or tsrc.endswith('\n')
            assert not ssrc.startswith('\n') or ssrc.endswith('\n')

            if options.get('_verify', True):
                t.f.verify(raise_=True)
                s.verify(raise_=True)

            newlines.extend(f'''(r"""{src}""", {elt!r}, {start}, {stop}, {options}, r"""\n{tsrc}\n""", r"""\n{ssrc}\n""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('""", r"""')
            newlines.extend(sdump)
            newlines.append('"""),\n')

        start = lines.index(f'{name} = [')
        stop  = lines.index(f']  # END OF {name}')

        lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_get_slice_stmt():
    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    for name in ('GET_SLICE_STMT_DATA', 'GET_SLICE_STMT_NOVERIFY_DATA'):
        verify   = 'NOVERIFY' not in name
        newlines = []

        for src, elt, start, stop, field, options, *_ in globals()[name]:
            t     = parse(src)
            f     = (eval(f't.{elt}', {'t': t}) if elt else t).f
            s     = f.get_slice(start, stop, field, cut=True, **options)
            tsrc  = t.f.src
            ssrc  = s.src
            tdump = t.f.dump(out=list, compact=True)
            sdump = s.dump(out=list, compact=True)

            if verify:
                t.f.verify(raise_=True)
                s.verify(raise_=True)

            newlines.extend(f'''(r"""{src}""", {elt!r}, {start}, {stop}, {field!r}, {options}, r"""{tsrc}""", r"""{ssrc}""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('""", r"""')
            newlines.extend(sdump)
            newlines.append('"""),\n')

        start = lines.index(f'{name} = [')
        stop  = lines.index(f']  # END OF {name}')

        lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_seq():
    newlines = []

    for dst, elt, start, stop, src, put_src, put_dump in PUT_SLICE_SEQ_DATA:
        t = parse(dst)
        f = eval(f't.{elt}', {'t': t}).f

        f.put_slice(None if src == '**DEL**' else src, start, stop)

        tdst  = t.f.src
        tdump = t.f.dump(out=list, compact=True)

        assert not tdst.startswith('\n') or tdst.endswith('\n')

        t.f.verify(raise_=True)

        newlines.extend(f'''(r"""{dst}""", {elt!r}, {start}, {stop}, r"""{src}""", r"""\n{tdst}\n""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_SEQ_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_SEQ_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_stmt():
    newlines = []

    for dst, stmt, start, stop, field, options, src, put_src, put_dump in PUT_SLICE_STMT_DATA:
        t = parse(dst)
        f = (eval(f't.{stmt}', {'t': t}) if stmt else t).f

        f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

        tdst  = t.f.src
        tdump = t.f.dump(out=list, compact=True)

        t.f.verify(raise_=True)

        newlines.extend(f'''(r"""{dst}""", {stmt!r}, {start}, {stop}, {field!r}, {options!r}, r"""{src}""", r"""{tdst}""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_STMT_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_STMT_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice():
    newlines = []

    for dst, attr, start, stop, field, options, src, put_src, put_dump in PUT_SLICE_DATA:
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

        except NotImplementedError as exc:
            tdst  = f'**{exc!r}**'
            tdump = ''

        else:
            tdst  = t.f.src
            tdump = t.f.dump(out=list, compact=True)

            t.f.verify(raise_=True)

        newlines.extend(f'''(r"""{dst}""", {attr!r}, {start}, {stop}, {field!r}, {options!r}, r"""{src}""", r"""{tdst}""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_one():
    newlines = []

    for i, (dst, attr, idx, field, options, src, put_src, put_dump) in enumerate(PUT_ONE_DATA):
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            if options.get('raw') is True:
                continue

            options_ = {**options, 'raw': False}

            try:
                f.put(None if src == '**DEL**' else src, idx, field=field, **options_)

            except Exception as exc:
                tdst  = '**SyntaxError**' if isinstance(exc, SyntaxError) else f'**{exc!r}**'
                tdump = ''

            else:
                tdst  = f.root.src
                tdump = f.root.dump(out=list, compact=True)

                if options.get('_verify', True):
                    f.root.verify(raise_=True)

            newlines.extend(f'''(r"""{dst}""", {attr!r}, {idx}, {field!r}, {options!r}, r"""{src}""", r"""{tdst}""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('"""),\n')

        except Exception:
            print(i, attr, idx, field, src, options)
            print('---')
            print(repr(dst))
            print('...')
            print(src)
            print('...')
            print(put_src)

            raise

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_put_one.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_ONE_DATA = [')
    stop  = lines.index(']  # END OF PUT_ONE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_src():
    newlines = []

    for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_SRC_DATA):
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            g = f.put_src(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root

            tdst  = f.root.src
            tdump = f.root.dump(out=list, compact=True)

            f.root.verify(raise_=True)

            newlines.extend(f'''(r"""{dst}""", {attr!r}, ({ln}, {col}, {end_ln}, {end_col}), {options!r}, r"""{src}""", r"""{g.src}""", r"""{tdst}""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('"""),\n')

        except Exception:
            print(i, attr, (ln, col, end_ln, end_col), src, options)
            print('---')
            print(repr(dst))
            print('...')
            print(src)
            print('...')
            print(put_src)

            raise

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SRC_DATA = [')
    stop  = lines.index(']  # END OF PUT_SRC_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_precedence_data():
    newlines = []

    # for dst, *attrs in PRECEDENCE_DST_STMTS + PRECEDENCE_DST_EXPRS + PRECEDENCE_SRC_EXPRS:
    #     for src, *_ in PRECEDENCE_SRC_EXPRS:
    #         for attr in attrs:
    #             d      = copy_ast(dst)
    #             s      = copy_ast(src)
    #             fields = attr.split('.')
    #             fdfull = fields[-1]
    #             p      = eval(f'd.{pattr}', {'d': d}) if (pattr := '.'.join(fields[:-1])) else d

    #             exec(f'p.{fdfull} = s', {'p': p, 'fdfull': fdfull, 's': s})

    #             truth = ast_.unparse(d)

    #             if dst == 'x, y':  # SPECIAL CASE!!! because unparse adds enclosing parentheses
    #                 truth = truth[1:-1]

    #             newlines.append(f'    {truth!r},')

    #             # fd = fdfull.split('[')[0]
    #             # ch = s.op.__class__ if (sac := s.__class__) in (BoolOp, BinOp, UnaryOp) else sac
    #             # pr = p.op.__class__ if (fpa := p.__class__) in (BoolOp, BinOp, UnaryOp) else fpa
    #             # dk = fpa is Dict and p.keys[0] is None
    #             # print(f"{'NY'[precedence_require_parens(ch, pr, fd, dict_key_or_matchas_pat_is_None=dk)]} -", ast_.unparse(d))

    for dst, *attrs in PRECEDENCE_DST_STMTS + PRECEDENCE_DST_EXPRS + PRECEDENCE_SRC_EXPRS:
        for src, *_ in PRECEDENCE_SRC_EXPRS:
            for attr in attrs:
                d            = dst.copy(fix=False)
                s            = src.body[0].value.copy(fix=False)
                is_stmt      = isinstance(d.a, stmt)
                f            = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})
                is_unpar_tup = False if is_stmt else (d.body[0].value.is_parenthesized_tuple() is False)

                f.pfield.set(f.parent.a, s.a)

                truth = ast_.unparse(f.root.a)

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
    def test__loc_block_header_end(self):
        self.assertEqual((0, 16), parse('def f(a) -> int: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 9),  parse('def f(a): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 8),  parse('def f(): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 22), parse('async def f(a) -> int: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 15), parse('async def f(a): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 14), parse('async def f(): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 27), parse('class cls(base, keyword=1): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 16), parse('class cls(base): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 11), parse('for a in b: pass\nelse: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 17), parse('async for a in b: pass\nelse: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 8),  parse('while a: pass\nelse: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 5),  parse('if a: pass\nelse: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 9),  parse('with f(): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 14), parse('with f() as v: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 15), parse('async with f(): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 20), parse('async with f() as v: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 8),  parse('match a:\n case 2: pass').body[0].f._loc_block_header_end())
        self.assertEqual((1, 8),  parse('match a:\n case 2: pass').body[0].cases[0].f._loc_block_header_end())
        self.assertEqual((1, 16), parse('match a:\n case 2 if True: pass').body[0].cases[0].f._loc_block_header_end())
        self.assertEqual((0, 4),  parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].f._loc_block_header_end())
        self.assertEqual((1, 7),  parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
        self.assertEqual((1, 17), parse('try: pass\nexcept Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
        self.assertEqual((1, 34), parse('try: pass\nexcept (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
        self.assertEqual((1, 39), parse('try: pass\nexcept (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())

        if _PY_VERSION >= (3, 12):
            self.assertEqual((0, 4),  parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].f._loc_block_header_end())
            self.assertEqual((1, 18), parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
            self.assertEqual((1, 35), parse('try: pass\nexcept* (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
            self.assertEqual((1, 40), parse('try: pass\nexcept* (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
            self.assertEqual((0, 13), parse('class cls[T]: pass').body[0].f._loc_block_header_end())

    def test__dict_key_or_mock_loc(self):
        a = parse('''{
    a: """test
two  # fake comment start""", **b
            }''').body[0].value
        self.assertEqual((2, 30, 2, 32), a.f._dict_key_or_mock_loc(a.keys[1], a.values[1].f))

        a = parse('''{
    a: """test""", **  # comment
    b
            }''').body[0].value
        self.assertEqual((1, 19, 1, 21), a.f._dict_key_or_mock_loc(a.keys[1], a.values[1].f))

    def test__next_prev_src(self):
        from fst.shared import _next_src, _prev_src

        lines = '''
  # pre
i \\
here \\
j \\
  # post
k \\
            '''.split('\n')

        self.assertEqual((4, 0, 'j'), _next_src(lines, 3, 4, 7, 0, False, False))
        self.assertEqual((4, 0, 'j'), _next_src(lines, 3, 4, 7, 0, True, False))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 4, 1, 7, 0, False, False))
        self.assertEqual((5, 2, '# post'), _next_src(lines, 4, 1, 7, 0, True, False))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 5, 8, 7, 0, False, False))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 5, 8, 7, 0, True, False))

        self.assertEqual((3, 5, '\\'), _next_src(lines, 3, 4, 7, 0, False, True))
        self.assertEqual((3, 5, '\\'), _next_src(lines, 3, 4, 7, 0, True, True))
        self.assertEqual((4, 2, '\\'), _next_src(lines, 4, 1, 7, 0, False, True))
        self.assertEqual((4, 2, '\\'), _next_src(lines, 4, 1, 7, 0, True, True))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 5, 8, 7, 0, False, True))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 5, 8, 7, 0, True, True))

        self.assertEqual((4, 0, 'j'), _next_src(lines, 3, 4, 7, 0, False, None))
        self.assertEqual((4, 0, 'j'), _next_src(lines, 3, 4, 7, 0, True, None))
        self.assertEqual(None, _next_src(lines, 4, 1, 7, 0, False, None))
        self.assertEqual((5, 2, '# post'), _next_src(lines, 4, 1, 7, 0, True, None))
        self.assertEqual(None, _next_src(lines, 5, 8, 7, 0, False, None))
        self.assertEqual(None, _next_src(lines, 5, 8, 7, 0, True, None))

        self.assertEqual(None, _prev_src(lines, 0, 0, 2, 0, False, False))
        self.assertEqual((1, 2, '# pre'), _prev_src(lines, 0, 0, 2, 0, True, False))
        self.assertEqual((2, 0, 'i'), _prev_src(lines, 0, 0, 3, 0, False, False))
        self.assertEqual((2, 0, 'i'), _prev_src(lines, 0, 0, 3, 0, True, False))
        self.assertEqual((4, 0, 'j'), _prev_src(lines, 0, 0, 6, 0, False, False))
        self.assertEqual((5, 2, '# post'), _prev_src(lines, 0, 0, 6, 0, True, False))

        self.assertEqual(None, _prev_src(lines, 0, 0, 2, 0, False, True))
        self.assertEqual((1, 2, '# pre'), _prev_src(lines, 0, 0, 2, 0, True, True))
        self.assertEqual((2, 2, '\\'), _prev_src(lines, 0, 0, 3, 0, False, True))
        self.assertEqual((2, 2, '\\'), _prev_src(lines, 0, 0, 3, 0, True, True))
        self.assertEqual((4, 2, '\\'), _prev_src(lines, 0, 0, 6, 0, False, True))
        self.assertEqual((5, 2, '# post'), _prev_src(lines, 0, 0, 6, 0, True, True))

        self.assertEqual(None, _prev_src(lines, 0, 0, 1, 7, False, None))
        self.assertEqual((1, 2, '# pre'), _prev_src(lines, 0, 0, 1, 7, True, None))
        self.assertEqual((2, 0, 'i'), _prev_src(lines, 0, 0, 3, 0, False, None))
        self.assertEqual((2, 0, 'i'), _prev_src(lines, 0, 0, 3, 0, True, None))
        self.assertEqual((4, 0, 'j'), _prev_src(lines, 0, 0, 5, 3, False, None))
        self.assertEqual((5, 2, '#'), _prev_src(lines, 0, 0, 5, 3, True, None))

        self.assertEqual((1, 1, 'a'), _next_src(['\\', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual((2, 1, 'a'), _next_src(['\\', '\\', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual(None, _next_src(['\\', '', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual((1, 1, '# c'), _next_src(['\\', ' # c'], 0, 0, 100, 0, True, None))
        self.assertEqual(None, _next_src(['\\', ' # c', 'a'], 0, 0, 100, 0, False, None))

        self.assertEqual((0, 0, 'a'), _prev_src(['a \\', ''], 0, 0, 1, 0, True, None))
        self.assertEqual((0, 0, 'a'), _prev_src(['a \\', '\\', ''], 0, 0, 2, 0, True, None))
        self.assertEqual((0, 0, 'a'), _prev_src(['a \\', '\\', '\\', ''], 0, 0, 3, 0, True, None))
        self.assertEqual((1, 1, '# c'), _prev_src(['a \\', ' # c'], 0, 0, 1, 4, True, None))
        self.assertEqual((1, 1, '# '), _prev_src(['a \\', ' # c'], 0, 0, 1, 3, True, None))
        self.assertEqual((1, 1, '#'), _prev_src(['a \\', ' # c'], 0, 0, 1, 2, True, None))
        self.assertEqual((0, 0, 'a'), _prev_src(['a \\', ' # c'], 0, 0, 1, 1, True, None))
        self.assertEqual((1, 1, '# c'), _prev_src(['a', ' # c'], 0, 0, 1, 4, True, None))
        self.assertEqual((1, 1, '# '), _prev_src(['a', ' # c'], 0, 0, 1, 3, True, None))
        self.assertEqual((1, 1, '#'), _prev_src(['a', ' # c'], 0, 0, 1, 2, True, None))
        self.assertEqual(None, _prev_src(['a', ' # c'], 0, 0, 1, 1, True, None))

        state = []
        self.assertEqual((0, 4, '# c \\'), _prev_src(['a b # c \\'], 0, 0, 0, 9, True, True, state=state))
        self.assertEqual((0, 2, 'b'), _prev_src(['a b # c \\'], 0, 0, 0, 4, True, True, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b # c \\'], 0, 0, 0, 2, True, True, state=state))
        self.assertEqual(None, _prev_src(['a b # c \\'], 0, 0, 0, 0, True, True, state=state))

        state = []
        self.assertEqual((0, 2, 'b'), _prev_src(['a b # c \\'], 0, 0, 0, 9, False, True, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b # c \\'], 0, 0, 0, 2, False, True, state=state))
        self.assertEqual(None, _prev_src(['a b # c \\'], 0, 0, 0, 0, False, True, state=state))

        state = []
        self.assertEqual((0, 2, 'b'), _prev_src(['a b # c \\'], 0, 0, 0, 9, False, None, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b # c \\'], 0, 0, 0, 2, False, None, state=state))
        self.assertEqual(None, _prev_src(['a b # c \\'], 0, 0, 0, 0, False, None, state=state))

        state = []
        self.assertEqual((0, 4, '# c \\'), _prev_src(['a b # c \\'], 0, 0, 0, 9, True, None, state=state))
        self.assertEqual((0, 2, 'b'), _prev_src(['a b # c \\'], 0, 0, 0, 4, True, None, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b # c \\'], 0, 0, 0, 2, True, None, state=state))
        self.assertEqual(None, _prev_src(['a b # c \\'], 0, 0, 0, 0, True, None, state=state))

        state = []
        self.assertEqual((0, 4, 'c'), _prev_src(['a b c \\'], 0, 0, 0, 9, True, None, state=state))
        self.assertEqual((0, 2, 'b'), _prev_src(['a b c \\'], 0, 0, 0, 4, True, None, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b c \\'], 0, 0, 0, 2, True, None, state=state))
        self.assertEqual(None, _prev_src(['a b c \\'], 0, 0, 0, 0, True, None, state=state))

        self.assertEqual((0, 0, '('), _prev_src(['(# comment', ''], 0, 0, 1, 0))
        self.assertEqual((0, 1, '# comment'), _prev_src(['(# comment', ''], 0, 0, 1, 0, True))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0, False, False))
        self.assertEqual((0, 1, '\\'), _prev_src(['(\\', ''], 0, 0, 1, 0, False, True))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0, False, None))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0, True, False))
        self.assertEqual((0, 1, '\\'), _prev_src(['(\\', ''], 0, 0, 1, 0, True, True))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0, True, None))

    def test__next_prev_find(self):
        from fst.shared import _next_find, _prev_find

        lines = '''
  ; \\
  # hello
  \\
  # world
  # word
            '''.split('\n')

        self.assertEqual((1, 2), _prev_find(lines, 0, 0, 5, 0, ';'))
        self.assertEqual((1, 2), _prev_find(lines, 0, 0, 5, 0, ';', True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, ';', True, comment=True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, ';', True, lcont=True))
        self.assertEqual((1, 2), _prev_find(lines, 0, 0, 2, 0, ';', True, lcont=None))
        self.assertEqual(None, _prev_find(lines, 0, 0, 3, 0, ';', True, lcont=None))
        self.assertEqual((1, 2), _prev_find(lines, 0, 0, 5, 0, ';', False, comment=True, lcont=True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, ';', True, comment=True, lcont=True))
        self.assertEqual((5, 2), _prev_find(lines, 0, 0, 6, 0, '# word', False, comment=True, lcont=True))
        self.assertEqual((4, 2), _prev_find(lines, 0, 0, 6, 0, '# world', False, comment=True, lcont=True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, '# world', False, comment=False, lcont=True))
        self.assertEqual((2, 2), _prev_find(lines, 0, 0, 5, 0, '# hello', False, comment=True, lcont=True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, '# hello', True, comment=True, lcont=True))

        lines = '''
  \\
  # hello
  ; \\
  # world
  # word
            '''.split('\n')

        self.assertEqual((3, 2), _next_find(lines, 2, 0, 6, 0, ';'))
        self.assertEqual((3, 2), _next_find(lines, 2, 0, 6, 0, ';', True))
        self.assertEqual(None, _next_find(lines, 2, 0, 6, 0, ';', True, comment=True))
        self.assertEqual((3, 2), _next_find(lines, 2, 0, 6, 0, ';', True, lcont=True))
        self.assertEqual(None, _next_find(lines, 2, 0, 6, 0, ';', True, lcont=None))
        self.assertEqual(None, _next_find(lines, 3, 3, 6, 0, '# word', False))
        self.assertEqual(None, _next_find(lines, 3, 3, 6, 0, '# word', True))
        self.assertEqual(None, _next_find(lines, 3, 3, 6, 0, '# word', True, comment=True))
        self.assertEqual((5, 2), _next_find(lines, 3, 3, 6, 0, '# word', False, comment=True))
        self.assertEqual(None, _next_find(lines, 3, 3, 6, 0, '# word', False, comment=True, lcont=None))
        self.assertEqual((4, 2), _next_find(lines, 3, 0, 6, 0, '# world', False, comment=True, lcont=None))
        self.assertEqual(None, _next_find(lines, 3, 0, 6, 0, '# word', False, comment=True, lcont=None))
        self.assertEqual((5, 2), _next_find(lines, 3, 0, 6, 0, '# word', False, comment=True, lcont=True))
        self.assertEqual(None, _next_find(lines, 3, 0, 6, 0, '# word', True, comment=True, lcont=True))

    def test__next_find_re(self):
        from fst.shared import _next_find_re

        lines = '''
  \\
  # hello
  aaab ; \\
  # world
b # word
            '''.split('\n')
        pat = re.compile('a*b')

        self.assertEqual((3, 2, 'aaab'), _next_find_re(lines, 2, 0, 6, 0, pat))
        self.assertEqual((3, 2, 'aaab'), _next_find_re(lines, 2, 0, 6, 0, pat, True))
        self.assertEqual(None, _next_find_re(lines, 2, 0, 6, 0, pat, True, comment=True))
        self.assertEqual((3, 2, 'aaab'), _next_find_re(lines, 2, 0, 6, 0, pat, True, lcont=True))
        self.assertEqual(None, _next_find_re(lines, 2, 0, 6, 0, pat, True, lcont=None))
        self.assertEqual((3, 3, 'aab'), _next_find_re(lines, 3, 3, 6, 0, pat, False))
        self.assertEqual((3, 4, 'ab'), _next_find_re(lines, 3, 4, 6, 0, pat, False))
        self.assertEqual((3, 5, 'b'), _next_find_re(lines, 3, 5, 6, 0, pat, True))
        self.assertEqual(None, _next_find_re(lines, 3, 6, 6, 0, pat, True))
        self.assertEqual((5, 0, 'b'), _next_find_re(lines, 3, 6, 6, 0, pat, False))
        self.assertEqual(None, _next_find_re(lines, 3, 6, 6, 0, pat, True))
        self.assertEqual((5, 0, 'b'), _next_find_re(lines, 3, 6, 6, 0, pat, False, comment=True))
        self.assertEqual(None, _next_find_re(lines, 3, 6, 6, 0, pat, False, comment=True, lcont=None))
        self.assertEqual((5, 0, 'b'), _next_find_re(lines, 4, 0, 6, 0, pat, False, comment=False, lcont=False))
        self.assertEqual(None, _next_find_re(lines, 4, 0, 6, 0, pat, False, comment=True, lcont=None))
        self.assertEqual((5, 0, 'b'), _next_find_re(lines, 4, 0, 6, 0, pat, False, comment=True, lcont=True))
        self.assertEqual(None, _next_find_re(lines, 4, 0, 6, 0, pat, True, comment=True, lcont=True))

    def test__multiline_str_continuation_lns(self):
        from fst.shared import _multiline_str_continuation_lns as mscl

        self.assertEqual([], mscl(ls := r'''
'a'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
"a"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"""a
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"""a

b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
"a"
"b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "z" "c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "z" "c\
b" """y"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" "z" "c\
b" """y
"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" "z" "c\
b" "x" """y
"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" """c
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" """c
b""" "d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3], mscl(ls := r'''
"a" """c
b"""
"d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3, 4], mscl(ls := r'''
"a" """c
b"""
"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
"a" """c
b"""

"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
b"a" b"""c
b"""

b"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
u"a" u"""c
b"""

u"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
r"a" r"""c
b"""

r"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

    def test__multiline_fstr_continuation_lns(self):
        from fst.shared import _multiline_fstr_continuation_lns as mscl

        self.assertEqual([], mscl(ls := r'''
f'a'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
f"a"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"""a
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"""a

b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
f"a"
"b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a" f"c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a" f"""c
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"a" f"""c
b""" "d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3], mscl(ls := r'''
f"a" f"""c
b"""
f"d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3, 4], mscl(ls := r'''
f"a" f"""c
b"""
f"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
f"a" f"""c
b"""

f"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        # with values

        self.assertEqual([], mscl(ls := r'''
f"a{1}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a{(1,
2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a{(1,\
2)}b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"a{(1,\
2)}b""" f"c\
d"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3], mscl(ls := r'''
f"a{(1,
2)}b" f"""{3}
{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5, 6], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x\
y"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

    def test__multiline_tstr_continuation_lns(self):
        from fst.shared import _multiline_fstr_continuation_lns as mscl

        if _PY_VERSION >= (3, 14):
            self.assertEqual([], mscl(ls := r'''
t'a'
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([], mscl(ls := r'''
t"a"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1], mscl(ls := r'''
t"""a
b"""
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 2], mscl(ls := r'''
t"""a

b"""
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([], mscl(ls := r'''
t"a"
"b"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1], mscl(ls := r'''
t"a\
b"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1], mscl(ls := r'''
t"a" t"c\
b"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1], mscl(ls := r'''
t"a" t"""c
b"""
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 2], mscl(ls := r'''
t"a" t"""c
b""" "d\
e"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 3], mscl(ls := r'''
t"a" t"""c
b"""
t"d\
e"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 3, 4], mscl(ls := r'''
t"a" t"""c
b"""
t"d\
\
e"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 4, 5], mscl(ls := r'''
t"a" t"""c
b"""

t"d\
\
e"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        # with values

            self.assertEqual([], mscl(ls := r'''
t"a{1}b"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1], mscl(ls := r'''
t"a{(1,
2)}b"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1], mscl(ls := r'''
t"a{(1,\
2)}b"""
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 2], mscl(ls := r'''
t"a{(1,\
2)}b""" t"c\
d"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 2, 3], mscl(ls := r'''
t"a{(1,
2)}b" t"""{3}
{4}
{5}"""
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}"""
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

            self.assertEqual([1, 2, 3, 4, 5, 6], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x\
y"
                '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

    def test__normalize_block(self):
        a = parse('''
if 1: i ; j ; l ; m
            '''.strip())
        a.body[0].f._normalize_block()
        a.f.verify()
        self.assertEqual(a.f.src, 'if 1:\n    i ; j ; l ; m')

        a = parse('''
def f() -> int: \\
  i \\
  ; \\
  j
            '''.strip())
        a.body[0].f._normalize_block()
        a.f.verify()
        self.assertEqual(a.f.src, 'def f() -> int:\n    i \\\n  ; \\\n  j')

        a = parse('''def f(a = """ a
...   # something """): i = 2''')
        a.body[0].f._normalize_block()
        self.assertEqual(a.f.src, 'def f(a = """ a\n...   # something """):\n    i = 2')

    def test__loc_Call_pars(self):
        self.assertEqual((0, 4, 0, 6), FST('call()', 'exec').body[0].value._loc_Call_pars())
        self.assertEqual((0, 4, 0, 7), FST('call(a)', 'exec').body[0].value._loc_Call_pars())
        self.assertEqual((0, 4, 2, 1), FST('call(\na\n)', 'exec').body[0].value._loc_Call_pars())
        self.assertEqual((0, 4, 2, 1), FST('call(\na, b=2\n)', 'exec').body[0].value._loc_Call_pars())
        self.assertEqual((0, 4, 0, 12), FST('call(c="()")', 'exec').body[0].value._loc_Call_pars())
        self.assertEqual((1, 0, 8, 1), FST('call\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n)', 'exec').body[0].value._loc_Call_pars())
        self.assertEqual((1, 0, 8, 1), FST('"()("\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n)', 'exec').body[0].value._loc_Call_pars())

    def test__loc_Subscript_brackets(self):
        self.assertEqual((0, 1, 0, 4), FST('a[b]', 'exec').body[0].value._loc_Subscript_brackets())
        self.assertEqual((0, 1, 0, 8), FST('a[b:c:d]', 'exec').body[0].value._loc_Subscript_brackets())
        self.assertEqual((0, 1, 0, 7), FST('a["[]"]', 'exec').body[0].value._loc_Subscript_brackets())
        self.assertEqual((1, 0, 7, 1), FST('a\\\n[\nb\n:\nc\n:\nd\n]', 'exec').body[0].value._loc_Subscript_brackets())
        self.assertEqual((1, 0, 7, 1), FST('"[]["\\\n[\nb\n:\nc\n:\nd\n]', 'exec').body[0].value._loc_Subscript_brackets())

    def test__loc_MatchClass_pars(self):
        self.assertEqual((1, 9, 1, 11), FST('match a:\n case cls(): pass', 'exec').body[0].cases[0].pattern._loc_MatchClass_pars())
        self.assertEqual((1, 9, 1, 12), FST('match a:\n case cls(a): pass', 'exec').body[0].cases[0].pattern._loc_MatchClass_pars())
        self.assertEqual((1, 9, 3, 1), FST('match a:\n case cls(\na\n): pass', 'exec').body[0].cases[0].pattern._loc_MatchClass_pars())
        self.assertEqual((1, 9, 3, 1), FST('match a:\n case cls(\na, b=2\n): pass', 'exec').body[0].cases[0].pattern._loc_MatchClass_pars())
        self.assertEqual((1, 9, 1, 17), FST('match a:\n case cls(c="()"): pass', 'exec').body[0].cases[0].pattern._loc_MatchClass_pars())
        self.assertEqual((2, 0, 9, 1), FST('match a:\n case cls\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n): pass', 'exec').body[0].cases[0].pattern._loc_MatchClass_pars())

    def test__loc_operator_no_parent(self):
        self.assertEqual((1, 0, 1, 1), FST(Invert(), ['# pre', '~ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(Not(), ['# pre', 'not # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(UAdd(), ['# pre', '+ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(USub(), ['# pre', '- # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Add(), ['# pre', '+ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Sub(), ['# pre', '- # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Mult(), ['# pre', '* # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(MatMult(), ['# pre', '@ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Div(), ['# pre', '/ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Mod(), ['# pre', '% # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(LShift(), ['# pre', '<< # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(RShift(), ['# pre', '>> # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitOr(), ['# pre', '| # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitXor(), ['# pre', '^ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitAnd(), ['# pre', '& # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(FloorDiv(), ['# pre', '// # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Pow(), ['# pre', '** # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Eq(), ['# pre', '== # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(NotEq(), ['# pre', '!= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Lt(), ['# pre', '< # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(LtE(), ['# pre', '<= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Gt(), ['# pre', '> # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(GtE(), ['# pre', '>= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Is(), ['# pre', 'is # post', '# next']).loc)
        self.assertEqual((1, 0, 2, 3), FST(IsNot(), ['# pre', 'is # inner', 'not # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(In(), ['# pre', 'in # post', '# next']).loc)
        self.assertEqual((1, 0, 2, 2), FST(NotIn(), ['# pre', 'not # inner', 'in # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(And(), ['# pre', 'and # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Or(), ['# pre', 'or # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Add(), ['# pre', '+= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Sub(), ['# pre', '-= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Mult(), ['# pre', '*= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(MatMult(), ['# pre', '@= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Div(), ['# pre', '/= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Mod(), ['# pre', '%= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(LShift(), ['# pre', '<<= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(RShift(), ['# pre', '>>= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(BitOr(), ['# pre', '|= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(BitXor(), ['# pre', '^= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(BitAnd(), ['# pre', '&= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(FloorDiv(), ['# pre', '//= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(Pow(), ['# pre', '**= # post', '# next']).loc)

    def test__elif_to_else_if(self):
        a = parse('''
if 1: pass
elif 2: pass
        '''.strip())
        a.body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
        '''.strip())
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
            '''.strip())

        a = parse('''
if 1: pass
elif 2: pass
return
        '''.strip())
        a.body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
return
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
    return
        '''.strip())
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
    return
            '''.strip())

        a = parse('''
if 1: pass
elif 2: pass
elif 3: pass
        '''.strip())
        a.body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
    elif 3: pass
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
    elif 3: pass
        '''.strip())
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
        elif 3: pass
            '''.strip())

    def test__parenthesize_grouping(self):
        f = parse('[i]').f
        f.body[0].value.elts[0]._parenthesize_grouping()
        self.assertEqual('[(i)]', f.src)
        self.assertEqual((0, 0, 0, 5), f.loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].value.loc)
        self.assertEqual((0, 2, 0, 3), f.body[0].value.elts[0].loc)

        f = parse('a + b').f
        f.body[0].value.left._parenthesize_grouping()
        f.body[0].value.right._parenthesize_grouping()
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)

        f = parse('a + b').f
        f.body[0].value.right._parenthesize_grouping()
        f.body[0].value.left._parenthesize_grouping()
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)
        f.body[0].value._parenthesize_grouping()
        self.assertEqual('((a) + (b))', f.src)
        f.body[0].value.left._parenthesize_grouping()
        self.assertEqual('(((a)) + (b))', f.src)
        f.body[0].value.right._parenthesize_grouping()
        self.assertEqual('(((a)) + ((b)))', f.src)

        f = parse('call(i for i in j)').f
        f.body[0].value.args[0]._parenthesize_grouping()
        self.assertEqual(f.src, 'call((i for i in j))')
        f.body[0].value.args[0]._parenthesize_grouping()
        self.assertEqual(f.src, 'call(((i for i in j)))')

        f = parse('i').body[0].value.f.copy()
        f._put_src('\n# post', 0, 1, 0, 1, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_grouping(whole=True)
        self.assertEqual((1, 0, 1, 1), f.loc)
        self.assertEqual(f.root.src, '(# pre\ni\n# post)')

        f = parse('i').body[0].value.f.copy()
        f._put_src('\n# post', 0, 1, 0, 1, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_grouping(whole=False)
        self.assertEqual((1, 1, 1, 2), f.loc)
        self.assertEqual(f.root.src, '# pre\n(i)\n# post')

    def test__parenthesize_tuple(self):
        f = parse('i,').f
        f.body[0].value._parenthesize_tuple()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('a, b').f
        f.body[0].value._parenthesize_tuple()
        self.assertEqual('(a, b)', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.elts[1].loc)

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_tuple(whole=True)
        self.assertEqual((0, 0, 2, 7), f.loc)
        self.assertEqual(f.src, '(# pre\ni,\n# post)')

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_tuple(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n(i,)\n# post')

    def test__unparenthesize_grouping(self):
        f = parse('a').f
        f.body[0].value._unparenthesize_grouping(share=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(a)').f
        f.body[0].value._unparenthesize_grouping(share=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((a))').f
        f.body[0].value._unparenthesize_grouping(share=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(\n ( (a) )  \n)').f
        f.body[0].value._unparenthesize_grouping(share=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((i,))').f
        f.body[0].value._unparenthesize_grouping(share=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('(\n ( (i,) ) \n)').f
        f.body[0].value._unparenthesize_grouping(share=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0]._unparenthesize_grouping(share=False)
        self.assertEqual(f.src, 'call((i for i in j))')
        self.assertEqual((0, 0, 0, 20), f.loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0]._unparenthesize_grouping(share=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call( ( ( (i for i in j) ) ) )').f
        f.body[0].value.args[0]._unparenthesize_grouping(share=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0]._unparenthesize_grouping(share=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0]._unparenthesize_grouping(share=False)
        self.assertEqual(f.src, 'call((i for i in j),)')
        self.assertEqual((0, 0, 0, 21), f.loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('( # pre\ni\n# post\n)').f
        f.body[0].value._unparenthesize_grouping(share=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('( # pre\ni\n# post\n)').body[0].value.f.copy(pars=True)
        f._unparenthesize_grouping(share=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        f = parse('( # pre\n(i,)\n# post\n)').f
        f.body[0].value._unparenthesize_grouping(share=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)

        f = parse('( # pre\n(i)\n# post\n)').body[0].value.f.copy(pars=True)
        f._unparenthesize_grouping(share=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a)if(a)]', 'exec')
        f.body[0].value.generators[0].ifs[0]._unparenthesize_grouping(share=False)
        f.body[0].value.generators[0].ifs[1]._unparenthesize_grouping(share=False)
        self.assertEqual('[a for a in b if a if a]', f.src)

        f = FST('for(a)in b: pass', 'exec')
        f.body[0].target._unparenthesize_grouping(share=False)
        self.assertEqual('for a in b: pass', f.src)

        f = FST('assert(test)', 'exec')
        f.body[0].test._unparenthesize_grouping(share=False)
        self.assertEqual('assert test', f.src)

        f = FST('assert({test})', 'exec')
        f.body[0].test._unparenthesize_grouping(share=False)
        self.assertEqual('assert{test}', f.src)

    def test__unparenthesize_tuple(self):
        f = parse('()').f
        f.body[0].value._unparenthesize_tuple()
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)

        f = parse('(i,)').f
        f.body[0].value._unparenthesize_tuple()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('(a, b)').f
        f.body[0].value._unparenthesize_tuple()
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.body[0].value.elts[1].loc)

        f = parse('( # pre\ni,\n# post\n)').f
        f.body[0].value._unparenthesize_tuple()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('( # pre\ni,\n# post\n)').body[0].value.f.copy()
        f._unparenthesize_tuple()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a,b)if(a,)if(a,b)]', 'exec')
        f.body[0].value.generators[0].ifs[0]._unparenthesize_tuple()
        f.body[0].value.generators[0].ifs[1]._unparenthesize_tuple()
        f.body[0].value.generators[0].ifs[2]._unparenthesize_tuple()
        self.assertEqual('[a for a in b if a,b if a,if a,b]', f.src)
        f.body[0].value.generators[0].ifs[0]._parenthesize_tuple()  # so that it will verify
        f.body[0].value.generators[0].ifs[1]._parenthesize_tuple()
        f.body[0].value.generators[0].ifs[2]._parenthesize_tuple()
        self.assertEqual('[a for a in b if (a,b) if (a,)if (a,b)]', f.src)
        f.verify()

        f = FST('for(a,b)in b: pass', 'exec')
        f.body[0].target._unparenthesize_tuple()
        self.assertEqual('for a,b in b: pass', f.src)
        f.verify()

        f = FST('for(a,)in b: pass', 'exec')
        f.body[0].target._unparenthesize_tuple()
        self.assertEqual('for a,in b: pass', f.src)
        f.verify()

    def test__maybe_fix(self):
        f = FST.fromsrc('if 1:\n a\nelif 2:\n b')
        fc = f.a.body[0].orelse[0].f.copy()
        self.assertEqual(fc.lines[0], 'if 2:')
        fc.verify(raise_=True)

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual(fc.src, '1 +\n2')
        fc._maybe_fix(pars=True)
        self.assertEqual(fc.src, '(1 +\n2)')
        fc.verify(raise_=True)

        f = FST.fromsrc('i = 1')
        self.assertIs(f.a.body[0].targets[0].ctx.__class__, Store)
        fc = f.a.body[0].targets[0].f.copy()
        self.assertIs(fc.a.ctx.__class__, Load)
        fc.verify(raise_=True)

        f = FST.fromsrc('if 1: pass\nelif 2: pass').a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual('if 2: pass', f.src)

        f = FST.fromsrc('i, j = 1, 2').a.body[0].targets[0].f.copy(pars=False)
        self.assertEqual('i, j', f.src)
        fc._maybe_fix(pars=True)
        self.assertEqual('i, j', f.src)  # because doesn't NEED them

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(pars=False)
        self.assertEqual('w := x,', f.src)
        f._maybe_fix(pars=True)
        self.assertEqual('(w := x,)', f.src)

        f = FST.fromsrc('yield a1, a2')
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual('yield a1, a2', fc.src)
        fc._maybe_fix(pars=True)
        self.assertEqual('yield a1, a2', fc.src)

        f = FST.fromsrc('yield from a')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('yield from a', fc.src)
        fc._maybe_fix(pars=True)
        self.assertEqual('yield from a', fc.src)

        f = FST.fromsrc("""[
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format
]""".strip())
        fc = f.a.body[0].value.elts[0].f.copy(pars=False)
        self.assertEqual("""
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format""".strip(), fc.src)
        fc._maybe_fix(pars=True)
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fc.src)

        f = FST.fromsrc("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))
        """.strip())
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual("""
(is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute))""".strip(), fc.src)
        fc._maybe_fix(pars=True)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fc.src)

        if _PY_VERSION >= (3, 12):
            fc = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(pars=False)
            self.assertEqual('*tuple[int, ...]', fc.src)
            fc._maybe_fix(pars=True)
            self.assertEqual('*tuple[int, ...],', fc.src)

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

                # test reparse

                test = 'reparse'
                unp  = ((s := ast_.unparse(ast)) and s.lstrip()) or src  # 'lstrip' because comprehension has leading space, 'or src' because unparse of operators gives nothing
                ast2 = FST._parse(unp, mode)

                compare_asts(ast, ast2, raise_=True)

                # test IndentationError

                if src.strip():  # won't get IndentationError on empty arguments
                    src = ' ' + src

                    self.assertRaises(IndentationError, FST._parse, src, mode)
                    self.assertRaises(IndentationError, func, src)

            except Exception:
                print()
                print(test, mode, src, res, func)

                raise

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
        self.assertEqual('', f.src)
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

        v = _PY_VERSION
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

        if _PY_VERSION >= (3, 12):
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

        self.assertEqual(None, parse('def f(): pass').body[0].args.f.src)
        self.assertEqual('a', parse('def f(a): pass').body[0].args.f.src)
        self.assertEqual('a', parse('def f( a ): pass').body[0].args.f.src)
        self.assertEqual(None, parse('lambda: None').body[0].value.args.f.src)
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
            fst = FST.fromast(ast_.parse(read(fnm)))

            for ast in walk(fst.a):
                ast.f.loc

            fst.verify(raise_=True)

    def test_fromast_special(self):
        f = FST.fromast(ast_.parse('*t').body[0].value)
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

        if _PY_VERSION >= (3, 12):
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
        self.assertIs(True, parse('f()').body[0].value.f.is_atom())
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

        self.assertTrue(FST('f(a, b=1)', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('f\\\n(a, b=1)', 'exec').body[0].copy(fix=False, pars=False).value.is_enclosed())
        self.assertTrue(FST('(f\\\n(a, b=1))', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(f\n(a, b=1))', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(f(\na\n,\nb\n=\n1))', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(f(\na\n,\nb\n=\n"()"))', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

        if _PY_VERSION >= (3, 12):
            self.assertTrue(FST(r'''
(f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x\
y")
                '''.strip(), 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
            self.assertFalse(FST(r'''
(f"a{(1,

2)}b" f"""{3}

{4}
{5}"""
f"x\
y")
                '''.strip(), 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

            self.assertTrue(FST(r'''
(f"a" f"""c
b""" f"d\
\
e")
                '''.strip(), 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

            self.assertFalse(FST(r'''
(f"a" f"""c
b"""

f"d\
\
e")
                '''.strip(), 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('a.b', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(a\n.\nb)', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(a\\\n.\\\nb)', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('a[b]', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(a\n[\nb\n])', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(a\n[(\nb\n)])', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(a\\\n[(\nb\n)])', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(a\\\n[\\\nb\\\n])', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('match a:\n case f(a, b=1): pass', 'exec').body[0].cases[0].pattern.is_enclosed())
        self.assertTrue(FST('match a:\n case f\\\n(a, b=1): pass', 'exec').body[0].cases[0].pattern.is_enclosed())
        self.assertTrue(FST('match a:\n case (f\\\n(a, b=1)): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('match a:\n case (f\n(a, b=1)): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('match a:\n case (f(\na\n,\nb\n=\n1)): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('match a:\n case (f(\na\n,\nb\n=\n"()")): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('match a:\n case *s,: pass', 'exec').body[0].cases[0].pattern.patterns[0].is_enclosed())
        self.assertFalse(FST('match a:\n case (*\ns,): pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('match a:\n case *\\\ns,: pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('match a:\n case (*\\\ns,): pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('match a:\n case a as b: pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('match a:\n case (a as b): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('match a:\n case (a\nas b): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('match a:\n case (a\\\nas b): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('match a:\n case (a\\\nas\nb): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('match a:\n case (a\\\nas\\\nb): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('match a:\n case (a\\\nas\n\\\nb): pass', 'exec').body[0].cases[0].pattern.copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('a not in b', 'exec').body[0].value.ops[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(a not in b)', 'exec').body[0].value.ops[0].copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(a not\nin b)', 'exec').body[0].value.ops[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(a not\\\nin b)', 'exec').body[0].value.ops[0].copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(a is\nnot b)', 'exec').body[0].value.ops[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(a is\\\nnot b)', 'exec').body[0].value.ops[0].copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.generators[0].copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('[i for\n i in j]', 'exec').body[0].value.generators[0].copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('[i for i\n in j]', 'exec').body[0].value.generators[0].copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('[i for i in\n j]', 'exec').body[0].value.generators[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('[i for\\\n i in j]', 'exec').body[0].value.generators[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('[i for i\\\n in j]', 'exec').body[0].value.generators[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('[i for i in\\\n j]', 'exec').body[0].value.generators[0].copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('def f(a, b=1): pass', 'exec').body[0].args.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('def f(a,\n b=1): pass', 'exec').body[0].args.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('def f(a,\\\n b=1): pass', 'exec').body[0].args.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('def f(a, b=(1,\n2)): pass', 'exec').body[0].args.copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('def f(a:\n int): pass', 'exec').body[0].args.args[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('def f(a:\\\n int): pass', 'exec').body[0].args.args[0].copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('from a import (b as c)', 'exec').body[0].names[0].copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('from a import (b\n as c)', 'exec').body[0].names[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('from a import (b\\\n as c)', 'exec').body[0].names[0].copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('with (b as c): pass', 'exec').body[0].items[0].copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('with (b\n as c): pass', 'exec').body[0].items[0].copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('with (b\\\n as c): pass', 'exec').body[0].items[0].copy(fix=False, pars=False).is_enclosed())

        if _PY_VERSION >= (3, 14):
            self.assertTrue(FST(r'''
(t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x\
y")
                '''.strip(), 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
            self.assertFalse(FST(r'''
(t"a{(1,

2)}b" t"""{3}

{4}
{5}"""
t"x\
y")
                '''.strip(), 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

    def test_is_enclosed_general(self):
        self.assertTrue(FST('a < b', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(a\n< b)', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(a\\\n< b)', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(a\\\n<\nb)', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('(a\\\n<\\\nb)', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertFalse(FST('(a\\\n<\n\\\nb)', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('a, b, c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, b\\\n, c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, [\nb\n], c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

        self.assertTrue(FST('a, {\nx: y\n}, c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, {\nb\n}, c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, [\ni for i in j\n], c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, {\ni for i in j\n}, c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, {\ni: j for i, j in k\n}, c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, (\ni for i in j\n), c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, [i,\nj], c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())
        self.assertTrue(FST('a, b[\ni:j:k\n], c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

        if _PY_VERSION >= (3, 12):
            self.assertTrue(FST('a, f"{(1,\n2)}", c', 'exec').body[0].value.copy(fix=False, pars=False).is_enclosed())

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

        if _PY_VERSION >= (3, 12):
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

        if _PY_VERSION >= (3, 14):
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

        if _PY_VERSION >= (3, 12):
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

        if _PY_VERSION >= (3, 14):
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

    def test_get_indentable_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = "... \\\n2"\n else:\n  j \\\n=\\\n 2'
        ast = parse(src)

        self.assertEqual({1, 2, 5, 7, 8, 9, 10}, ast.f.get_indentable_lns(1))
        self.assertEqual({0, 1, 2, 5, 7, 8, 9, 10}, ast.f.get_indentable_lns(0))

        f = FST.fromsrc('''
def _splitext(p, sep, altsep, extsep):
    """Split the extension from a pathname.

    Extension is everything from the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work for text and bytes strings.

    sepIndex = p.rfind(sep)
            '''.strip())
        self.assertEqual({0, 1, 2, 3, 4, 5, 6, 7}, f.get_indentable_lns(docstr=True))
        self.assertEqual({0, 1, 5, 6, 7}, f.get_indentable_lns(docstr=False))

        f = FST.fromsrc(r'''
_CookiePattern = re.compile(r"""
    \s*                            # Optional whitespace at start of cookie
    (?P<key>                       # Start of group 'key'
    [""" + _LegalKeyChars + r"""]+?   # Any word of at least one letter
    )                              # End of group 'key'
    (                              # Optional group: there may not be a value.
    \s*=\s*                          # Equal Sign
    (?P<val>                         # Start of group 'val'
    "(?:[^\\"]|\\.)*"                  # Any doublequoted string
    |                                  # or
    \w{3},\s[\w\d\s-]{9,11}\s[\d:]{8}\sGMT  # Special case for "expires" attr
    |                                  # or
    [""" + _LegalValueChars + r"""]*      # Any word or empty string
    )                                # End of group 'val'
    )?                             # End of optional value group
    \s*                            # Any number of spaces.
    (\s+|;|$)                      # Ending either at space, semicolon, or EOS.
    """, re.ASCII | re.VERBOSE)    # re.ASCII may be removed if safe.
            '''.strip())
        self.assertEqual({0}, f.get_indentable_lns(docstr=True))
        self.assertEqual({0}, f.get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0, 1}, f.get_indentable_lns(docstr=True))
        self.assertEqual({0}, f.get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
f"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0}, f.get_indentable_lns(docstr=True))  # because f-strings cannot be docstrings
        self.assertEqual({0}, f.get_indentable_lns(docstr=False))

    def test__touchall(self):
        a = parse('i = [1]').body[0]
        self.assertEqual(7, a.f.end_col)
        self.assertEqual(7, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.end_col_offset = 8
        a.value.end_col_offset = 8
        a.value.elts[0].end_col_offset = 7

        self.assertEqual(7, a.f.end_col)
        self.assertEqual(7, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall()
        self.assertEqual(7, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall(parents=True)
        self.assertEqual(8, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall(children=True)
        self.assertEqual(8, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(7, a.value.elts[0].f.end_col)

    def test__offset(self):
        src = 'i = 1\nj = 2\nk = 3'

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 5, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1, exclude=ast.body[1].f)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1, exclude=ast.body[1].f, offset_excluded=False)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1, True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 3, 4), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 3, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1, True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 3, 4), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        def get():
            m = parse('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nbbbb\ncccc')

            m.body[0] = m.body[0].value
            m.body[1] = m.body[1].value
            m.body[2] = m.body[2].value

            m.body[0].lineno         = 1
            m.body[0].end_lineno     = 1
            m.body[0].col_offset     = 2
            m.body[0].end_col_offset = 6
            m.body[1].lineno         = 1
            m.body[1].end_lineno     = 1
            m.body[1].col_offset     = 6
            m.body[1].end_col_offset = 10
            m.body[2].lineno         = 1
            m.body[2].end_lineno     = 1
            m.body[2].col_offset     = 6
            m.body[2].end_col_offset = 6

            return m

        m = get()
        m.f._offset(0, 6, 0, 2, False, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, True, True)
        self.assertEqual((0, 2, 0, 8), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 8, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, False, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, True, False)
        self.assertEqual((0, 2, 0, 8), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, True)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, False)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 8, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, None)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, None, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

    def test__offset_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j = 2'

        ast = parse(src)
        lns = ast.f.get_indentable_lns(1)
        ast.f._offset_lns(lns, 1)
        self.assertEqual({1, 2, 5, 6, 7}, lns)
        self.assertEqual((0, 0, 7, 7), ast.f.loc)
        self.assertEqual((0, 0, 7, 8), ast.body[0].f.loc)
        self.assertEqual((1, 2, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 5, 1, 9), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].f.get_indentable_lns(1)
        ast.body[0].body[0].f._offset_lns(lns, 1)
        self.assertEqual({2, 5, 6, 7}, lns)
        self.assertEqual((1, 1, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 4, 1, 8), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f.get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._offset_lns(lns, 1)
        self.assertEqual(set(), lns)
        self.assertEqual((2, 2, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 6, 4, 3), ast.body[0].body[0].body[0].value.f.loc)

        src = 'i = 1\nj = 2\nk = 3\nl = \\\n4'
        ast = parse(src)
        off = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

        ast.f._offset_lns(off)
        self.assertEqual((0, 0, 4, 1), ast.f.loc)
        self.assertEqual((0, 0, 0, 5), ast.body[0].f.loc)
        self.assertEqual((0, 0, 0, 1), ast.body[0].targets[0].f.loc)
        self.assertEqual((0, 4, 0, 5), ast.body[0].value.f.loc)
        self.assertEqual((1, 1, 1, 6), ast.body[1].f.loc)
        self.assertEqual((1, 1, 1, 2), ast.body[1].targets[0].f.loc)
        self.assertEqual((1, 5, 1, 6), ast.body[1].value.f.loc)
        self.assertEqual((2, 2, 2, 7), ast.body[2].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[2].targets[0].f.loc)
        self.assertEqual((2, 6, 2, 7), ast.body[2].value.f.loc)
        self.assertEqual((3, 3, 4, 5), ast.body[3].f.loc)
        self.assertEqual((3, 3, 3, 4), ast.body[3].targets[0].f.loc)
        self.assertEqual((4, 4, 4, 5), ast.body[3].value.f.loc)

    def test__indent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._indent_lns('  ')
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n   if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._indent_lns('  ')
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._indent_lns('  ')
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._indent_lns('  ')
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n  =\\\n   2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.f._indent_lns('  ')
        self.assertEqual({1, 2}, lns)
        self.assertEqual('@decorator\n  class cls:\n   pass', ast.f.src)

    def test__dedent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._dedent_lns(' ')
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\nif True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._dedent_lns(' ')
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._dedent_lns(' ')
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._dedent_lns(' ')
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.body[0].body[0].f._dedent_lns(' ')
        self.assertEqual(set(), lns)
        self.assertEqual('@decorator\nclass cls:\n pass', ast.f.src)

        # ast = parse(src)
        # lns = ast.body[0].body[0].f._dedent_lns(' ', skip=0)
        # self.assertEqual({2}, lns)
        # self.assertEqual('@decorator\nclass cls:\npass', ast.f.src)

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

        if _PY_VERSION >= (3, 14):  # make sure parent Interpolation.str gets modified
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

        # tuple

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

    def test_unpar(self):
        f = parse('((1,))').body[0].value.f.copy(pars=True)
        self.assertEqual('((1,))', f.src)
        f.unpar()  # self.assertTrue()
        self.assertEqual('(1,)', f.src)
        f.unpar()  # self.assertFalse()
        self.assertEqual('(1,)', f.src)
        f.unpar(tuple_=True)  # self.assertTrue()
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
        f.unpar(tuple_=True)  # self.assertTrue()
        self.assertEqual('1,', f.src)

        if _PY_VERSION >= (3, 14):  # make sure parent Interpolation.str gets modified
            f = FST('t"{(a)}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar()
            self.assertEqual('t"{a}"', f.src)
            self.assertEqual('a', f.values[0].str)

            f = FST('t"{((a,))}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar()
            self.assertEqual('t"{(a,)}"', f.src)
            self.assertEqual('(a,)', f.values[0].str)

            f = FST('t"{((a,))}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar(tuple_=True)
            self.assertEqual('t"{a,}"', f.src)
            self.assertEqual('a,', f.values[0].str)

        # grouping

        f = parse('a').f
        f.body[0].value.unpar(share=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(a)').f
        f.body[0].value.unpar(share=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((a))').f
        f.body[0].value.unpar(share=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(\n ( (a) )  \n)').f
        f.body[0].value.unpar(share=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((i,))').f
        f.body[0].value.unpar(share=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('(\n ( (i,) ) \n)').f
        f.body[0].value.unpar(share=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0].unpar(share=False)
        self.assertEqual(f.src, 'call((i for i in j))')
        self.assertEqual((0, 0, 0, 20), f.loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0].unpar(share=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call( ( ( (i for i in j) ) ) )').f
        f.body[0].value.args[0].unpar(share=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0].unpar(share=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0].unpar(share=False)
        self.assertEqual(f.src, 'call((i for i in j),)')
        self.assertEqual((0, 0, 0, 21), f.loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('( # pre\ni\n# post\n)').f
        f.body[0].value.unpar(share=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('( # pre\ni\n# post\n)').body[0].value.f.copy(pars=True)
        f.unpar(share=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        f = parse('( # pre\n(i,)\n# post\n)').f
        f.body[0].value.unpar(share=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)

        f = parse('( # pre\n(i)\n# post\n)').body[0].value.f.copy(pars=True)
        f.unpar(share=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a)if(a)]', 'exec')
        f.body[0].value.generators[0].ifs[0].unpar(share=False)
        f.body[0].value.generators[0].ifs[1].unpar(share=False)
        self.assertEqual('[a for a in b if a if a]', f.src)

        f = FST('for(a)in b: pass', 'exec')
        f.body[0].target.unpar(share=False)
        self.assertEqual('for a in b: pass', f.src)

        f = FST('assert(test)', 'exec')
        f.body[0].test.unpar(share=False)
        self.assertEqual('assert test', f.src)

        f = FST('assert({test})', 'exec')
        f.body[0].test.unpar(share=False)
        self.assertEqual('assert{test}', f.src)

        # tuple

        f = parse('()').f
        f.body[0].value.unpar()
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)

        f = parse('(i,)').f
        f.body[0].value.unpar(tuple_=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('(a, b)').f
        f.body[0].value.unpar(tuple_=True)
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.body[0].value.elts[1].loc)

        f = parse('( # pre\ni,\n# post\n)').f
        f.body[0].value.unpar(tuple_=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('( # pre\ni,\n# post\n)').body[0].value.f.copy()
        f.unpar(tuple_=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a,b)if(a,)if(a,b)]', 'exec')
        f.body[0].value.generators[0].ifs[0].unpar(tuple_=True)
        f.body[0].value.generators[0].ifs[1].unpar(tuple_=True)
        f.body[0].value.generators[0].ifs[2].unpar(tuple_=True)
        self.assertEqual('[a for a in b if a,b if a,if a,b]', f.src)
        f.body[0].value.generators[0].ifs[0].par()  # so that it will verify
        f.body[0].value.generators[0].ifs[1].par()
        f.body[0].value.generators[0].ifs[2].par()
        self.assertEqual('[a for a in b if (a,b) if (a,)if (a,b)]', f.src)
        f.verify()

        f = FST('for(a,b)in b: pass', 'exec')
        f.body[0].target.unpar(tuple_=True)
        self.assertEqual('for a,b in b: pass', f.src)
        f.verify()

        f = FST('for(a,)in b: pass', 'exec')
        f.body[0].target.unpar(tuple_=True)
        self.assertEqual('for a,in b: pass', f.src)
        f.verify()

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
        self.assertEqual(ast_.unparse(f0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f0.a, locs=False, raise_=True))

        f1 = f.body[1].copy()
        h = f._code_as_stmts(f1.a)
        self.assertEqual(ast_.unparse(f1.a), h.src)
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
        self.assertEqual(ast_.unparse(g.a), h.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=False, raise_=True))

        self.assertRaises(ValueError, f._code_as_expr, FST('i = 1', 'exec').body[0])
        self.assertRaises(NodeError, f._code_as_expr, FST('i = 1', 'exec').body[0].copy())
        self.assertRaises(NodeError, f._code_as_expr, f.body[0].a)
        self.assertRaises(NodeError, f._code_as_expr, 'pass')

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
        self.assertEqual(ast_.unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = f._code_as_ExceptHandlers(g1.a)
        self.assertEqual(ast_.unparse(g1.a), h.src)
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
        self.assertEqual(ast_.unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = f._code_as_match_cases(g1.a)
        self.assertEqual(ast_.unparse(g1.a), h.src)
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
            (FST._code_as_slice, 'body[0].value.slice', 'a[1]'),
            (FST._code_as_slice, 'body[0].value.slice', 'a[b:c:d]'),
            (FST._code_as_slice, 'body[0].value.slice', 'a[b:c:d, e:f]'),
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

        if _PY_VERSION >= (3, 12):
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
            self.assertEqual(ast_.unparse(g.a), ast_.unparse(f.a))
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
        self.assertEqual(ast_.unparse(f0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f0.a, locs=False, raise_=True))

        f1 = f.body[1].copy()
        h = f._code_as_stmtishs(f1.a)
        self.assertEqual(ast_.unparse(f1.a), h.src)
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
        self.assertEqual(ast_.unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = f._code_as_stmtishs(g1.a)
        self.assertEqual(ast_.unparse(g1.a), h.src)
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
        self.assertEqual(ast_.unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = f._code_as_stmtishs(g1.a)
        self.assertEqual(ast_.unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, f._code_as_stmtishs, f.body[0].cases[0])

        # special 'case' non-keyword

        self.assertIsInstance(FST._code_as_stmtishs('case 1: pass').body[0].a, match_case)
        self.assertIsInstance(FST._code_as_stmtishs('case = 1').body[0].a, Assign)
        self.assertIsInstance(FST._code_as_stmtishs('case.b = 1').body[0].a, Assign)

    def test_code_as_sanitize(self):
        CODE_ASES = [
            (FST._code_as_expr, 'f(a)'),
            (FST._code_as_slice, 'b:c:d'),
            (FST._code_as_slice, 'b:c:d, e:f'),
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

        if _PY_VERSION >= (3, 12):
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

    def test__put_src(self):
        f = FST(Load(), [''])
        f._put_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['test'])
        f._put_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['testtest'])
        f._put_src('tost', 0, 0, 0, 8)
        self.assertEqual(f.lines, ['tost'])
        f._put_src('a\nb\nc', 0, 2, 0, 2)
        self.assertEqual(f.lines, ['toa', 'b', 'cst'])
        f._put_src('', 0, 3, 2, 1)
        self.assertEqual(f.lines, ['toast'])
        f._put_src('a\nb\nc\nd', 0, 0, 0, 5)
        self.assertEqual(f.lines, ['a', 'b', 'c', 'd'])
        f._put_src('efg\nhij', 1, 0, 2, 1)
        self.assertEqual(f.lines, ['a', 'efg', 'hij', 'd'])
        f._put_src('***', 1, 2, 2, 1)
        self.assertEqual(f.lines, ['a', 'ef***ij', 'd'])

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
        self.assertEqual(1, f.elts[0].pars(True)[1])
        self.assertEqual(2, f.elts[1].pars(True)[1])
        self.assertEqual(0, f.pars(True)[1])

        self.assertEqual(1, parse('call(((i for i in j)))').body[0].value.args[0].f.pars(True)[1])
        self.assertEqual(0, parse('call((i for i in j))').body[0].value.args[0].f.pars(True)[1])
        self.assertEqual(0, parse('call(i for i in j)').body[0].value.args[0].f.pars(True)[1])
        self.assertEqual(-1, parse('call(i for i in j)').body[0].value.args[0].f.pars(True, shared=False)[1])

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
        self.assertEqual(f.a.body[0].f.copy(fix=False).src, '@decorator\nclass cls:\n  pass')
        # self.assertEqual(f.a.body[0].f.copy(decos=False, fix=False).src, 'class cls:\n  pass')

        l = FST.fromsrc("['\\u007f', '\\u0080', 'ʁ', 'ᛇ', '時', '🐍', '\\ud800', 'Źdźbło']").a.body[0].value.elts
        self.assertEqual("'\\u007f'", l[0].f.copy().src)
        self.assertEqual("'\\u0080'", l[1].f.copy().src)
        self.assertEqual("'ʁ'", l[2].f.copy().src)
        self.assertEqual("'ᛇ'", l[3].f.copy().src)
        self.assertEqual("'時'", l[4].f.copy().src)
        self.assertEqual("'🐍'", l[5].f.copy().src)
        self.assertEqual("'\\ud800'", l[6].f.copy().src)
        self.assertEqual("'Źdźbło'", l[7].f.copy().src)

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(fix=True)
        self.assertEqual('(w := x,)', f.src)

        # f = FST.fromsrc('a[1:2, 3:4]').a.body[0].value.slice.f.copy(fix=False)
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

        if _PY_VERSION >= (3, 12):
            f = FST.fromsrc('a[*b]').a.body[0].value.slice.f.copy(fix=True)
            self.assertEqual('*b,', f.src)

            f = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(fix=True)
            self.assertEqual('*tuple[int, ...],', f.src)

    def test_copy_bulk(self):
        for fnm in PYFNMS:
            ast = FST.fromsrc(read(fnm)).a

            for a in walk(ast):
                if a.f.is_parsable():
                    f = a.f.copy(fix=True)
                    f.verify(raise_=True)

    def test_copy(self):
        for src, elt, slice_copy, slice_dump in COPY_DATA:
            src   = src.strip()
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.copy(fix=True)
            ssrc  = s.src
            sdump = s.dump(out=list, compact=True)

            try:
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print(elt)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_cut_special(self):
        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('i', a.body[0].f.cut(precomms=False, postcomms=False).src)
        self.assertEqual('# prepre\n\n# pre\n# post\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# pre\ni', a.body[0].f.cut(precomms=True, postcomms=False).src)
        self.assertEqual('# prepre\n\n# post\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# pre\ni # post\n', a.body[0].f.cut(precomms=True, postcomms=True).src)
        self.assertEqual('# prepre\n\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# prepre\n\n# pre\ni', a.body[0].f.cut(precomms='all', postcomms=False).src)
        self.assertEqual('# post\n# postpost', a.f.src)

        a = parse('( ( i ), )')
        f = a.body[0].value.elts[0].f.cut(precomms=False, postcomms=False)
        self.assertEqual('()', a.f.src)
        self.assertEqual('i', f.src)

        a = parse('( ( i ), )')
        f = a.body[0].value.elts[0].f.cut(precomms=False, postcomms=False, pars=True)
        self.assertEqual('()', a.f.src)
        self.assertEqual('( i )', f.src)

        a = parse('''
match a:
  case 1:
    if 1:
      pass
    else:
      pass
  case 2:
    try:
      pass
    except:
      pass
    else:
      pass
    finally:
      pass
  case 2:
    for a in b:
      pass
    else:
      pass
  case 3:
    async for a in b:
      pass
    else:
      pass
  case 4:
    while a in b:
      pass
    else:
      pass
  case 5:
    with a as b:
      pass
  case 6:
    async with a as b:
      pass
  case 7:
    def func():
      pass
  case 8:
    async def func():
      pass
  case 9:
    class cls:
      pass
            '''.strip())
        a.body[0].cases[0].body[0].body[0].f.cut()
        a.body[0].cases[0].body[0].orelse[0].f.cut()
        a.body[0].cases[1].body[0].body[0].f.cut()
        a.body[0].cases[1].body[0].handlers[0].f.cut()
        a.body[0].cases[1].body[0].orelse[0].f.cut()
        a.body[0].cases[1].body[0].finalbody[0].f.cut()
        a.body[0].cases[2].body[0].body[0].f.cut()
        a.body[0].cases[2].body[0].orelse[0].f.cut()
        a.body[0].cases[3].body[0].body[0].f.cut()
        a.body[0].cases[3].body[0].orelse[0].f.cut()
        a.body[0].cases[4].body[0].body[0].f.cut()
        a.body[0].cases[4].body[0].orelse[0].f.cut()
        a.body[0].cases[5].body[0].body[0].f.cut()
        a.body[0].cases[6].body[0].body[0].f.cut()
        a.body[0].cases[7].body[0].body[0].f.cut()
        a.body[0].cases[8].body[0].body[0].f.cut()
        a.body[0].cases[9].body[0].body[0].f.cut()

        self.assertEqual(a.f.src, '''
match a:
  case 1:
    if 1:
  case 2:
    try:
  case 2:
    for a in b:
  case 3:
    async for a in b:
  case 4:
    while a in b:
  case 5:
    with a as b:
  case 6:
    async with a as b:
  case 7:
    def func():
  case 8:
    async def func():
  case 9:
    class cls:
'''.lstrip())

        a.body[0].cases[0].body[0].f.cut()
        a.body[0].cases[1].body[0].f.cut()
        a.body[0].cases[2].body[0].f.cut()
        a.body[0].cases[3].body[0].f.cut()
        a.body[0].cases[4].body[0].f.cut()
        a.body[0].cases[5].body[0].f.cut()
        a.body[0].cases[6].body[0].f.cut()
        a.body[0].cases[7].body[0].f.cut()
        a.body[0].cases[8].body[0].f.cut()
        a.body[0].cases[9].body[0].f.cut()

        self.assertEqual(a.f.src, '''
match a:
  case 1:
  case 2:
  case 2:
  case 3:
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 9:
'''.lstrip())

        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()
        a.body[0].cases[0].f.cut()

        self.assertEqual(a.f.src, '''match a:\n''')

        a = parse('''
match a:
  case 1:
    if 1:
      pass
    else:
      pass
  case 2:
    try:
      pass
    except:
      pass
    else:
      pass
    finally:
      pass
  case 2:
    for a in b:
      pass
    else:
      pass
  case 3:
    async for a in b:
      pass
    else:
      pass
  case 4:
    while a in b:
      pass
    else:
      pass
  case 5:
    with a as b:
      pass
  case 6:
    async with a as b:
      pass
  case 7:
    def func():
      pass
  case 8:
    async def func():
      pass
  case 9:
    class cls:
      pass
            '''.strip())
        a.body[0].cases[9].body[0].body[0].f.cut()
        a.body[0].cases[8].body[0].body[0].f.cut()
        a.body[0].cases[7].body[0].body[0].f.cut()
        a.body[0].cases[6].body[0].body[0].f.cut()
        a.body[0].cases[5].body[0].body[0].f.cut()
        a.body[0].cases[4].body[0].orelse[0].f.cut()
        a.body[0].cases[4].body[0].body[0].f.cut()
        a.body[0].cases[3].body[0].orelse[0].f.cut()
        a.body[0].cases[3].body[0].body[0].f.cut()
        a.body[0].cases[2].body[0].orelse[0].f.cut()
        a.body[0].cases[2].body[0].body[0].f.cut()
        a.body[0].cases[1].body[0].finalbody[0].f.cut()
        a.body[0].cases[1].body[0].orelse[0].f.cut()
        a.body[0].cases[1].body[0].handlers[0].f.cut()
        a.body[0].cases[1].body[0].body[0].f.cut()
        a.body[0].cases[0].body[0].orelse[0].f.cut()
        a.body[0].cases[0].body[0].body[0].f.cut()

        self.assertEqual(a.f.src, '''
match a:
  case 1:
    if 1:
  case 2:
    try:
  case 2:
    for a in b:
  case 3:
    async for a in b:
  case 4:
    while a in b:
  case 5:
    with a as b:
  case 6:
    async with a as b:
  case 7:
    def func():
  case 8:
    async def func():
  case 9:
    class cls:
'''.lstrip())

        a.body[0].cases[9].body[0].f.cut()
        a.body[0].cases[8].body[0].f.cut()
        a.body[0].cases[7].body[0].f.cut()
        a.body[0].cases[6].body[0].f.cut()
        a.body[0].cases[5].body[0].f.cut()
        a.body[0].cases[4].body[0].f.cut()
        a.body[0].cases[3].body[0].f.cut()
        a.body[0].cases[2].body[0].f.cut()
        a.body[0].cases[1].body[0].f.cut()
        a.body[0].cases[0].body[0].f.cut()

        self.assertEqual(a.f.src, '''
match a:
  case 1:
  case 2:
  case 2:
  case 3:
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 9:
'''.lstrip())

        a.body[0].cases[9].f.cut()
        a.body[0].cases[8].f.cut()
        a.body[0].cases[7].f.cut()
        a.body[0].cases[6].f.cut()
        a.body[0].cases[5].f.cut()
        a.body[0].cases[4].f.cut()
        a.body[0].cases[3].f.cut()
        a.body[0].cases[2].f.cut()
        a.body[0].cases[1].f.cut()
        a.body[0].cases[0].f.cut()

        self.assertEqual(a.f.src, '''match a:\n''')

    def test_cut_and_del_special(self):
        fst = parse('''
match a:
    case 1:  # CASE
        i = 1

match b:  # MATCH
    case 2:
        pass  # this is removed

if 1:  # IF
    j; k
else:  # ELSE
    l ; \\
  m

try:  # TRY
    # pre
    n  # post
except:  # EXCEPT
    if 1: break
else:  # delelse
    if 2: continue
    elif 3: o
    else: p
finally:  # delfinally
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q

for a in b:  # FOR
    # pre-classdeco
    @classdeco
    class cls:
        @methdeco
        def meth(self):
            mvar = 5  # post-meth
else:  # delelse
    """Multi
    line # notcomment
    string."""

async for a in b:  # ASYNC FOR
    ("Multi"
     "line  # notcomment"
     "string \\\\ not linecont")
else:  # delelse
    r = [i for i in range(100)]  # post-list-comprehension

while a in b:  # WHILE
    # pre-global
    global c
else:  # delelse
    lambda x: x**2

with a as b:  # WITH
    try: a ; #  post-try
    except: b ; c  # post-except
    else: return 5
    finally: yield 6

async with a as b:  # ASYNC WITH
    del x, y, z

def func(a = """ \\\\ not linecont
            # notcomment"""):  # FUNC
    assert s, t

@asyncdeco
async def func():  # ASYNC FUNC
    match z:
        case 1: zz
        case 2:
            zzz

class cls:  # CLASS
    def docfunc(a, /, b=2, *c, d=""" # not \\\\ linecont
            # comment
            """, **e):
        """Doc
        string # ."""

        return -1

if clause:
    while something:  # WHILE
        yield from blah
    else:  # delelse
        @funcdeco
        def func(args) -> list[int]:
            return [2]

if indented:
    try:  # TRY
        try: raise
        except Exception as exc:
            raise exc from exc
    except:  # EXCEPT
        aa or bb or cc
    else:  # delelse
        f'{i:2} plus 1'
    finally:  # delelse
        j = (i := k)
'''.lstrip()).f

        fst2 = fst.copy()

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),

            (fst.a.body[3].f, 'body'),
            (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'orelse'),

            (fst.a.body[13].body[0].f, 'body'),
            (fst.a.body[13].body[0].f, 'handlers'),
            (fst.a.body[13].body[0].f, 'orelse'),
            (fst.a.body[13].body[0].f, 'finalbody'),
        ]

        lines = []

        for point, field in points:
            f = point.get_slice(field=field, cut=True)

            lines.extend(f.lines)
            lines.append('...')

        lines.extend(fst.lines)

        self.assertEqual(lines, [
            'i = 1',
            '...',
            'pass',
            '...',
            'j; k',
            '...',
            'l ; \\',
            'm',
            '...',
            '# pre',
            'n  # post',
            '',
            '...',
            'except:  # EXCEPT',
            '    if 1: break',
            '...',
            'if 2: continue',
            'elif 3: o',
            'else: p',
            '...',
            '@deco',
            'def inner() -> list[int]:',
            '    q = 4  # post-inner-q',
            '',
            '...',
            '# pre-classdeco',
            '@classdeco',
            'class cls:',
            '    @methdeco',
            '    def meth(self):',
            '        mvar = 5  # post-meth',
            '',
            '...',
            '"""Multi',
            'line # notcomment',
            'string."""',
            '...',
            '("Multi"',
            ' "line  # notcomment"',
            ' "string \\\\ not linecont")',
            '...',
            'r = [i for i in range(100)]  # post-list-comprehension',
            '',
            '...',
            '# pre-global',
            'global c',
            '...',
            'lambda x: x**2',
            '...',
            'try: a ; #  post-try',
            'except: b ; c  # post-except',
            'else: return 5',
            'finally: yield 6',
            '...',
            'del x, y, z',
            '...',
            'assert s, t',
            '...',
            'match z:',
            '    case 1: zz',
            '    case 2:',
            '        zzz',
            '...',
            'def docfunc(a, /, b=2, *c, d=""" # not \\\\ linecont',
            '            # comment',
            '            """, **e):',
            '    """Doc',
            '    string # ."""',
            '',
            '    return -1',
            '...',
            'yield from blah',
            '...',
            '@funcdeco',
            'def func(args) -> list[int]:',
            '    return [2]',
            '...',
            'try: raise',
            'except Exception as exc:',
            '    raise exc from exc',
            '...',
            'except:  # EXCEPT',
            '    aa or bb or cc',
            '...',
            "f'{i:2} plus 1'",
            '...',
            'j = (i := k)',
            '...',
            'match a:',
            '    case 1:  # CASE',
            '',
            'match b:  # MATCH',
            '',
            'if 1:  # IF',
            '',
            'try:  # TRY',
            '',
            'for a in b:  # FOR',
            '',
            'async for a in b:  # ASYNC FOR',
            '',
            'while a in b:  # WHILE',
            '',
            'with a as b:  # WITH',
            '',
            'async with a as b:  # ASYNC WITH',
            '',
            'def func(a = """ \\\\ not linecont',
            '            # notcomment"""):  # FUNC',
            '',
            '@asyncdeco',
            'async def func():  # ASYNC FUNC',
            '',
            'class cls:  # CLASS',
            '',
            'if clause:',
            '    while something:  # WHILE',
            '',
            'if indented:',
            '    try:  # TRY',
            ''
        ])

        fst = fst2

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),

            (fst.a.body[3].f, 'body'),
            (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'orelse'),

            (fst.a.body[13].body[0].f, 'body'),
            (fst.a.body[13].body[0].f, 'handlers'),
            (fst.a.body[13].body[0].f, 'orelse'),
            (fst.a.body[13].body[0].f, 'finalbody'),
        ]

        for point, field in points:
            point.put_slice(None, field=field, check_node_type=False)

        self.assertEqual(fst.lines, [
            'match a:',
            '    case 1:  # CASE',
            '',
            'match b:  # MATCH',
            '',
            'if 1:  # IF',
            '',
            'try:  # TRY',
            '',
            'for a in b:  # FOR',
            '',
            'async for a in b:  # ASYNC FOR',
            '',
            'while a in b:  # WHILE',
            '',
            'with a as b:  # WITH',
            '',
            'async with a as b:  # ASYNC WITH',
            '',
            'def func(a = """ \\\\ not linecont',
            '            # notcomment"""):  # FUNC',
            '',
            '@asyncdeco',
            'async def func():  # ASYNC FUNC',
            '',
            'class cls:  # CLASS',
            '',
            'if clause:',
            '    while something:  # WHILE',
            '',
            'if indented:',
            '    try:  # TRY',
            ''
        ])

        fst = parse('''
match a:
    case 1:  \\
  # CASE
        i = 1

match b:  \\
  # MATCH
    case 2:
        pass  # this is removed

if 1:  \\
  # IF
    j; k
else:  \\
  # ELSE
    l ; \\
      m

try:  \\
  # TRY
    # pre
    n  # post
except:  \\
  # EXCEPT
    if 1: break
else:  \\
  # delelse
    if 2: continue
    elif 3: o
    else: p
finally:  \\
  # delfinally
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q

for a in b:  \\
  # FOR
    # pre-classdeco
    @classdeco
    class cls:
        @methdeco
        def meth(self):
            mvar = 5  # post-meth
else:  \\
  # delelse
    """Multi
    line # notcomment
    string."""

async for a in b:  \\
  # ASYNC FOR
    ("Multi"
     "line  # notcomment"
     "string \\\\ not linecont")
else:  \\
  # delelse
    r = [i for i in range(100)]  # post-list-comprehension

while a in b:  \\
  # WHILE
    # pre-global
    global c
else:  \\
  # delelse
    lambda x: x**2

with a as b:  \\
  # WITH
    try: a ; #  post-try
    except: b ; c  # post-except
    else: return 5
    finally: yield 6

async with a as b:  \\
  # ASYNC WITH
    del x, y, z

def func(a = """ \\\\ not linecont
            # notcomment"""):  \\
  # FUNC
    assert s, t

@asyncdeco
async def func():  \\
  # ASYNC FUNC
    match z:
        case 1: zz
        case 2:
            zzz

class cls:  \\
  # CLASS
    def docfunc(a, /, b=2, *c, d=""" # not \\\\ linecont
            # comment
            """, **e):
        """Doc
        string # ."""

        return -1

if clause:
    while something:  \\
  # WHILE
        yield from blah
    else:  \\
  # delelse
        @funcdeco
        def func(args) -> list[int]:
            return [2]

if indented:
    try:  \\
  # TRY
        try: raise
        except Exception as exc:
            raise exc from exc
    except:  \\
  # EXCEPT
        aa or bb or cc
    else:  \\
  # delelse
        f'{i:2} plus 1'
    finally:  \\
  # delelse
        j = (i := k)
'''.lstrip()).f

        fst2 = fst.copy()

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),

            (fst.a.body[3].f, 'body'),
            (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'orelse'),

            (fst.a.body[13].body[0].f, 'body'),
            (fst.a.body[13].body[0].f, 'handlers'),
            (fst.a.body[13].body[0].f, 'orelse'),
            (fst.a.body[13].body[0].f, 'finalbody'),
        ]

        lines = []

        for point, field in points:
            f = point.get_slice(field=field, cut=True)

            lines.extend(f.lines)
            lines.append('...')

        lines.extend(fst.lines)

        self.assertEqual(lines, [
            '# CASE',
            'i = 1',
            '...',
            'pass',
            '...',
            '# IF',
            'j; k',
            '...',
            '# ELSE',
            'l ; \\',
            '  m',
            '...',
            '# TRY',
            '# pre',
            'n  # post',
            '',
            '...',
            'except:  \\',
            '  # EXCEPT',
            '    if 1: break',
            '...',
            '# delelse',
            'if 2: continue',
            'elif 3: o',
            'else: p',
            '...',
            '# delfinally',
            '@deco',
            'def inner() -> list[int]:',
            '    q = 4  # post-inner-q',
            '',
            '...',
            '# FOR',
            '# pre-classdeco',
            '@classdeco',
            'class cls:',
            '    @methdeco',
            '    def meth(self):',
            '        mvar = 5  # post-meth',
            '',
            '...',
            '# delelse',
            '"""Multi',
            'line # notcomment',
            'string."""',
            '...',
            '# ASYNC FOR',
            '("Multi"',
            ' "line  # notcomment"',
            ' "string \\\\ not linecont")',
            '...',
            '# delelse',
            'r = [i for i in range(100)]  # post-list-comprehension',
            '',
            '...',
            '# WHILE',
            '# pre-global',
            'global c',
            '...',
            '# delelse',
            'lambda x: x**2',
            '...',
            '# WITH',
            'try: a ; #  post-try',
            'except: b ; c  # post-except',
            'else: return 5',
            'finally: yield 6',
            '...',
            '# ASYNC WITH',
            'del x, y, z',
            '...',
            '# FUNC',
            'assert s, t',
            '...',
            '# ASYNC FUNC',
            'match z:',
            '    case 1: zz',
            '    case 2:',
            '        zzz',
            '...',
            '# CLASS',
            'def docfunc(a, /, b=2, *c, d=""" # not \\\\ linecont',
            '            # comment',
            '            """, **e):',
            '    """Doc',
            '    string # ."""',
            '',
            '    return -1',
            '...',
            '# WHILE',
            'yield from blah',
            '...',
            '# delelse',
            '@funcdeco',
            'def func(args) -> list[int]:',
            '    return [2]',
            '...',
            '# TRY',
            'try: raise',
            'except Exception as exc:',
            '    raise exc from exc',
            '...',
            'except:  \\',
            '# EXCEPT',
            '    aa or bb or cc',
            '...',
            '# delelse',
            "f'{i:2} plus 1'",
            '...',
            '# delelse',
            'j = (i := k)',
            '...',
            'match a:',
            '    case 1:',
            '',
            'match b:',
            '',
            'if 1:',
            '',
            'try:',
            '',
            'for a in b:',
            '',
            'async for a in b:',
            '',
            'while a in b:',
            '',
            'with a as b:',
            '',
            'async with a as b:',
            '',
            'def func(a = """ \\\\ not linecont',
            '            # notcomment"""):',
            '',
            '@asyncdeco',
            'async def func():',
            '',
            'class cls:',
            '',
            'if clause:',
            '    while something:',
            '',
            'if indented:',
            '    try:',
            ''
        ])

        fst = fst2

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),

            (fst.a.body[3].f, 'body'),
            (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'orelse'),

            (fst.a.body[13].body[0].f, 'body'),
            (fst.a.body[13].body[0].f, 'handlers'),
            (fst.a.body[13].body[0].f, 'orelse'),
            (fst.a.body[13].body[0].f, 'finalbody'),
        ]

        for point, field in points:
            point.put_slice(None, field=field)

        self.assertEqual(fst.lines, [
            'match a:',
            '    case 1:',
            '',
            'match b:',
            '',
            'if 1:',
            '',
            'try:',
            '',
            'for a in b:',
            '',
            'async for a in b:',
            '',
            'while a in b:',
            '',
            'with a as b:',
            '',
            'async with a as b:',
            '',
            'def func(a = """ \\\\ not linecont',
            '            # notcomment"""):',
            '',
            '@asyncdeco',
            'async def func():',
            '',
            'class cls:',
            '',
            'if clause:',
            '    while something:',
            '',
            'if indented:',
            '    try:',
            ''
        ])

    def test_cut_block_everything(self):
        for src in ('''
if mo:
    if 1:
        a = 1
        b = 2
    else:
        c = 3
else:
    d = 4
''', '''
try:
    pass
except:
    try:
        pass
    except:
        pass
else:
    pass
''', '''
def func(args):
    pass
''', '''
@decorator(arg)
def func():
    pass
'''     ):

            ast  = parse(src.strip())
            asts = [a for a in walk(ast) if isinstance(a, fst.STMTISH)]

            for a in asts[::-1]:
                a.f.cut()

            ast  = parse(src.strip())
            asts = [a for a in walk(ast) if isinstance(a, fst.STMTISH)]

            for a in asts[::-1]:
                field, idx = a.f.pfield

                a.f.parent.put_slice(None, idx, idx + 1, field)

    def test_insert_into_empty_block(self):
        a = parse('''
if 1:
    i \\

'''.lstrip())
        a.body[0].f.put_slice('j', field='orelse')
        a.f.verify()
        self.assertEqual(a.f.src, 'if 1:\n    i\nelse:\n    j\n\n')

        a = parse('''
def f():
    pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'def f():\n    i\n')

        a = parse('''
def f(): pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'def f():\n    i\n')

        a = parse('''
def f():
    pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'def f():\n    # pre\n    i  # post\n')

        a = parse('''
def f(): pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'def f():\n    # pre\n    i  # post\n')

        a = parse('''
match a:
    case 1: pass
        '''.strip())
        a.body[0].cases[0].body[0].f.cut()
        a.body[0].cases[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'match a:\n    case 1:\n        i\n')

        a = parse('''
match a:
    case 1: pass
        '''.strip())
        a.body[0].cases[0].f.cut()
        a.body[0].f.put_slice('i', check_node_type=False)
        self.assertEqual(a.f.src, 'match a:\n    i\n')


        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 1:\n    i\n')

        a = parse('''
if 1:
    pass
else: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 1:\n    i\nelse: pass')

        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 1:\nelse:\n    i\n')

        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 1:\n    pass\nelse:\n    i\n')


        a = parse('''if 2:
    def f():
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        i\n')

        a = parse('''if 2:
    def f(): pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        i\n')

        a = parse('''if 2:
    def f():
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        # pre\n        i  # post\n')

        a = parse('''if 2:
    def f(): pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        # pre\n        i  # post\n')

        a = parse('''if 2:
    match a:
        case 1: pass
        '''.strip())
        a.body[0].body[0].cases[0].body[0].f.cut()
        a.body[0].body[0].cases[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    match a:\n        case 1:\n            i\n')

        a = parse('''if 2:
    match a:
        case 1: pass
        '''.strip())
        a.body[0].body[0].cases[0].f.cut()
        a.body[0].body[0].f.put_slice('i', check_node_type=False)
        self.assertEqual(a.f.src, 'if 2:\n    match a:\n        i\n')


        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        i\n')

        a = parse('''if 2:
    if 1:
        pass
    else: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        i\n    else: pass')

        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n    else:\n        i\n')

        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        pass\n    else:\n        i\n')


        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'try:\nfinally:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'try:\nelse:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        handler = a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'try:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'try:\nelse: pass\nfinally:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\nfinally:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'try: pass\nfinally:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'try:\nelse:\n    i\nfinally: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\nelse:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'try: pass\nelse:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        handler = a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\nfinally: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        handler = a.body[0].handlers[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\nelse: pass\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        handler = a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'try: pass\nexcept: pass\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'try:\n    i\nfinally: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'try:\n    i\nelse: pass\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'try:\n    i\nexcept: pass\n')


        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    finally:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    else:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        handler = a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    else: pass\n    finally:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    finally:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    finally:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    else:\n        i\n    finally: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    else:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    else:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        handler = a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    finally: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        handler = a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    else: pass\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        handler = a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    except: pass\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n    finally: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n    else: pass\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n    except: pass\n')

    def test_insert_into_empty_block_shuffle(self):
        fst = parse('''
match a:
    case 1:
        i = 1

match b:
    case 2:
        pass  # this is removed

if 1:
    j; k
else:
    l
    m

try:
    # pre
    n  # post
except:
    if 1: break
else:
    if 2: continue
    elif 3: o
    else: p
finally:
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q

for a in b:
    # pre-classdeco
    @classdeco
    class cls:
        @methdeco
        def meth(self):
            mvar = 5  # post-meth
else:
    """Multi
    line
    string."""

async for a in b:
    ("Multi"
    "line"
    "string")
else:
    r = [i for i in range(100)]  # post-list-comprehension

while a in b:
    global c
else:
    lambda x: x**2

with a as b:
    try: a ; #  post-try
    except: b ; c  # post-except
    else: return 5
    finally: yield 6

async with a as b:
    del x, y, z

def func():
    assert s, t

@asyncdeco
async def func():
    match z:
        case 1: zz
        case 2:
            zzz

class cls:
    def docfunc(a, /, b=2, *c, d=3, **e):
        """Doc
        string."""

        return -1

if indented:
    try:
        try: raise
        except Exception as exc:
            raise exc from exc
    except:
        aa or bb or cc
    else:
        f'{i:2} plus 1'
    finally:
        j = (i := k)
'''.lstrip()).f

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),
            (fst.a.body[3].f, 'body'),
            (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),
            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'handlers'),
            (fst.a.body[12].body[0].f, 'orelse'),
            (fst.a.body[12].body[0].f, 'finalbody'),
        ]

        seed(0)

        bs = []
        ps = points[:]

        shuffle(ps)

        while ps:
            f, field = ps.pop()

            bs.append(f.get_slice(field=field, cut=True))

        ps = points[:]

        shuffle(ps)
        shuffle(bs)

        while ps:
            f, field = ps.pop()

            f.put_slice(bs.pop(), 0, 0, field=field, check_node_type=False)

        self.assertEqual(fst.src, '''
match a:
    case 1:
        try: a ; #  post-try
        except: b ; c  # post-except
        else: return 5
        finally: yield 6

match b:
    if 2: continue
    elif 3: o
    else: p

if 1:
    r = [i for i in range(100)]  # post-list-comprehension
else:
    try: raise
    except Exception as exc:
        raise exc from exc

try:
    assert s, t
j; k
else:
    l
    m
finally:
    ("Multi"
    "line"
    "string")

for a in b:
    # pre
    n  # post
else:
    pass

async for a in b:
    global c
else:
    i = 1

while a in b:
    except:
        aa or bb or cc
else:
    del x, y, z

with a as b:
    j = (i := k)

async with a as b:
    def docfunc(a, /, b=2, *c, d=3, **e):
        """Doc
        string."""

        return -1

def func():
    except:
        if 1: break

@asyncdeco
async def func():
    match z:
        case 1: zz
        case 2:
            zzz

class cls:
    f'{i:2} plus 1'

if indented:
    try:
        # pre-classdeco
        @classdeco
        class cls:
            @methdeco
            def meth(self):
                mvar = 5  # post-meth
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q
    else:
        """Multi
        line
        string."""
    finally:
        lambda x: x**2
'''.lstrip())

        for _ in range(25):  # now just fuzz it a bit, just in case
            bs = []
            ps = points[:]

            shuffle(ps)

            while ps:
                f, field = ps.pop()

                bs.append(f.get_slice(field=field, cut=True))

            ps = points[:]

            shuffle(ps)
            shuffle(bs)

            while ps:
                f, field = ps.pop()

                f.put_slice(bs.pop(), 0, 0, field=field, check_node_type=False)

    def test_insert_comment_into_empty_field(self):
        fst = parse('''
match a:
    case 1:  # CASE
        pass

match b:  # MATCH
    case 2:
        pass

if 1:  # IF
    pass

try:  # TRY
    pass
except:  # EXCEPT
    pass

for a in b:  # FOR
    pass

async for a in b:  # ASYNC FOR
    pass

while a in b:  # WHILE
    pass

with a as b:  # WITH
    pass

async with a as b:  # ASYNC WITH
    pass

def func(a = """ \\\\ not linecont
         # comment
         """, **e):
    pass

@asyncdeco
async def func():  # ASYNC FUNC
    pass

class cls:  # CLASS
    pass

if clause:
    while something:  # WHILE
        pass

if indented:
    try:  # TRY
        pass
    except:  # EXCEPT
        pass
'''.lstrip()).f

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),

            (fst.a.body[3].f, 'body'),
            (fst.a.body[3].f, 'handlers'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),

            (fst.a.body[13].body[0].f, 'body'),
            (fst.a.body[13].body[0].f, 'handlers'),
        ]

        for point, field in points:
            point.get_slice(field=field, cut=True)

        for i, (point, field) in enumerate(reversed(points)):
            point.put_slice(f'# {i}', 0, 0, field, check_node_type=False)

        self.assertEqual(fst.lines, [
            'match a:',
            '    case 1:  # CASE',
            '        # 15',
            '',
            'match b:  # MATCH',
            '    # 14',
            '',
            'if 1:  # IF',
            '    # 13',
            '',
            'try:  # TRY',
            '    # 12',
            '# 11',
            '',
            'for a in b:  # FOR',
            '    # 10',
            '',
            'async for a in b:  # ASYNC FOR',
            '    # 9',
            '',
            'while a in b:  # WHILE',
            '    # 8',
            '',
            'with a as b:  # WITH',
            '    # 7',
            '',
            'async with a as b:  # ASYNC WITH',
            '    # 6',
            '',
            'def func(a = """ \\\\ not linecont',
            '         # comment',
            '         """, **e):',
            '    # 5',
            '',
            '@asyncdeco',
            'async def func():  # ASYNC FUNC',
            '    # 4',
            '',
            'class cls:  # CLASS',
            '    # 3',
            '',
            'if clause:',
            '    while something:  # WHILE',
            '        # 2',
            '',
            'if indented:',
            '    try:  # TRY',
            '        # 1',
            '    # 0',
            ''
        ])

    def test_insert_stmt_special(self):
        a = parse('''
pass

try:
    break
except:
    continue
else:
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q
finally:
    pass
        '''.strip())
        a.body[1].body[0].f.cut()
        a.body[1].handlers[0].f.cut()
        a.body[1].f.put_slice('# pre\nn  # post', 0, 0, 'handlers', check_node_type=False)
        a.body[1].f.put_slice('i', 0, 0, 'handlers', check_node_type=False)
        self.assertEqual(a.f.src, '''
pass

try:
i
# pre
n  # post
else:
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q
finally:
    pass
            '''.strip())

    def test_replace_and_put_pars_special(self):
        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.elts[1].f.replace(f, pars=True).root.src)

        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, a, 3]', parse('[1, 2, 3]').body[0].value.f.put(f, 1, pars='auto').root.src)

        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.f.put_slice(f, 1, 2, pars='auto', one=True).root.src)

    def test_replace_stmt_special(self):
        a = parse('''
if 1: pass
elif 2:
    pass
        '''.strip())
        a.body[0].orelse[0].f.put_slice(None, 0, 1)
        a.body[0].f.put_slice('break', 0, 1, 'orelse')
        self.assertEqual(a.f.src, 'if 1: pass\nelse:\n    break\n')

        a = parse('''
class cls:
    if 1: pass
    elif 2:
        pass
        '''.strip())
        a.body[0].body[0].orelse[0].f.put_slice(None, 0, 1)
        a.body[0].body[0].f.put_slice('break', 0, 1, 'orelse')
        self.assertEqual(a.f.src, 'class cls:\n    if 1: pass\n    else:\n        break\n')

    def test_replace_returns_new_node(self):
        a = parse('a\nb\nc')
        g = a.body[1].f
        f = g.replace('d')
        self.assertEqual(a.f.src, 'a\nd\nc')
        self.assertEqual(f.src, 'd')
        self.assertIsNone(g.a)

        a = parse('[a, b, c]')
        g = a.body[0].value.elts[1].f
        f = g.replace('d')
        self.assertEqual(a.f.src, '[a, d, c]')
        self.assertEqual(f.src, 'd')
        # self.assertIsNone(g.a)

    def test_replace_raw(self):
        f = parse('def f(a, b): pass').f
        g = f.body[0].args.args[1]
        self.assertEqual('b', g.src)
        h = f.body[0].args.args[1].replace('c=1', raw=True, pars=False)
        self.assertEqual('def f(a, c=1): pass', f.src)
        self.assertEqual('c', h.src)
        self.assertIsNone(g.a)
        i = f.body[0].args.args[1].replace('**d', raw=True, pars=False, to=f.body[0].args.defaults[0])
        self.assertEqual('def f(a, **d): pass', f.src)
        self.assertEqual('d', i.src)
        self.assertIsNone(h.a)

        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.generators[1].replace('for x in y', raw=True, pars=False)
        f = f.repath()
        self.assertEqual(f.src, '[a for c in d for x in y for a in b]')
        self.assertEqual(g.src, 'for x in y')
        # g = f.generators[1].replace(None, raw=True, pars=False)
        # f = f.repath()
        # self.assertEqual(f.src, '[a for c in d  for a in b]')
        # self.assertIsNone(g)
        # # self.assertEqual(g.src, '[a for c in d  for a in b]')
        # g = f.generators[1].replace(None, raw=True, pars=False)
        # f = f.repath()
        # self.assertEqual(f.src, '[a for c in d  ]')
        # self.assertIsNone(g)
        # # self.assertEqual(g.src, '[a for c in d  ]')

        f = parse('f(i for i in j)').body[0].value.args[0].f
        g = f.replace('a', raw=True, pars=False)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f(a)')

        f = parse('f((i for i in j))').body[0].value.args[0].f
        g = f.replace('a', raw=True, pars=False)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f(a)')

        f = parse('f(((i for i in j)))').body[0].value.args[0].f
        g = f.replace('a', raw=True, pars=False)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f((a))')

        self.assertEqual('y', parse('n', mode='eval').body.f.replace('y', raw=True, pars=False).root.src)  # Expression.body

        # parentheses handling

        f = parse('( # 1\ni\n# 2\n)').f
        g = parse('( # 3\nj\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.replace(g, raw=True, pars=False)
        self.assertEqual('( # 1\n( # 3\nj\n# 4\n)\n# 2\n)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        g = parse('( # 3\nj\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.replace(g, raw=True, pars=True)
        self.assertEqual('( # 3\nj\n# 4\n)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        g = parse('( # 3\nj\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.replace(g, raw=True, pars='auto')
        self.assertEqual('( # 3\nj\n# 4\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('( # 3\na + b\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars=False)
        self.assertEqual('i * ( # 1\n( # 3\na + b\n# 4\n)\n# 2\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('( # 3\na + b\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars=True)
        self.assertEqual('i * ( # 3\na + b\n# 4\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('( # 3\na + b\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars='auto')
        self.assertEqual('i * ( # 3\na + b\n# 4\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('a + b').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars=False)
        self.assertEqual('i * ( # 1\na + b\n# 2\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('a + b').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars=True)
        self.assertEqual('i * a + b', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('a + b').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars='auto')
        self.assertEqual('i * a + b', f.src)

        # put AST

        f = parse('( # 1\ni\n# 2\n)').f
        a = Yield(value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars=False)
        self.assertEqual('( # 1\n(yield 1)\n# 2\n)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = Yield(value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars=True)
        self.assertEqual('(yield 1)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = Yield(value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars='auto')
        self.assertEqual('(yield 1)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = NamedExpr(target=Name(id='i', ctx=Store()), value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars=False)
        self.assertEqual('( # 1\n(i := 1)\n# 2\n)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = NamedExpr(target=Name(id='i', ctx=Store()), value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars=True)
        self.assertEqual('(i := 1)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = NamedExpr(target=Name(id='i', ctx=Store()), value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars='auto')
        self.assertEqual('(i := 1)', f.src)

    def test_replace_existing_one(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_ONE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.replace(None if src == '**DEL**' else src, raw=False, **options) or f.root

                tdst = f.root.src

                f.root.verify(raise_=True)

                self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst.rstrip(), put_src)  # rstrip() because at current time stmt operations can add trailing newline

            except Exception:
                print(i, attr, options, src)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_ret)
                print('...')
                print(put_src)

                raise

    def test_replace_existing_one_raw(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_ONE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.replace(None if src == '**DEL**' else src, raw=True, **options) or f.root

                tdst = f.root.src

                f.root.verify(raise_=True)

                self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst, put_src)

            except Exception:
                print(i, attr, options, src)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_ret)
                print('...')
                print(put_src)

                raise

    def test_put_existing_one(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_ONE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                # g = f.replace(None if src == '**DEL**' else src, **options) or f.root
                f.parent.put(None if src == '**DEL**' else src, f.pfield.idx, field=f.pfield.name, raw=False, **options)

                tdst = f.root.src

                f.root.verify(raise_=True)

                # self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst.rstrip(), put_src)  # rstrip() because at current time stmt operations can add trailing newline

            except Exception:
                print(i, attr, options, src)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_ret)
                print('...')
                print(put_src)

                raise

    def test_put_existing_one_raw(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_ONE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                # g = f.replace(None if src == '**DEL**' else src, **options) or f.root
                f.parent.put(None if src == '**DEL**' else src, f.pfield.idx, field=f.pfield.name, raw=True, **options)

                tdst = f.root.src

                f.root.verify(raise_=True)

                # self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst, put_src)

            except Exception:
                print(i, attr, options, src)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_ret)
                print('...')
                print(put_src)

                raise

    def test_put_slice_raw(self):
        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.put_slice('for x in y', 1, 2, raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d for x in y for a in b]')
        f = g
        # g = f.put_slice(None, 1, 2, raw=True)
        # self.assertIsNot(g, f)
        # self.assertEqual(g.src, '[a for c in d  for a in b]')
        # f = g
        # g = f.put_slice(None, 1, 2, raw=True)
        # self.assertIsNot(g, f)
        # self.assertEqual(g.src, '[a for c in d  ]')
        # f = g

        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('{a, x, y, c}', parse('{a, b, c}').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice('x: x, y: y', 1, 2, raw=True).root.src)

        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice('(x, y)', 1, 2, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice('[x, y]', 1, 2, raw=True).root.src)
        self.assertEqual('{a, {x, y}, c}', parse('{a, b, c}').body[0].value.f.put_slice('{x, y}', 1, 2, raw=True).root.src)  # invalid set but valid syntax
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, '{x: x, y: y}', 1, 2, raw=True)

        # strip delimiters if present
        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_.parse('x, y'), 1, 2, raw=True).root.src)
        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_.parse('(x, y)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x, y]'), 1, 2, raw=True).root.src)
        self.assertEqual('{a, x, y, c}', parse('{a, b, c}').body[0].value.f.put_slice(ast_.parse('{x, y}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_.parse('{x: x, y: y}'), 1, 2, raw=True).root.src)

        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(FST.fromsrc('x, y'), 1, 2, raw=True).root.src)
        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(FST.fromsrc('(x, y)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x, y]'), 1, 2, raw=True).root.src)
        self.assertEqual('{a, x, y, c}', parse('{a, b, c}').body[0].value.f.put_slice(FST.fromsrc('{x, y}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(FST.fromsrc('{x: x, y: y}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('x,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('(x,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('{x,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(FST.fromsrc('{x: x,}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('x, y,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('(x, y,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x, y,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('{x, y,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(FST.fromsrc('{x: x, y: y,}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('x,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('(x,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('{x,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_.parse('{x: x,}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('x, y,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('(x, y,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x, y,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('{x, y,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_.parse('{x: x, y: y,}'), 1, 2, raw=True).root.src)

        # as one so dont strip delimiters or add to unparenthesized tuple
        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_.parse('x, y'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_.parse('(x, y)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x, y]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('{a, {x, y}, c}', parse('{a, b, c}').body[0].value.f.put_slice(ast_.parse('{x, y}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_.parse('{x: x, y: y}'), 1, 2, one=True, raw=True)

        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(FST.fromsrc('x, y'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(FST.fromsrc('(x, y)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x, y]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('{a, {x, y}, c}', parse('{a, b, c}').body[0].value.f.put_slice(FST.fromsrc('{x, y}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, FST.fromsrc('{x: x, y: y}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('x,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('(x,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x,], c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x,}, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('{x,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, FST.fromsrc('{x: x,}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x, y,), c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('x, y,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x, y,), c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('(x, y,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y,], c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x, y,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x, y,}, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('{x, y,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, FST.fromsrc('{x: x, y: y,}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('x,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('(x,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x}, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('{x,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_.parse('{x: x,}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x, y), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('x, y,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x, y), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('(x, y,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x, y,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x, y}, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('{x, y,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_.parse('{x: x, y: y,}'), 1, 2, one=True, raw=True)

    def test_put_special_fields(self):
        old_options = FST.set_option(pars=False, raw=True)

        self.assertEqual('{a: b, **c, e: f}', parse('{a: b, **d, e: f}').body[0].value.f.put('c', 1, field='values').root.src)
        self.assertEqual('{a: b, c: d, e: f}', parse('{a: b, **d, e: f}').body[0].value.f.put('c', 1, field='keys').root.src)
        self.assertEqual('{a: b, **g, e: f}', parse('{a: b, c: d, e: f}').body[0].value.f.put('**g', 1).root.src)
        self.assertEqual('{a: b, c: d, e: f}', parse('{a: b, **g, e: f}').body[0].value.f.put('c: d', 1).root.src)
        self.assertEqual('{a: b, g: d, e: f}', parse('{a: b, c: d, e: f}').body[0].value.f.put('g', 1, field='keys').root.src)
        self.assertEqual('{a: b, c: g, e: f}', parse('{a: b, c: d, e: f}').body[0].value.f.put('g', 1, field='values').root.src)
        self.assertEqual('{a: b, **g, e: f}', parse('{a: b, c: d, e: f}').body[0].value.f.put_slice('**g', 1, 2).root.src)

        self.assertEqual('match a:\n case {4: d, 2: b, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put('4: d', 0).root.src)
        self.assertEqual('match a:\n case {4: a, 2: b, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put('4', 0, field='keys').root.src)
        self.assertEqual('match a:\n case {1: d, 2: b, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put('d', 0, field='patterns').root.src)
        self.assertEqual('match a:\n case {1: a, 2: b, **d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put('**d', 2).root.src)
        self.assertEqual('match a:\n case {4: d, 2: b, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 0, 1).root.src)
        self.assertEqual('match a:\n case {1: a, 4: d, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 1, 2).root.src)
        self.assertEqual('match a:\n case {1: a, 2: b, 4: d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 2, 3).root.src)
        self.assertEqual('match a:\n case {1: a, 4: d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 1, 3).root.src)
        self.assertEqual('match a:\n case {4: d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 0, 3).root.src)
        self.assertEqual('match a:\n case {4: d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d').root.src)

        self.assertEqual('z < b < c', parse('a < b < c').body[0].value.f.put('z', 0).root.src)
        self.assertEqual('a < z < c', parse('a < b < c').body[0].value.f.put('z', 1).root.src)
        self.assertEqual('a < b < z', parse('a < b < c').body[0].value.f.put('z', 2).root.src)
        self.assertEqual('a < b < z', parse('a < b < c').body[0].value.f.put('z', -1).root.src)
        self.assertEqual('a < z < c', parse('a < b < c').body[0].value.f.put('z', -2).root.src)
        self.assertEqual('z < b < c', parse('a < b < c').body[0].value.f.put('z', -3).root.src)
        self.assertRaises(IndexError, parse('a < b < c').body[0].value.f.put, 'z', 4)
        self.assertRaises(IndexError, parse('a < b < c').body[0].value.f.put, 'z', -4)
        self.assertEqual('z < b < c', parse('a < b < c').body[0].value.f.put('z', field='left').root.src)
        self.assertEqual('a < b < z', parse('a < b < c').body[0].value.f.put('z', 1, field='comparators').root.src)
        self.assertEqual('a < b > c', parse('a < b < c').body[0].value.f.put('>', 1, field='ops').root.src)
        self.assertRaises(ValueError, parse('a < b < c').body[0].value.f.put_slice, 'z', 0, 0)
        self.assertEqual('z < b < c', parse('a < b < c').body[0].value.f.put_slice('z', 0, 1).root.src)
        self.assertEqual('z < c', parse('a < b < c').body[0].value.f.put_slice('z', 0, 2).root.src)
        self.assertEqual('z', parse('a < b < c').body[0].value.f.put_slice('z', 0, 3).root.src)
        self.assertRaises(ValueError, parse('a < b < c').body[0].value.f.put_slice, 'z', 1, 1)
        self.assertEqual('a < z < c', parse('a < b < c').body[0].value.f.put_slice('z', 1, 2).root.src)
        self.assertEqual('a < z', parse('a < b < c').body[0].value.f.put_slice('z', 1, 3).root.src)
        self.assertRaises(ValueError, parse('a < b < c').body[0].value.f.put_slice, 'z', 2, 2)
        self.assertEqual('a < b < z', parse('a < b < c').body[0].value.f.put_slice('z', 2, 3).root.src)
        self.assertRaises(ValueError, parse('a < b < c').body[0].value.f.put_slice, 'z', 3, 3)

        self.assertEqual('[i for i in j if a if z if c]', parse('[i for i in j if a if b if c]').body[0].value.generators[0].f.put('z', 1, field='ifs').root.src)
        self.assertEqual('[i for i in j if a if z if c]', parse('[i for i in j if a if b if c]').body[0].value.generators[0].f.put_slice('if z', 1, 2, field='ifs').root.src)
        self.assertEqual('[i for i in j if a if z]', parse('[i for i in j if a if b if c]').body[0].value.generators[0].f.put_slice('if z', 1, 3, field='ifs').root.src)
        self.assertEqual('[i for i in j if z]', parse('[i for i in j if a if b if c]').body[0].value.generators[0].f.put_slice('if z', field='ifs').root.src)
        self.assertEqual('[i for i in j if a if (z) if c]', parse('[i for i in j if a if (b) if c]').body[0].value.generators[0].f.put('z', 1, field='ifs').root.src)
        self.assertEqual('[i for i in j if a if z if c]', parse('[i for i in j if a if (b) if c]').body[0].value.generators[0].f.put_slice('if z', 1, 2, field='ifs').root.src)
        self.assertEqual('[i for i in j if a if z]', parse('[i for i in j if a if (b) if (c)]').body[0].value.generators[0].f.put_slice('if z', 1, 3, field='ifs').root.src)

        self.assertEqual('@a\n@z\n@c\nclass cls: pass', parse('@a\n@b\n@c\nclass cls: pass').body[0].f.put('z', 1, field='decorator_list').root.src)
        self.assertEqual('@a\n@z\n@c\nclass cls: pass', parse('@a\n@b\n@c\nclass cls: pass').body[0].f.put_slice('@z', 1, 2, field='decorator_list').root.src)
        self.assertEqual('@a\n@z\nclass cls: pass', parse('@a\n@b\n@c\nclass cls: pass').body[0].f.put_slice('@z', 1, 3, field='decorator_list').root.src)
        self.assertEqual('@z\nclass cls: pass', parse('@a\n@b\n@c\nclass cls: pass').body[0].f.put_slice('@z', field='decorator_list').root.src)
        self.assertEqual('@a\n@(z)\n@c\nclass cls: pass', parse('@a\n@(b)\n@c\nclass cls: pass').body[0].f.put('z', 1, field='decorator_list').root.src)
        self.assertEqual('@a\n@z\n@c\nclass cls: pass', parse('@a\n@(b)\n@c\nclass cls: pass').body[0].f.put_slice('@z', 1, 2, field='decorator_list').root.src)
        self.assertEqual('@a\n@z\nclass cls: pass', parse('@a\n@(b)\n@(c)\nclass cls: pass').body[0].f.put_slice('@z', 1, 3, field='decorator_list').root.src)

        self.assertEqual('{a: b, e: f}', FST('{a: b, c: d, e: f}', 'exec').body[0].value.put(None, 1, raw='auto').root.src)
        self.assertEqual('{a: b, e: f}', FST('{a: b, c: d, e: f}', 'exec').body[0].value.put(None, 1, raw=False).root.src)

        FST.set_option(**old_options)

    def test_get_slice_seq_copy(self):
        for src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump in GET_SLICE_SEQ_DATA:
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                s     = f.get_slice(start, stop, cut=False, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                sdump = s.dump(out=list, compact=True)

                self.assertEqual(tsrc, src.strip())
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_get_slice_seq_cut(self):
        for i, (src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump) in enumerate(GET_SLICE_SEQ_DATA):
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                s     = f.get_slice(start, stop, cut=True, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                t.f._touchall()
                tdump = t.f.dump(out=list, compact=True)
                sdump = s.dump(out=list, compact=True)

                self.assertEqual(tsrc, src_cut.strip())
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(tdump, src_dump.strip().split('\n'))
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print(i, elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(src_cut)
                print('...')
                print(slice_copy)

                print('='*80)
                print('\n'.join(tdump))
                print('-'*80)
                print('\n'.join(src_dump.strip().split('\n')))
                print('.'*80)

                raise

    def test_get_slice_stmt_copy(self):
        for name in ('GET_SLICE_STMT_DATA', 'GET_SLICE_STMT_NOVERIFY_DATA'):
            verify = 'NOVERIFY' not in name

            for src, elt, start, stop, field, options, _, slice_cut, _, slice_dump in globals()[name]:
                t = parse(src)
                f = (eval(f't.{elt}', {'t': t}) if elt else t).f

                try:
                    s     = f.get_slice(start, stop, field, cut=False, **options)
                    tsrc  = t.f.src
                    ssrc  = s.src
                    sdump = s.dump(out=list, compact=True)

                    if verify:
                        t.f.verify(raise_=True)
                        s.verify(raise_=True)

                    self.assertEqual(tsrc, src)
                    self.assertEqual(ssrc, slice_cut)
                    self.assertEqual(sdump, slice_dump.strip().split('\n'))

                except Exception:
                    print(elt, start, stop)
                    print('---')
                    print(src)
                    print('...')
                    print(slice_cut)

                    raise

    def test_get_slice_stmt_cut(self):
        for name in ('GET_SLICE_STMT_DATA', 'GET_SLICE_STMT_NOVERIFY_DATA'):
            verify = 'NOVERIFY' not in name

            for src, elt, start, stop, field, options, src_cut, slice_cut, src_dump, slice_dump in globals()[name]:
                t = parse(src)
                f = (eval(f't.{elt}', {'t': t}) if elt else t).f

                try:
                    s     = f.get_slice(start, stop, field, cut=True, **options)
                    tsrc  = t.f.src
                    ssrc  = s.src
                    tdump = t.f.dump(out=list, compact=True)
                    sdump = s.dump(out=list, compact=True)

                    if verify:
                        t.f.verify(raise_=True)
                        s.verify(raise_=True)

                    self.assertEqual(tsrc, src_cut)
                    self.assertEqual(ssrc, slice_cut)
                    self.assertEqual(tdump, src_dump.strip().split('\n'))
                    self.assertEqual(sdump, slice_dump.strip().split('\n'))

                except Exception:
                    print(elt, start, stop)
                    print('---')
                    print(src)
                    print('...')
                    print(src_cut)
                    print('...')
                    print(slice_cut)

                    raise

    def test_get_one_special(self):
        f = FST('a = b', 'exec').body[0]
        self.assertRaises(ValueError, f.targets[0].get, 'ctx')  # cannot copy node which does not have a location
        self.assertRaises(ValueError, f.value.get, 'ctx')

        f = FST('{a: b}', 'exec').body[0].value
        self.assertRaises(ValueError, f.get, 0)  # cannot get single element from combined field of Dict

        f = FST('match a:\n case {1: b}: pass', 'exec').body[0].cases[0].pattern
        self.assertRaises(ValueError, f.get, 0)  # cannot get single element from combined field of MatchMapping

        f = FST('a < b < c', 'exec').body[0].value
        self.assertEqual('a', f.get(0).src)
        self.assertEqual('b', f.get(1).src)
        self.assertEqual('c', f.get(2).src)
        self.assertEqual('a', f.get('left').src)
        self.assertEqual('b', f.get(0, 'comparators').src)
        self.assertEqual('c', f.get(1, 'comparators').src)

        f = FST('def func() -> int: pass', 'exec').body[0]  # identifier
        self.assertEqual('func', f.get('name'))
        self.assertRaises(ValueError, f.get, 'name', cut=True)  # cannot delete FunctionDef.name
        self.assertEqual('int', f.get('returns', cut=True).src)
        self.assertEqual('def func(): pass', f.src)

        f = FST('from .a import *', 'exec').body[0]
        self.assertEqual('a', f.get('module', cut=True))
        self.assertEqual('from . import *', f.src)

        f = FST('from a import *', 'exec').body[0]
        self.assertRaises(ValueError, f.get, 'module', cut=True)

        f = FST('import a as b', 'exec').body[0]
        self.assertEqual('b', f.names[0].get('asname', cut=True))
        self.assertEqual('import a', f.src)

        f = FST('match a:\n case {**a}: pass', 'exec').body[0]
        self.assertEqual('a', f.cases[0].pattern.get('rest', cut=True))
        self.assertEqual('match a:\n case {}: pass', f.src)

        # other

        f = FST('a and b').get('op')
        self.assertIsInstance(f.a, And)
        self.assertEqual('and', f.src)

        f = FST('a or b').get('op')
        self.assertIsInstance(f.a, Or)
        self.assertEqual('or', f.src)

        f = FST('a or b').get('op')
        self.assertIsInstance(f.a, Or)
        self.assertEqual('or', f.src)

        self.assertRaises(ValueError, FST('{a: b}').get, 0)
        self.assertRaises(ValueError, FST('match a:\n case {1: b}: pass').cases[0].pattern.get, 0)

        f = FST('a < b < c')
        self.assertEqual('a', f.get(0).src)
        self.assertEqual('b', f.get(1).src)
        self.assertEqual('c', f.get(2).src)

        f = FST('def f(): pass').get('args')
        self.assertIsInstance(f.a, arguments)
        self.assertEqual('', f.src)

        f = FST('lambda: None').get('args')
        self.assertIsInstance(f.a, arguments)
        self.assertEqual('', f.src)

        # identifier

        self.assertEqual('ident', FST('def ident(): pass').get('name'))
        self.assertEqual('ident', FST('async def ident(): pass').get('name'))
        self.assertEqual('ident', FST('class ident: pass').get('name'))
        self.assertEqual('ident', FST('from ident import *').get('module'))
        self.assertEqual('ident', FST('global ident').get(0, 'names'))
        self.assertEqual('ident', FST('nonlocal ident').get(0, 'names'))
        self.assertEqual('ident', FST('obj.ident').get('attr'))
        self.assertEqual('ident', FST('ident').get('id'))
        self.assertEqual('ident', FST('except Exception as ident: pass').get('name'))
        self.assertEqual('ident', FST('def f(ident): pass').args.args[0].get('arg'))
        self.assertEqual('ident', FST('call(ident=1)').keywords[0].get('arg'))
        self.assertEqual('ident', FST('import ident as b').names[0].get('name'))
        self.assertEqual('ident', FST('import a as ident').names[0].get('asname'))
        self.assertEqual('ident', FST('match a:\n case {**ident}: pass').cases[0].pattern.get('rest'))
        self.assertEqual('ident', FST('match a:\n case cls(ident=1): pass').cases[0].pattern.get(0, 'kwd_attrs'))
        self.assertEqual('ident', FST('match a:\n case (*ident,): pass').cases[0].pattern.patterns[0].get('name'))
        self.assertEqual('ident', FST('match a:\n case 1 as ident: pass').cases[0].pattern.get('name'))

        if _PY_VERSION >= (3, 12):
            self.assertEqual('ident', FST('type t[ident] = ...').type_params[0].get('name'))
            self.assertEqual('ident', FST('type t[*ident] = ...').type_params[0].get('name'))
            self.assertEqual('ident', FST('type t[**ident] = ...').type_params[0].get('name'))

        # get constant

        for v in (True, False, None):
            f = FST(f'match a:\n case {v}: pass').cases[0].pattern
            g = f.get('value')
            self.assertIsInstance(g.a, Constant)
            self.assertEqual(str(v), g.src)
            self.assertIs(v, g.value)

        for s in ('...', '2', '2.0', '2j', '"str"', 'b"bytes"', 'True', 'False', 'None'):
            f = FST(s)
            self.assertIsInstance(f.a, Constant)

            g = f.get('value')
            self.assertIsInstance(g.a, Constant)
            self.assertEqual(g.loc, f.loc)
            compare_asts(g.a, f.a, locs=True, raise_=True)

        # FormattedValue/Interpolation conversion and format_spec, JoinedStr/TemplateStr values

        if _PY_VERSION >= (3, 12):
            self.assertIsNone(None, FST('f"{a}"').values[0].get('conversion'))
            self.assertEqual("'a'", FST('f"{a!a}"').values[0].get('conversion').src)
            self.assertEqual("'r'", FST('f"{a!r}"').values[0].get('conversion').src)
            self.assertEqual("'s'", FST('f"{a!s}"').values[0].get('conversion').src)
            self.assertEqual("'r'", FST('f"{a=}"').values[1].get('conversion').src)

            f = FST('if 1:\n    f"{a!r\n : {\'0.5f<12\'} }"').body[0].value.values[0].get('format_spec')
            self.assertEqual("f' {'0.5f<12'} '", f.src)
            f.verify()

            f = FST('f"{a!r\n : {\'0.5f<12\'} }"').values[0].get('format_spec')
            self.assertEqual("f' {'0.5f<12'} '", f.src)
            f.verify()

            f = FST('f"{a!r\n : 0.5f<12 }"').values[0].get('format_spec')
            self.assertEqual("f' 0.5f<12 '", f.src)
            f.verify()

            f = FST('f"{a!r : 0.5f<12 }"').values[0].get('format_spec')
            self.assertEqual("f' 0.5f<12 '", f.src)
            f.verify()

            f = FST('f"{a!r:0.5f<12}"').values[0].get('format_spec')
            self.assertEqual("f'0.5f<12'", f.src)
            f.verify()

            f = FST(r'''
f'\
{a:0.5f<12}a' "b" \
 "c" \
f"{d : {"0.5f<12"} }"
                '''.strip())
            g = f.get(1, 'values')
            self.assertEqual("'abc'", g.src)
            g.verify()
            g = f.get(0, 'values')
            self.assertEqual("f'{a:0.5f<12}'", g.src)
            g.verify()
            g = f.get(2, 'values')
            self.assertEqual("""f'{d : {"0.5f<12"} }'""", g.src)
            g.verify()

            f = FST(r'''
if 1:
    f'\
    {a:0.5f<12}a' "b" \
     "c" \
    f"{d : {"0.5f<12"} }"
                '''.strip())
            g = f.body[0].value.get(2, 'values')
            self.assertEqual("'abc'", g.src)
            g.verify()
            g = f.body[0].value.get(1, 'values')
            self.assertEqual("f'{a:0.5f<12}'", g.src)
            g.verify()
            g = f.body[0].value.get(3, 'values')
            self.assertEqual("""f'{d : {"0.5f<12"} }'""", g.src)
            g.verify()

        if _PY_VERSION >= (3, 14):
            self.assertIsNone(None, FST('t"{a}"').values[0].get('conversion'))
            self.assertEqual("'a'", FST('t"{a!a}"').values[0].get('conversion').src)
            self.assertEqual("'r'", FST('t"{a!r}"').values[0].get('conversion').src)
            self.assertEqual("'s'", FST('t"{a!s}"').values[0].get('conversion').src)
            self.assertEqual("'r'", FST('t"{a=}"').values[1].get('conversion').src)

            f = FST('if 1:\n    t"{a!r\n : {\'0.5f<12\'} }"').body[0].value.values[0].get('format_spec')
            self.assertEqual("f' {'0.5f<12'} '", f.src)
            f.verify()

            f = FST('t"{a!r\n : {\'0.5f<12\'} }"').values[0].get('format_spec')
            self.assertEqual("f' {'0.5f<12'} '", f.src)
            f.verify()

            f = FST('t"{a!r\n : 0.5f<12 }"').values[0].get('format_spec')
            self.assertEqual("f' 0.5f<12 '", f.src)
            f.verify()

            f = FST('t"{a!r : 0.5f<12 }"').values[0].get('format_spec')
            self.assertEqual("f' 0.5f<12 '", f.src)
            f.verify()

            f = FST('t"{a!r:0.5f<12}"').values[0].get('format_spec')
            self.assertEqual("f'0.5f<12'", f.src)
            f.verify()

            f = FST(r'''
t'\
{a:0.5f<12}a' "b" \
 "c" \
f"{d : {"0.5f<12"} }"
                '''.strip())
            g = f.get(1, 'values')
            self.assertEqual("'abc'", g.src)
            g.verify()
            g = f.get(0, 'values')
            self.assertEqual("t'{a:0.5f<12}'", g.src)
            g.verify()
            g = f.get(2, 'values')
            self.assertEqual("""f'{d : {"0.5f<12"} }'""", g.src)
            g.verify()

            f = FST(r'''
if 1:
    t'\
    {a:0.5f<12}a' "b" \
     "c" \
    f"{d : {"0.5f<12"} }"
                '''.strip())
            g = f.body[0].value.get(2, 'values')
            self.assertEqual("'abc'", g.src)
            g.verify()
            g = f.body[0].value.get(1, 'values')
            self.assertEqual("t'{a:0.5f<12}'", g.src)
            g.verify()
            g = f.body[0].value.get(3, 'values')
            self.assertEqual("""f'{d : {"0.5f<12"} }'""", g.src)
            g.verify()

            f = FST("f'a{b:<3}'")
            self.assertEqual("'a'", (g := f.get(0)).src)
            g.verify()

            f = FST('f"{a}" \'b\' "c" \'d\'')
            self.assertEqual("'bcd'", (g := f.get(1)).src)
            g.verify()

            f = FST('f"{a}" \'b\' f"{c}"')
            self.assertEqual("'b'", (g := f.get(1)).src)
            g.verify()

            f = FST('f"abc"')
            self.assertEqual("'abc'", (g := f.get(0)).src)
            g.verify()

    def test_put_slice_seq_del(self):
        for i, (src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump) in enumerate(GET_SLICE_SEQ_DATA):
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                f.put_slice(None, start, stop, **options)

                tdst  = t.f.src
                tdump = t.f.dump(out=list, compact=True)

                self.assertEqual(tdst, src_cut.strip())
                self.assertEqual(tdump, src_dump.strip().split('\n'))

            except Exception:
                print(i, elt, start, stop)
                print('---')
                print(src)

                raise

    def test_put_slice_seq(self):
        for i, (dst, elt, start, stop, src, put_src, put_dump) in enumerate(PUT_SLICE_SEQ_DATA):
            t = parse(dst)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                f.put_slice(None if src == '**DEL**' else src, start, stop)

                tdst  = t.f.src
                tdump = t.f.dump(out=list, compact=True)

                self.assertEqual(tdst, put_src.strip())
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, elt, start, stop)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_slice_stmt_del(self):
        for name in ('GET_SLICE_STMT_DATA', 'GET_SLICE_STMT_NOVERIFY_DATA'):
            verify = 'NOVERIFY' not in name

            for i, (src, elt, start, stop, field, options, src_cut, _, src_dump, _) in enumerate(globals()[name]):
                t = parse(src)
                f = (eval(f't.{elt}', {'t': t}) if elt else t).f

                try:
                    f.put_slice(None, start, stop, field, **options)

                    tsrc  = t.f.src
                    tdump = t.f.dump(out=list, compact=True)

                    if verify:
                        t.f.verify(raise_=True)

                    self.assertEqual(tsrc, src_cut)
                    self.assertEqual(tdump, src_dump.strip().split('\n'))

                except Exception:
                    print(i, name, elt, start, stop)
                    print('---')
                    print(src)
                    print('...')
                    print(src_cut)

                    raise

    def test_put_slice_stmt(self):
        for i, (dst, stmt, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_STMT_DATA):
            t = parse(dst)
            f = (eval(f't.{stmt}', {'t': t}) if stmt else t).f

            try:
                f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

                tdst  = t.f.src
                tdump = t.f.dump(out=list, compact=True)

                t.f.verify(raise_=True)

                self.assertEqual(tdst, put_src)
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, stmt, start, stop, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_slice(self):
        for i, (dst, attr, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

                tdst  = t.f.src
                tdump = t.f.dump(out=list, compact=True)

                t.f.verify(raise_=True)

                self.assertEqual(tdst, put_src)
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, src, start, stop, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_slice_special(self):
        if _PY_VERSION >= (3, 14):  # make sure parent Interpolation.str gets modified
            f = FST('t"{(1, 2)}"', 'exec').body[0].value.copy()
            f.values[0].value.put_slice("()")
            self.assertEqual('()', f.values[0].value.src)
            self.assertEqual('()', f.values[0].str)

            f = FST('t"{(1, 2)}"', 'exec').body[0].value.copy()
            f.values[0].value.put("()", None, None, one=False)
            self.assertEqual('()', f.values[0].value.src)
            self.assertEqual('()', f.values[0].str)

    def test_put_slice_empty_set(self):
        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, empty_set=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set=True).src)

        self.assertRaises(ValueError, FST('[1, 2]').put_slice, 'set()', raw=False, empty_set='seq')
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set='seq').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set='seq').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set='seq').src)

        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, empty_set='call').src)
        self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set='call').src)
        self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set='call').src)
        self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set='call').src)

        self.assertRaises(ValueError, FST('[1, 2]').put_slice, 'set()', raw=False, empty_set=False)
        self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set=False).src)
        self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set=False).src)
        self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set=False).src)

    def test_put_one(self):
        ver = _PY_VERSION[1]
        for i, (dst, attr, idx, field, options, src, put_src, put_dump) in enumerate(PUT_ONE_DATA):
            if options.get('_ver', 0) > ver:
                continue

            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                if options.get('raw') is True:
                    continue

                options = {**options, 'raw': False}

                try:
                    f.put(None if src == '**DEL**' else src, idx, field=field, **options)

                except Exception as exc:
                    if not put_dump.strip() and put_src.startswith('**') and put_src.endswith('**'):
                        tdst  = '**SyntaxError**' if isinstance(exc, SyntaxError) else f'**{exc!r}**'
                        tdump = ['']

                    else:
                        raise

                else:
                    tdst  = f.root.src
                    tdump = f.root.dump(out=list, compact=True)

                    if options.get('_verify', True):
                        f.root.verify(raise_=True)

                self.assertEqual(tdst, put_src)

                if (vd := options.get('_verdump')) and _PY_VERSION < (3, vd):
                    continue

                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, attr, idx, field, src, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_one_raw(self):
        ver = _PY_VERSION[1]
        for i, (dst, attr, idx, field, options, src, put_src, put_dump) in enumerate(PUT_ONE_DATA):
            if options.get('_ver', 0) > ver:
                continue

            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                if options.get('raw') is False:
                    continue

                options = {**options, 'raw': True}

                try:
                    f.put(None if src == '**DEL**' else src, idx, field=field, **options)

                except Exception as exc:
                    if not put_dump.strip() and put_src.startswith('**') and put_src.endswith('**'):
                        continue  # assume raw errors in line with non-raw, just different actual error
                    else:
                        raise

                else:
                    tdst  = f.root.src
                    tdump = f.root.dump(out=list, compact=True)

                    if options.get('_verify', True):
                        f.root.verify(raise_=True)

                self.assertEqual(tdst.rstrip(), put_src.rstrip())

                if (vd := options.get('_verdump')) and _PY_VERSION < (3, vd):
                    continue

                # self.assertEqual(tdump, put_dump.strip().split('\n'))  # don't compare this because of the trailing newline difference

            except Exception:
                print(i, attr, idx, field, src, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_one_special(self):
        f = parse('i', mode='eval').f
        self.assertIsInstance(f.a.body, expr)
        f.put('j', raw=False)
        self.assertEqual('j', f.src)
        self.assertRaises(NodeError, f.put, 'k = 1', raw=False)
        self.assertRaises(IndexError, f.put, 'k', 1, raw=False)

        g = parse('yield 1').body[0].value.f.copy(fix=False)
        self.assertEqual('yield 1', g.src)
        f.put(g, raw=False)
        self.assertEqual('(yield 1)', f.src)

        f.put('yield from a', raw=False)
        self.assertEqual('(yield from a)', f.src)

        f.put('await x', raw=False)
        self.assertEqual('await x', f.src)

        g = parse('l = 2').body[0].f.copy()
        self.assertEqual('l = 2', g.src)
        self.assertRaises(NodeError, f.put, g, raw=False)

        f.put('m', raw=False)
        self.assertEqual('m', f.src)

        f = parse('[1, 2, 3, 4]').body[0].value.f
        self.assertRaises(NodeError, f.put, '5', 1, raw=False, to=f.elts[2])

        f = parse('[1, 2, 3, 4]').body[0].value.f
        g = f.put('5', 1, raw='auto', to=f.elts[2])
        self.assertEqual('[1, 5, 4]', g.src)

        # make sure put doesn't eat arguments pars

        f = parse('f(i for i in j)').body[0].value.f
        f.put('a', 0, 'args', pars=False, raw=False)
        self.assertEqual('f(a)', f.src)

        f = parse('f((i for i in j))').body[0].value.f
        f.put('a', 0, 'args', pars=False, raw=False)
        self.assertEqual('f(a)', f.src)

        f = parse('f(((i for i in j)))').body[0].value.f
        f.put('a', 0, 'args', pars=False, raw=False)
        self.assertEqual('f((a))', f.src)

        # ops

        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put('>>=', field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, 'and', field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, '*', field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, '~', field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, '<', field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put('and', field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, '/', field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, '~', field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, 'and', field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put('>>', field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, '~', field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, 'and', field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, '*', field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put('+', field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(NodeError, parse('a is not b').body[0].value.f.put, '*=', 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a is not b').body[0].value.f.put, 'and', 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a is not b').body[0].value.f.put, '*', 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a is not b').body[0].value.f.put, '~', 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a is not b').body[0].value.f.put('>', 0, field='ops', raw=False).src)

        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(['>>='], field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, ['and'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, ['*'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, ['~'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, ['<'], field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put(['and'], field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, ['/'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, ['~'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, ['and'], field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put(['>>'], field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, ['~'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, ['and'], field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, ['*'], field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put(['+'], field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, ['*='], 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, ['and'], 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, ['*'], 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, ['~'], 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a < b').body[0].value.f.put(['>'], 0, field='ops', raw=False).src)

        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(RShift(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, And(), field='op', raw=False)
        self.assertEqual('a *= b', parse('a *= b').body[0].f.put(Mult(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, Invert(), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, Lt(), field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, Mult(), field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put(And(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, Div(), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, Invert(), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, Lt(), field='op', raw=False)

        self.assertEqual('a * b', parse('a + b').body[0].value.f.put(Mult(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, And(), field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put(RShift(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, Invert(), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, Lt(), field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, Mult(), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, And(), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, Sub(), field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put(UAdd(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, Lt(), field='op', raw=False)

        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, Mult(), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, And(), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, Sub(), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, UAdd(), 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a < b').body[0].value.f.put(Gt(), 0, field='ops', raw=False).src)

        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(FST(RShift(), ['>>=']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(And(), ['and']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(Add(), ['+']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(Invert(), ['~']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(Lt(), ['~']), field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Mult(), ['*']), field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put(FST(And(), ['and']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Div(), ['/']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Invert(), ['~']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Lt(), ['~']), field='op', raw=False)

        self.assertEqual('a * b', parse('a + b').body[0].value.f.put(FST(Mult(), ['*']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(And(), ['and']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(RShift(), ['>>=']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(Invert(), ['~']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(Lt(), ['~']), field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Mult(), ['*']), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(And(), ['and']), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Sub(), ['-=']), field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put(FST(UAdd(), ['+']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Lt(), ['-=']), field='op', raw=False)

        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(Mult(), ['*']), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(And(), ['and']), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(Sub(), ['-=']), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(UAdd(), ['-=']), 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a < b').body[0].value.f.put(FST(Gt(), ['>']), 0, field='ops', raw=False).src)

        # make sure we can't put TO invalid locations

        f = parse('[1, 2, 3]').body[0].value.f
        # self.assertEqual('[1, 4]', f.elts[1].replace('4', to=f.elts[2], raw=False).root.src)
        self.assertRaises(NodeError, f.elts[1].replace, '4', to=f.elts[2], raw=False)

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertRaises(ValueError, f.elts[1].replace, '4', to=f.elts[0], raw=False)

        f = parse('a = b').body[0].f
        self.assertRaises(NodeError, f.targets[0].replace, 'c', to=f.value, raw=False)

        f = parse('a = b').body[0].f
        self.assertRaises(ValueError, f.value.replace, 'c', to=f.targets[0], raw=False)

        # reject Slice putting to expr

        f = parse('a = b').body[0].f
        s = parse('s[a:b]').body[0].value.slice.f.copy()
        self.assertRaises(NodeError, f.put, s, field='value', raw=False)

        # slice in tuple

        f = parse('s[a:b, x:y:z]').body[0].value.f
        t = f.slice.copy()
        s0 = t.elts[0].copy()
        s1 = t.elts[1].copy()
        self.assertEqual('a:b, x:y:z', t.src)
        self.assertEqual('a:b', s0.src)
        self.assertEqual('x:y:z', s1.src)

        f.put(t, field='slice', raw=False)
        self.assertEqual('a:b, x:y:z', f.slice.src)
        f.slice.put(s1, 0, raw=False)
        self.assertEqual('x:y:z, x:y:z', f.slice.src)
        f.slice.put(s0, 1, raw=False)
        self.assertEqual('x:y:z, a:b', f.slice.src)

        # make sure we don't merge alnums on unparenthesize

        f = FST('[a for a in b if(a)if(a)]', 'exec')
        f.body[0].value.generators[0].put('a', 0, field='ifs')
        f.body[0].value.generators[0].put('a', 1, field='ifs')
        self.assertEqual('[a for a in b if a if a]', f.src)
        f.verify()

        # check that it sanitizes

        f = FST('a = b', 'exec')
        g = FST('c', 'exec').body[0].value.copy()
        g._put_src(' # line\n# post', 0, 1, 0, 1, False)
        g._put_src('# pre\n', 0, 0, 0, 0, False)
        f.body[0].put(g, 'value', pars=False)
        self.assertEqual('a = c', f.src)

        # don't parenthesize put of starred to tuple

        f = FST('a, *b = c', 'exec')
        g = f.body[0].targets[0].elts[1].copy()
        f.body[0].targets[0].put(g.a, 1, raw=False)
        self.assertEqual('a, *b = c', f.src)

        if _PY_VERSION >= (3, 12):
            # except vs. except*

            f = FST('try:\n    pass\nexcept Exception:\n    pass', 'exec').body[0].handlers[0].copy()

            g = FST('try:\n    pass\nexcept* ValueError:\n    pass', 'exec')
            g.body[0].put(f.copy().a, 0, field='handlers', raw=False)
            self.assertEqual('try:\n    pass\nexcept* Exception:\n    pass\n', g.src)

            g = FST('try:\n    pass\nexcept ValueError:\n    pass', 'exec')
            g.body[0].put(f.a, 0, field='handlers', raw=False)
            self.assertEqual('try:\n    pass\nexcept Exception:\n    pass\n', g.src)

			# except* can't delete type

            f = FST('''
try:
	raise ExceptionGroup("eg", [ValueError(42)])
except* (TypeError, ExceptionGroup):
	pass
            '''.strip(), 'exec')
            g = f.body[0].handlers[0]
            self.assertRaises(ValueError, g.put, None, 'type', raw=False)

            # *args: *starred annotation

            f = FST('def f(*args: *starred): pass', 'exec')
            g = f.body[0].args.vararg.copy()
            f.body[0].args.put(g.a, 'vararg', raw=False)
            self.assertEqual('def f(*args: *starred): pass', f.src)
            f.verify()

        # tuple slice in annotation

        f = FST('def f(x: a[b:c, d:e]): pass', 'exec')
        g = f.body[0].args.args[0].annotation.slice.elts[0].copy()
        f.body[0].args.args[0].annotation.slice.put(g.src, 0, 'elts', raw=False)
        self.assertEqual('def f(x: a[b:c, d:e]): pass', f.src)
        f.verify()

        # naked MatchStar and other star/sequence

        f = FST('match x: \n case [*_]: pass', 'exec')
        g = f.body[0].cases[0].pattern.patterns[0].copy()
        f.body[0].cases[0].pattern.put(g.a, 0, 'patterns', raw=False)
        self.assertEqual('match x: \n case [*_]: pass', f.src)
        f.verify()

        f = FST('match x: \n case 1: pass', 'exec')
        f.body[0].cases[0].put('*x, 1,', 'pattern', raw=False)
        self.assertEqual('match x: \n case *x, 1,: pass', f.src)
        f.verify()

        f = FST('match x: \n case 1: pass', 'exec')
        f.body[0].cases[0].put('1, *x,', 'pattern', raw=False)
        self.assertEqual('match x: \n case 1, *x,: pass', f.src)
        f.verify()

        # special Call.args but not otherwise

        f = FST('call(a)', 'exec')
        f.body[0].value.put('*[] or []', 0, 'args', raw=False)
        self.assertEqual('call(*[] or [])', f.src)
        f.verify()

        f = FST('call(a)', 'exec')
        f.body[0].value.put('yield 1', 0, 'args', raw=False)
        self.assertEqual('call((yield 1))', f.src)
        f.verify()

        # MatchAs, ugh...

        f = FST('match a:\n case _ as unknown: pass', 'exec')
        g = f.body[0].cases[0].pattern.pattern.copy()
        f.body[0].cases[0].pattern.put(None, 'pattern', raw=False)
        self.assertEqual('match a:\n case unknown: pass', f.src)
        f.body[0].cases[0].pattern.put(g, 'pattern', raw=False)
        self.assertEqual('match a:\n case _ as unknown: pass', f.src)
        f.verify()

        # can't delete keyword.arg if non-keywords follow

        f = FST('call(a=b, *c)', 'exec').body[0].value.copy()
        self.assertRaises(ValueError, f.keywords[0].put, None, 'arg')

        f = FST('class c(a=b, *c): pass', 'exec').body[0].copy()
        self.assertRaises(ValueError, f.keywords[0].put, None, 'arg')

        # parenthesize value of deleted Dict key if it needs it

        f = FST('{a: lambda b: None}', 'exec')
        g = f.body[0].value.keys[0].copy()
        f.body[0].value.put(None, 0, 'keys')
        self.assertEqual('{**(lambda b: None)}', f.src)
        f.body[0].value.put(g.a, 0, 'keys')
        self.assertEqual('{a: (lambda b: None)}', f.src)
        f.verify()

        # lone vararg del trailing comma

        f = FST('lambda *args,: 0', 'exec').body[0].value.copy()
        g = f.args.vararg.copy()
        f.args.put(None, 'vararg')
        self.assertEqual('lambda: 0', f.src)
        f.args.put(g, 'vararg')
        self.assertEqual('lambda *args: 0', f.src)

        f = FST('def f(*args,): pass', 'exec').body[0].copy()
        g = f.args.vararg.copy()
        f.args.put(None, 'vararg')
        self.assertEqual('def f(): pass', f.src)
        f.args.put(g, 'vararg')
        self.assertEqual('def f(*args): pass', f.src)

        # lone parenthesized tuple in unparenthesized With.items left after delete of optional_vars needs grouping pars

        f = FST('with (a, b) as c: pass', 'exec').body[0].copy()
        f.items[0].put(None, 'optional_vars', raw=False)
        self.assertEqual('with ((a, b)): pass', f.src)
        f.verify()

        f = FST('with ((a, b) as c): pass', 'exec').body[0].copy()
        f.items[0].put(None, 'optional_vars', raw=False)
        self.assertEqual('with ((a, b)): pass', f.src)
        f.verify()

        f = FST('with ((a, b)) as c: pass', 'exec').body[0].copy()
        f.items[0].put(None, 'optional_vars', raw=False)
        self.assertEqual('with ((a, b)): pass', f.src)
        f.verify()

        f = FST('with (a) as c: pass', 'exec').body[0].copy()
        f.items[0].put(None, 'optional_vars', raw=False)
        self.assertEqual('with (a): pass', f.src)
        f.verify()

        if _PY_VERSION >= (3, 14):
            # make sure TemplateStr.str gets modified

            f = FST('''
t"{
t'{
(
a
)
=
!r:>16}'
!r:>16}"
'''.strip(), 'exec')
            self.assertEqual("\nt'{\n(\na\n)\n=\n!r:>16}'", f.body[0].value.values[0].str)
            self.assertEqual('\n(\na\n)', f.body[0].value.values[0].value.values[1].str)

            f.body[0].value.values[0].value.values[1].put('b')
            self.assertEqual("\nt'{\nb\n=\n!r:>16}'", f.body[0].value.values[0].str)
            self.assertEqual('\nb', f.body[0].value.values[0].value.values[1].str)

            f = FST('t"{a}"', 'exec').body[0].value.copy()
            f.values[0].put('b')
            self.assertEqual('b', f.a.values[0].str)

        # put constant

        f = FST('match a:\n case None: pass').cases[0].pattern
        self.assertIsInstance((g := FST('True')).a, Constant)
        f.put(g, 'value', raw=False)
        self.assertEqual('True', g.src)
        self.assertIs(True, g.value)

        self.assertIsInstance((g := FST('False')).a, Constant)
        f.put(g, 'value', raw=False)
        self.assertEqual('False', g.src)
        self.assertIs(False, g.value)

        self.assertIsInstance((g := FST('None')).a, Constant)
        f.put(g, 'value', raw=False)
        self.assertEqual('None', g.src)
        self.assertIs(None, g.value)

        self.assertIsInstance((h := FST('None')).a, Constant)

        for s in ('...', '2', '2.0', '2j', '"str"', 'b"bytes"', 'True', 'False', 'None'):
            self.assertIsInstance((g := FST(s)).a, Constant)

            if g.a.value not in (True, False, None):
                self.assertRaises(NodeError, f.put, g, 'value', raw=False)

            h.put(g, 'value', raw=False)
            self.assertEqual(s, g.src)
            self.assertEqual(h.value, g.value)

        # FormattedValue/Interpolation conversion and format_spec, JoinedStr/TemplateStr values

        if _PY_VERSION >= (3, 12):
            self.assertRaises(NodeError, FST('f"{a}"').values[0].put, '"s"', 'conversion', raw=False)  # not implemented yet
            self.assertRaises(NodeError, FST('f"{a}"').values[0].put, 'f"0.5f"', 'format_spec', raw=False)  # not implemented yet
            self.assertRaises(NodeError, FST('f"{a}"').put, '"s"', 0, 'values', raw=False)  # not implemented yet

            f = FST('f"{a}"', stmt)

            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            self.assertEqual('f"{a:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('f"{a}"', f.src)
            f.verify()

            f.value.values[0].put('r', 'conversion', raw=True)
            self.assertEqual('f"{a!r}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a}"', f.src)
            f.verify()

            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            f.value.values[0].put('r', 'conversion', raw=True)
            self.assertEqual('f"{a!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('f"{a!r}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a}"', f.src)
            f.verify()

            f.value.values[0].put('r', 'conversion', raw=True)
            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            self.assertEqual('f"{a!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('f"{a}"', f.src)
            f.verify()

            f.value.put('{z}', 0, 'values', raw=True)
            self.assertEqual('f"{z}"', f.src)
            f.verify()

            f = FST('f"{a=}"', stmt)

            f.value.values[1].put('r', 'conversion', raw=True)
            self.assertEqual('f"{a=!r}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a=}"', f.src)
            f.verify()

            f.value.values[1].put('0.5f<8', 'format_spec', raw=True)
            f.value.values[1].put('r', 'conversion', raw=True)
            self.assertEqual('f"{a=!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a=:0.5f<8}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'format_spec', raw=True)
            self.assertEqual('f"{a=}"', f.src)
            f.verify()

        if _PY_VERSION >= (3, 14):
            self.assertRaises(NodeError, FST('t"{a}"').values[0].put, '"s"', 'conversion', raw=False)  # not implemented yet
            self.assertRaises(NodeError, FST('t"{a}"').values[0].put, 'f"0.5f"', 'format_spec', raw=False)  # not implemented yet
            self.assertRaises(NodeError, FST('t"{a}"').put, '"s"', 0, 'values', raw=False)  # not implemented yet

            f = FST('t"{a}"', stmt)

            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            self.assertEqual('t"{a:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('t"{a}"', f.src)
            f.verify()

            f.value.values[0].put('r', 'conversion', raw=True)
            self.assertEqual('t"{a!r}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a}"', f.src)
            f.verify()

            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            f.value.values[0].put('r', 'conversion', raw=True)
            self.assertEqual('t"{a!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('t"{a!r}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a}"', f.src)
            f.verify()

            f.value.values[0].put('r', 'conversion', raw=True)
            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            self.assertEqual('t"{a!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('t"{a}"', f.src)
            f.verify()

            f.value.put('{z}', 0, 'values', raw=True)
            self.assertEqual('t"{z}"', f.src)
            f.verify()

            f = FST('t"{a=}"', stmt)

            f.value.values[1].put('r', 'conversion', raw=True)
            self.assertEqual('t"{a=!r}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a=}"', f.src)
            f.verify()

            f.value.values[1].put('0.5f<8', 'format_spec', raw=True)
            f.value.values[1].put('r', 'conversion', raw=True)
            self.assertEqual('t"{a=!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a=:0.5f<8}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'format_spec', raw=True)
            self.assertEqual('t"{a=}"', f.src)
            f.verify()

    def test_put_one_pars(self):
        f = FST('a = b', 'exec').body[0]
        g = FST('(i := j)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('i := j', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = i := j')
        f.put(g.copy(), field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = (i := j)')
        f.put(g, field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = (i := j)')

        f = FST('a = b', 'exec').body[0]
        g = FST('("i"\n"j")', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('"i"\n"j"', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = "i"\n"j"')
        f.put(g.copy(), field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = ("i"\n"j")')
        f.put(g, field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = ("i"\n"j")')

        f = FST('a = b', 'exec').body[0]
        g = FST('[i, j]', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('[i, j]', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = [i, j]')
        f.put(g.copy(), field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = [i, j]')
        f.put(g, field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = [i, j]')

        f = FST('a = b', 'exec').body[0]
        g = FST('(i,\nj)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('(i,\nj)', g.src)
        g.unpar(tuple_=True)
        self.assertEqual('i,\nj', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = i,\nj')
        f.put(g.copy(), field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = (i,\nj)')
        f.put(g, field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = (i,\nj)')

        f = FST('a = ( # pre\nb\n# post\n)', 'exec').body[0]
        g = FST('( i )', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('( i )', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = ( # pre\n( i )\n# post\n)')
        f.put(g.copy(), field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = ( i )')
        f.put(g, field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = i')

        # leave needed pars in target

        f = FST('a = ( # pre\nb\n# post\n)', 'exec').body[0]
        g = FST('(1\n+\n2)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('1\n+\n2', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = ( # pre\n1\n+\n2\n# post\n)')
        f.put(g.copy(), field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = ( # pre\n1\n+\n2\n# post\n)')
        f.put(g, field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = ( # pre\n1\n+\n2\n# post\n)')

        # annoying solo MatchValue

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].pattern.put('(2)', pars='auto')
        self.assertEqual('match a:\n case (2): pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].pattern.put('(2)', pars=True)
        self.assertEqual('match a:\n case ((2)): pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].pattern.put('(2)', pars=False)
        self.assertEqual('match a:\n case ((2)): pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].put('(2)', field='pattern', pars='auto')
        self.assertEqual('match a:\n case 2: pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].put('(2)', field='pattern', pars=True)
        self.assertEqual('match a:\n case (2): pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].put('(2)', field='pattern', pars=False)
        self.assertEqual('match a:\n case ((2)): pass', f.src)
        f.verify()

        # misc cases

        f = FST('match a:\n case (0 as z) | (1 as z): pass', 'exec')
        g = f.body[0].cases[0].pattern.patterns[0].copy(pars=False)
        f.body[0].cases[0].pattern.put(g, 0, field='patterns', raw=False)
        self.assertEqual('match a:\n case (0 as z) | (1 as z): pass', f.src)

        f = FST('match a:\n case range(10): pass', 'exec')
        g = f.body[0].cases[0].pattern.patterns[0].value.copy(pars=False)
        f.body[0].cases[0].pattern.patterns[0].put(g, None, field='value')
        self.assertEqual('match a:\n case range(10): pass', f.src)

        f = FST('(1).to_bytes(2, "little")', 'exec')
        f.body[0].value.func.put('2', raw=False)
        self.assertEqual('(2).to_bytes(2, "little")', f.src)

        f = FST('(a): int', 'exec')
        f.body[0].put('b', 'target', raw=False, pars='auto')
        self.assertEqual('(b): int', f.src)

        f = FST('(a): int', 'exec')
        f.body[0].put('b', 'target', raw=False, pars=True)
        self.assertEqual('b: int', f.src)

        f = FST('with (\na\n): pass', 'exec')
        g = f.body[0].items[0].copy()
        f.body[0].put(g, 0, 'items')
        self.assertEqual('with (\na\n): pass', f.src)

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].pattern.put('(2)')
        self.assertEqual('match a:\n case (2): pass', f.src)
        f.body[0].cases[0].pattern.put('(3)', pars=True)

    def test_put_one_pars_need_matrix(self):
        # pars=True, needed for precedence, needed for parse, present in dst, present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n+\ny # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# src\nx\n+\ny # src\n)', f.root.src)

        # pars=True, needed for precedence, needed for parse, present in dst, not present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n+\ny', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# dst\nx\n+\ny # dst\n)', f.root.src)

        # pars=True, needed for precedence, needed for parse, not present in dst, present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n+\ny # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# src\nx\n+\ny # src\n)', f.root.src)

        # pars=True, needed for precedence, needed for parse, not present in dst, not present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n+\ny', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (x\n+\ny)', f.root.src)

        # pars=True, needed for precedence, not needed for parse, present in dst, present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx + y # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# src\nx + y # src\n)', f.root.src)

        # pars=True, needed for precedence, not needed for parse, present in dst, not present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x + y', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# dst\nx + y # dst\n)', f.root.src)

        # pars=True, needed for precedence, not needed for parse, not present in dst, present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx + y # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# src\nx + y # src\n)', f.root.src)

        # pars=True, needed for precedence, not needed for parse, not present in dst, not present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x + y', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (x + y)', f.root.src)

        # pars=True, not needed for precedence, needed for parse, present in dst, present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n*\ny # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# src\nx\n*\ny # src\n)', f.root.src)

        # pars=True, not needed for precedence, needed for parse, present in dst, not present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n*\ny', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# dst\nx\n*\ny # dst\n)', f.root.src)

        # pars=True, not needed for precedence, needed for parse, not present in dst, present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n*\ny # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# src\nx\n*\ny # src\n)', f.root.src)

        # pars=True, not needed for precedence, needed for parse, not present in dst, not present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n*\ny', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (x\n*\ny)', f.root.src)

        # pars=True, not needed for precedence, not needed for parse, present in dst, present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx * y # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# src\nx * y # src\n)', f.root.src)

        # pars=True, not needed for precedence, not needed for parse, present in dst, not present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x * y', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + x * y', f.root.src)

        # pars=True, not needed for precedence, not needed for parse, not present in dst, present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx * y # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# src\nx * y # src\n)', f.root.src)

        # pars=True, not needed for precedence, not needed for parse, not present in dst, not present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x * y', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + x * y', f.root.src)

        # pars='auto', needed for precedence, needed for parse, present in dst, present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n+\ny # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# src\nx\n+\ny # src\n)', f.root.src)

        # pars='auto', needed for precedence, needed for parse, present in dst, not present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n+\ny', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# dst\nx\n+\ny # dst\n)', f.root.src)

        # pars='auto', needed for precedence, needed for parse, not present in dst, present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n+\ny # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# src\nx\n+\ny # src\n)', f.root.src)

        # pars='auto', needed for precedence, needed for parse, not present in dst, not present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n+\ny', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (x\n+\ny)', f.root.src)

        # pars='auto', needed for precedence, not needed for parse, present in dst, present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx + y # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# src\nx + y # src\n)', f.root.src)

        # pars='auto', needed for precedence, not needed for parse, present in dst, not present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x + y', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# dst\nx + y # dst\n)', f.root.src)

        # pars='auto', needed for precedence, not needed for parse, not present in dst, present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx + y # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# src\nx + y # src\n)', f.root.src)

        # pars='auto', needed for precedence, not needed for parse, not present in dst, not present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x + y', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (x + y)', f.root.src)

        # pars='auto', not needed for precedence, needed for parse, present in dst, present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n*\ny # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + (# src\nx\n*\ny # src\n)', f.root.src)

        # pars='auto', not needed for precedence, needed for parse, present in dst, not present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n*\ny', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + (# dst\nx\n*\ny # dst\n)', f.root.src)

        # pars='auto', not needed for precedence, needed for parse, not present in dst, present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n*\ny # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + (# src\nx\n*\ny # src\n)', f.root.src)

        # pars='auto', not needed for precedence, needed for parse, not present in dst, not present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n*\ny', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + (x\n*\ny)', f.root.src)

        # pars='auto', not needed for precedence, not needed for parse, present in dst, present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx * y # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + x * y', f.root.src)

        # pars='auto', not needed for precedence, not needed for parse, present in dst, not present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x * y', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + x * y', f.root.src)

        # pars='auto', not needed for precedence, not needed for parse, not present in dst, present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx * y # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + x * y', f.root.src)

        # pars='auto', not needed for precedence, not needed for parse, not present in dst, not present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x * y', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + x * y', f.root.src)

    def test_put_src(self):
        for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_SRC_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.put_src(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root

                tdst  = f.root.src
                tdump = f.root.dump(out=list, compact=True)

                f.root.verify(raise_=True)

                self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst, put_src)
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, attr, (ln, col, end_ln, end_col), src, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_src_random_same(self):
        seed(rndseed := randint(0, 0x7fffffff))

        try:
            master = parse('''
def f():
    i = 1

async def af():
    i = 2

class cls:
    i = 3

for _ in ():
    i = 4
else:
    i = 5

async for _ in ():
    i = 6
else:
    i = 7

while _:
    i = 8
else:
    i = 9

if _:
    i = 10
elif _:
    i = 11
else:
    i = 12

with _:
    i = 13

async with _:
    i = 14

match _:
    case 15:
        i = 15

    case 16:
        i = 16

    case 17:
        i = 17

try:
    i = 18
except Exception as e:
    i = 19
except ValueError as v:
    i = 20
except:
    i = 21
else:
    i = 22
finally:
    i = 23
                '''.strip()).f

            lines = master._lines

            for i in range(100):
                copy      = master.copy()
                ln        = randint(0, len(lines) - 1)
                col       = randint(0, len(lines[ln]))
                end_ln    = randint(ln, len(lines) - 1)
                end_col   = randint(col if end_ln == ln else 0, len(lines[end_ln]))
                put_lines = master.get_src(ln, col, end_ln, end_col, True)

                copy.put_src(put_lines, ln, col, end_ln, end_col)
                copy.verify()

                compare_asts(master.a, copy.a, locs=True, raise_=True)

                assert copy.src == master.src

        except Exception:
            print('Random seed was:', rndseed)
            print(i, ln, col, end_ln, end_col)
            print('-'*80)
            print(copy.src)

            raise

    def test_put_src_from_put_slice_data(self):
        from fst.shared import _fixup_field_body
        from fst.fst_slice import _raw_slice_loc

        for i, (dst, attr, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_DATA):
            if options != {'raw': True}:
                continue

            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                field, _ = _fixup_field_body(f.a, field)
                loc      = _raw_slice_loc(f, start, stop, field)

                f.put_src(None if src == '**DEL**' else src, *loc)

                tdst  = f.root.src
                tdump = f.root.dump(out=list, compact=True)

                f.root.verify(raise_=True)

                self.assertEqual(tdst, put_src)
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, src, start, stop, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_default_non_list_field(self):
        self.assertEqual('y', parse('n').body[0].f.put('y').root.src)  # Expr
        self.assertEqual('return y', parse('return n').body[0].f.put('y').root.src)  # Return
        self.assertEqual('await y', parse('await n').body[0].value.f.put('y').root.src)  # Await
        self.assertEqual('yield y', parse('yield n').body[0].value.f.put('y').root.src)  # Yield
        self.assertEqual('yield from y', parse('yield from n').body[0].value.f.put('y').root.src)  # YieldFrom
        self.assertEqual('[*y]', parse('[*n]').body[0].value.elts[0].f.put('y').root.src)  # Starred
        self.assertEqual('match a:\n case "y": pass', parse('match a:\n case "n": pass').body[0].cases[0].pattern.f.put('"y"').root.src)  # MatchValue

    def test_raw_special(self):
        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.put('for x in y', 1, raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d for x in y for a in b]')
        f = g
        # g = f.put(None, 1, raw=True)
        # self.assertIsNot(g, f)
        # self.assertEqual(g.src, '[a for c in d  for a in b]')
        # f = g
        # g = f.put(None, 1, raw=True)
        # self.assertIsNot(g, f)
        # self.assertEqual(g.src, '[a for c in d  ]')
        # f = g

        f = parse('try:pass\nfinally: pass').body[0].f
        g = f.put('break', 0, raw=True)
        self.assertIs(g, f)
        self.assertEqual(g.src, 'try:break\nfinally: pass')

        f = parse('try: pass\nexcept: pass').body[0].handlers[0].f
        g = f.put('break', 0, raw=True)
        self.assertIs(g, f)
        self.assertEqual(g.src, 'except: break')

        f = parse('match a:\n case 1: pass').body[0].cases[0].f
        g = f.put('break', 0, raw=True)
        self.assertIs(g, f)
        self.assertEqual(g.src, 'case 1: break')

        self.assertEqual('y', parse('n', mode='eval').f.put('y', field='body', raw=True).root.src)  # Expression.body

        # strip or add delimiters from/to different type of node to put as slice

        f = parse('{a: b, c: d, e: f}').body[0].value.f
        g = parse('match a:\n case {1: x}: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('{a: b, 1: x, e: f}', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('match a:\n case {1: x, 2: y, 3: z}: pass').body[0].cases[0].pattern.f
        g = parse('{1: a}').body[0].value.f.copy()
        self.assertEqual('match a:\n case {1: x, 1: a, 3: z}: pass', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        g = parse('match a:\n case a, b: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('[1, a, b, 3]', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        g = parse('match a:\n case (a, b): pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('[1, a, b, 3]', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, a, b, 3: pass', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, [a, b], 3: pass', f.put_slice(g.a, 1, 2, raw=True, one=True).root.src)

        f = parse('match a:\n case 1 | 2 | 3: pass').body[0].cases[0].pattern.f
        g = parse('a | b').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1 | a | b | 3: pass', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('{a: b, c: d, e: f}').body[0].value.f
        g = parse('match a:\n case {1: x}: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('{a: b, 1: x, e: f}', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('match a:\n case {1: x, 2: y, 3: z}: pass').body[0].cases[0].pattern.f
        g = parse('{1: a}').body[0].value.f.copy()
        self.assertEqual('match a:\n case {1: x, 1: a, 3: z}: pass', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        g = parse('match a:\n case a, b: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('[1, a, b, 3]', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        g = parse('match a:\n case a, b: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('[1, (a, b), 3]', f.put_slice(g, 1, 2, raw=True, one=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, a, b, 3: pass', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, [a, b], 3: pass', f.put_slice(g, 1, 2, raw=True, one=True).root.src)

        f = parse('match a:\n case 1 | 2 | 3: pass').body[0].cases[0].pattern.f
        g = parse('a | b').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1 | a | b | 3: pass', f.put_slice(g, 1, 2, raw=True).root.src)

        # make sure we can't put TO location behind self

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertEqual('[1, 4]', f.elts[1].replace('4', to=f.elts[2], raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertRaises(ValueError, f.elts[1].replace, '4', to=f.elts[0], raw=True)

        f = parse('a = b').body[0].f
        self.assertEqual('c', f.targets[0].replace('c', to=f.value, raw=True).root.src)

        f = parse('a = b').body[0].f
        self.assertRaises(ValueError, f.value.replace, 'c', to=f.targets[0], raw=True)

    def test_raw_non_mod_stmt_root(self):
        f = FST('call(a, *b, **c)')
        f.args[0].replace('d', to=f.keywords[-1], raw=True)
        self.assertEqual('call(d)', f.src)
        self.assertIsInstance(f.a, Call)
        f.verify()

        f = FST('1, 2')
        f.elts[0].replace('d', to=f.elts[-1], raw=True)
        self.assertEqual('d', f.src)
        self.assertIsInstance(f.a, Name)
        f.verify()

        f = FST('for i in range(-5, 5) if i', 'all')
        f.iter.args[0].replace('99', to=f.iter.args[-1], raw=True)
        self.assertEqual('for i in range(99) if i', f.src)
        self.assertIsInstance(f.a, comprehension)
        f.verify()

        f = FST('1 * 1', 'all')
        f.left.replace('+', to=f.right, raw=True)
        self.assertEqual('+', f.src)
        self.assertIsInstance(f.a, Add)
        f.verify()

    def test_modify_parent_fmtvals_and_interpolations(self):
        if _PY_VERSION >= (3, 12):
            f = FST('f"{a=}"')
            f.values[-1].value.replace('b')
            self.assertEqual('b=', f.values[0].value)
            f.verify()

            f = FST('f"c{a=}"')
            f.values[-1].value.replace('b')
            self.assertEqual('cb=', f.values[0].value)
            f.verify()

            f = FST('''f"""c
{
# 1
a
# 2
=
# 3
!r:0.5f<5}"""''')
            f.values[-1].value.replace('b')
            self.assertEqual('c\n\n\nb\n\n=\n\n', f.values[0].value)
            f.verify()

            f = FST('''f"""c
{
# 1
f'd{f"e{f=!s:0.1f<1}"=}'
# 2
=
# 3
!r:0.5f<5}"""''')
            f.values[-1].value.values[-1].value.values[-1].value.replace('z')
            self.assertEqual('ez=', f.values[-1].value.values[-1].value.values[0].value)
            self.assertEqual('df"e{z=!s:0.1f<1}"=', f.values[-1].value.values[0].value)
            self.assertEqual('c\n\n\nf\'d{f"e{z=!s:0.1f<1}"=}\'\n\n=\n\n', f.values[0].value)
            f.verify()

        if _PY_VERSION >= (3, 14):
            f = FST('''t"""c
{
# 1
f'd{t"e{f=!s:0.1f<1}"=}'
# 2
=
# 3
!r:0.5f<5}"""''')
            f.values[-1].value.values[-1].value.values[-1].value.replace('z')
            self.assertEqual('ez=', f.values[-1].value.values[-1].value.values[0].value)
            self.assertEqual('z', f.values[-1].value.values[-1].value.values[-1].str)
            self.assertEqual('dt"e{z=!s:0.1f<1}"=', f.values[-1].value.values[0].value)
            self.assertEqual('c\n\n\nf\'d{t"e{z=!s:0.1f<1}"=}\'\n\n=\n\n', f.values[0].value)
            self.assertEqual('\n\nf\'d{t"e{z=!s:0.1f<1}"=}\'', f.values[-1].str)
            f.verify()

    def test_empty_set_slice(self):
        # f = parse('set()').body[0].value.f
        # self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
        # self.assertEqual('set()', f.src)
        # self.assertEqual('set()', f.put_slice('{*()}', 0, 0).src)
        # f.root.verify()

        f = parse('{*()}').body[0].value.f
        self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
        self.assertEqual('{*()}', f.src)
        self.assertEqual('{*()}', f.put_slice('{*()}', 0, 0).src)
        f.root.verify()

        f = parse('{*[]}').body[0].value.f
        self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
        self.assertEqual('{*[]}', f.src)
        self.assertEqual('{*[]}', f.put_slice('{*()}', 0, 0).src)
        f.root.verify()

        f = parse('{*{}}').body[0].value.f
        self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
        self.assertEqual('{*{}}', f.src)
        self.assertEqual('{*{}}', f.put_slice('{*()}', 0, 0).src)
        f.root.verify()

        f = parse('{ * ( ) }').body[0].value.f
        self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
        self.assertEqual('{ * ( ) }', f.src)
        self.assertEqual('{ * ( ) }', f.put_slice('{*()}', 0, 0).src)
        f.root.verify()

    def test_ctx_change(self):
        a = parse('a, b = x, y').body[0]
        a.targets[0].f.put(a.value.f.get())
        self.assertEqual('(x, y), = x, y', a.f.src)
        self.assertIsInstance(a.targets[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[0].elts[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[0].elts[1].ctx, Store)

        a = parse('a, b = x, y').body[0]
        a.value.f.put(a.targets[0].f.get())
        self.assertEqual('a, b = (a, b),', a.f.src)
        self.assertIsInstance(a.value.ctx, Load)
        self.assertIsInstance(a.value.elts[0].ctx, Load)
        self.assertIsInstance(a.value.elts[0].elts[0].ctx, Load)
        self.assertIsInstance(a.value.elts[0].elts[1].ctx, Load)

        a = parse('a, b = x, y').body[0]
        a.targets[0].f.put_slice(a.value.f.get())
        self.assertEqual('x, y = x, y', a.f.src)
        self.assertIsInstance(a.targets[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[1].ctx, Store)

        a = parse('a, b = x, y').body[0]
        a.value.f.put_slice(a.targets[0].f.get())
        self.assertEqual('a, b = a, b', a.f.src)
        self.assertIsInstance(a.value.ctx, Load)
        self.assertIsInstance(a.value.elts[0].ctx, Load)
        self.assertIsInstance(a.value.elts[1].ctx, Load)

    def test_line_continuation_issue_at_top_level(self):
        a = parse('''
i ; \\
 j
        '''.strip())
        a.f.put_slice(None, 0, 1)
        self.assertTrue(a.f.verify(raise_=False))

        a = parse('''
i ; \\
 j
        '''.strip())
        a.f.put_slice('l', 0, 1)
        self.assertTrue(a.f.verify(raise_=False))

    def test_unparenthesized_tuple_with_line_continuations(self):
        # backslashes are annoying to include in the regenerable test cases

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 1, cut=True)
        self.assertEqual(a.f.src, '(2, \\\n3)')
        self.assertEqual(s.src, '(1, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(1, 2, cut=True)
        self.assertEqual(a.f.src, '(1, \\\n3)')
        self.assertEqual(s.src, '(\n2, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(2, 3, cut=True)
        self.assertEqual(a.f.src, '(1, \\\n2, \\\n)')
        self.assertEqual(s.src, '(\n3,)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 2, cut=True)
        self.assertEqual(a.f.src, '3,')
        self.assertEqual(s.src, '(1, \\\n2, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(1, 3, cut=True)
        self.assertEqual(a.f.src, '(1, \\\n)')
        self.assertEqual(s.src, '(\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 3, cut=True)
        self.assertEqual(a.f.src, '()')
        self.assertEqual(s.src, '(1, \\\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 0)
        self.assertEqual(a.f.src, '(a, \\\n1, \\\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 1)
        self.assertEqual(a.f.src, '(1, \\\na, \\\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 2, 2)
        self.assertEqual(a.f.src, '(1, \\\n2, \\\na, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 3, 3)
        self.assertEqual(a.f.src, '(1, \\\n2, \\\n3, a, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 1)
        self.assertEqual(a.f.src, '(a, \\\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 2)
        self.assertEqual(a.f.src, '(1, \\\na, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 2, 3)
        self.assertEqual(a.f.src, '(1, \\\n2, \\\na, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 2)
        self.assertEqual(a.f.src, '(a, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 3)
        self.assertEqual(a.f.src, '(1, \\\na, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 3)
        self.assertEqual(a.f.src, '(a, \\\n)')

    def test_unparenthesized_tuple_put_as_one(self):
        f = parse('(1, 2, 3)').body[0].value.f
        f.put('a, b', 1)
        self.assertEqual('(1, (a, b), 3)', f.src)

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

    def test_fstlist(self):
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
        self.assertIsInstance(a.f.body, fstlist)
        self.assertIsInstance(a.body[0].f.body, fstlist)
        a.body[0].f.body.cut()
        self.assertIsInstance(a.body[0].f.body, fstlist)

        a = parse('a\nb\nc\nd\ne')
        p = a.f.body[1:4]
        g = p[1]
        f = p.replace('f')
        self.assertEqual('a\nf\ne', a.f.src)
        self.assertEqual(1, len(f))
        self.assertEqual('f', f[0].src)
        self.assertIsNone(g.a)

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
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertFalse(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtish)
        self.assertFalse(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_scope()).a, ListComp)
        self.assertTrue(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertFalse(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtish)
        self.assertFalse(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_named_scope()).a, FunctionDef)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_named_scope()).a, ClassDef)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmtish()).a, ExceptHandler)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmt()).a, Try)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmtish()).a, match_case)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_block()).a, Match)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_scope()).a, Module)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
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

        old    = FST.set_option(**new)
        newset = FST.set_option(**old)
        oldset = FST.set_option(**old)

        self.assertEqual(newset, new)
        self.assertEqual(oldset, old)

        with FST.option(**new) as opts:
            self.assertEqual(opts, old)
            self.assertEqual(new, FST.set_option(**new))

        self.assertEqual(old, FST.set_option(**old))

        try:
            with FST.option(**new) as opts:
                self.assertEqual(opts, old)
                self.assertEqual(new, FST.set_option(**new))

                raise NodeError

        except NodeError:
            pass

        self.assertEqual(old, FST.set_option(**old))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-pars', default=False, action='store_true', help="regenerate parentheses test data")
    parser.add_argument('--regen-copy', default=False, action='store_true', help="regenerate copy test data")
    parser.add_argument('--regen-get-slice-seq', default=False, action='store_true', help="regenerate get slice sequence test data")
    parser.add_argument('--regen-get-slice-stmt', default=False, action='store_true', help="regenerate get slice statement test data")
    parser.add_argument('--regen-put-slice-seq', default=False, action='store_true', help="regenerate put slice sequence test data")
    parser.add_argument('--regen-put-slice-stmt', default=False, action='store_true', help="regenerate put slice statement test data")
    parser.add_argument('--regen-put-slice', default=False, action='store_true', help="regenerate put slice test data")
    parser.add_argument('--regen-put-one', default=False, action='store_true', help="regenerate put one test data")
    parser.add_argument('--regen-put-raw', default=False, action='store_true', help="regenerate put raw test data")
    parser.add_argument('--regen-precedence', default=False, action='store_true', help="regenerate precedence test data")

    args = parser.parse_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if _PY_VERSION < (3, 12):
            raise RuntimeError('cannot regenerate on python version < 3.12')

    if args.regen_pars or args.regen_all:
        print('Regenerating parentheses test data...')
        regen_pars_data()

    if args.regen_copy or args.regen_all:
        print('Regenerating copy test data...')
        regen_copy_data()

    if args.regen_get_slice_seq or args.regen_all:
        print('Regenerating get slice sequence test data...')
        regen_get_slice_seq()

    if args.regen_get_slice_stmt or args.regen_all:
        print('Regenerating get slice statement cut test data...')
        regen_get_slice_stmt()

    if args.regen_put_slice_seq or args.regen_all:
        print('Regenerating put slice sequence test data...')
        regen_put_slice_seq()

    if args.regen_put_slice_stmt or args.regen_all:
        print('Regenerating put slice statement test data...')
        regen_put_slice_stmt()

    if args.regen_put_slice or args.regen_all:
        print('Regenerating put slice test data...')
        regen_put_slice()

    if args.regen_put_one or args.regen_all:
        print('Regenerating put one test data...')
        regen_put_one()

    if args.regen_put_raw or args.regen_all:
        print('Regenerating put raw test data...')
        regen_put_raw()

    if args.regen_precedence or args.regen_all:
        print('Regenerating precedence test data...')
        regen_precedence_data()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
