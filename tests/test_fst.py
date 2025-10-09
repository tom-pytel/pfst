#!/usr/bin/env python

import os
import threading
import unittest
from ast import parse as ast_parse, unparse as ast_unparse
from random import randint, seed

from fst import *
from fst.asttypes import _slice_Assign_targets, _slice_aliases, _slice_withitems, _slice_type_params
from fst.astutil import OPCLS2STR, WalkFail, copy_ast, compare_asts
from fst.common import PYVER, PYLT11, PYLT12, PYLT13, PYLT14, PYGE11, PYGE12, PYGE13, PYGE14, astfield, fstloc
from fst.view import fstview

from fst.code import (
    code_as_all,
    code_as_stmts,
    code_as_ExceptHandlers,
    code_as_match_cases,
    code_as_expr,
    code_as_expr_slice,
    code_as_boolop,
    code_as_binop,
    code_as_augop,
    code_as_unaryop,
    code_as_cmpop,
    code_as_comprehension,
    code_as_arguments,
    code_as_arguments_lambda,
    code_as_arg,
    code_as_keyword,
    code_as_alias,
    code_as_Import_name,
    code_as_ImportFrom_name,
    code_as_ImportFrom_names,
    code_as_withitem,
    code_as_pattern,
    code_as_type_param,
    code_as_identifier,
    code_as_identifier_dotted,
    code_as_identifier_star,
    code_as_identifier_alias,
)

from fst.locations import (
    loc_ClassDef_bases_pars, loc_ImportFrom_names_pars, loc_With_items_pars, loc_block_header_end, loc_Call_pars,
    loc_Subscript_brackets, loc_MatchClass_pars,
)

from fst import parsex as px, code

from support import ParseCases
from data.data_other import PARS_DATA, PUT_SRC_REPARSE_DATA, PRECEDENCE_DATA


DIR_NAME = os.path.dirname(__file__)
FNM_PARSE_AUTOGEN = os.path.join(DIR_NAME, 'data/data_parse_autogen.py')

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
    ('all',               px.parse_stmts,             Module,                   'i: int = 1\nj'),
    ('all',               px.parse_ExceptHandlers,    Module,                   'except Exception: pass\nexcept: pass'),
    ('all',               px.parse_match_cases,       Module,                   'case None: pass\ncase 1: pass'),
    ('all',               px.parse_stmt,              AnnAssign,                'i: int = 1'),
    ('all',               px.parse_ExceptHandler,     ExceptHandler,            'except: pass'),
    ('all',               px.parse_match_case,        match_case,               'case None: pass'),
    ('all',               px.parse_stmts,             Module,                   'i: int = 1\nj'),
    ('all',               px.parse_stmt,              AnnAssign,                'i: int = 1'),
    ('all',               px.parse_ExceptHandlers,    Module,                   'except Exception: pass\nexcept: pass'),
    ('all',               px.parse_ExceptHandler,     ExceptHandler,            'except: pass'),
    ('all',               px.parse_match_cases,       Module,                   'case None: pass\ncase 1: pass'),
    ('all',               px.parse_match_case,        match_case,               'case None: pass'),
    ('all',               px.parse_expr,              Name,                     'j'),
    ('all',               px.parse_expr,              Starred,                  '*s'),
    ('all',               px.parse_expr_all,          Starred,                  '*not a'),
    ('all',               px.parse_stmt,              AnnAssign,                'a:b'),
    ('all',               px.parse_expr_all,          Slice,                    'a:b:c'),
    ('all',               px.parse_pattern,           MatchAs,                  '1 as a'),
    ('all',               px.parse_arguments,         arguments,                'a: list[str], /, b: int = 1, *c, d=100, **e'),
    ('all',               px.parse_arguments_lambda,  arguments,                'a, /, b, *c, d=100, **e'),
    ('all',               px.parse_arguments,         arguments,                '**a: dict'),
    ('all',               px.parse_pattern,           MatchSequence,            '*a, b as c'),
    ('all',               px.parse_comprehension,     comprehension,            'for i in range(5) if i'),
    ('all',               px.parse_withitem,          withitem,                 'f(**a) as b'),
    ('all',               px.parse_operator,          Mult,                     '*'),
    ('all',               px.parse_augop,             Mult,                     '*='),
    ('all',               px.parse_cmpop,             Gt,                       '>'),
    ('all',               px.parse_boolop,            And,                      'and'),
    ('all',               px.parse_unaryop,           Invert,                   '~'),

    ('strict',            px.parse_stmts,             Module,                   'i: int = 1\nj'),
    ('strict',            px.parse_ExceptHandlers,    SyntaxError,              'except Exception: pass\nexcept: pass'),
    ('strict',            px.parse_match_cases,       SyntaxError,              'case None: pass\ncase 1: pass'),
    ('strict',            px.parse_stmt,              AnnAssign,                'i: int = 1'),
    ('strict',            px.parse_ExceptHandler,     SyntaxError,              'except: pass'),
    ('strict',            px.parse_match_case,        SyntaxError,              'case None: pass'),
    ('strict',            px.parse_stmts,             Module,                   'i: int = 1\nj'),
    ('strict',            px.parse_stmt,              AnnAssign,                'i: int = 1'),
    ('strict',            px.parse_ExceptHandlers,    SyntaxError,              'except Exception: pass\nexcept: pass'),
    ('strict',            px.parse_ExceptHandler,     SyntaxError,              'except: pass'),
    ('strict',            px.parse_match_cases,       SyntaxError,              'case None: pass\ncase 1: pass'),
    ('strict',            px.parse_match_case,        SyntaxError,              'case None: pass'),
    ('strict',            px.parse_expr,              Name,                     'j'),
    ('strict',            px.parse_expr,              Starred,                  '*s'),
    ('strict',            px.parse_all,               SyntaxError,              '*not a'),
    ('strict',            px.parse_stmt,              AnnAssign,                'a:b'),
    ('strict',            px.parse_all,               SyntaxError,              'a:b:c'),
    ('strict',            px.parse_all,               SyntaxError,              '1 as a'),
    ('strict',            px.parse_all,               SyntaxError,              'a: list[str], /, b: int = 1, *c, d=100, **e'),
    ('strict',            px.parse_all,               SyntaxError,              'a, /, b, *c, d=100, **e'),
    ('strict',            px.parse_all,               SyntaxError,              '*not a'),
    ('strict',            px.parse_all,               SyntaxError,              'for i in range(5) if i'),
    ('strict',            px.parse_all,               SyntaxError,              'f(**a) as b'),
    ('strict',            px.parse_all,               SyntaxError,              '*'),
    ('strict',            px.parse_all,               SyntaxError,              '*='),
    ('strict',            px.parse_all,               SyntaxError,              '>'),
    ('strict',            px.parse_all,               SyntaxError,              'and'),
    ('strict',            px.parse_all,               SyntaxError,              '~'),

    ('exec',              px.parse_Module,            Module,                   'i: int = 1'),
    ('eval',              px.parse_Expression,        Expression,               'None'),
    ('single',            px.parse_Interactive,       Interactive,              'i: int = 1'),

    ('stmts',             px.parse_stmts,             Module,                   'i: int = 1\nj'),
    ('stmts',             px.parse_stmts,             SyntaxError,              'except Exception: pass\nexcept: pass'),
    ('stmt',              px.parse_stmt,              AnnAssign,                'i: int = 1'),
    ('stmt',              px.parse_stmt,              Expr,                     'j'),
    ('stmt',              px.parse_stmt,              ParseError,               'i: int = 1\nj'),
    ('stmt',              px.parse_stmt,              SyntaxError,              'except: pass'),

    ('ExceptHandlers',    px.parse_ExceptHandlers,    Module,                   'except Exception: pass\nexcept: pass'),
    ('ExceptHandlers',    px.parse_ExceptHandlers,    IndentationError,         ' except Exception: pass\nexcept: pass'),
    ('ExceptHandlers',    px.parse_ExceptHandlers,    ParseError,               'except Exception: pass\nexcept: pass\nelse: pass'),
    ('ExceptHandlers',    px.parse_ExceptHandlers,    ParseError,               'except Exception: pass\nexcept: pass\nfinally: pass'),
    ('ExceptHandlers',    px.parse_ExceptHandlers,    SyntaxError,              'i: int = 1\nj'),
    ('ExceptHandler',     px.parse_ExceptHandler,     ExceptHandler,            'except: pass'),
    ('ExceptHandler',     px.parse_ExceptHandler,     ParseError,               'except Exception: pass\nexcept: pass'),
    ('ExceptHandler',     px.parse_ExceptHandler,     SyntaxError,              'i: int = 1'),

    ('match_cases',       px.parse_match_cases,       Module,                   'case None: pass\ncase 1: pass'),
    ('match_cases',       px.parse_match_cases,       IndentationError,         ' case None: pass\ncase 1: pass'),
    ('match_cases',       px.parse_match_cases,       SyntaxError,              'i: int = 1'),
    ('match_case',        px.parse_match_case,        match_case,               'case None: pass'),
    ('match_case',        px.parse_match_case,        ParseError,               'case None: pass\ncase 1: pass'),
    ('match_case',        px.parse_match_case,        SyntaxError,              'i: int = 1'),

    ('Assign_targets',    px.parse_Assign_targets,    _slice_Assign_targets,    ''),
    ('Assign_targets',    px.parse_Assign_targets,    _slice_Assign_targets,    'a'),
    ('Assign_targets',    px.parse_Assign_targets,    _slice_Assign_targets,    'a ='),
    ('Assign_targets',    px.parse_Assign_targets,    _slice_Assign_targets,    'a = b'),
    ('Assign_targets',    px.parse_Assign_targets,    _slice_Assign_targets,    'a = b ='),
    ('Assign_targets',    px.parse_Assign_targets,    _slice_Assign_targets,    '\\\na\\\n = \\\n'),
    ('Assign_targets',    px.parse_Assign_targets,    _slice_Assign_targets,    ' a'),
    ('Assign_targets',    px.parse_Assign_targets,    _slice_Assign_targets,    '\na'),
    ('Assign_targets',    px.parse_Assign_targets,    SyntaxError,              '\n\na'),
    ('Assign_targets',    px.parse_Assign_targets,    SyntaxError,              'a\n='),
    ('Assign_targets',    px.parse_Assign_targets,    SyntaxError,              'a =  # tail'),
    ('Assign_targets',    px.parse_Assign_targets,    SyntaxError,              '# head\na ='),
    ('all',               px.parse_Assign_targets,    _slice_Assign_targets,    'a = b ='),

    ('expr',              px.parse_expr,              Name,                     'j'),
    ('expr',              px.parse_expr,              Starred,                  '*s'),
    ('expr',              px.parse_expr,              Starred,                  '*\ns'),
    ('expr',              px.parse_expr,              Tuple,                    '*\ns,'),
    ('expr',              px.parse_expr,              Tuple,                    '1\n,\n2\n,'),
    ('expr',              px.parse_expr,              SyntaxError,              '*not a'),
    ('expr',              px.parse_expr,              SyntaxError,              'a:b'),
    ('expr',              px.parse_expr,              SyntaxError,              'a:b:c'),

    ('expr_all',          px.parse_expr_all,          Name,                     'j'),
    ('expr_all',          px.parse_expr_all,          Starred,                  '*s'),
    ('expr_all',          px.parse_expr_all,          Starred,                  '*\ns'),
    ('expr_all',          px.parse_expr_all,          Tuple,                    '*\ns,'),
    ('expr_all',          px.parse_expr_all,          Tuple,                    '1\n,\n2\n,'),
    ('expr_all',          px.parse_expr_all,          Slice,                    'a:b'),
    ('expr_all',          px.parse_expr_all,          Slice,                    'a:b:c'),
    ('expr_all',          px.parse_expr_all,          Tuple,                    'j, k'),
    ('expr_all',          px.parse_expr_all,          Tuple,                    'a:b:c, x:y:z'),

    ('expr_arglike',      px.parse_expr_arglike,      Name,                     'j'),
    ('expr_arglike',      px.parse_expr_arglike,      Starred,                  '*s'),
    ('expr_arglike',      px.parse_expr_arglike,      Tuple,                    '*s,'),
    ('expr_arglike',      px.parse_expr_arglike,      Starred,                  '*not a'),
    ('expr_arglike',      px.parse_expr_arglike,      SyntaxError,              '*not a,'),
    ('expr_arglike',      px.parse_expr_arglike,      Tuple,                    'j, k'),
    ('expr_arglike',      px.parse_expr_arglike,      ParseError,               'i=1'),
    ('expr_arglike',      px.parse_expr_arglike,      SyntaxError,              'a:b'),
    ('expr_arglike',      px.parse_expr_arglike,      SyntaxError,              'a:b:c'),

    ('_expr_arglikes',    px.parse__expr_arglikes,    Tuple,                    'j'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    Tuple,                    '*s'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    Tuple,                    '*s,'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    Tuple,                    '*not a'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    Tuple,                    '*not a,'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    Tuple,                    '*not a, *b or c'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    Tuple,                    'j, k'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    ParseError,               'i=1'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    SyntaxError,              'a:b'),
    ('_expr_arglikes',    px.parse__expr_arglikes,    SyntaxError,              'a:b:c'),

    ('expr_slice',        px.parse_expr_slice,        Name,                     'j'),
    ('expr_slice',        px.parse_expr_slice,        Slice,                    'a:b'),
    ('expr_slice',        px.parse_expr_slice,        Tuple,                    'j, k'),
    ('expr_slice',        px.parse_expr_slice,        Tuple,                    'a:b:c, x:y:z'),

    ('expr_sliceelt',     px.parse_expr_sliceelt,     Name,                     'j'),
    ('expr_sliceelt',     px.parse_expr_sliceelt,     Slice,                    'a:b'),
    ('expr_sliceelt',     px.parse_expr_sliceelt,     Tuple,                    'j, k'),
    ('expr_sliceelt',     px.parse_expr_sliceelt,     SyntaxError,              'a:b:c, x:y:z'),

    ('boolop',            px.parse_boolop,            And,                      'and'),
    ('boolop',            px.parse_boolop,            ParseError,               '*'),
    ('operator',          px.parse_operator,          Mult,                     '*'),
    ('operator',          px.parse_operator,          Mult,                     '*='),
    ('operator',          px.parse_operator,          ParseError,               'and'),
    ('binop',             px.parse_binop,             Mult,                     '*'),
    ('binop',             px.parse_binop,             SyntaxError,              '*='),
    ('augop',             px.parse_augop,             ParseError,               '*'),
    ('augop',             px.parse_augop,             Mult,                     '*='),
    ('unaryop',           px.parse_unaryop,           UAdd,                     '+'),
    ('unaryop',           px.parse_unaryop,           SyntaxError,              'and'),
    ('cmpop',             px.parse_cmpop,             GtE,                      '>='),
    ('cmpop',             px.parse_cmpop,             IsNot,                    'is\nnot'),
    ('cmpop',             px.parse_cmpop,             ParseError,               '>= a >='),
    ('cmpop',             px.parse_cmpop,             ParseError,               'and'),

    ('comprehension',     px.parse_comprehension,     comprehension,            'for u in v'),
    ('comprehension',     px.parse_comprehension,     comprehension,            'for u in v if w'),
    ('comprehension',     px.parse_comprehension,     ParseError,               'for u in v for s in t'),

    ('arguments',         px.parse_arguments,         arguments,                ''),
    ('arguments',         px.parse_arguments,         arguments,                'a: list[str], /, b: int = 1, *c, d=100, **e'),

    ('arguments_lambda',  px.parse_arguments_lambda,  arguments,                ''),
    ('arguments_lambda',  px.parse_arguments_lambda,  arguments,                'a, /, b, *c, d=100, **e'),
    ('arguments_lambda',  px.parse_arguments_lambda,  arguments,                'a,\n/,\nb,\n*c,\nd=100,\n**e'),
    ('arguments_lambda',  px.parse_arguments_lambda,  SyntaxError,              'a: list[str], /, b: int = 1, *c, d=100, **e'),

    ('arg',               px.parse_arg,               arg,                      'a: b'),
    ('arg',               px.parse_arg,               ParseError,               'a: b = c'),
    ('arg',               px.parse_arg,               ParseError,               'a, b'),
    ('arg',               px.parse_arg,               ParseError,               'a, /'),
    ('arg',               px.parse_arg,               ParseError,               '*, a'),
    ('arg',               px.parse_arg,               ParseError,               '*a'),
    ('arg',               px.parse_arg,               ParseError,               '**a'),

    ('keyword',           px.parse_keyword,           keyword,                  'a=1'),
    ('keyword',           px.parse_keyword,           keyword,                  '**a'),
    ('keyword',           px.parse_keyword,           ParseError,               '1'),
    ('keyword',           px.parse_keyword,           ParseError,               'a'),
    ('keyword',           px.parse_keyword,           ParseError,               'a=1, b=2'),

    ('alias',             px.parse_alias,             SyntaxError,              ''),
    ('alias',             px.parse_alias,             alias,                    'a'),
    ('alias',             px.parse_alias,             alias,                    'a.b'),
    ('alias',             px.parse_alias,             alias,                    '*'),
    ('alias',             px.parse_alias,             ParseError,               'a, b'),
    ('alias',             px.parse_alias,             alias,                    'a as c'),
    ('alias',             px.parse_alias,             alias,                    'a.b as c'),
    ('alias',             px.parse_alias,             SyntaxError,              '* as c'),
    ('alias',             px.parse_alias,             ParseError,               'a as x, b as y'),
    ('alias',             px.parse_alias,             ParseError,               'a as x, a.b as y'),

    ('aliases',           px.parse_aliases,           _slice_aliases,           ''),
    ('aliases',           px.parse_aliases,           _slice_aliases,           'a'),
    ('aliases',           px.parse_aliases,           _slice_aliases,           'a.b'),
    ('aliases',           px.parse_aliases,           _slice_aliases,           '*'),
    ('aliases',           px.parse_aliases,           _slice_aliases,           'a, b'),
    ('aliases',           px.parse_aliases,           _slice_aliases,           'a as c'),
    ('aliases',           px.parse_aliases,           _slice_aliases,           'a.b as c'),
    ('aliases',           px.parse_aliases,           SyntaxError,              '* as c'),
    ('aliases',           px.parse_aliases,           _slice_aliases,           'a as x, b as y'),
    ('aliases',           px.parse_aliases,           _slice_aliases,           'a as x, a.b as y'),

    ('Import_name',       px.parse_Import_name,       SyntaxError,              ''),
    ('Import_name',       px.parse_Import_name,       alias,                    'a'),
    ('Import_name',       px.parse_Import_name,       alias,                    'a.b'),
    ('Import_name',       px.parse_Import_name,       SyntaxError,              '*'),
    ('Import_name',       px.parse_Import_name,       ParseError,               'a, b'),
    ('Import_name',       px.parse_Import_name,       alias,                    'a as c'),
    ('Import_name',       px.parse_Import_name,       alias,                    'a.b as c'),
    ('Import_name',       px.parse_Import_name,       SyntaxError,              '* as c'),
    ('Import_name',       px.parse_Import_name,       ParseError,               'a as x, b as y'),
    ('Import_name',       px.parse_Import_name,       ParseError,               'a as x, a.b as y'),

    ('Import_names',      px.parse_Import_names,      _slice_aliases,           ''),
    ('Import_names',      px.parse_Import_names,      _slice_aliases,           'a'),
    ('Import_names',      px.parse_Import_names,      _slice_aliases,           'a.b'),
    ('Import_names',      px.parse_Import_names,      SyntaxError,              '*'),
    ('Import_names',      px.parse_Import_names,      _slice_aliases,           'a, b'),
    ('Import_names',      px.parse_Import_names,      _slice_aliases,           'a as c'),
    ('Import_names',      px.parse_Import_names,      _slice_aliases,           'a.b as c'),
    ('Import_names',      px.parse_Import_names,      SyntaxError,              '* as c'),
    ('Import_names',      px.parse_Import_names,      _slice_aliases,           'a as x, b as y'),
    ('Import_names',      px.parse_Import_names,      _slice_aliases,           'a as x, a.b as y'),

    ('ImportFrom_name',   px.parse_ImportFrom_name,   SyntaxError,              ''),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   alias,                    'a'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   SyntaxError,              'a.b'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   alias,                    '*'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   ParseError,               'a, b'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   alias,                    'a as c'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   SyntaxError,              'a.b as c'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   SyntaxError,              '* as c'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   ParseError,               'a as x, b as y'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   SyntaxError,              'a as x, a.b as y'),

    ('ImportFrom_names',  px.parse_ImportFrom_names,  _slice_aliases,           ''),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  _slice_aliases,           'a'),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  SyntaxError,              'a.b'),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  _slice_aliases,           '*'),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  _slice_aliases,           'a, b'),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  _slice_aliases,           'a as c'),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  SyntaxError,              'a.b as c'),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  SyntaxError,              '* as c'),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  _slice_aliases,           'a as x, b as y'),
    ('ImportFrom_names',  px.parse_ImportFrom_names,  SyntaxError,              'a as x, a.b as y'),

    ('withitem',          px.parse_withitem,          SyntaxError,              ''),
    ('withitem',          px.parse_withitem,          withitem,                 'a'),
    ('withitem',          px.parse_withitem,          withitem,                 'a, b'),
    ('withitem',          px.parse_withitem,          withitem,                 '(a, b)'),
    ('withitem',          px.parse_withitem,          withitem,                 '()'),
    ('withitem',          px.parse_withitem,          withitem,                 'a as b'),
    ('withitem',          px.parse_withitem,          withitem,                 '(a) as (b)'),
    ('withitem',          px.parse_withitem,          ParseError,               'a, b as c'),
    ('withitem',          px.parse_withitem,          ParseError,               'a as b, x as y'),
    ('withitem',          px.parse_withitem,          withitem,                 '(a)'),
    ('withitem',          px.parse_withitem,          SyntaxError,              '(a as b)'),
    ('withitem',          px.parse_withitem,          SyntaxError,              '(a as b, x as y)'),

    ('withitems',         px.parse_withitems,         _slice_withitems,         ''),
    ('withitems',         px.parse_withitems,         _slice_withitems,         'a'),
    ('withitems',         px.parse_withitems,         _slice_withitems,         'a, b'),
    ('withitems',         px.parse_withitems,         _slice_withitems,         '(a, b)'),
    ('withitems',         px.parse_withitems,         _slice_withitems,         '()'),
    ('withitems',         px.parse_withitems,         _slice_withitems,         'a as b'),
    ('withitems',         px.parse_withitems,         _slice_withitems,         '(a) as (b)'),
    ('withitems',         px.parse_withitems,         _slice_withitems,         'a, b as c'),
    ('withitems',         px.parse_withitems,         _slice_withitems,         'a as b, x as y'),
    ('withitems',         px.parse_withitems,         _slice_withitems,         '(a)'),
    ('withitems',         px.parse_withitems,         SyntaxError,              '(a as b)'),
    ('withitems',         px.parse_withitems,         SyntaxError,              '(a as b, x as y)'),

    ('pattern',           px.parse_pattern,           MatchValue,               '42'),
    ('pattern',           px.parse_pattern,           MatchSingleton,           'None'),
    ('pattern',           px.parse_pattern,           MatchSequence,            '[a, *_]'),
    ('pattern',           px.parse_pattern,           MatchSequence,            '[]'),
    ('pattern',           px.parse_pattern,           MatchMapping,             '{"key": _}'),
    ('pattern',           px.parse_pattern,           MatchMapping,             '{}'),
    ('pattern',           px.parse_pattern,           MatchClass,               'SomeClass()'),
    ('pattern',           px.parse_pattern,           MatchClass,               'SomeClass(attr=val)'),
    ('pattern',           px.parse_pattern,           MatchAs,                  'as_var'),
    ('pattern',           px.parse_pattern,           MatchAs,                  '1 as as_var'),
    ('pattern',           px.parse_pattern,           MatchOr,                  '1 | 2 | 3'),
    ('pattern',           px.parse_pattern,           MatchAs,                  '_'),
    ('pattern',           px.parse_pattern,           MatchStar,                '*a'),
    ('pattern',           px.parse_pattern,           SyntaxError,              ''),

    ('expr',              px.parse_expr,              BoolOp,                   '\na\nor\nb\n'),
    ('expr',              px.parse_expr,              NamedExpr,                '\na\n:=\nb\n'),
    ('expr',              px.parse_expr,              BinOp,                    '\na\n|\nb\n'),
    ('expr',              px.parse_expr,              BinOp,                    '\na\n**\nb\n'),
    ('expr',              px.parse_expr,              UnaryOp,                  '\nnot\na\n'),
    ('expr',              px.parse_expr,              UnaryOp,                  '\n~\na\n'),
    ('expr',              px.parse_expr,              Lambda,                   '\nlambda\n:\nNone\n'),
    ('expr',              px.parse_expr,              IfExp,                    '\na\nif\nb\nelse\nc\n'),
    ('expr',              px.parse_expr,              Dict,                     '\n{\na\n:\nb\n}\n'),
    ('expr',              px.parse_expr,              Set,                      '\n{\na\n,\nb\n}\n'),
    ('expr',              px.parse_expr,              ListComp,                 '\n[\na\nfor\na\nin\nb\n]\n'),
    ('expr',              px.parse_expr,              SetComp,                  '\n{\na\nfor\na\nin\nb\n}\n'),
    ('expr',              px.parse_expr,              DictComp,                 '\n{\na\n:\nc\nfor\na\n,\nc\nin\nb\n}\n'),
    ('expr',              px.parse_expr,              GeneratorExp,             '\n(\na\nfor\na\nin\nb\n)\n'),
    ('expr',              px.parse_expr,              Await,                    '\nawait\na\n'),
    ('expr',              px.parse_expr,              Yield,                    '\nyield\n'),
    ('expr',              px.parse_expr,              Yield,                    '\nyield\na\n'),
    ('expr',              px.parse_expr,              YieldFrom,                '\nyield\nfrom\na\n'),
    ('expr',              px.parse_expr,              Compare,                  '\na\n<\nb\n'),
    ('expr',              px.parse_expr,              Call,                     '\nf\n(\na\n)\n'),
    ('expr',              px.parse_expr,              JoinedStr,                "\nf'{a}'\n"),
    ('expr',              px.parse_expr,              JoinedStr,                '\nf"{a}"\n'),
    ('expr',              px.parse_expr,              JoinedStr,                "\nf'''\n{\na\n}\n'''\n"),
    ('expr',              px.parse_expr,              JoinedStr,                '\nf"""\n{\na\n}\n"""\n'),
    ('expr',              px.parse_expr,              Constant,                 '\n...\n'),
    ('expr',              px.parse_expr,              Constant,                 '\nNone\n'),
    ('expr',              px.parse_expr,              Constant,                 '\nTrue\n'),
    ('expr',              px.parse_expr,              Constant,                 '\nFalse\n'),
    ('expr',              px.parse_expr,              Constant,                 '\n1\n'),
    ('expr',              px.parse_expr,              Constant,                 '\n1.0\n'),
    ('expr',              px.parse_expr,              Constant,                 '\n1j\n'),
    ('expr',              px.parse_expr,              Constant,                 "\n'a'\n"),
    ('expr',              px.parse_expr,              Constant,                 '\n"a"\n'),
    ('expr',              px.parse_expr,              Constant,                 "\n'''\na\n'''\n"),
    ('expr',              px.parse_expr,              Constant,                 '\n"""\na\n"""\n'),
    ('expr',              px.parse_expr,              Constant,                 "\nb'a'\n"),
    ('expr',              px.parse_expr,              Constant,                 '\nb"a"\n'),
    ('expr',              px.parse_expr,              Constant,                 "\nb'''\na\n'''\n"),
    ('expr',              px.parse_expr,              Constant,                 '\nb"""\na\n"""\n'),
    ('expr',              px.parse_expr,              Attribute,                '\na\n.\nb\n'),
    ('expr',              px.parse_expr,              Subscript,                '\na\n[\nb\n]\n'),
    ('expr',              px.parse_expr,              Starred,                  '\n*\na\n'),
    ('expr',              px.parse_expr,              List,                     '\n[\na\n,\nb\n]\n'),
    ('expr',              px.parse_expr,              Tuple,                    '\n(\na\n,\nb\n)\n'),
    ('expr',              px.parse_expr,              Tuple,                    '\na\n,\n'),
    ('expr',              px.parse_expr,              Tuple,                    '\na\n,\nb\n'),

    ('pattern',           px.parse_pattern,           MatchValue,               '\n42\n'),
    ('pattern',           px.parse_pattern,           MatchSingleton,           '\nNone\n'),
    ('pattern',           px.parse_pattern,           MatchSequence,            '\n[\na\n,\n*\nb\n]\n'),
    ('pattern',           px.parse_pattern,           MatchSequence,            '\n\na\n,\n*\nb\n\n'),
    ('pattern',           px.parse_pattern,           MatchMapping,             '\n{\n"key"\n:\n_\n}\n'),
    ('pattern',           px.parse_pattern,           MatchClass,               '\nSomeClass\n(\nattr\n=\nval\n)\n'),
    ('pattern',           px.parse_pattern,           MatchAs,                  '\nas_var\n'),
    ('pattern',           px.parse_pattern,           MatchAs,                  '\n1\nas\nas_var\n'),
    ('pattern',           px.parse_pattern,           MatchOr,                  '\n1\n|\n2\n'),

    ('expr',              px.parse_expr,              BoolOp,                   '\n a\n or\n b\n         '),
    ('expr',              px.parse_expr,              NamedExpr,                '\n a\n :=\n b\n         '),
    ('expr',              px.parse_expr,              BinOp,                    '\n a\n |\n b\n         '),
    ('expr',              px.parse_expr,              BinOp,                    '\n a\n **\n b\n         '),
    ('expr',              px.parse_expr,              UnaryOp,                  '\n not\n a\n         '),
    ('expr',              px.parse_expr,              UnaryOp,                  '\n ~\n a\n         '),
    ('expr',              px.parse_expr,              Lambda,                   '\n lambda\n :\n None\n         '),
    ('expr',              px.parse_expr,              IfExp,                    '\n a\n if\n b\n else\n c\n         '),
    ('expr',              px.parse_expr,              Dict,                     '\n {\n a\n :\n b\n }\n         '),
    ('expr',              px.parse_expr,              Set,                      '\n {\n a\n ,\n b\n }\n         '),
    ('expr',              px.parse_expr,              ListComp,                 '\n [\n a\n for\n a\n in\n b\n ]\n         '),
    ('expr',              px.parse_expr,              SetComp,                  '\n {\n a\n for\n a\n in\n b\n }\n         '),
    ('expr',              px.parse_expr,              DictComp,                 '\n {\n a\n :\n c\n for\n a\n ,\n c\n in\n b\n }\n         '),
    ('expr',              px.parse_expr,              GeneratorExp,             '\n (\n a\n for\n a\n in\n b\n )\n         '),
    ('expr',              px.parse_expr,              Await,                    '\n await\n a\n         '),
    ('expr',              px.parse_expr,              Yield,                    '\n yield\n         '),
    ('expr',              px.parse_expr,              Yield,                    '\n yield\n a\n         '),
    ('expr',              px.parse_expr,              YieldFrom,                '\n yield\n from\n a\n         '),
    ('expr',              px.parse_expr,              Compare,                  '\n a\n <\n b\n         '),
    ('expr',              px.parse_expr,              Call,                     '\n f\n (\n a\n )\n         '),
    ('expr',              px.parse_expr,              JoinedStr,                "\n f'{a}'\n "),
    ('expr',              px.parse_expr,              JoinedStr,                '\n f"{a}"\n         '),
    ('expr',              px.parse_expr,              JoinedStr,                "\n f'''\n {\n a\n }\n         '''\n "),
    ('expr',              px.parse_expr,              JoinedStr,                '\n f"""\n {\n a\n }\n """\n         '),
    ('expr',              px.parse_expr,              Constant,                 '\n ...\n         '),
    ('expr',              px.parse_expr,              Constant,                 '\n None\n         '),
    ('expr',              px.parse_expr,              Constant,                 '\n True\n         '),
    ('expr',              px.parse_expr,              Constant,                 '\n False\n         '),
    ('expr',              px.parse_expr,              Constant,                 '\n 1\n         '),
    ('expr',              px.parse_expr,              Constant,                 '\n 1.0\n         '),
    ('expr',              px.parse_expr,              Constant,                 '\n 1j\n         '),
    ('expr',              px.parse_expr,              Constant,                 "\n         'a'\n "),
    ('expr',              px.parse_expr,              Constant,                 '\n "a"\n         '),
    ('expr',              px.parse_expr,              Constant,                 "\n         '''\n a\n         '''\n "),
    ('expr',              px.parse_expr,              Constant,                 '\n """\n a\n """\n         '),
    ('expr',              px.parse_expr,              Constant,                 "\n b'a'\n "),
    ('expr',              px.parse_expr,              Constant,                 '\n b"a"\n         '),
    ('expr',              px.parse_expr,              Constant,                 "\n b'''\n a\n         '''\n "),
    ('expr',              px.parse_expr,              Constant,                 '\n b"""\n a\n """\n         '),
    ('expr',              px.parse_expr,              Attribute,                '\n a\n .\n b\n         '),
    ('expr',              px.parse_expr,              Subscript,                '\n a\n [\n b\n ]\n         '),
    ('expr',              px.parse_expr,              Starred,                  '\n *\n a\n         '),
    ('expr',              px.parse_expr,              List,                     '\n [\n a\n ,\n b\n ]\n         '),
    ('expr',              px.parse_expr,              Tuple,                    '\n (\n a\n ,\n b\n )\n         '),
    ('expr',              px.parse_expr,              Tuple,                    '\n a\n ,\n         '),
    ('expr',              px.parse_expr,              Tuple,                    '\n a\n ,\n b\n         '),

    ('pattern',           px.parse_pattern,           MatchValue,               '\n 42\n         '),
    ('pattern',           px.parse_pattern,           MatchSingleton,           '\n None\n         '),
    ('pattern',           px.parse_pattern,           MatchSequence,            '\n [\n a\n ,\n *\n b\n ]\n         '),
    ('pattern',           px.parse_pattern,           MatchSequence,            '\n \n a\n ,\n *\n b\n \n         '),
    ('pattern',           px.parse_pattern,           MatchMapping,             '\n {\n "key"\n :\n _\n }\n         '),
    ('pattern',           px.parse_pattern,           MatchClass,               '\n SomeClass\n (\n attr\n =\n val\n )\n         '),
    ('pattern',           px.parse_pattern,           MatchAs,                  '\n as_var\n         '),
    ('pattern',           px.parse_pattern,           MatchAs,                  '\n 1\n as\n as_var\n         '),
    ('pattern',           px.parse_pattern,           MatchOr,                  '\n 1\n |\n 2\n         '),

    (mod,                 px.parse_Module,            Module,                   'j'),
    (Module,              px.parse_Module,            Module,                   'j'),
    (Expression,          px.parse_Expression,        Expression,               'None'),
    (Interactive,         px.parse_Interactive,       Interactive,              'j'),

    (stmt,                px.parse_stmt,              AnnAssign,                'i: int = 1'),
    (stmt,                px.parse_stmt,              Expr,                     'j'),
    (stmt,                px.parse_stmt,              ParseError,               'i: int = 1\nj'),
    (stmt,                px.parse_stmt,              SyntaxError,              'except: pass'),
    (AnnAssign,           px.parse_stmt,              AnnAssign,                'i: int = 1'),
    (Expr,                px.parse_stmt,              Expr,                     'j'),

    (ExceptHandler,       px.parse_ExceptHandler,     ExceptHandler,            'except: pass'),
    (ExceptHandler,       px.parse_ExceptHandler,     ParseError,               'except Exception: pass\nexcept: pass'),
    (ExceptHandler,       px.parse_ExceptHandler,     SyntaxError,              'i: int = 1'),

    (match_case,          px.parse_match_case,        match_case,               'case None: pass'),
    (match_case,          px.parse_match_case,        ParseError,               'case None: pass\ncase 1: pass'),
    (match_case,          px.parse_match_case,        SyntaxError,              'i: int = 1'),

    (expr,                px.parse_expr,              Name,                     'j'),
    (expr,                px.parse_expr,              Starred,                  '*s'),
    (expr,                px.parse_expr,              Starred,                  '*\ns'),
    (expr,                px.parse_expr,              Tuple,                    '*\ns,'),
    (expr,                px.parse_expr,              Tuple,                    '1\n,\n2\n,'),
    (expr,                px.parse_expr,              SyntaxError,              '*not a'),
    (expr,                px.parse_expr,              SyntaxError,              'a:b'),
    (expr,                px.parse_expr,              SyntaxError,              'a:b:c'),
    (Name,                px.parse_expr,              Name,                     'j'),
    (Starred,             px.parse_expr,              Starred,                  '*s'),

    (Starred,             px.parse_expr_arglike,      Starred,                  '*not a'),

    (Slice,               px.parse_expr_slice,        Slice,                    'a:b'),

    (boolop,              px.parse_boolop,            And,                      'and'),
    (boolop,              px.parse_boolop,            ParseError,               '*'),
    (operator,            px.parse_operator,          Mult,                     '*'),
    (operator,            px.parse_operator,          Mult,                     '*='),
    (operator,            px.parse_operator,          ParseError,               'and'),
    (unaryop,             px.parse_unaryop,           UAdd,                     '+'),
    (unaryop,             px.parse_unaryop,           SyntaxError,              'and'),
    (cmpop,               px.parse_cmpop,             GtE,                      '>='),
    (cmpop,               px.parse_cmpop,             IsNot,                    'is\nnot'),
    (cmpop,               px.parse_cmpop,             ParseError,               '>= a >='),
    (cmpop,               px.parse_cmpop,             ParseError,               'and'),

    (comprehension,       px.parse_comprehension,     comprehension,            'for u in v'),
    (comprehension,       px.parse_comprehension,     comprehension,            'for u in v if w'),
    (comprehension,       px.parse_comprehension,     ParseError,               '()'),

    (arguments,           px.parse_arguments,         arguments,                ''),
    (arguments,           px.parse_arguments,         arguments,                'a: list[str], /, b: int = 1, *c, d=100, **e'),
    (arguments,           px.parse_arguments_lambda,  arguments,                'a, /, b, *c, d=100, **e'),

    (arg,                 px.parse_arg,               arg,                      'a: b'),
    (arg,                 px.parse_arg,               ParseError,               'a: b = c'),
    (arg,                 px.parse_arg,               ParseError,               'a, b'),
    (arg,                 px.parse_arg,               ParseError,               'a, /'),
    (arg,                 px.parse_arg,               ParseError,               '*, a'),
    (arg,                 px.parse_arg,               ParseError,               '*a'),
    (arg,                 px.parse_arg,               ParseError,               '**a'),

    (keyword,             px.parse_keyword,           keyword,                  'a=1'),
    (keyword,             px.parse_keyword,           keyword,                  '**a'),
    (keyword,             px.parse_keyword,           ParseError,               '1'),
    (keyword,             px.parse_keyword,           ParseError,               'a'),
    (keyword,             px.parse_keyword,           ParseError,               'a=1, b=2'),

    (alias,               px.parse_alias,             alias,                    'a'),
    (alias,               px.parse_alias,             alias,                    'a.b'),
    (alias,               px.parse_alias,             alias,                    '*'),
    (alias,               px.parse_alias,             ParseError,               'a, b'),
    (alias,               px.parse_alias,             alias,                    'a as c'),
    (alias,               px.parse_alias,             alias,                    'a.b as c'),
    (alias,               px.parse_alias,             SyntaxError,              '* as c'),

    (withitem,            px.parse_withitem,          withitem,                 'a'),
    (withitem,            px.parse_withitem,          withitem,                 'a, b'),
    (withitem,            px.parse_withitem,          withitem,                 '(a, b)'),
    (withitem,            px.parse_withitem,          withitem,                 'a as b'),
    (withitem,            px.parse_withitem,          ParseError,               'a as b, x as y'),
    (withitem,            px.parse_withitem,          withitem,                 '(a)'),
    (withitem,            px.parse_withitem,          SyntaxError,              '(a as b)'),
    (withitem,            px.parse_withitem,          SyntaxError,              '(a as b, x as y)'),

    (pattern,             px.parse_pattern,           MatchValue,               '42'),
    (pattern,             px.parse_pattern,           MatchSingleton,           'None'),
    (pattern,             px.parse_pattern,           MatchSequence,            '[a, *_]'),
    (pattern,             px.parse_pattern,           MatchSequence,            '[]'),
    (pattern,             px.parse_pattern,           MatchMapping,             '{"key": _}'),
    (pattern,             px.parse_pattern,           MatchMapping,             '{}'),
    (pattern,             px.parse_pattern,           MatchClass,               'SomeClass()'),
    (pattern,             px.parse_pattern,           MatchClass,               'SomeClass(attr=val)'),
    (pattern,             px.parse_pattern,           MatchAs,                  'as_var'),
    (pattern,             px.parse_pattern,           MatchAs,                  '1 as as_var'),
    (pattern,             px.parse_pattern,           MatchOr,                  '1 | 2 | 3'),
    (pattern,             px.parse_pattern,           MatchAs,                  '_'),
    (pattern,             px.parse_pattern,           MatchStar,                '*a'),
    (pattern,             px.parse_pattern,           SyntaxError,              ''),

    (MatchValue,          px.parse_pattern,           MatchValue,               '42'),
    (MatchSingleton,      px.parse_pattern,           MatchSingleton,           'None'),
    (MatchSequence,       px.parse_pattern,           MatchSequence,            '[a, *_]'),
    (MatchSequence,       px.parse_pattern,           MatchSequence,            '[]'),
    (MatchMapping,        px.parse_pattern,           MatchMapping,             '{"key": _}'),
    (MatchMapping,        px.parse_pattern,           MatchMapping,             '{}'),
    (MatchClass,          px.parse_pattern,           MatchClass,               'SomeClass()'),
    (MatchClass,          px.parse_pattern,           MatchClass,               'SomeClass(attr=val)'),
    (MatchAs,             px.parse_pattern,           MatchAs,                  'as_var'),
    (MatchAs,             px.parse_pattern,           MatchAs,                  '1 as as_var'),
    (MatchOr,             px.parse_pattern,           MatchOr,                  '1 | 2 | 3'),
    (MatchAs,             px.parse_pattern,           MatchAs,                  '_'),
    (MatchStar,           px.parse_pattern,           MatchStar,                '*a'),

    ('expr',              px.parse_expr,              Tuple,                    ' *a,  # tail'),
    ('expr_arglike',      px.parse_expr_arglike,      Starred,                  ' *not a  # tail'),
    ('expr_slice',        px.parse_expr_slice,        Slice,                    ' a:b:c  # tail'),
    ('expr_slice',        px.parse_expr_slice,        Yield,                    ' yield  # tail'),
    ('boolop',            px.parse_boolop,            And,                      ' and  # tail'),
    ('binop',             px.parse_binop,             RShift,                   ' >>  # tail'),
    ('augop',             px.parse_augop,             SyntaxError,              ' >>=  # tail'),  # this can never be as a statement can never be enclosed and a line continuation cannot follow a comment
    ('unaryop',           px.parse_unaryop,           Invert,                   ' ~  # tail'),
    ('cmpop',             px.parse_cmpop,             GtE,                      ' >=  # tail'),
    ('comprehension',     px.parse_comprehension,     comprehension,            ' for i in j  # tail'),
    ('arguments',         px.parse_arguments,         arguments,                ' a: list[str], /, b: int = 1, *c, d=100, **e  # tail'),
    ('arguments_lambda',  px.parse_arguments_lambda,  arguments,                ' a, /, b, *c, d=100, **e  # tail'),
    ('arg',               px.parse_arg,               arg,                      ' a: b  # tail'),
    ('keyword',           px.parse_keyword,           keyword,                  ' a=1  # tail'),
    ('Import_name',       px.parse_Import_name,       alias,                    ' a.b  # tail'),
    ('ImportFrom_name',   px.parse_ImportFrom_name,   alias,                    ' *  # tail'),
    ('withitem',          px.parse_withitem,          withitem,                 ' a as b,  # tail'),
    ('pattern',           px.parse_pattern,           MatchOr,                  ' 1 | 2 | 3  # tail'),
    ('pattern',           px.parse_pattern,           MatchStar,                ' *a  # tail'),
  ]

PARSE_TESTS_10 = PARSE_TESTS.copy()

if PYGE11:
    PARSE_TESTS.extend(PARSE_TESTS_11 := [
        ('ExceptHandler',     px.parse_ExceptHandler,     ExceptHandler,          'except* Exception: pass'),

        ('expr_all',          px.parse_expr_all,          Starred,                '*not a'),

        ('expr_slice',        px.parse_expr_slice,        Tuple,                  '*s'),
        ('expr_slice',        px.parse_expr_slice,        Tuple,                  '*not a'),

        ('expr_sliceelt',     px.parse_expr_sliceelt,     Starred,                '*not a'),
        ('expr_sliceelt',     px.parse_expr_sliceelt,     SyntaxError,            '*not a, *b or c'),

        (ExceptHandler,       px.parse_ExceptHandler,     ExceptHandler,          'except* Exception: pass'),

        ('arg',               px.parse_arg,               arg,                    ' a: *b  # tail'),
    ])

if PYGE12:
    PARSE_TESTS.extend(PARSE_TESTS_12 := [
        ('all',               px.parse_type_params,       _slice_type_params,     '*U, **V, **Z'),
        ('all',               px.parse_type_params,       _slice_type_params,     'T: int, *U, **V, **Z'),

        ('type_param',        px.parse_type_param,        TypeVar,                'a: int'),
        ('type_param',        px.parse_type_param,        ParamSpec,              '**a'),
        ('type_param',        px.parse_type_param,        TypeVarTuple,           '*a'),
        ('type_param',        px.parse_type_param,        ParseError,             'a: int,'),

        ('type_params',       px.parse_type_params,       _slice_type_params,     ''),
        ('type_params',       px.parse_type_params,       _slice_type_params,     'a: int'),
        ('type_params',       px.parse_type_params,       _slice_type_params,     'a: int,'),
        ('type_params',       px.parse_type_params,       _slice_type_params,     'a: int, *b, **c'),

        (type_param,          px.parse_type_param,        TypeVar,                'a: int'),
        (TypeVar,             px.parse_type_param,        TypeVar,                'a: int'),
        (type_param,          px.parse_type_param,        ParamSpec,              '**a'),
        (ParamSpec,           px.parse_type_param,        ParamSpec,              '**a'),
        (type_param,          px.parse_type_param,        TypeVarTuple,           '*a'),
        (TypeVarTuple,        px.parse_type_param,        TypeVarTuple,           '*a'),

        ('type_param',        px.parse_type_param,        TypeVar,                ' a: int  # tail'),
        ('type_params',       px.parse_type_params,       _slice_type_params,     ' a: int, *b, **c  # tail'),
    ])

if PYGE13:
    PARSE_TESTS.extend(PARSE_TESTS_13 := [
        ('all',               px.parse_type_param,        ParamSpec,              '**a = {T: int, U: str}'),
        ('all',               px.parse_type_param,        TypeVarTuple,           '*a = (int, str)'),

        ('type_param',        px.parse_type_param,        TypeVar,                'a: int = int'),
        ('type_param',        px.parse_type_param,        ParamSpec,              '**a = {T: int, U: str}'),
        ('type_param',        px.parse_type_param,        TypeVarTuple,           '*a = (int, str)'),

        (type_param,          px.parse_type_param,        TypeVar,                'a: int = int'),
        (TypeVar,             px.parse_type_param,        TypeVar,                'a: int = int'),
        (type_param,          px.parse_type_param,        ParamSpec,              '**a = {T: int, U: str}'),
        (ParamSpec,           px.parse_type_param,        ParamSpec,              '**a = {T: int, U: str}'),
        (type_param,          px.parse_type_param,        TypeVarTuple,           '*a = (int, str)'),
        (TypeVarTuple,        px.parse_type_param,        TypeVarTuple,           '*a = (int, str)'),
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
        ssrc  = f._get_src(*l)

        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        newlines.append('(r"""')
        newlines.extend(f'''{src}\n""", {elt!r}, r"""\n{ssrc}\n"""),\n'''.split('\n'))

    fnm = os.path.join(DIR_NAME, 'data/data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PARS_DATA = [')
    stop  = lines.index(']  # END OF PARS_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_src():
    newlines = []

    for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_SRC_REPARSE_DATA):
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            eln, ecol = f.put_src(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root
            g = f.root.find_loc(ln, col, eln, ecol)

            tdst  = f.root.src
            tdump = f.root.dump(out=list)

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

    fnm = os.path.join(DIR_NAME, 'data/data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SRC_REPARSE_DATA = [')
    stop  = lines.index(']  # END OF PUT_SRC_REPARSE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_precedence_data():
    newlines = []

    for dst, *attrs in PRECEDENCE_DST_STMTS + PRECEDENCE_DST_EXPRS + PRECEDENCE_SRC_EXPRS:
        for src, *_ in PRECEDENCE_SRC_EXPRS:
            for attr in attrs:
                d       = dst.copy()
                s       = src.body[0].value.copy()
                is_stmt = isinstance(d.a, stmt)
                f       = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})

                # # put python precedence

                # is_unpar_tup = False if is_stmt else (d.body[0].value._is_parenthesized_tuple() is False)

                # f.pfield.set(f.parent.a, s.a)

                # truth = ast_unparse(f.root.a)

                # if is_unpar_tup:
                #     truth = truth[1:-1]

                # newlines.append(f'    {truth!r},')

                # put our precedence

                d            = dst.copy()
                s            = src.body[0].value.copy()
                is_stmt      = isinstance(d.a, stmt)
                f            = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})

                try:
                    f.parent.put(s, f.pfield.idx, f.pfield.name)
                except Exception as exc:
                    truth = str(exc)

                else:
                    f.root.verify()

                    truth = f.root.src

                newlines.append(f'    {truth!r},')

    fnm = os.path.join(DIR_NAME, 'data/data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PRECEDENCE_DATA = [')
    stop  = lines.index(']  # END OF PRECEDENCE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_parse_autogen_data():
    with open(FNM_PARSE_AUTOGEN) as f:
        lines = f.readlines()

    for i, l in enumerate(lines):
        if l.startswith('DATA_PARSE_AUTOGEN'):
            del lines[i + 1:]

    lines.append("'autogen': [\n")

    for tests, _ver in ((PARSE_TESTS_10, 10), (PARSE_TESTS_11, 11), (PARSE_TESTS_12, 12), (PARSE_TESTS_13, 13)):
        for mode, func, res, src in tests:
            mode_str = repr(mode) if isinstance(mode, str) else mode.__name__
            options = '{}' if _ver < 11 else "{'_ver': 11}" if _ver == 11 else "{'_ver': 12}" if _ver == 12 else "{'_ver': 13}"

            lines.append(f'(-1, {func.__name__!r}, 0, 0, {res.__name__!r}, {options}, ({mode_str}, {src!r})),\n')

    lines.append(']}\n')

    with open(FNM_PARSE_AUTOGEN, 'w') as f:
        f.writelines(lines)

    DATA_PARSE_AUTOGEN = ParseCases(FNM_PARSE_AUTOGEN)

    DATA_PARSE_AUTOGEN.generate()
    DATA_PARSE_AUTOGEN.write()


class TestFST(unittest.TestCase):
    def test_parse_autogen(self):
        DATA_PARSE_AUTOGEN = ParseCases(FNM_PARSE_AUTOGEN)

        for key, case, rest in DATA_PARSE_AUTOGEN.iterate(True):
            for idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                if not (c.startswith('**SyntaxError(') and r.startswith('**SyntaxError(')):  # because we will get different texts for different py versions
                    self.assertEqual(c, r, f'{key = }, {case.idx = }, rest {idx = }')

    def test_unparse(self):
        self.assertEqual('for i in j', px.unparse(FST('[i for i in j]').generators[0].a))

        for op in (Add, Sub, Mult, Div, Mod, Pow, LShift, RShift, BitOr, BitXor, BitAnd, FloorDiv, And, Or):
            self.assertEqual(OPCLS2STR[op], px.unparse(FST(f'a {OPCLS2STR[op]} b').op.a))

        for op in (Add, Sub, Mult, Div, Mod, Pow, LShift, RShift, BitOr, BitXor, BitAnd, FloorDiv):
            self.assertEqual(OPCLS2STR[op], px.unparse(FST(f'a {OPCLS2STR[op]}= b').op.a))

        for op in (Invert, Not, UAdd, USub):
            self.assertEqual(OPCLS2STR[op], px.unparse(FST(f'{OPCLS2STR[op]} a').op.a))

        for op in (Eq, NotEq, Lt, LtE, Gt, GtE, Is, IsNot, In, NotIn):
            self.assertEqual(OPCLS2STR[op], px.unparse(FST(f'a {OPCLS2STR[op]} b').ops[0].a))

    def test_parse(self):
        for mode, func, res, src in PARSE_TESTS:
            try:
                test = 'parse'
                ast  = None
                unp  = None

                try:
                    ast = px.parse(src, mode)

                except SyntaxError as exc:
                    if res is not exc.__class__:
                        raise

                else:
                    if issubclass(res, Exception):
                        raise RuntimeError(f'expected {res.__name__}')

                    ref = func(src)

                    self.assertEqual(ast.__class__, res)
                    self.assertTrue(compare_asts(ast, ref, locs=True))

                if issubclass(res, Exception) or (isinstance(mode, str) and mode.startswith('_')):
                    continue

                # reparse

                if (src != '*=' and  # augassign is ambiguous for unparse
                    (src or func not in (px.parse_aliases, px.parse_Import_names, px.parse_ImportFrom_names))  # these unparse to '()' which can't be reparsed as these
                ):
                    test = 'reparse'
                    unp  = ((s := px.unparse(ast)) and s.lstrip()) or src  # 'lstrip' because comprehension has leading space, 'or src' because unparse of operators gives nothing
                    ast2 = px.parse(unp, mode)

                    compare_asts(ast, ast2, raise_=True)

                # trailing newline

                if (src != '*=' and                  # newline following augassign is syntactically impossible
                    func != px.parse_Assign_targets  # this can't take trailing newline
                ):
                    test = 'newline'
                    srcn = src + '\n'
                    ast  = px.parse(srcn, mode)

                # # IndentationError

                # test = 'indent'

                # if not src.startswith('\n') and src.strip():  # won't get IndentationError on stuff that starts with newlines or empty arguments
                #     src = ' ' + src

                #     self.assertRaises(IndentationError, px.parse, src, mode)
                #     self.assertRaises(IndentationError, func, src)

            except Exception:
                print()
                print(f'{test = }')
                print(f'{mode = }')
                print(f'{func = }')
                print(f'{res = }')
                print(f'{src = !r}')
                print(f'{ast = }')
                print(f'{unp = }')

                raise

    def test_parse_special(self):
        self.assertRaises(SyntaxError, px.parse_expr, 'i for i in j')
        self.assertRaises(SyntaxError, px.parse_expr_slice, 'i for i in j')
        self.assertRaises(SyntaxError, px.parse_expr_arglike, 'i for i in j')

        self.assertRaises(SyntaxError, px.parse_withitem, 'i for i in j')
        self.assertRaises(SyntaxError, px.parse_withitem, '')

    def test_code_as_simple(self):
        # stmts

        f = FST(r'''
if 1:
    pass

call(a)
'''.strip(), 'exec')

        h = code_as_stmts(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.a)
        self.assertTrue(compare_asts(h.a, f.a, locs=False, raise_=True))

        f0 = f.body[0].copy()
        h = code_as_stmts(f0.a)
        self.assertEqual(ast_unparse(f0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f0.a, locs=False, raise_=True))

        f1 = f.body[1].copy()
        h = code_as_stmts(f1.a)
        self.assertEqual(ast_unparse(f1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f1.a, locs=False, raise_=True))

        g = FST('from a import b', 'exec').body[0].names[0]
        self.assertRaises(ValueError, code_as_stmts, f.body[0].test)
        self.assertRaises(NodeError, code_as_stmts, g.copy())
        self.assertRaises(NodeError, code_as_stmts, g.a)
        self.assertRaises(SyntaxError, code_as_stmts, 'except Exception: pass')

        f = FST('f(a)', 'exec')
        h = code_as_stmts(f.body[0].value.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.src)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.a)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        # expr

        f = FST('a if b else {"c": f()}', 'eval')

        h = code_as_expr(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body.a, locs=True, raise_=True))

        f = FST('a if b else {"c": f()}', 'single')

        h = code_as_expr(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        f = FST('a if b else {"c": f()}', 'exec')

        h = code_as_expr(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        h = code_as_expr(f.body[0].copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        h = code_as_expr(f.body[0].value.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        h = code_as_expr(f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        g = f.body[0].value.copy()
        h = code_as_expr(g.a)
        self.assertEqual(ast_unparse(g.a), h.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as_expr, FST('i = 1', 'exec').body[0])
        self.assertRaises(NodeError, code_as_expr, FST('i = 1', 'exec').body[0].copy())
        self.assertRaises(NodeError, code_as_expr, f.body[0].a)
        self.assertRaises(SyntaxError, code_as_expr, 'pass')

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

        h = code_as_ExceptHandlers(g.copy())
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = code_as_ExceptHandlers(g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.body[0].copy()
        h = code_as_ExceptHandlers(g0.a)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = code_as_ExceptHandlers(g1.a)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as_ExceptHandlers, f.body[0].handlers[0])

        self.assertEqual(0, len(code_as_ExceptHandlers('').body))  # make sure we can parse zero ExceptHandlers

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

        h = code_as_match_cases(g.copy())
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = code_as_match_cases(g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.body[0].copy()
        h = code_as_match_cases(g0.a)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = code_as_match_cases(g1.a)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as_match_cases, f.body[0].cases[0])

        self.assertEqual(0, len(code_as_match_cases('').body))  # make sure we can parse zero match_cases

        # boolop

        f = FST(And(), ['and'])

        h = code_as_boolop(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_boolop(f.a)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=False, raise_=True))

        h = code_as_boolop(f.src)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        # rest of AST ones

        CODE_ASES = [
            (code_as_expr_slice, 'body[0].value.slice', 'a[1]'),
            (code_as_expr_slice, 'body[0].value.slice', 'a[b:c:d]'),
            (code_as_expr_slice, 'body[0].value.slice', 'a[b:c:d, e:f]'),
            (code_as_binop, 'body[0].value.op', 'a + b'),
            (code_as_augop, 'body[0].op', 'a += b'),
            (code_as_unaryop, 'body[0].value.op', '~a'),
            (code_as_cmpop, 'body[0].value.ops[0]', 'a < b'),
            (code_as_comprehension, 'body[0].value.generators[0]', '[i for i in j if i < 0]'),
            (code_as_arguments, 'body[0].args', 'def f(a: str, /, b: int = 1, *c: tuple[bool], d: float = 2.0, **e: dict): pass'),
            (code_as_arguments_lambda, 'body[0].value.args', 'lambda a, /, b=1, *c, d=2, **e: None'),
            (code_as_arg, 'body[0].args.args[0]', 'def f(a: str = "test"): pass'),
            (code_as_keyword, 'body[0].keywords[0]', 'class cls(meta=something): pass'),
            (code_as_keyword, 'body[0].value.keywords[0]', 'call(key = word)'),
            (code_as_alias, 'body[0].names[0]', 'from a import b'),
            (code_as_alias, 'body[0].names[0]', 'from a import *'),
            (code_as_alias, 'body[0].names[0]', 'import a.b'),
            (code_as_Import_name, 'body[0].names[0]', 'import a'),
            (code_as_Import_name, 'body[0].names[0]', 'import a.b'),
            (code_as_ImportFrom_name, 'body[0].names[0]', 'from a import b'),
            (code_as_ImportFrom_name, 'body[0].names[0]', 'from a import *'),
            (code_as_withitem, 'body[0].items[0]', 'with a: pass'),
            (code_as_withitem, 'body[0].items[0]', 'with (a): pass'),
            (code_as_withitem, 'body[0].items[0]', 'with a as b: pass'),
            (code_as_withitem, 'body[0].items[0]', 'with (a as b): pass'),
            (code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case 42: pass'),
            (code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case None: pass'),
            (code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case [_, *_]: pass'),
            (code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case {"key": _}: pass'),
            (code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case SomeClass(attr=val): pass'),
            (code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case as_var: pass'),
            (code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case 1 | 2 | 3: pass'),
            (code_as_pattern, 'body[0].cases[0].pattern', 'match x:\n case _: pass'),
        ]

        if PYGE12:
            CODE_ASES.extend([
                (code_as_type_param, 'body[0].type_params[0]', 'type t[T: int] = ...'),
                (code_as_type_param, 'body[0].type_params[0]', 'class c[T: int]: pass'),
                (code_as_type_param, 'body[0].type_params[0]', 'def f[T: int](): pass'),
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

        self.assertEqual('name', code_as_identifier(f.copy()))
        self.assertEqual('name', code_as_identifier(f.a))
        self.assertEqual('name', code_as_identifier(f.src))

        self.assertEqual('name', code_as_identifier_alias(f.copy()))
        self.assertEqual('name', code_as_identifier_alias(f.a))
        self.assertEqual('name', code_as_identifier_alias(f.src))

        f = FST('name.attr', 'exec').body[0].value.copy()

        self.assertEqual('name.attr', code_as_identifier_dotted(f.copy()))
        self.assertEqual('name.attr', code_as_identifier_dotted(f.a))
        self.assertEqual('name.attr', code_as_identifier_dotted(f.src))

        self.assertEqual('name.attr', code_as_identifier_alias(f.copy()))
        self.assertEqual('name.attr', code_as_identifier_alias(f.a))
        self.assertEqual('name.attr', code_as_identifier_alias(f.src))

        f = FST('from a import *', 'exec').body[0].names[0].copy()

        self.assertEqual('*', code_as_identifier_star(f.copy()))
        self.assertEqual('*', code_as_identifier_star(f.a))
        self.assertEqual('*', code_as_identifier_star(f.src))

        self.assertEqual('*', code_as_identifier_alias(f.copy()))
        self.assertEqual('*', code_as_identifier_alias(f.a))
        self.assertEqual('*', code_as_identifier_alias(f.src))

    def test_code_as_stmts(self):
        f = FST(r'''
if 1:
    pass

call(a)
'''.strip(), 'exec')

        h = code_as_stmts(f.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.a)
        self.assertTrue(compare_asts(h.a, f.a, locs=False, raise_=True))

        f0 = f.body[0].copy()
        h = code_as_stmts(f0.a)
        self.assertEqual(ast_unparse(f0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f0.a, locs=False, raise_=True))

        f1 = f.body[1].copy()
        h = code_as_stmts(f1.a)
        self.assertEqual(ast_unparse(f1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f1.a, locs=False, raise_=True))

        g = FST('from a import b', 'exec').body[0].names[0]
        self.assertRaises(ValueError, code_as_stmts, f.body[0].test)
        self.assertRaises(NodeError, code_as_stmts, g.copy())
        self.assertRaises(NodeError, code_as_stmts, g.a)

        f = FST('f(a)', 'exec')
        h = code_as_stmts(f.body[0].value.copy())
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.src)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.a)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

    def test_code_as_ExceptHandlers(self):
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

        h = code_as_ExceptHandlers(g.copy())
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = code_as_ExceptHandlers(g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.body[0].copy()
        h = code_as_ExceptHandlers(g0.a)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = code_as_ExceptHandlers(g1.a)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as_ExceptHandlers, f.body[0].handlers[0])

    def test_code_as_match_cases(self):
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

        h = code_as_match_cases(g.copy())
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = code_as_match_cases(g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.body[0].copy()
        h = code_as_match_cases(g0.a)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g0.a, locs=False, raise_=True))

        g1 = g.body[1].copy()
        h = code_as_match_cases(g1.a)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as_match_cases, f.body[0].cases[0])

        # special 'case' non-keyword

        self.assertIsInstance(code_as_match_cases('case 1: pass').body[0].a, match_case)
        self.assertRaises(SyntaxError, code_as_match_cases, 'case = 1')
        self.assertRaises(SyntaxError, code_as_match_cases, 'case.b = 1')

    def test_code_as_sanitize(self):
        CODE_ASES = [
            (code_as_expr, 'f(a)'),
            (code_as_expr_slice, 'b:c:d'),
            (code_as_expr_slice, 'b:c:d, e:f'),
            (code_as_binop, '+'),
            (code_as_augop, '+='),
            (code_as_unaryop, '~'),
            (code_as_cmpop, '<'),
            (code_as_comprehension, 'for i in j if i < 0'),
            (code_as_arguments, 'a: str, /, b: int = 1, *c: tuple[bool], d: float = 2.0, **e: dict'),
            (code_as_arguments_lambda, 'a, /, b=1, *c, d=2, **e'),
            (code_as_arg, 'a: str'),
            (code_as_keyword, 'meta=something'),
            (code_as_keyword, 'key = word'),
            (code_as_Import_name, 'a'),
            (code_as_Import_name, 'a.b'),
            (code_as_ImportFrom_name, 'b'),
            (code_as_ImportFrom_name, '*'),
            (code_as_withitem, 'a'),
            (code_as_withitem, 'a as b'),
            (code_as_pattern, '42'),
            (code_as_pattern, 'None'),
            (code_as_pattern, '[_, *_]'),
            (code_as_pattern, '{"key": _}'),
            (code_as_pattern, 'SomeClass(attr=val)'),
            (code_as_pattern, 'as_var'),
            (code_as_pattern, '1 | 2 | 3'),
            (code_as_pattern, '_'),
        ]

        if PYGE12:
            CODE_ASES.extend([
                (code_as_type_param, 'T: int'),
            ])

        for code_as, src in CODE_ASES:
            self.assertEqual(src, code_as(src).src)
            self.assertEqual(src, code_as(f'{src}  ').src)

            if code_as in (code_as_expr, code_as_pattern):  # parenthesizable things so lets abuse
                srcp = f'(\n# pre\n{src} # post\n# post2\n)'

                self.assertEqual(srcp, code_as(srcp).src)

                if code_as is code_as_expr:
                    self.assertEqual(src, code_as(srcp[1:-1]).src)

    def test_code_as_all_from_ast(self):
        for mode, func, res, src in PARSE_TESTS:
            if issubclass(res, Exception):
                continue

            ast = None

            try:
                ast = px.parse(src, mode)

                if px.get_special_parse_mode(ast):  # this tells us if it is a SPECIAL SLICE, which are not handled as input to `code_as_all()`  TODO: remove this check once ExceptHandler and match_case special slices moved from Module to their own _slice_? AST classes
                    continue

                astc = copy_ast(ast)
                fst  = code_as_all(ast)

                for a in walk(ast):
                    self.assertIs(False, getattr(a, 'f', False))

                self.assertIsNot(fst.a, ast)

                compare_asts(ast, fst.a, locs=False, raise_=True)
                compare_asts(ast, astc, locs=True, raise_=True)

            except Exception:
                print()
                print(f'{mode = }')
                print(f'{func = }')
                print(f'{res = }')
                print(f'{src = !r}')
                print(ast)

                raise

    def test_code_as_from_parse_data(self):
        for mode, func, res, src in PARSE_TESTS:
            if issubclass(res, Exception):
                continue

            if not isinstance(mode, str):
                continue

            try:
                for name in dict.fromkeys((mode, func.__name__[6:])):  # func.__name__[6:] means 'parse_something' -> 'something'
                    test = None

                    if not (code_as := getattr(code, f'code_as_{name}', False)):
                        continue

                    test    = 'parse'
                    ref_ast = px.parse(src, mode)

                    test = 'src'

                    try:
                        fst = code_as(src, sanitize=False)
                    except TypeError:
                        fst = code_as(src)

                    compare_asts(ref_ast, fst.a, locs=True, raise_=True)

                    if fst._get_parse_mode() not in ('ExceptHandlers', 'match_cases'):  # this tells us if it is a SPECIAL SLICE, which can not be unparsed  TODO: remove this check once ExceptHandler and match_case special slices moved from Module to their own _slice_? AST classes
                        test = 'ast'

                        try:
                            ast_fst = code_as(fst.a, sanitize=False)
                        except TypeError:
                            ast_fst = code_as(fst.a)

                        compare_asts(ref_ast, ast_fst.a, locs=False, raise_=True)

                    test    = 'fst'
                    fst_src = fst.src

                    try:
                        fst_fst = code_as(fst, sanitize=False)
                    except TypeError:
                        fst_fst = code_as(fst)

                    compare_asts(ref_ast, fst_fst.a, locs=False, raise_=True)

                    self.assertEqual(fst_fst.src, fst_src)

            except Exception:
                print()
                print(f'{test = }')
                print(f'{code_as = }')
                print(f'{mode = }')
                print(f'{func = }')
                print(f'{res = }')
                print(f'{src = !r}')

                raise

    def test_code_as_special(self):
        # aliases slice multiple stars

        self.assertRaises(ParseError, code_as_ImportFrom_names, FST('*', 'aliases').names.append('*').fst)
        self.assertRaises(ParseError, code_as_ImportFrom_names, FST('a', 'aliases').names.append('*').fst)
        self.assertEqual('*', code_as_ImportFrom_names(FST('*', 'aliases')).src)

    def test_loc_operator_no_parent(self):
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

    def test_loc_block_header_end(self):
        self.assertEqual((0, 15), loc_block_header_end(parse('def f(a) -> int: pass').body[0].f))
        self.assertEqual((0, 8),  loc_block_header_end(parse('def f(a): pass').body[0].f))
        self.assertEqual((0, 7),  loc_block_header_end(parse('def f(): pass').body[0].f))
        self.assertEqual((0, 21), loc_block_header_end(parse('async def f(a) -> int: pass').body[0].f))
        self.assertEqual((0, 14), loc_block_header_end(parse('async def f(a): pass').body[0].f))
        self.assertEqual((0, 13), loc_block_header_end(parse('async def f(): pass').body[0].f))
        self.assertEqual((0, 26), loc_block_header_end(parse('class cls(base, keyword=1): pass').body[0].f))
        self.assertEqual((0, 15), loc_block_header_end(parse('class cls(base): pass').body[0].f))
        self.assertEqual((0, 10), loc_block_header_end(parse('for a in b: pass\nelse: pass').body[0].f))
        self.assertEqual((0, 16), loc_block_header_end(parse('async for a in b: pass\nelse: pass').body[0].f))
        self.assertEqual((0, 7),  loc_block_header_end(parse('while a: pass\nelse: pass').body[0].f))
        self.assertEqual((0, 4),  loc_block_header_end(parse('if a: pass\nelse: pass').body[0].f))
        self.assertEqual((0, 8),  loc_block_header_end(parse('with f(): pass').body[0].f))
        self.assertEqual((0, 13), loc_block_header_end(parse('with f() as v: pass').body[0].f))
        self.assertEqual((0, 14), loc_block_header_end(parse('async with f(): pass').body[0].f))
        self.assertEqual((0, 19), loc_block_header_end(parse('async with f() as v: pass').body[0].f))
        self.assertEqual((0, 7),  loc_block_header_end(parse('match a:\n case 2: pass').body[0].f))
        self.assertEqual((1, 7),  loc_block_header_end(parse('match a:\n case 2: pass').body[0].cases[0].f))
        self.assertEqual((1, 15), loc_block_header_end(parse('match a:\n case 2 if True: pass').body[0].cases[0].f))
        self.assertEqual((0, 3),  loc_block_header_end(parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].f))
        self.assertEqual((1, 6),  loc_block_header_end(parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
        self.assertEqual((1, 16), loc_block_header_end(parse('try: pass\nexcept Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
        self.assertEqual((1, 33), loc_block_header_end(parse('try: pass\nexcept (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
        self.assertEqual((1, 38), loc_block_header_end(parse('try: pass\nexcept (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))

        if PYGE12:
            self.assertEqual((0, 3),  loc_block_header_end(parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].f))
            self.assertEqual((1, 17), loc_block_header_end(parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
            self.assertEqual((1, 34), loc_block_header_end(parse('try: pass\nexcept* (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
            self.assertEqual((1, 39), loc_block_header_end(parse('try: pass\nexcept* (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
            self.assertEqual((0, 12), loc_block_header_end(parse('class cls[T]: pass').body[0].f))

        self.assertEqual((0, 15, 0, 15), loc_block_header_end(parse('def f(a) -> int: pass').body[0].f, True))
        self.assertEqual((0, 8, 0, 7), loc_block_header_end(parse('def f(a): pass').body[0].f, True))
        self.assertEqual((0, 7, 0, 0), loc_block_header_end(parse('def f(): pass').body[0].f, True))
        self.assertEqual((0, 21, 0, 21), loc_block_header_end(parse('async def f(a) -> int: pass').body[0].f, True))
        self.assertEqual((0, 14, 0, 13), loc_block_header_end(parse('async def f(a): pass').body[0].f, True))
        self.assertEqual((0, 13, 0, 0), loc_block_header_end(parse('async def f(): pass').body[0].f, True))
        self.assertEqual((0, 26, 0, 25), loc_block_header_end(parse('class cls(base, keyword=1): pass').body[0].f, True))
        self.assertEqual((0, 15, 0, 14), loc_block_header_end(parse('class cls(base): pass').body[0].f, True))
        self.assertEqual((0, 10, 0, 10), loc_block_header_end(parse('for a in b: pass\nelse: pass').body[0].f, True))
        self.assertEqual((0, 16, 0, 16), loc_block_header_end(parse('async for a in b: pass\nelse: pass').body[0].f, True))
        self.assertEqual((0, 7, 0, 7), loc_block_header_end(parse('while a: pass\nelse: pass').body[0].f, True))
        self.assertEqual((0, 4, 0, 4), loc_block_header_end(parse('if a: pass\nelse: pass').body[0].f, True))
        self.assertEqual((0, 8, 0, 8), loc_block_header_end(parse('with f(): pass').body[0].f, True))
        self.assertEqual((0, 13, 0, 13), loc_block_header_end(parse('with f() as v: pass').body[0].f, True))
        self.assertEqual((0, 14, 0, 14), loc_block_header_end(parse('async with f(): pass').body[0].f, True))
        self.assertEqual((0, 19, 0, 19), loc_block_header_end(parse('async with f() as v: pass').body[0].f, True))
        self.assertEqual((0, 7, 0, 7), loc_block_header_end(parse('match a:\n case 2: pass').body[0].f, True))
        self.assertEqual((1, 7, 1, 7), loc_block_header_end(parse('match a:\n case 2: pass').body[0].cases[0].f, True))
        self.assertEqual((1, 15, 1, 15), loc_block_header_end(parse('match a:\n case 2 if True: pass').body[0].cases[0].f, True))
        self.assertEqual((0, 3, 0, 0), loc_block_header_end(parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].f, True))
        self.assertEqual((1, 6, 1, 0), loc_block_header_end(parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f, True))
        self.assertEqual((1, 16, 1, 16), loc_block_header_end(parse('try: pass\nexcept Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f, True))
        self.assertEqual((1, 33, 1, 33), loc_block_header_end(parse('try: pass\nexcept (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f, True))
        self.assertEqual((1, 38, 1, 33), loc_block_header_end(parse('try: pass\nexcept (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f, True))

        if PYGE12:
            self.assertEqual((0, 3, 0, 0), loc_block_header_end(parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].f, True))
            self.assertEqual((1, 17, 1, 17), loc_block_header_end(parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f, True))
            self.assertEqual((1, 34, 1, 34), loc_block_header_end(parse('try: pass\nexcept* (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f, True))
            self.assertEqual((1, 39, 1, 34), loc_block_header_end(parse('try: pass\nexcept* (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f, True))
            self.assertEqual((0, 12, 0, 11), loc_block_header_end(parse('class cls[T]: pass').body[0].f, True))

        self.assertEqual((0, 17, 0, 16), loc_block_header_end(parse('def f(a) -> (int): pass').body[0].f, True))
        self.assertEqual((0, 28, 0, 27), loc_block_header_end(parse('class cls(base, keyword=(1)): pass').body[0].f, True))
        self.assertEqual((0, 17, 0, 15), loc_block_header_end(parse('class cls((base)): pass').body[0].f, True))
        self.assertEqual((0, 12, 0, 11), loc_block_header_end(parse('for a in (b): pass\nelse: pass').body[0].f, True))

    def test_loc_ClassDef_bases_pars(self):
        self.assertEqual('fstlocn(0, 9, 0, 9, n=0)', str(loc_ClassDef_bases_pars(FST('class cls: pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 10, n=0)', str(loc_ClassDef_bases_pars(FST('class cls : pass'))))
        self.assertEqual('fstlocn(1, 3, 1, 4, n=0)', str(loc_ClassDef_bases_pars(FST('class \\\ncls : pass'))))
        self.assertEqual('fstlocn(0, 9, 1, 0, n=0)', str(loc_ClassDef_bases_pars(FST('class cls \\\n: pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 11, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(): pass'))))
        self.assertEqual('fstlocn(1, 0, 1, 2, n=1)', str(loc_ClassDef_bases_pars(FST('class cls\\\n(): pass'))))
        self.assertEqual('fstlocn(0, 9, 1, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(\n): pass'))))
        self.assertEqual('fstlocn(1, 0, 2, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n(\n): pass'))))

        self.assertEqual('fstlocn(0, 9, 0, 12, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(b): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 14, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(k=v): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 14, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(**v): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 17, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(b, k=v): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 17, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(b, **v): pass'))))
        self.assertEqual('fstlocn(0, 9, 2, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(\nb\n): pass'))))
        self.assertEqual('fstlocn(1, 1, 3, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n (\nb\n) \\\n: pass'))))

        self.assertEqual('fstlocn(0, 9, 0, 13, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(b,): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 15, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(k=v,): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 15, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(**v,): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 18, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(b, k=v,): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 18, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(b, **v,): pass'))))
        self.assertEqual('fstlocn(0, 9, 3, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls(\nb\n,\n): pass'))))
        self.assertEqual('fstlocn(1, 1, 4, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n (\nb\n,\n) \\\n: pass'))))

        if PYGE12:
            self.assertEqual('fstlocn(0, 12, 0, 12, n=0)', str(loc_ClassDef_bases_pars(FST('class cls[T]: pass'))))
            self.assertEqual('fstlocn(0, 12, 0, 13, n=0)', str(loc_ClassDef_bases_pars(FST('class cls[T] : pass'))))
            self.assertEqual('fstlocn(0, 13, 0, 13, n=0)', str(loc_ClassDef_bases_pars(FST('class cls[T,]: pass'))))
            self.assertEqual('fstlocn(0, 12, 0, 14, n=1)', str(loc_ClassDef_bases_pars(FST('class cls[T](): pass'))))
            self.assertEqual('fstlocn(0, 13, 0, 15, n=1)', str(loc_ClassDef_bases_pars(FST('class cls[T,](): pass'))))
            self.assertEqual('fstlocn(0, 15, 0, 17, n=1)', str(loc_ClassDef_bases_pars(FST('class cls[T, U](): pass'))))
            self.assertEqual('fstlocn(1, 3, 1, 5, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n[T](): pass'))))
            self.assertEqual('fstlocn(2, 1, 2, 3, n=1)', str(loc_ClassDef_bases_pars(FST('class cls[\nT\n](): pass'))))
            self.assertEqual('fstlocn(3, 1, 3, 3, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n](): pass'))))
            self.assertEqual('fstlocn(4, 0, 5, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n]\\\n(\n): pass'))))
            self.assertEqual('fstlocn(6, 0, 7, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n,\nU\n]\\\n( \\\n): pass'))))

            self.assertEqual('fstlocn(0, 12, 0, 15, n=1)', str(loc_ClassDef_bases_pars(FST('class cls[T](b): pass'))))
            self.assertEqual('fstlocn(0, 18, 0, 25, n=1)', str(loc_ClassDef_bases_pars(FST('class cls[T, **U,]( b , ): pass'))))
            self.assertEqual('fstlocn(1, 3, 1, 6, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n[T](b): pass'))))
            self.assertEqual('fstlocn(2, 1, 2, 4, n=1)', str(loc_ClassDef_bases_pars(FST('class cls[\nT\n](b): pass'))))
            self.assertEqual('fstlocn(3, 1, 3, 4, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n](b): pass'))))

            self.assertEqual('fstlocn(4, 0, 7, 1, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n]\\\n(\nb\n,\n): pass'))))
            self.assertEqual('fstlocn(6, 0, 7, 3, n=1)', str(loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n,\nU\n]\\\n( \\\nb,): pass'))))

    def test_loc_ImportFrom_names_pars(self):
        self.assertEqual('fstlocn(0, 14, 0, 15, n=0)', str(loc_ImportFrom_names_pars(FST('from . import a'))))
        self.assertEqual('fstlocn(0, 14, 0, 17, n=1)', str(loc_ImportFrom_names_pars(FST('from . import (a)'))))
        self.assertEqual('fstlocn(0, 14, 2, 1, n=1)', str(loc_ImportFrom_names_pars(FST('from . import (\na\n)'))))
        self.assertEqual('fstlocn(1, 0, 3, 1, n=1)', str(loc_ImportFrom_names_pars(FST('from . import \\\n(\na\n)'))))
        self.assertEqual('fstlocn(0, 14, 1, 1, n=0)', str(loc_ImportFrom_names_pars(FST('from . import \\\na'))))
        self.assertEqual('fstlocn(0, 13, 1, 1, n=0)', str(loc_ImportFrom_names_pars(FST('from . import\\\na'))))

        self.assertEqual('fstlocn(0, 22, 0, 23, n=0)', str(loc_ImportFrom_names_pars(FST('from importlib import b'))))
        self.assertEqual('fstlocn(0, 22, 1, 1, n=0)', str(loc_ImportFrom_names_pars(FST('from importlib import \\\nb'))))
        self.assertEqual('fstlocn(0, 22, 0, 25, n=1)', str(loc_ImportFrom_names_pars(FST('from importlib import (b)'))))
        self.assertEqual('fstlocn(0, 22, 2, 1, n=1)', str(loc_ImportFrom_names_pars(FST('from importlib import (\nb\n)'))))

        f = FST('from . import a')
        f._put_src(None, 0, 14, 0, 15, True)
        del f.a.names[:]
        self.assertEqual('fstlocn(0, 14, 0, 14, n=0)', str(loc_ImportFrom_names_pars(f)))
        f._put_src(None, 0, 13, 0, 14, True)
        self.assertEqual('fstlocn(0, 13, 0, 13, n=0)', str(loc_ImportFrom_names_pars(f)))
        f._put_src('\n', 0, 13, 0, 13, True)
        self.assertEqual('fstlocn(0, 13, 1, 0, n=0)', str(loc_ImportFrom_names_pars(f)))

    def test_loc_With_items_pars(self):
        def str_(loc_ret):
            del loc_ret.bound

            return str(loc_ret)

        self.assertEqual('fstlocn(0, 5, 0, 6, n=0)', str_(loc_With_items_pars(FST('with a: pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 8, n=0)', str_(loc_With_items_pars(FST('with (a): pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 13, n=1)', str_(loc_With_items_pars(FST('with (a as b): pass'))))
        self.assertEqual('fstlocn(0, 5, 2, 1, n=1)', str_(loc_With_items_pars(FST('with (\na as b\n): pass'))))
        self.assertEqual('fstlocn(1, 0, 3, 1, n=1)', str_(loc_With_items_pars(FST('with \\\n(\na as b\n): pass'))))
        self.assertEqual('fstlocn(0, 5, 1, 1, n=0)', str_(loc_With_items_pars(FST('with \\\na: pass'))))
        self.assertEqual('fstlocn(0, 4, 1, 1, n=0)', str_(loc_With_items_pars(FST('with\\\na: pass'))))
        self.assertEqual('fstlocn(0, 4, 3, 0, n=0)', str_(loc_With_items_pars(FST('with\\\n\\\na\\\n: pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 8, n=0)', str_(loc_With_items_pars(FST('with  a : pass'))))
        self.assertEqual('fstlocn(0, 6, 0, 14, n=1)', str_(loc_With_items_pars(FST('with  (a as b)  : pass'))))

        self.assertEqual('fstlocn(0, 11, 0, 12, n=0)', str_(loc_With_items_pars(FST('async with a: pass'))))
        self.assertEqual('fstlocn(0, 11, 0, 14, n=0)', str_(loc_With_items_pars(FST('async with (a): pass'))))
        self.assertEqual('fstlocn(0, 11, 0, 19, n=1)', str_(loc_With_items_pars(FST('async with (a as b): pass'))))
        self.assertEqual('fstlocn(0, 11, 2, 1, n=1)', str_(loc_With_items_pars(FST('async with (\na as b\n): pass'))))
        self.assertEqual('fstlocn(1, 0, 3, 1, n=1)', str_(loc_With_items_pars(FST('async with \\\n(\na as b\n): pass'))))
        self.assertEqual('fstlocn(0, 11, 1, 1, n=0)', str_(loc_With_items_pars(FST('async with \\\na: pass'))))
        self.assertEqual('fstlocn(0, 10, 1, 1, n=0)', str_(loc_With_items_pars(FST('async with\\\na: pass'))))
        self.assertEqual('fstlocn(0, 10, 3, 0, n=0)', str_(loc_With_items_pars(FST('async with\\\n\\\na\\\n: pass'))))
        self.assertEqual('fstlocn(0, 11, 0, 14, n=0)', str_(loc_With_items_pars(FST('async with  a : pass'))))
        self.assertEqual('fstlocn(0, 12, 0, 20, n=1)', str_(loc_With_items_pars(FST('async with  (a as b)  : pass'))))

        self.assertEqual('fstlocn(1, 6, 1, 7, n=0)', str_(loc_With_items_pars(FST('async \\\n with a: pass'))))
        self.assertEqual('fstlocn(1, 6, 1, 9, n=0)', str_(loc_With_items_pars(FST('async \\\n with (a): pass'))))
        self.assertEqual('fstlocn(1, 6, 1, 14, n=1)', str_(loc_With_items_pars(FST('async \\\n with (a as b): pass'))))
        self.assertEqual('fstlocn(1, 6, 3, 1, n=1)', str_(loc_With_items_pars(FST('async \\\n with (\na as b\n): pass'))))
        self.assertEqual('fstlocn(2, 0, 4, 1, n=1)', str_(loc_With_items_pars(FST('async \\\n with \\\n(\na as b\n): pass'))))
        self.assertEqual('fstlocn(1, 6, 2, 1, n=0)', str_(loc_With_items_pars(FST('async \\\n with \\\na: pass'))))
        self.assertEqual('fstlocn(1, 5, 2, 1, n=0)', str_(loc_With_items_pars(FST('async \\\n with\\\na: pass'))))
        self.assertEqual('fstlocn(1, 5, 4, 0, n=0)', str_(loc_With_items_pars(FST('async \\\n with\\\n\\\na\\\n: pass'))))
        self.assertEqual('fstlocn(1, 6, 1, 9, n=0)', str_(loc_With_items_pars(FST('async \\\n with  a : pass'))))
        self.assertEqual('fstlocn(1, 7, 1, 15, n=1)', str_(loc_With_items_pars(FST('async \\\n with  (a as b)  : pass'))))

        f = FST('with a: pass')
        f._put_src(None, 0, 5, 0, 6, True)
        del f.a.items[:]
        self.assertEqual('fstlocn(0, 5, 0, 5, n=0)', str_(loc_With_items_pars(f)))
        f._put_src(None, 0, 4, 0, 5, True)
        self.assertEqual('fstlocn(0, 4, 0, 4, n=0)', str_(loc_With_items_pars(f)))
        f._put_src('\n', 0, 4, 0, 4, True)
        self.assertEqual('fstlocn(0, 4, 1, 0, n=0)', str_(loc_With_items_pars(f)))

        self.assertEqual('fstlocn(0, 5, 0, 8, n=0)', str_(loc_With_items_pars(FST('with (a): pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 13, n=0)', str_(loc_With_items_pars(FST('with (a) as b: pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 15, n=1)', str_(loc_With_items_pars(FST('with ((a) as b): pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 15, n=0)', str_(loc_With_items_pars(FST('with (a) as (b): pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 17, n=1)', str_(loc_With_items_pars(FST('with ((a) as (b)): pass'))))

    def test_loc_Call_pars(self):
        self.assertEqual((0, 4, 0, 6), loc_Call_pars(FST('call()', 'exec').body[0].value))
        self.assertEqual((0, 4, 0, 7), loc_Call_pars(FST('call(a)', 'exec').body[0].value))
        self.assertEqual((0, 4, 2, 1), loc_Call_pars(FST('call(\na\n)', 'exec').body[0].value))
        self.assertEqual((0, 4, 2, 1), loc_Call_pars(FST('call(\na, b=2\n)', 'exec').body[0].value))
        self.assertEqual((0, 4, 0, 12), loc_Call_pars(FST('call(c="()")', 'exec').body[0].value))
        self.assertEqual((1, 0, 8, 1), loc_Call_pars(FST('call\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n)', 'exec').body[0].value))
        self.assertEqual((1, 0, 8, 1), loc_Call_pars(FST('"()("\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n)', 'exec').body[0].value))

    def test_loc_Subscript_brackets(self):
        self.assertEqual((0, 1, 0, 4), loc_Subscript_brackets(FST('a[b]', 'exec').body[0].value))
        self.assertEqual((0, 1, 0, 8), loc_Subscript_brackets(FST('a[b:c:d]', 'exec').body[0].value))
        self.assertEqual((0, 1, 0, 7), loc_Subscript_brackets(FST('a["[]"]', 'exec').body[0].value))
        self.assertEqual((1, 0, 7, 1), loc_Subscript_brackets(FST('a\\\n[\nb\n:\nc\n:\nd\n]', 'exec').body[0].value))
        self.assertEqual((1, 0, 7, 1), loc_Subscript_brackets(FST('"[]["\\\n[\nb\n:\nc\n:\nd\n]', 'exec').body[0].value))

    def test_loc_MatchClass_pars(self):
        self.assertEqual((1, 9, 1, 11), loc_MatchClass_pars(FST('match a:\n case cls(): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((1, 9, 1, 12), loc_MatchClass_pars(FST('match a:\n case cls(a): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((1, 9, 3, 1), loc_MatchClass_pars(FST('match a:\n case cls(\na\n): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((1, 9, 3, 1), loc_MatchClass_pars(FST('match a:\n case cls(\na, b=2\n): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((1, 9, 1, 17), loc_MatchClass_pars(FST('match a:\n case cls(c="()"): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((2, 0, 9, 1), loc_MatchClass_pars(FST('match a:\n case cls\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n): pass', 'exec').body[0].cases[0].pattern))

    def test__is_atom(self):
        self.assertIs(False, parse('1 + 2').body[0].value.f._is_atom())
        self.assertEqual('unenclosable', parse('f()').body[0].value.f._is_atom())
        self.assertEqual('pars', parse('(1 + 2)').body[0].value.f._is_atom())
        self.assertIs(False, parse('(1 + 2)').body[0].value.f._is_atom(pars=False))

        self.assertIs(False, parse('1, 2').body[0].value.f._is_atom())
        self.assertIs(True, parse('(1, 2)').body[0].value.f._is_atom())
        self.assertIs(True, parse('[1, 2]').body[0].value.f._is_atom())

        self.assertIs(False, parse('match a:\n case 1, 2: pass').body[0].cases[0].pattern.f._is_atom())
        self.assertIs(True, parse('match a:\n case (1, 2): pass').body[0].cases[0].pattern.f._is_atom())
        self.assertIs(True, parse('match a:\n case [1, 2]: pass').body[0].cases[0].pattern.f._is_atom())

        self.assertIs(False, FST('*a')._is_atom())  # because of `*a or b`

    def test__is_enclosed_or_line_special(self):
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

        self.assertTrue(FST('f(a, b=1)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('f\\\n(a, b=1)', 'exec').body[0].copy(pars=False).value._is_enclosed_or_line())
        self.assertTrue(FST('(f\\\n(a, b=1))', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(f\n(a, b=1))', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(f(\na\n,\nb\n=\n1))', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(f(\na\n,\nb\n=\n"()"))', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        if PYGE12:
            self.assertTrue(FST(r'''
(f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
            self.assertFalse(FST(r'''
(f"a{(1,

2)}b" f"""{3}

{4}
{5}"""
f"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

            self.assertTrue(FST(r'''
(f"a" f"""c
b""" f"d\
\
e")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

            self.assertFalse(FST(r'''
(f"a" f"""c
b"""

f"d\
\
e")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a.b', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\n.\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n.\\\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a[b]', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\n[\nb\n])', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\n[(\nb\n)])', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n[(\nb\n)])', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n[\\\nb\\\n])', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case f(a, b=1): pass', 'exec').body[0].cases[0].pattern._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case f\\\n(a, b=1): pass', 'exec').body[0].cases[0].pattern._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f\\\n(a, b=1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (f\n(a, b=1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f(\na\n,\nb\n=\n1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f(\na\n,\nb\n=\n"()")): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case *s,: pass', 'exec').body[0].cases[0].pattern.patterns[0]._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (*\ns,): pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case *\\\ns,: pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (*\\\ns,): pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case a as b: pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a as b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\nas b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a\\\nas b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\\\nas\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a\\\nas\\\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\\\nas\n\\\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a not in b', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a not in b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a not\nin b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a not\\\nin b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a is\nnot b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a is\\\nnot b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('[i for\n i in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('[i for i\n in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('[i for i in\n j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('[i for\\\n i in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('[i for i\\\n in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('[i for i in\\\n j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('def f(a, b=1): pass', 'exec').body[0].args.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('def f(a,\n b=1): pass', 'exec').body[0].args.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('def f(a,\\\n b=1): pass', 'exec').body[0].args.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('def f(a, b=(1,\n2)): pass', 'exec').body[0].args.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('def f(a:\n int): pass', 'exec').body[0].args.args[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('def f(a:\\\n int): pass', 'exec').body[0].args.args[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('from a import (b as c)', 'exec').body[0].names[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('from a import (b\n as c)', 'exec').body[0].names[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('from a import (b\\\n as c)', 'exec').body[0].names[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('with (b as c): pass', 'exec').body[0].items[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('with (b\n as c): pass', 'exec').body[0].items[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('with (b\\\n as c): pass', 'exec').body[0].items[0].copy(pars=False)._is_enclosed_or_line())

        if PYGE14:
            self.assertTrue(FST(r'''
(t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
            self.assertFalse(FST(r'''
(t"a{(1,

2)}b" t"""{3}

{4}
{5}"""
t"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

    def test__is_enclosed_or_line_general(self):
        self.assertTrue(FST('a < b', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\n< b)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n< b)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\\\n<\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n<\\\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\\\n<\n\\\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a, b, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, b\\\n, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, [\nb\n], c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a, {\nx: y\n}, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, {\nb\n}, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, [\ni for i in j\n], c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, {\ni for i in j\n}, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, {\ni: j for i, j in k\n}, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, (\ni for i in j\n), c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, [i,\nj], c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, b[\ni:j:k\n], c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a\n: \nb: \nc', 'expr_slice')._is_enclosed_or_line())  # because is never used unenclosed
        self.assertTrue(FST('a\\\n: \\\nb: \\\nc', 'expr_slice')._is_enclosed_or_line())

        if PYGE12:
            self.assertTrue(FST('a, f"{(1,\n2)}", c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        # whole

        self.assertTrue(FST('\na + b\n')._is_enclosed_or_line(whole=False))
        self.assertFalse(FST('\na + b\n')._is_enclosed_or_line(whole=True))
        self.assertFalse(FST('\\\na + b\n')._is_enclosed_or_line(whole=True))
        self.assertFalse(FST('\na + b\\\n')._is_enclosed_or_line(whole=True))
        self.assertTrue(FST('\\\na + b\\\n')._is_enclosed_or_line(whole=True))

        self.assertTrue(FST('\na + b * c\n').right._is_enclosed_or_line(whole=False))
        self.assertRaises(ValueError, FST('\na + b * c\n').right._is_enclosed_or_line, whole=True)

        # out_lns

        self.assertTrue(FST('\na + \\\n(b\n*\nc)\n')._is_enclosed_or_line(whole=False, out_lns=(lns := set())))
        self.assertEqual(set(), lns)

        self.assertFalse(FST('\na + \n(b\n*\nc)\n')._is_enclosed_or_line(whole=False, out_lns=(lns := set())))
        self.assertEqual({1}, lns)

        self.assertFalse(FST('\na + \n(b\n*\nc)\n')._is_enclosed_or_line(whole=True, out_lns=(lns := set())))
        self.assertEqual({0, 1, 4}, lns)

        f = FST(r'''
a + \
("""
*"""
"c")
''')
        self.assertTrue(f._is_enclosed_or_line(whole=False, out_lns=(lns := set())))
        self.assertEqual(set(), lns)
        f.right.unpar()
        self.assertFalse(f._is_enclosed_or_line(whole=False, out_lns=(lns := set())))
        self.assertEqual({3}, lns)
        self.assertFalse(f._is_enclosed_or_line(whole=True, out_lns=(lns := set())))
        self.assertEqual({0, 3, 4}, lns)

        # ImportFrom

        self.assertTrue(FST('from a import \\\nb')._is_enclosed_or_line())
        self.assertTrue(FST('from a import (\nb)')._is_enclosed_or_line())

        f = FST('from a import (\nb)')
        f._put_src(None, 1, 1, 1, 2, True)
        f._put_src(None, 0, 14, 0, 15, False)
        self.assertFalse(f._is_enclosed_or_line())

        # With / AsyncWith

        self.assertTrue(FST('with \\\nb\\\n:\n  pass')._is_enclosed_or_line())
        self.assertTrue(FST('with (\nb\n):\n  pass')._is_enclosed_or_line())

        f = FST('with (\na\n):\n  pass')
        f._put_src(None, 2, 0, 2, 1, True)
        f._put_src(None, 0, 5, 0, 6, False)
        self.assertFalse(f._is_enclosed_or_line())

    def test__is_enclosed_or_multiline_str(self):
        self.assertTrue(FST(r'''["""a
b
c"""]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''["a \
b \
c"]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''["a" \
"b" \
"c"]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''["a" \
"b \
c"]''').elts[0]._is_enclosed_or_line())

        self.assertFalse(FST(r'''["a" \
"b"
"c"]''').elts[0]._is_enclosed_or_line())

        # f-string

        self.assertTrue(FST(r'''[f"""a
b
c"""]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''[f"a \
b \
c"]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''[f"a" \
f"b" \
f"c"]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''[f"a" \
f"b \
c"]''').elts[0]._is_enclosed_or_line())

        self.assertFalse(FST(r'''[f"a" \
f"b"
f"c"]''').elts[0]._is_enclosed_or_line())

        # t-string

        if PYGE14:
            self.assertTrue(FST(r'''[t"""a
b
c"""]''').elts[0]._is_enclosed_or_line())

            self.assertTrue(FST(r'''[t"a \
b \
c"]''').elts[0]._is_enclosed_or_line())

            self.assertTrue(FST(r'''[t"a" \
t"b" \
t"c"]''').elts[0]._is_enclosed_or_line())

            self.assertTrue(FST(r'''[t"a" \
t"b \
c"]''').elts[0]._is_enclosed_or_line())

            self.assertFalse(FST(r'''[t"a" \
t"b"
t"c"]''').elts[0]._is_enclosed_or_line())

    def test__is_enclosed_in_parents(self):
        self.assertFalse(FST('i', 'exec').body[0]._is_enclosed_in_parents())
        self.assertFalse(FST('i', 'single').body[0]._is_enclosed_in_parents())
        self.assertFalse(FST('i', 'eval').body._is_enclosed_in_parents())

        self.assertFalse(FST('@d\ndef f(): pass', 'exec').body[0].decorator_list[0]._is_enclosed_in_parents())
        self.assertTrue(FST('def f(): pass', 'exec').body[0].args._is_enclosed_in_parents())
        self.assertTrue(FST('def f(a) -> int: pass', 'exec').body[0].args._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a) -> int: pass', 'exec').body[0].returns._is_enclosed_in_parents())

        self.assertFalse(FST('@d\nasync def f(): pass', 'exec').body[0].decorator_list[0]._is_enclosed_in_parents())
        self.assertTrue(FST('async def f(): pass', 'exec').body[0].args._is_enclosed_in_parents())
        self.assertTrue(FST('async def f(a) -> int: pass', 'exec').body[0].args._is_enclosed_in_parents())
        self.assertFalse(FST('async def f(a) -> int: pass', 'exec').body[0].returns._is_enclosed_in_parents())

        self.assertFalse(FST('@d\nclass c: pass', 'exec').body[0].decorator_list[0]._is_enclosed_in_parents())
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0].bases[0]._is_enclosed_in_parents())
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0].keywords[0]._is_enclosed_in_parents())

        self.assertFalse(FST('return v', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('del v', 'exec').body[0].targets[0]._is_enclosed_in_parents())
        self.assertFalse(FST('t = v', 'exec').body[0].targets[0]._is_enclosed_in_parents())
        self.assertFalse(FST('t = v', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].target._is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].op._is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].target._is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].annotation._is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].value._is_enclosed_in_parents())

        self.assertFalse(FST('for a in b: pass', 'exec').body[0].target._is_enclosed_in_parents())
        self.assertFalse(FST('for a in b: pass', 'exec').body[0].iter._is_enclosed_in_parents())
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0].target._is_enclosed_in_parents())
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0].iter._is_enclosed_in_parents())
        self.assertFalse(FST('while a: pass', 'exec').body[0].test._is_enclosed_in_parents())
        self.assertFalse(FST('if a: pass', 'exec').body[0].test._is_enclosed_in_parents())

        self.assertFalse(FST('with a: pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertFalse(FST('with (a): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())  # pars belong to `a`
        self.assertFalse(FST('with ((a)): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())  # pars belong to `a`
        self.assertTrue(FST('with (a as b): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())  # pars belong to `with`
        self.assertTrue(FST('with ((a) as b): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())  # outer pars belong to `with`
        self.assertFalse(FST('async with a: pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertFalse(FST('async with (a): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertFalse(FST('async with ((a)): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertTrue(FST('async with (a as b): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertTrue(FST('async with ((a) as b): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())

        self.assertFalse(FST('match (a):\n case 1: pass', 'exec').body[0].subject._is_enclosed_in_parents())
        self.assertFalse(FST('raise exc from cause', 'exec').body[0].exc._is_enclosed_in_parents())
        self.assertFalse(FST('raise exc from cause', 'exec').body[0].cause._is_enclosed_in_parents())
        self.assertFalse(FST('try: pass\nexcept Exception as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())
        self.assertFalse(FST('try: pass\nexcept (Exception) as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())  # because pars belong to `type`
        self.assertFalse(FST('try: pass\nexcept ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())  # same
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0].test._is_enclosed_in_parents())
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0].msg._is_enclosed_in_parents())
        self.assertFalse(FST('import a as b', 'exec').body[0].names[0]._is_enclosed_in_parents())
        self.assertFalse(FST('from a import b', 'exec').body[0].names[0]._is_enclosed_in_parents())
        self.assertFalse(FST('from a import b as c', 'exec').body[0].names[0]._is_enclosed_in_parents())
        self.assertTrue(FST('from a import (b)', 'exec').body[0].names[0]._is_enclosed_in_parents())
        self.assertTrue(FST('from a import (b as c)', 'exec').body[0].names[0]._is_enclosed_in_parents())

        self.assertFalse(FST('(a)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.op._is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[0]._is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[1]._is_enclosed_in_parents())
        self.assertFalse(FST('(a := b)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.left._is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.op._is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.right._is_enclosed_in_parents())
        self.assertFalse(FST('-(a)', 'exec').body[0].value.op._is_enclosed_in_parents())
        self.assertFalse(FST('-(a)', 'exec').body[0].value.operand._is_enclosed_in_parents())
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value.args._is_enclosed_in_parents())
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value.body._is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.body._is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.test._is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.orelse._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v}', 'exec').body[0].value.keys[0]._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v}', 'exec').body[0].value.values[0]._is_enclosed_in_parents())
        self.assertTrue(FST('{a}', 'exec').body[0].value.elts[0]._is_enclosed_in_parents())
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.elt._is_enclosed_in_parents())
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.generators[0]._is_enclosed_in_parents())
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value.elt._is_enclosed_in_parents())
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value.generators[0]._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.key._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.value._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.generators[0]._is_enclosed_in_parents())
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value.elt._is_enclosed_in_parents())
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value.generators[0]._is_enclosed_in_parents())
        self.assertFalse(FST('await (a)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('yield (a)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('yield from (a)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.left._is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.ops[0]._is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.comparators[0]._is_enclosed_in_parents())
        self.assertFalse(FST('call(a, b=c)', 'exec').body[0].value.func._is_enclosed_in_parents())
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value.args[0]._is_enclosed_in_parents())
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value.keywords[0]._is_enclosed_in_parents())
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[0]._is_enclosed_in_parents())
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[1].value._is_enclosed_in_parents())

        self.assertFalse(FST('(a).b', 'exec').body[0].value.value._is_enclosed_in_parents())
        self.assertFalse(FST('(a).b', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value.value._is_enclosed_in_parents())
        self.assertTrue(FST('(a)[b]', 'exec').body[0].value.slice._is_enclosed_in_parents())
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('*(a)', 'exec').body[0].value.value._is_enclosed_in_parents())
        self.assertFalse(FST('*(a)', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('a', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('(a)', 'exec').body[0].value.ctx._is_enclosed_in_parents())

        self.assertTrue(FST('[a]', 'exec').body[0].value.elts[0]._is_enclosed_in_parents())
        self.assertFalse(FST('[a]', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertTrue(FST('(a,)', 'exec').body[0].value.elts[0]._is_enclosed_in_parents())
        self.assertFalse(FST('(a,)', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('a,', 'exec').body[0].value.elts[0]._is_enclosed_in_parents())
        self.assertFalse(FST('a,', 'exec').body[0].value.ctx._is_enclosed_in_parents())

        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).lower._is_enclosed_in_parents())
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).upper._is_enclosed_in_parents())
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).step._is_enclosed_in_parents())

        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).target._is_enclosed_in_parents())
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).iter._is_enclosed_in_parents())
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).ifs[0]._is_enclosed_in_parents())

        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).posonlyargs[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).args[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).defaults[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).vararg._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kwonlyargs[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kw_defaults[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kwarg._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=True).annotation._is_enclosed_in_parents())

        self.assertFalse(FST('call(k=v)', 'exec').body[0].value.keywords[0].copy(pars=True).value._is_enclosed_in_parents())

        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True).context_expr._is_enclosed_in_parents())
        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True).optional_vars._is_enclosed_in_parents())

        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True).pattern._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True).guard._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).value._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).value._is_enclosed_in_parents())  # inconsistent case, MatchValue owns the pars
        self.assertFalse(FST('match a:\n case 1, 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1, 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case [1, 2]: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).keys[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).cls._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).kwd_patterns[0]._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1 as a: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).pattern._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1 as a): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).pattern._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1 | 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1 | 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())

        if PYGE12:
            self.assertTrue(FST('def f[T]() -> int: pass', 'exec').body[0].type_params[0]._is_enclosed_in_parents())
            self.assertTrue(FST('async def f[T]() -> int: pass', 'exec').body[0].type_params[0]._is_enclosed_in_parents())
            self.assertTrue(FST('class c[T]: pass', 'exec').body[0].type_params[0]._is_enclosed_in_parents())

            self.assertFalse(FST('type t[T] = v', 'exec').body[0].name._is_enclosed_in_parents())
            self.assertTrue(FST('type t[T] = v', 'exec').body[0].type_params[0]._is_enclosed_in_parents())
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].value._is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* Exception as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* (Exception) as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())
            self.assertFalse(FST('type t[*T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())
            self.assertFalse(FST('type t[**T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())

        if PYGE14:
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[0]._is_enclosed_in_parents())
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[1].value._is_enclosed_in_parents())

        # with field

        self.assertFalse(FST('i', 'exec')._is_enclosed_in_parents('body'))
        self.assertFalse(FST('i', 'single')._is_enclosed_in_parents('body'))
        self.assertFalse(FST('i', 'eval')._is_enclosed_in_parents('body'))

        self.assertFalse(FST('@d\ndef f(): pass', 'exec').body[0]._is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('def f(): pass', 'exec').body[0]._is_enclosed_in_parents('args'))
        self.assertTrue(FST('def f(a) -> int: pass', 'exec').body[0]._is_enclosed_in_parents('args'))
        self.assertFalse(FST('def f(a) -> int: pass', 'exec').body[0]._is_enclosed_in_parents('returns'))

        self.assertFalse(FST('@d\nasync def f(): pass', 'exec').body[0]._is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('async def f(): pass', 'exec').body[0]._is_enclosed_in_parents('args'))
        self.assertTrue(FST('async def f(a) -> int: pass', 'exec').body[0]._is_enclosed_in_parents('args'))
        self.assertFalse(FST('async def f(a) -> int: pass', 'exec').body[0]._is_enclosed_in_parents('returns'))

        self.assertFalse(FST('@d\nclass c: pass', 'exec').body[0]._is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0]._is_enclosed_in_parents('bases'))
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0]._is_enclosed_in_parents('keywords'))

        self.assertFalse(FST('return v', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('del v', 'exec').body[0]._is_enclosed_in_parents('targets'))
        self.assertFalse(FST('t = v', 'exec').body[0]._is_enclosed_in_parents('targets'))
        self.assertFalse(FST('t = v', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('t += v', 'exec').body[0]._is_enclosed_in_parents('target'))
        self.assertFalse(FST('t += v', 'exec').body[0]._is_enclosed_in_parents('op'))
        self.assertFalse(FST('t += v', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('t: int = v', 'exec').body[0]._is_enclosed_in_parents('target'))
        self.assertFalse(FST('t: int = v', 'exec').body[0]._is_enclosed_in_parents('annotation'))
        self.assertFalse(FST('t: int = v', 'exec').body[0]._is_enclosed_in_parents('value'))

        self.assertFalse(FST('for a in b: pass', 'exec').body[0]._is_enclosed_in_parents('target'))
        self.assertFalse(FST('for a in b: pass', 'exec').body[0]._is_enclosed_in_parents('iter'))
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0]._is_enclosed_in_parents('target'))
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0]._is_enclosed_in_parents('iter'))
        self.assertFalse(FST('while a: pass', 'exec').body[0]._is_enclosed_in_parents('test'))
        self.assertFalse(FST('if a: pass', 'exec').body[0]._is_enclosed_in_parents('test'))

        self.assertFalse(FST('with a: pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertFalse(FST('with (a): pass', 'exec').body[0]._is_enclosed_in_parents('items'))  # pars belong to `a`
        self.assertFalse(FST('with ((a)): pass', 'exec').body[0]._is_enclosed_in_parents('items'))  # pars belong to `a`
        self.assertTrue(FST('with (a as b): pass', 'exec').body[0]._is_enclosed_in_parents('items'))  # pars belong to `with`
        self.assertTrue(FST('with ((a) as b): pass', 'exec').body[0]._is_enclosed_in_parents('items'))  # outer pars belong to `with`
        self.assertFalse(FST('async with a: pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertFalse(FST('async with (a): pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertFalse(FST('async with ((a)): pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertTrue(FST('async with (a as b): pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertTrue(FST('async with ((a) as b): pass', 'exec').body[0]._is_enclosed_in_parents('items'))

        self.assertFalse(FST('match (a):\n case 1: pass', 'exec').body[0]._is_enclosed_in_parents('subject'))
        self.assertFalse(FST('raise exc from cause', 'exec').body[0]._is_enclosed_in_parents('exc'))
        self.assertFalse(FST('raise exc from cause', 'exec').body[0]._is_enclosed_in_parents('cause'))
        self.assertFalse(FST('try: pass\nexcept Exception as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))
        self.assertFalse(FST('try: pass\nexcept (Exception) as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))  # because pars belong to `type`
        self.assertFalse(FST('try: pass\nexcept ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))  # same
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0]._is_enclosed_in_parents('test'))
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0]._is_enclosed_in_parents('msg'))
        self.assertFalse(FST('import a as b', 'exec').body[0]._is_enclosed_in_parents('names'))
        self.assertFalse(FST('from a import b', 'exec').body[0]._is_enclosed_in_parents('names'))
        self.assertFalse(FST('from a import b as c', 'exec').body[0]._is_enclosed_in_parents('names'))
        self.assertTrue(FST('from a import (b)', 'exec').body[0]._is_enclosed_in_parents('names'))
        self.assertTrue(FST('from a import (b as c)', 'exec').body[0]._is_enclosed_in_parents('names'))

        self.assertFalse(FST('(a)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value._is_enclosed_in_parents('op'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value._is_enclosed_in_parents('values'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[1]._is_enclosed_in_parents())
        self.assertFalse(FST('(a := b)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value._is_enclosed_in_parents('left'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value._is_enclosed_in_parents('op'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value._is_enclosed_in_parents('right'))
        self.assertFalse(FST('-(a)', 'exec').body[0].value._is_enclosed_in_parents('op'))
        self.assertFalse(FST('-(a)', 'exec').body[0].value._is_enclosed_in_parents('operand'))
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value._is_enclosed_in_parents('args'))
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value._is_enclosed_in_parents('body'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value._is_enclosed_in_parents('body'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value._is_enclosed_in_parents('test'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value._is_enclosed_in_parents('orelse'))
        self.assertTrue(FST('{k: v}', 'exec').body[0].value._is_enclosed_in_parents('keys'))
        self.assertTrue(FST('{k: v}', 'exec').body[0].value._is_enclosed_in_parents('values'))
        self.assertTrue(FST('{a}', 'exec').body[0].value._is_enclosed_in_parents('elts'))
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value._is_enclosed_in_parents('elt'))
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value._is_enclosed_in_parents('generators'))
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value._is_enclosed_in_parents('elt'))
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value._is_enclosed_in_parents('generators'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value._is_enclosed_in_parents('key'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value._is_enclosed_in_parents('value'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value._is_enclosed_in_parents('generators'))
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value._is_enclosed_in_parents('elt'))
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value._is_enclosed_in_parents('generators'))
        self.assertFalse(FST('await (a)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('yield (a)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('yield from (a)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value._is_enclosed_in_parents('left'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value._is_enclosed_in_parents('ops'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value._is_enclosed_in_parents('comparators'))
        self.assertFalse(FST('call(a, b=c)', 'exec').body[0].value._is_enclosed_in_parents('func'))
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value._is_enclosed_in_parents('args'))
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value._is_enclosed_in_parents('keywords'))
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value._is_enclosed_in_parents('values'))
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[1]._is_enclosed_in_parents('value'))

        self.assertFalse(FST('(a).b', 'exec').body[0].value._is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a).b', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value._is_enclosed_in_parents('value'))
        self.assertTrue(FST('(a)[b]', 'exec').body[0].value._is_enclosed_in_parents('slice'))
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('*(a)', 'exec').body[0].value._is_enclosed_in_parents('value'))
        self.assertFalse(FST('*(a)', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('a', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('(a)', 'exec').body[0].value._is_enclosed_in_parents('ctx'))

        self.assertTrue(FST('[a]', 'exec').body[0].value._is_enclosed_in_parents('elts'))
        self.assertFalse(FST('[a]', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertTrue(FST('(a,)', 'exec').body[0].value._is_enclosed_in_parents('elts'))
        self.assertFalse(FST('(a,)', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('a,', 'exec').body[0].value._is_enclosed_in_parents('elts'))
        self.assertFalse(FST('a,', 'exec').body[0].value._is_enclosed_in_parents('ctx'))

        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True)._is_enclosed_in_parents('lower'))
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True)._is_enclosed_in_parents('upper'))
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True)._is_enclosed_in_parents('step'))

        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True)._is_enclosed_in_parents('target'))
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True)._is_enclosed_in_parents('iter'))
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True)._is_enclosed_in_parents('ifs'))

        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('posonlyargs'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('args'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('defaults'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('vararg'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('kwonlyargs'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('kw_defaults'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('kwarg'))
        self.assertFalse(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=True)._is_enclosed_in_parents('annotation'))

        self.assertFalse(FST('call(k=v)', 'exec').body[0].value.keywords[0].copy(pars=True)._is_enclosed_in_parents('value'))

        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True)._is_enclosed_in_parents('context_expr'))
        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True)._is_enclosed_in_parents('optional_vars'))

        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True)._is_enclosed_in_parents('pattern'))
        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True)._is_enclosed_in_parents('guard'))
        self.assertFalse(FST('match a:\n case 1: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('value'))
        self.assertTrue(FST('match a:\n case (1): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('value'))  # inconsistent case, MatchValue owns the pars
        self.assertFalse(FST('match a:\n case 1, 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case (1, 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case [1, 2]: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('keys'))
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertFalse(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('cls'))
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('kwd_patterns'))
        self.assertFalse(FST('match a:\n case 1 as a: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('pattern'))
        self.assertTrue(FST('match a:\n case (1 as a): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('pattern'))
        self.assertFalse(FST('match a:\n case 1 | 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case (1 | 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))

        if PYGE12:
            self.assertTrue(FST('def f[T]() -> int: pass', 'exec').body[0]._is_enclosed_in_parents('type_params'))
            self.assertTrue(FST('async def f[T]() -> int: pass', 'exec').body[0]._is_enclosed_in_parents('type_params'))
            self.assertTrue(FST('class c[T]: pass', 'exec').body[0]._is_enclosed_in_parents('type_params'))

            self.assertFalse(FST('type t[T] = v', 'exec').body[0]._is_enclosed_in_parents('name'))
            self.assertTrue(FST('type t[T] = v', 'exec').body[0]._is_enclosed_in_parents('type_params'))
            self.assertFalse(FST('type t[T] = v', 'exec').body[0]._is_enclosed_in_parents('value'))
            self.assertFalse(FST('try: pass\nexcept* Exception as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))
            self.assertFalse(FST('try: pass\nexcept* (Exception) as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))
            self.assertFalse(FST('try: pass\nexcept* ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())
            self.assertFalse(FST('type t[*T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())
            self.assertFalse(FST('type t[**T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())

        if PYGE14:
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value._is_enclosed_in_parents('values'))
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[1]._is_enclosed_in_parents('value'))

    def test__loc_key(self):
        a = parse('''{
    a: """test
two  # fake comment start""", **b
            }''').body[0].value
        self.assertEqual((2, 30, 2, 32), a.f._loc_key(1))

        a = parse('''{
    a: """test""", **  # comment
    b
            }''').body[0].value
        self.assertEqual((1, 19, 1, 21), a.f._loc_key(1))

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

    def test__get_indent(self):
        ast = parse('i = 1; j = 2')

        self.assertEqual('', ast.body[0].f._get_indent())
        self.assertEqual('', ast.body[1].f._get_indent())

        ast = parse('def f(): \\\n i = 1')

        self.assertEqual('', ast.body[0].f._get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f._get_indent())

        ast = parse('class cls: i = 1')

        self.assertEqual('', ast.body[0].f._get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f._get_indent())

        ast = parse('class cls: i = 1; \\\n    j = 2')

        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f._get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[1].f._get_indent())

        ast = parse('class cls:\n  i = 1; \\\n    j = 2')

        self.assertEqual('  ', ast.body[0].body[0].f._get_indent())
        self.assertEqual('  ', ast.body[0].body[1].f._get_indent())

        ast = parse('class cls:\n   def f(): i = 1')

        self.assertEqual('   ', ast.body[0].body[0].f._get_indent())
        self.assertEqual('   ' + ast.f.root.indent, ast.body[0].body[0].body[0].f._get_indent())

        self.assertEqual('   ', parse('def f():\n   1').body[0].body[0].f._get_indent())
        self.assertEqual('    ', parse('def f(): 1').body[0].body[0].f._get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1').body[0].body[0].f._get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1').body[0].body[0].f._get_indent())

        self.assertEqual('    ', parse('class cls:\n def f():\n    1').body[0].body[0].body[0].f._get_indent())
        self.assertEqual('  ', parse('class cls:\n def f(): 1').body[0].body[0].body[0].f._get_indent())  # indentation inferred otherwise would be '     '
        self.assertEqual('  ', parse('class cls:\n def f(): \\\n   1').body[0].body[0].body[0].f._get_indent())  # indentation inferred otherwise would be '     '
        self.assertEqual('   ', parse('class cls:\n def f(): # \\\n   1').body[0].body[0].body[0].f._get_indent())

        self.assertEqual('  ', parse('if 1:\n  2\nelse:\n   3').body[0].body[0].f._get_indent())
        self.assertEqual('   ', parse('if 1: 2\nelse:\n   3').body[0].body[0].f._get_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('   ', parse('if 1: \\\n 2\nelse:\n   3').body[0].body[0].f._get_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('  ', parse('if 1: # \\\n  2\nelse:\n   3').body[0].body[0].f._get_indent())

        self.assertEqual('   ', parse('if 1:\n  2\nelse:\n   3').body[0].orelse[0].f._get_indent())
        self.assertEqual('  ', parse('if 1:\n  2\nelse: 3').body[0].orelse[0].f._get_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('  ', parse('if 1:\n  2\nelse: \\\n 3').body[0].orelse[0].f._get_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('   ', parse('if 1:\n  2\nelse: # \\\n   3').body[0].orelse[0].f._get_indent())

        self.assertEqual('   ', parse('def f():\n   1; 2').body[0].body[1].f._get_indent())
        self.assertEqual('    ', parse('def f(): 1; 2').body[0].body[1].f._get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1; 2').body[0].body[1].f._get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1; 2').body[0].body[1].f._get_indent())

        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f._get_indent())
        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f._get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f._get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f._get_indent())

        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[0].f._get_indent())
        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[1].f._get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[0].f._get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[1].f._get_indent())

        self.assertEqual('', parse('\\\ni').body[0].f._get_indent())
        self.assertEqual('    ', parse('try: i\nexcept: pass').body[0].body[0].f._get_indent())

        self.assertEqual('', parse('if 1: i\nelif 2: j').body[0].f._get_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j').body[0].body[0].f._get_indent())
        self.assertEqual('', parse('if 1: i\nelif 2: j').body[0].orelse[0].f._get_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j').body[0].orelse[0].body[0].f._get_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j\nelse: k').body[0].orelse[0].orelse[0].f._get_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j\nelif 3: k').body[0].orelse[0].orelse[0].body[0].f._get_indent())

        # self.assertEqual('  ', parse('if 1: i\nelse:\n  j').body[0].body[0].f._get_indent())  # candidate for sibling indentation, nope, not doing this

        self.assertEqual('  ', parse('if 1:\n\\\n  \\\n i').body[0].body[0].f._get_indent())
        self.assertEqual('  ', parse('if 1:\n  \\\n\\\n i').body[0].body[0].f._get_indent())
        self.assertEqual('  ', parse('if 1:\n  \\\n   \\\n\\\n i').body[0].body[0].f._get_indent())
        self.assertEqual('   ', parse('if 1:\n   \\\n  \\\n\\\n i').body[0].body[0].f._get_indent())
        self.assertEqual('    ', parse('if 1: \\\n\\\n  \\\n   \\\n\\\n i').body[0].body[0].f._get_indent())
        self.assertEqual('  ', parse('if 1:\n\\\n  \\\n   \\\n\\\n i').body[0].body[0].f._get_indent())
        self.assertEqual('     ', parse('if 1:\n\\\n\\\n     \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].f._get_indent())

        self.assertEqual('          ', parse('if 2:\n     if 1:\\\n\\\n\\\n  \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].body[0].f._get_indent())  # indentation inferred otherwise would be '         '
        self.assertEqual('      ', parse('if 2:\n     if 1:\n\\\n      \\\n  \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].body[0].f._get_indent())

    def test__get_indentable_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = "... \\\n2"\n else:\n  j \\\n=\\\n 2'
        ast = parse(src)

        self.assertEqual({1, 2, 5, 7, 8, 9, 10}, ast.f._get_indentable_lns(1))
        self.assertEqual({0, 1, 2, 5, 7, 8, 9, 10}, ast.f._get_indentable_lns(0))

        f = FST.fromsrc('''
def _splitext(p, sep, altsep, extsep):
    """Split the extension from a pathname.

    Extension is everything from the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work for text and bytes strings.

    sepIndex = p.rfind(sep)
            '''.strip())
        self.assertEqual({0, 1, 2, 3, 4, 5, 6, 7}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0, 1, 5, 6, 7}, f._get_indentable_lns(docstr=False))

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
        self.assertEqual({0}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0, 1}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
f"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0}, f._get_indentable_lns(docstr=True))  # because f-strings cannot be docstrings
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

    def test__offset_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j = 2'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
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
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
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
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
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
        lns = ast.f._get_indentable_lns(1)
        ast.f._indent_lns('  ', lns)
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n   if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._indent_lns('  ', lns)
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._indent_lns('  ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._get_indentable_lns(1)
        ast.body[0].body[0].orelse[0].f._indent_lns('  ', lns)
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n  =\\\n   2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._indent_lns('  ', lns)
        self.assertEqual({1, 2}, lns)
        self.assertEqual('@decorator\n  class cls:\n   pass', ast.f.src)

    def test__dedent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._dedent_lns(' ', lns)
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\nif True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._get_indentable_lns(1)
        ast.body[0].body[0].orelse[0].f._dedent_lns(' ', lns)
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('@decorator\nclass cls:\n pass', ast.f.src)

        # ast = parse(src)
        # lns = ast.body[0].body[0].f._dedent_lns(' ', skip=0)
        # self.assertEqual({2}, lns)
        # self.assertEqual('@decorator\nclass cls:\npass', ast.f.src)

    def test__redent_lns(self):
        f = FST('''
[
a,
 b,
  c,
   d,
    e,
     f,
      g,

a,
 b,
  c,
   d,
    e,
     f,
      g,
]
            '''.strip())
        f._redent_lns('    ', '012')
        self.assertEqual('''
[
a,
b,
0c,
01d,
012e,
012 f,
012  g,

a,
b,
0c,
01d,
012e,
012 f,
012  g,
]
            '''.strip(), f.src)
        self.assertEqual((0, 0, 16, 1), f.loc)
        self.assertEqual((1, 0, 1, 1), f.elts[0].loc)
        self.assertEqual((2, 0, 2, 1), f.elts[1].loc)
        self.assertEqual((3, 1, 3, 2), f.elts[2].loc)
        self.assertEqual((4, 2, 4, 3), f.elts[3].loc)
        self.assertEqual((5, 3, 5, 4), f.elts[4].loc)
        self.assertEqual((6, 4, 6, 5), f.elts[5].loc)
        self.assertEqual((7, 5, 7, 6), f.elts[6].loc)
        self.assertEqual((9, 0, 9, 1), f.elts[7].loc)
        self.assertEqual((10, 0, 10, 1), f.elts[8].loc)
        self.assertEqual((11, 1, 11, 2), f.elts[9].loc)
        self.assertEqual((12, 2, 12, 3), f.elts[10].loc)
        self.assertEqual((13, 3, 13, 4), f.elts[11].loc)
        self.assertEqual((14, 4, 14, 5), f.elts[12].loc)
        self.assertEqual((15, 5, 15, 6), f.elts[13].loc)

        f = FST('''
    "OFFENDING RULE", self.ex.rule,
''')
        f.a.lineno = 1
        f.a.col_offset = f.a.end_col_offset = 0
        f.a.end_lineno = 3
        f._redent_lns('    ', ' ')
        self.assertEqual((0, 0, 2, 0), f.loc)
        self.assertEqual((1, 1, 1, 17), f.elts[0].loc)
        self.assertEqual((1, 19, 1, 31), f.elts[1].loc)
        self.assertEqual((1, 19, 1, 26), f.elts[1].value.loc)
        self.assertEqual((1, 19, 1, 23), f.elts[1].value.value.loc)

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

    def test__is_parenthesized_tuple(self):
        self.assertTrue(parse('(1, 2)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(1,)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1),)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1,))').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1,),)').body[0].value.f._is_parenthesized_tuple())

        self.assertTrue(parse('((a), b)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(a, (b))').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((a), (b))').body[0].value.f._is_parenthesized_tuple())

        self.assertTrue(parse('(\n1,2)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(1\n,2)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(1,\n2)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(1,2\n)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(1\n,)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(1,\n)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1),)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((\n1),)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1\n),)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1)\n,)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1),\n)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1,))').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((\n1,))').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1\n,))').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1,\n))').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1,)\n)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1,),)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((\n1,),)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1\n,),)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1,\n),)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1,)\n,)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((1,),\n)').body[0].value.f._is_parenthesized_tuple())

        self.assertTrue(parse('((a), b)').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('(a, (b))').body[0].value.f._is_parenthesized_tuple())
        self.assertTrue(parse('((a), (b))').body[0].value.f._is_parenthesized_tuple())

        self.assertFalse(parse('(1,),').body[0].value.f._is_parenthesized_tuple())
        self.assertFalse(parse('(1),').body[0].value.f._is_parenthesized_tuple())
        self.assertFalse(parse('((1)),').body[0].value.f._is_parenthesized_tuple())
        self.assertFalse(parse('((1,),),').body[0].value.f._is_parenthesized_tuple())

        self.assertFalse(parse('(a), b').body[0].value.f._is_parenthesized_tuple())
        self.assertFalse(parse('((a)), b').body[0].value.f._is_parenthesized_tuple())
        self.assertFalse(parse('a, (b)').body[0].value.f._is_parenthesized_tuple())
        self.assertFalse(parse('a, ((b))').body[0].value.f._is_parenthesized_tuple())
        self.assertFalse(parse('(a), (b)').body[0].value.f._is_parenthesized_tuple())
        self.assertFalse(parse('((a)), ((b))').body[0].value.f._is_parenthesized_tuple())

        self.assertIsNone(parse('[(a), (b)]').body[0].value.f._is_parenthesized_tuple())

    def test__is_delimited_seq(self):
        self.assertFalse(FST('((pos < len(ranges))>>32),(r&((1<<32)-1))')._is_delimited_seq())
        self.assertFalse(FST('((1)+1),(1)')._is_delimited_seq())

    def test__maybe_add_line_continuations(self):
        f = FST(r'''
a + \
("""
*"""
"c")
''')
        self.assertFalse(f._maybe_add_line_continuations(whole=False))
        self.assertEqual(r'''
a + \
("""
*"""
"c")
''', f.src)
        f.verify('strict')

        f = FST(r'''
a + \
("""
*"""
"c")
''')
        f.right.unpar()
        self.assertTrue(f._maybe_add_line_continuations(whole=False))
        self.assertEqual(r'''
a + \
"""
*""" \
"c"
''', f.src)
        f.verify('strict')

        f = FST(r'''
a + \
("""
*"""
"c")
''')
        f.right.unpar()
        self.assertTrue(f._maybe_add_line_continuations(whole=True))
        self.assertEqual(r'''\
a + \
"""
*""" \
"c" \
''', f.src)
        f.verify('strict')

        f = FST(r'''(""" a
b # c""",
d)''')
        f.unpar(True)
        f._maybe_add_line_continuations()
        self.assertEqual(r'''""" a
b # c""", \
d''', f.src)

        f = FST(r'''(""" a
b # c""",
# comment0
  # comment1
e,  # comment2
d)  # comment3''')
        f.unpar(True)
        self.assertRaises(NodeError, f._maybe_add_line_continuations, del_comments=False)

        f = FST(r'''(""" a
b # c""",
# comment0
  # comment1
e,  # comment2
d)  # comment3''')
        f.unpar(True)
        f._maybe_add_line_continuations(del_comments=True)
        self.assertEqual(r'''""" a
b # c""", \
\
  \
e, \
d  # comment3''', f.src)

    def test__maybe_ins_separator(self):
        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, False, 0, 2)
        self.assertEqual('[a,#c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, True, 0, 2)
        self.assertEqual('[a, #c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, False, 0, 6)
        self.assertEqual('[a,#c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, True, 0, 6)
        self.assertEqual('[a, #c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, False, 1, 0)
        self.assertEqual('[a,#c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, True, 1, 0)
        self.assertEqual('[a, #c\n]', f.src)

    def test__maybe_fix_tuple(self):
        # parenthesize naked tuple preserve comments if present

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=0), ['# comment', ''])
        f._maybe_fix_tuple()
        self.assertEqual('(# comment\n)', f.src)
        f.verify()

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=1), [' # comment', ' '])
        f._maybe_fix_tuple()
        self.assertEqual('(# comment\n)', f.src)
        f.verify()

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=0), ['         ', ''])
        f._maybe_fix_tuple()
        self.assertEqual('()', f.src)
        f.verify()

    def test__maybe_fix_copy(self):
        from fst.fst_one import _maybe_fix_copy

        f = FST.fromsrc('if 1:\n a\nelif 2:\n b')
        fc = f.a.body[0].orelse[0].f.copy()
        self.assertEqual(fc.lines[0], 'if 2:')
        fc.verify(raise_=True)

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual(fc.src, '1 +\n2')
        _maybe_fix_copy(fc, pars=True)
        self.assertEqual(fc.src, '(1 +\n2)')
        fc.verify(raise_=True)

        f = FST.fromsrc('i = 1')
        self.assertIs(f.a.body[0].targets[0].ctx.__class__, Store)
        fc = f.a.body[0].targets[0].f.copy()
        self.assertIs(fc.a.ctx.__class__, Load)
        fc.verify(raise_=True)

        f = FST.fromsrc('if 1: pass\nelif 2: pass').a.body[0].orelse[0].f.copy()
        self.assertEqual('if 2: pass', f.src)

        f = FST.fromsrc('i, j = 1, 2').a.body[0].targets[0].f.copy(pars=False)
        self.assertEqual('i, j', f.src)
        _maybe_fix_copy(fc, pars=True)
        self.assertEqual('i, j', f.src)  # because doesn't NEED them

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(pars=False)
        self.assertEqual('w := x,', f.src)
        _maybe_fix_copy(f, pars=True)
        self.assertEqual('(w := x,)', f.src)

        f = FST.fromsrc('yield a1, a2')
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual('yield a1, a2', fc.src)
        _maybe_fix_copy(fc, pars=True)
        self.assertEqual('yield a1, a2', fc.src)

        f = FST.fromsrc('yield from a')
        fc = f.a.body[0].value.f.copy()
        self.assertEqual('yield from a', fc.src)
        _maybe_fix_copy(fc, pars=True)
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
        _maybe_fix_copy(fc, pars=True)
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
        _maybe_fix_copy(fc, pars=True)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fc.src)

        if PYGE12:
            fc = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(pars=False)
            self.assertEqual('*tuple[int, ...]', fc.src)
            _maybe_fix_copy(fc, pars=True)
            self.assertEqual('*tuple[int, ...],', fc.src)

        # don't parenthesize copied Slice even if it looks like it needs it

        self.assertEqual('b:\nc', (f := FST('a[b:\nc]').get('slice')).src)
        f.verify()

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

        # special rules for Starred

        f = FST('*\na')
        f._parenthesize_grouping()
        self.assertEqual('*(\na)', f.src)
        f.verify()

        f = FST('*\na')
        f._parenthesize_grouping(star_child=False)
        self.assertEqual('(*\na)', f.src)

    def test__unparenthesize_grouping(self):
        f = parse('a').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(a)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((a))').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(\n ( (a) )  \n)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((i,))').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('(\n ( (i,) ) \n)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=False)
        self.assertEqual(f.src, 'call((i for i in j))')
        self.assertEqual((0, 0, 0, 20), f.loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call( ( ( (i for i in j) ) ) )').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=False)
        self.assertEqual(f.src, 'call((i for i in j),)')
        self.assertEqual((0, 0, 0, 21), f.loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('( # pre\ni\n# post\n)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('( # pre\ni\n# post\n)').body[0].value.f.copy(pars=True)
        f._unparenthesize_grouping(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        f = parse('( # pre\n(i,)\n# post\n)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)

        f = parse('( # pre\n(i)\n# post\n)').body[0].value.f.copy(pars=True)
        f._unparenthesize_grouping(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a)if(a)]', 'exec')
        f.body[0].value.generators[0].ifs[0]._unparenthesize_grouping(shared=False)
        f.body[0].value.generators[0].ifs[1]._unparenthesize_grouping(shared=False)
        self.assertEqual('[a for a in b if a if a]', f.src)

        f = FST('for(a)in b: pass', 'exec')
        f.body[0].target._unparenthesize_grouping(shared=False)
        self.assertEqual('for a in b: pass', f.src)

        f = FST('assert(test)', 'exec')
        f.body[0].test._unparenthesize_grouping(shared=False)
        self.assertEqual('assert test', f.src)

        f = FST('assert({test})', 'exec')
        f.body[0].test._unparenthesize_grouping(shared=False)
        self.assertEqual('assert{test}', f.src)

        # special rules for Starred

        f = FST('*(\na)')
        self.assertEqual('*(\na)', f.src)
        f._unparenthesize_grouping(star_child=False)
        self.assertEqual('*(\na)', f.src)
        f._unparenthesize_grouping()
        self.assertEqual('*a', f.src)
        f.verify()

        f = FST('*\na')
        f._parenthesize_grouping(star_child=False)
        self.assertEqual('(*\na)', f.src)
        f._unparenthesize_grouping()
        self.assertEqual('(*\na)', f.src)
        f._unparenthesize_grouping(star_child=False)
        self.assertEqual('*\na', f.src)
        f.verify()

    def test__delimit_node(self):
        # Tuple

        f = parse('i,').f
        f.body[0].value._delimit_node()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('a, b').f
        f.body[0].value._delimit_node()
        self.assertEqual('(a, b)', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.elts[1].loc)

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=True)
        self.assertEqual((0, 0, 2, 7), f.loc)
        self.assertEqual(f.src, '(# pre\ni,\n# post)')

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n(i,)\n# post')

        # MatchSequence

        f = FST('i,', pattern)
        f._delimit_node(delims='[]')
        self.assertEqual('[i,]', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 1, 0, 2), f.patterns[0].loc)

        f = FST('a, b', pattern)
        f._delimit_node(delims='[]')
        self.assertEqual('[a, b]', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 1, 0, 2), f.patterns[0].loc)
        self.assertEqual((0, 4, 0, 5), f.patterns[1].loc)

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=True, delims='[]')
        self.assertEqual((0, 0, 2, 7), f.loc)
        self.assertEqual(f.src, '[# pre\ni,\n# post]')

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=False, delims='[]')
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n[i,]\n# post')

    def test__undelimit_node(self):
        # Tuple

        f = parse('()').f
        f.body[0].value._undelimit_node()
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)

        f = parse('(i,)').f
        f.body[0].value._undelimit_node()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('(a, b)').f
        f.body[0].value._undelimit_node()
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.body[0].value.elts[1].loc)

        f = parse('( # pre\ni,\n# post\n)').f
        f.body[0].value._undelimit_node()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('( # pre\ni,\n# post\n)').body[0].value.f.copy()
        f._undelimit_node()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)

        # MatchSequence

        f = FST('()', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)

        f = FST('[i,]', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.patterns[0].loc)

        f = FST('(a, b)', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 1), f.patterns[0].loc)
        self.assertEqual((0, 3, 0, 4), f.patterns[1].loc)

        f = FST('[ # pre\ni,\n# post\n]', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.patterns[0].loc)

        f = FST('( # pre\ni,\n# post\n)', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 1), f.patterns[0].loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a,b)if(a,)if(a,b)]', 'exec')
        f.body[0].value.generators[0].ifs[0]._undelimit_node()
        f.body[0].value.generators[0].ifs[1]._undelimit_node()
        f.body[0].value.generators[0].ifs[2]._undelimit_node()
        self.assertEqual('[a for a in b if a,b if a,if a,b]', f.src)
        f.body[0].value.generators[0].ifs[0]._delimit_node()  # so that it will verify
        f.body[0].value.generators[0].ifs[1]._delimit_node()
        f.body[0].value.generators[0].ifs[2]._delimit_node()
        self.assertEqual('[a for a in b if (a,b) if (a,)if (a,b)]', f.src)
        f.verify()

        f = FST('for(a,b)in b: pass', 'exec')
        f.body[0].target._undelimit_node()
        self.assertEqual('for a,b in b: pass', f.src)
        f.verify()

        f = FST('for(a,)in b: pass', 'exec')
        f.body[0].target._undelimit_node()
        self.assertEqual('for a,in b: pass', f.src)
        f.verify()

        f = FST('case[1,2]as c: pass')
        f.pattern.pattern._undelimit_node('patterns')
        self.assertEqual('case 1,2 as c: pass', f.src)

        f = FST('case(1,2)as c: pass')
        f.pattern.pattern._undelimit_node('patterns')
        self.assertEqual('case 1,2 as c: pass', f.src)

    def test__get_trivia_params(self):
        with FST.options(trivia=False):
            self.assertEqual(('none', False, False, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=(True, True), neg=False))

        with FST.options(trivia=(False, False)):
            self.assertEqual(('none', False, False, 'none', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'none', False, False), FST._get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=(True, True), neg=False))

        with FST.options(trivia=(False, True)):
            self.assertEqual(('none', False, False, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=(True, True), neg=False))
            self.assertEqual(('block', False, False, 'none', False, False), FST._get_trivia_params(trivia=(True, False), neg=False))

        with FST.options(trivia='all+1'):
            self.assertEqual(('all', 1, False, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('all', 1, False, 'line', False, False), FST._get_trivia_params(neg=True))

        with FST.options(trivia='all-1'):
            self.assertEqual(('all', False, True, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('all', 1, True, 'line', False, False), FST._get_trivia_params(neg=True))

        with FST.options(trivia='all-1'):
            self.assertEqual(('block', 2, False, 'line', False, False), FST._get_trivia_params(trivia='block+2', neg=False))
            self.assertEqual(('block', 2, False, 'line', False, False), FST._get_trivia_params(trivia='block+2', neg=True))
            self.assertEqual(('block', 2, False, 'line', 3, False), FST._get_trivia_params(trivia=('block+2', 'line+3'), neg=False))
            self.assertEqual(('block', 2, False, 'line', 3, False), FST._get_trivia_params(trivia=('block+2', 'line+3'), neg=True))
            self.assertEqual(('block', 2, False, 'line', 3, True), FST._get_trivia_params(trivia=('block+2', 'line-3'), neg=True))
            self.assertEqual(('block', 2, False, 'line', False, True), FST._get_trivia_params(trivia=('block+2', 'line-3'), neg=False))
            self.assertEqual(('block', False, True, 'line', False, True), FST._get_trivia_params(trivia=('block-2', 'line-3'), neg=False))

        with FST.options(trivia=1):
            self.assertEqual((1, False, False, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual((2, False, False, 'line', False, False), FST._get_trivia_params(trivia=2, neg=False))
            self.assertEqual((2, False, False, 3, False, False), FST._get_trivia_params(trivia=(2, 3), neg=False))

    def test__normalize_block(self):
        from fst.fst_slice_old import _normalize_block

        a = parse('''
if 1: i ; j ; l ; m
            '''.strip())
        _normalize_block(a.body[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, 'if 1:\n    i ; j ; l ; m')

        a = parse('''
def f() -> int: \\
  i \\
  ; \\
  j
            '''.strip())
        _normalize_block(a.body[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, 'def f() -> int:\n    i \\\n  ; \\\n  j')

        a = parse('''def f(a = """ a
...   # something """): i = 2''')
        _normalize_block(a.body[0].f)
        self.assertEqual(a.f.src, 'def f(a = """ a\n...   # something """):\n    i = 2')

    def test__elif_to_else_if(self):
        from fst.fst_slice_old import _elif_to_else_if

        a = parse('''
if 1: pass
elif 2: pass
        '''.strip())
        _elif_to_else_if(a.body[0].orelse[0].f)
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
        _elif_to_else_if(a.body[0].body[0].orelse[0].f)
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
        _elif_to_else_if(a.body[0].orelse[0].f)
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
        _elif_to_else_if(a.body[0].body[0].orelse[0].f)
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
        _elif_to_else_if(a.body[0].orelse[0].f)
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
        _elif_to_else_if(a.body[0].body[0].orelse[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
        elif 3: pass
            '''.strip())

    def test_fst_parse_non_str(self):
        self.assertEqual('if 1: pass', parse(b'if 1: pass').f.src)
        self.assertEqual('if 1: pass', parse(memoryview(b'if 1: pass')).f.src)

        self.assertEqual('if 1:\n    pass', parse(FST('if 1: pass').a).f.src)
        self.assertEqual('a:b:c', parse(FST('a:b:c').a).f.src)
        self.assertEqual('except:\n    pass', parse(FST('except: pass').a).f.src)

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
                    self.assertTrue(compare_asts(fst.a, ref, locs=True, raise_=True))

            except Exception:
                print()
                print(f'{mode = }')
                print(f'{func = }')
                print(f'{res = }')
                print(f'{src = !r}')

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
                if issubclass(res, Exception) or (isinstance(mode, str) and mode.startswith('_')):
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

    def test_get_src_clip(self):
        f = FST('if 1:\n    j = 2\n    pass')

        self.assertEqual('if', f.get_src(-1, -1, 0, 2))
        self.assertEqual('pass', f.get_src(2, 4, 999, 999))
        self.assertEqual('if 1:\n    j = 2\n    pass', f.get_src(-1, -1, 999, 999))
        self.assertEqual('    j = 2', f.get_src(1, -1, 1, 999))
        self.assertEqual('1:\n    j = 2\n    p', f.get_src(-1, 3, 999, 5))

        self.assertRaises(ValueError, f.get_src, 2, 0, 1, 0)
        self.assertRaises(ValueError, f.get_src, 1, 2, 1, 1)

    def test_put_src_clip(self):
        f = FST('if 1:\n    j = 2\n    pass')

        f.put_src('if', -1, -1, 0, 2)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        f.put_src('pass', 2, 4, 999, 999)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        f.put_src('if 1:\n    j = 2\n    pass', -1, -1, 999, 999)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        f.put_src('    j = 2', 1, -1, 1, 999)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        f.put_src('1:\n    j = 2\n    p', -1, 3, 999, 5)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        self.assertRaises(ValueError, f.put_src, None, 2, 0, 1, 0)
        self.assertRaises(ValueError, f.put_src, None, 1, 2, 1, 1)

    def test_put_src_reparse(self):
        for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_SRC_REPARSE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                eln, ecol = f.put_src(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root
                g = f.root.find_loc(ln, col, eln, ecol)

                tdst  = f.root.src
                tdump = f.root.dump(out=list)

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

    def test_put_src_reparse_random_same(self):
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
                put_lines = master._get_src(ln, col, end_ln, end_col, True)

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

    def test_put_src_reparse_special(self):
        # tabs

        src = '''
if u:
\tif a:
\t\tpass
\telif x:
\t\tif y:
\t\t\toutput.append('/')
\t\tif z:
\t\t\tpass
\t\t\t# directory (with paths underneath it). E.g., "foo" matches "foo",
\t\t\tpass
            '''.strip()
        f = FST(src)
        s = f._get_src(5, 8, 8, 14)
        f.put_src(s, 5, 8, 8, 14)
        self.assertEqual(f.src, src)
        f.verify()

        f = FST('''
if u:
\tmatch x:
\t\tcase 1:
\t\t\ti = 2
            '''.strip())
        f.put_src('2', 2, 7, 2, 8)
        self.assertEqual(f.src, '''
if u:
\tmatch x:
\t\tcase 2:
\t\t\ti = 2
            '''.strip())
        f.verify()

        f = FST('''
if u:
\tmatch x:
\t\tcase 1:
\t\t\ti = 2
            '''.strip())
        f.put_src('2:\n\t\t\tj', 2, 7, 3, 4)
        self.assertEqual(f.src, '''
if u:
\tmatch x:
\t\tcase 2:
\t\t\tj = 2
            '''.strip())
        f.verify()

        # comments trailing single global root statement

        src = '''
if u:
  if a:
    pass
  elif x:
    if y:
      output.append('/')
    if z:
      pass
      # directory (with paths underneath it). E.g., "foo" matches "foo",
            '''.strip()
        f = FST(src)
        s = f._get_src(5, 8, 8, 14)
        f.put_src(s, 5, 8, 8, 14)
        self.assertEqual(f.src, src)
        f.verify()

        # semicoloned statements

        f = FST('\na; b = 1; c')
        f.put_src(' = 2', 1, 4, 1, 8)
        self.assertEqual('\na; b = 2; c', f.src)
        f.verify()

        f = FST('aaa;b = 1; c')
        f.put_src(' = 2', 0, 5, 0, 9)
        self.assertEqual('aaa;b = 2; c', f.src)
        f.verify()

        f = FST('a;b = 1; c')
        self.assertRaises(NotImplementedError, f.put_src, ' = 2', 0, 3, 0, 7)
        f.verify()

        f = FST('a; b = 1; c')
        self.assertRaises(NotImplementedError, f.put_src, ' = 2', 0, 4, 0, 8)
        f.verify()

        # line continuations

        f = FST('\\\nb = 1')
        f.put_src(' = 2', 1, 1, 1, 5)
        self.assertEqual('\\\nb = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\nb = 1')
        f.put_src(' = 2', 2, 1, 2, 5)
        self.assertEqual('if 1:\n \\\nb = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\n b = 1')
        f.put_src(' = 2', 2, 2, 2, 6)
        self.assertEqual('if 1:\n \\\n b = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\n  b = 1')
        f.put_src(' = 2', 2, 3, 2, 7)
        self.assertEqual('if 1:\n \\\n  b = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\naa; b = 1')
        f.put_src(' = 2', 2, 5, 2, 9)
        self.assertEqual('if 1:\n \\\naa; b = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\n a; b = 1')
        f.put_src(' = 2', 2, 5, 2, 9)
        self.assertEqual('if 1:\n \\\n a; b = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\n  a;b = 1')
        f.put_src(' = 2', 2, 5, 2, 9)
        self.assertEqual('if 1:\n \\\n  a;b = 2', f.src)
        f.verify()

        if PYGE11:
            # make sure TryStar reparses to TryStar

            f = FST('''
try:
    raise Exception('yarr!')
except* BaseException:
    hit_except = True
finally:
    hit_finally = True
                '''.strip())
            f.put_src('ry', 0, 1, 0, 3)
            self.assertIsInstance(f.a, TryStar)
            f.verify()

        # statement that lives on compound block header line

        f = FST(src := r'''
if 1:
    if \
 args:args=['-']
            '''.strip())
        f.put_src('', 2, 15, 2, 15)
        self.assertEqual(src, f.src)
        f.verify()

        # calling on a node which is not in the location of source being changed

        f = FST(r'''
if 1: pass
else:
    if 2:
        i = 3
            '''.strip(), 'exec')
        f.body[0].orelse[0].body[0].value.put_src(r'''
if 2:
    if 3:
        j +='''.strip(), 1, 2, 3, 11)
        self.assertEqual(r'''
if 1: pass
elif 2:
    if 3:
        j += 3
            '''.strip(), f.src)
        f.verify()

    def test_put_src_offset(self):
        f = FST('a, b, c')
        f.put_src(' ', 0, 0, 0, 0, 'offset')
        self.assertEqual(' a, b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 1, 0, 2), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 1, 0, 1, 'offset')
        self.assertEqual('a , b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 3, 0, 3, 'offset')
        self.assertEqual('a,  b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 4, 0, 4, 'offset')
        self.assertEqual('a, b , c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 6, 0, 6, 'offset')
        self.assertEqual('a, b,  c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 7, 0, 7, 'offset')
        self.assertEqual('a, b, c ', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 6, 0, 7), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[0].put_src(' ', 0, 0, 0, 0, 'offset')
        self.assertEqual(' a, b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 2), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[0].put_src(' ', 0, 1, 0, 1, 'offset')
        self.assertEqual('a , b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 2), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[1].put_src(' ', 0, 3, 0, 3, 'offset')
        self.assertEqual('a,  b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[1].put_src(' ', 0, 4, 0, 4, 'offset')
        self.assertEqual('a, b , c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[2].put_src(' ', 0, 6, 0, 6, 'offset')
        self.assertEqual('a, b,  c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 6, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[2].put_src(' ', 0, 7, 0, 7, 'offset')
        self.assertEqual('a, b, c ', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 6, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        self.assertRaises(ValueError, f.elts[0].put_src, ' ', 0, 2, 0, 2, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 2, 0, 2, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 5, 0, 5, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 2, 0, 4, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 3, 0, 5, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 2, 0, 5, 'offset')

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

        self.assertEqual(src.split('\n'), ast.f._get_src(*ast.f.loc, True))
        self.assertEqual(src.split('\n'), ast.body[0].f._get_src(*ast.body[0].f.loc, True))
        self.assertEqual('if True:\n  i = 1\n else:\n  j = 2'.split('\n'), ast.body[0].body[0].f._get_src(*ast.body[0].body[0].f.loc, True))
        self.assertEqual(['i = 1'], ast.body[0].body[0].body[0].f._get_src(*ast.body[0].body[0].body[0].f.loc, True))
        self.assertEqual(['j = 2'], ast.body[0].body[0].orelse[0].f._get_src(*ast.body[0].body[0].orelse[0].f.loc, True))

        self.assertEqual(['True:', '  i'], ast.f.root._get_src(1, 4, 2, 3, True))

    def test_par(self):
        f = parse('1,').body[0].value.f.copy()
        f.par()
        self.assertEqual('(1,)', f.src)
        f.par()
        self.assertEqual('(1,)', f.src)
        f.par(force=True)
        self.assertEqual('((1,))', f.src)
        self.assertEqual((0, 1, 0, 5), f.loc)
        f.par()
        self.assertEqual('((1,))', f.src)
        self.assertEqual((0, 1, 0, 5), f.loc)

        # self.assertFalse(parse('()').body[0].value.f.copy().par())
        # self.assertFalse(parse('[]').body[0].value.f.copy().par())
        # self.assertFalse(parse('{}').body[0].value.f.copy().par())
        self.assertEqual('()', parse('()').body[0].value.f.copy().par().src)
        self.assertEqual('[]', parse('[]').body[0].value.f.copy().par().src)
        self.assertEqual('{}', parse('{}').body[0].value.f.copy().par().src)

        f = parse('i = 1').body[0].f.copy()
        f._put_src(['# comment', ''], 0, 0, 0, 0)
        f.par()
        self.assertEqual('# comment\ni = 1', f.src)
        f.par(force=True)
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

        f.par()
        self.assertEqual('*(\na)', f.src)
        f.verify()

        f = FST('\n*\na\n')
        f.par()
        self.assertEqual('\n*(\na\n)', f.src)
        f.verify()

        f.par()
        self.assertEqual('\n*(\na\n)', f.src)
        f.verify()

        f = FST('\n*\na\n')
        f.par(whole=False)
        self.assertEqual('\n*(\na)\n', f.src)
        f.verify()

        f.par(whole=False)
        self.assertEqual('\n*(\na)\n', f.src)
        f.verify()

        f = FST('*a')
        f.par(True)
        self.assertEqual('*(a)', f.src)
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

        # make sure parenthesized elements update parent locations

        self.assertEqual('if 1: *(a.b)', (f := FST('if 1: *a.b')).body[0].value.par().root.src)
        self.assertEqual((0, 0, 0, 12), f.loc)
        self.assertEqual((0, 6, 0, 12), f.body[0].loc)
        self.assertEqual((0, 6, 0, 12), f.body[0].value.loc)
        self.assertEqual((0, 8, 0, 11), f.body[0].value.value.loc)

        self.assertEqual('if 1: (a, b)', (f := FST('if 1: a, b')).body[0].value.par().root.src)
        self.assertEqual((0, 0, 0, 12), f.loc)
        self.assertEqual((0, 6, 0, 12), f.body[0].loc)
        self.assertEqual((0, 6, 0, 12), f.body[0].value.loc)

        self.assertEqual('if 1: ((a, b))', f.body[0].value.par(force=True).root.src)
        self.assertEqual((0, 0, 0, 14), f.loc)
        self.assertEqual((0, 6, 0, 14), f.body[0].loc)
        self.assertEqual((0, 7, 0, 13), f.body[0].value.loc)

        self.assertEqual('case [a, b]: pass', (f := FST('case a, b: pass')).pattern.par().root.src)
        self.assertEqual((0, 0, 0, 17), f.loc)
        self.assertEqual((0, 5, 0, 11), f.pattern.loc)
        self.assertEqual((0, 13, 0, 17), f.body[0].loc)

        self.assertEqual('case ([a, b]): pass', f.pattern.par(force=True).root.src)
        self.assertEqual((0, 0, 0, 19), f.loc)
        self.assertEqual((0, 6, 0, 12), f.pattern.loc)
        self.assertEqual((0, 15, 0, 19), f.body[0].loc)

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

        f = FST('*(\na\n)')
        self.assertEqual('*(\na\n)', f.src)
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
            ssrc = f._get_src(*l)

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
        self.assertEqual((0, 0, 0, 7), f.pars(shared=None))

        f = FST('f(a)')
        self.assertEqual((0, 2, 0, 3), f.args[0].pars())
        self.assertEqual((0, 1, 0, 4), f.args[0].pars(shared=None))

        f = FST('class c(a): pass')
        self.assertEqual((0, 8, 0, 9), f.bases[0].pars())
        self.assertEqual((0, 7, 0, 10), f.bases[0].pars(shared=None))

        f = FST('case f(a): pass')
        self.assertEqual((0, 7, 0, 8), f.pattern.patterns[0].pars())
        self.assertEqual((0, 6, 0, 9), f.pattern.patterns[0].pars(shared=None))

        f = FST('from a import (b)')
        self.assertEqual((0, 15, 0, 16), f.names[0].pars())
        self.assertEqual((0, 14, 0, 17), f.names[0].pars(shared=None))

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
        self.assertEqual((g := f.copy())._get_src(*g.loc), f.src)

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

    def test_find_loc_in(self):
        f    = parse('abc += xyz').f
        fass = f.body[0]
        fabc = fass.target
        fpeq = fass.op
        fxyz = fass.value

        self.assertIs(fass, f.find_loc_in(0, 0, 0, 10))
        self.assertIs(None, f.find_loc_in(0, 0, 0, 10, False))
        self.assertIs(f, f.find_loc_in(0, 0, 0, 10, 'top'))
        self.assertIs(fabc, f.find_loc_in(0, 0, 0, 3))
        self.assertIs(fass, f.find_loc_in(0, 0, 0, 3, False))
        self.assertIs(fabc, f.find_loc_in(0, 0, 0, 3, 'top'))
        self.assertIs(fass, f.find_loc_in(0, 0, 0, 4))
        self.assertIs(fass, f.find_loc_in(0, 0, 0, 4, False))
        self.assertIs(fass, f.find_loc_in(0, 0, 0, 4, 'top'))
        self.assertIs(fass, f.find_loc_in(0, 3, 0, 4, False))
        self.assertIs(fass, f.find_loc_in(0, 3, 0, 4, 'top'))
        self.assertIs(fpeq, f.find_loc_in(0, 4, 0, 6))
        self.assertIs(fass, f.find_loc_in(0, 4, 0, 6, False))
        self.assertIs(fpeq, f.find_loc_in(0, 4, 0, 6, 'top'))
        self.assertIs(fxyz, f.find_loc_in(0, 7, 0, 10))
        self.assertIs(fass, f.find_loc_in(0, 7, 0, 10, False))
        self.assertIs(fxyz, f.find_loc_in(0, 7, 0, 10, 'top'))
        self.assertIs(fass, f.find_loc_in(0, 6, 0, 10))
        self.assertIs(fass, f.find_loc_in(0, 7, 0, 10, False))
        self.assertIs(fass, f.find_loc_in(0, 6, 0, 10, 'top'))

        f  = parse('a+b').f
        fx = f.body[0]
        fo = fx.value
        fa = fo.left
        fp = fo.op
        fb = fo.right

        self.assertIs(fa, f.find_loc_in(0, 0, 0, 0))
        self.assertIs(fp, f.find_loc_in(0, 1, 0, 1))
        self.assertIs(fb, f.find_loc_in(0, 2, 0, 2))
        self.assertIs(f, f.find_loc_in(0, 3, 0, 3))
        self.assertIs(fa, f.find_loc_in(0, 0, 0, 1))
        self.assertIs(fo, f.find_loc_in(0, 0, 0, 2))
        self.assertIs(fo, f.find_loc_in(0, 0, 0, 3))
        self.assertIs(fp, f.find_loc_in(0, 1, 0, 2))
        self.assertIs(fo, f.find_loc_in(0, 1, 0, 3))
        self.assertIs(fb, f.find_loc_in(0, 2, 0, 3))

        froot = FST('var', 'exec')
        fexpr = froot.body[0]
        fname = fexpr.value

        self.assertIs(fname, froot.find_loc_in(0, 0, 0, 3, True))
        self.assertIs(None, froot.find_loc_in(0, 0, 0, 3, False))
        self.assertIs(froot, froot.find_loc_in(0, 0, 0, 3, 'top'))
        self.assertIs(fname, froot.find_loc_in(0, 1, 0, 2, True))
        self.assertIs(fname, froot.find_loc_in(0, 1, 0, 2, False))
        self.assertIs(fname, froot.find_loc_in(0, 1, 0, 2, 'top'))
        self.assertIs(fname, froot.find_loc_in(0, 0, 0, 1, True))
        self.assertIs(fname, froot.find_loc_in(0, 0, 0, 1, False))
        self.assertIs(fname, froot.find_loc_in(0, 0, 0, 1, 'top'))
        self.assertIs(fname, froot.find_loc_in(0, 2, 0, 3, True))
        self.assertIs(fname, froot.find_loc_in(0, 2, 0, 3, False))
        self.assertIs(fname, froot.find_loc_in(0, 2, 0, 3, 'top'))

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

    def test_find_loc(self):
        f    = parse('abc += xyz').f
        fass = f.body[0]
        fabc = fass.target
        fpeq = fass.op
        fxyz = fass.value

        self.assertIs(fass, f.find_loc(0, 0, 0, 10))
        self.assertIs(f, f.find_loc(0, 0, 0, 10, True))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 3))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 3, True))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 4))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 4, True))
        self.assertIs(fass, f.find_loc(0, 3, 0, 4))
        self.assertIs(fass, f.find_loc(0, 3, 0, 4, True))
        self.assertIs(fpeq, f.find_loc(0, 4, 0, 6))
        self.assertIs(fpeq, f.find_loc(0, 4, 0, 6, True))
        self.assertIs(fxyz, f.find_loc(0, 7, 0, 10))
        self.assertIs(fxyz, f.find_loc(0, 7, 0, 10, True))
        self.assertIs(fxyz, f.find_loc(0, 6, 0, 10))
        self.assertIs(fxyz, f.find_loc(0, 6, 0, 10, True))
        self.assertIs(fass, f.find_loc(0, 6, 0, 9))
        self.assertIs(fass, f.find_loc(0, 6, 0, 9, True))

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
        self.assertIs(fa, f.find_loc(0, 0, 0, 2))
        self.assertIs(fo, f.find_loc(0, 0, 0, 3))
        self.assertIs(f, f.find_loc(0, 0, 0, 3, True))
        self.assertIs(fp, f.find_loc(0, 1, 0, 2))
        self.assertIs(fp, f.find_loc(0, 1, 0, 3))
        self.assertIs(fb, f.find_loc(0, 2, 0, 3))

        froot = FST('var', 'exec')
        fexpr = froot.body[0]
        fname = fexpr.value

        self.assertIs(fname, froot.find_loc(0, 0, 0, 3))
        self.assertIs(froot, froot.find_loc(0, 0, 0, 3, True))
        self.assertIs(fname, froot.find_loc(0, 1, 0, 2))
        self.assertIs(fname, froot.find_loc(0, 1, 0, 2, True))
        self.assertIs(fname, froot.find_loc(0, 0, 0, 1))
        self.assertIs(fname, froot.find_loc(0, 0, 0, 1, True))
        self.assertIs(fname, froot.find_loc(0, 2, 0, 3))
        self.assertIs(fname, froot.find_loc(0, 2, 0, 3, True))

        f    = parse('abc += xyz').f
        fass = f.body[0]
        fabc = fass.target
        fpeq = fass.op
        fxyz = fass.value

        self.assertIs(fass, f.find_loc(0, 0, 0, 10))
        self.assertIs(f, f.find_loc(0, 0, 0, 10, True))
        self.assertIs(f, f.find_loc(-1, -1, 1, 11))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 3))
        self.assertIs(fpeq, f.find_loc(0, 1, 0, 10))
        self.assertIs(fxyz, f.find_loc(0, 5, 0, 10))
        self.assertIs(fpeq, f.find_loc(0, 5, 0, 6))
        self.assertIs(fass, f.find_loc(0, 6, 0, 7))
        self.assertIs(fass, f.find_loc(0, 6, 0, 7, True))

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

    def test_options_thread_local(self):
        def threadfunc(barrier, ret, option, value):
            FST.set_options(**{option: value})
            barrier.wait()

            ret[0] = FST.get_option(option)

        barrier = threading.Barrier(2)
        thread0 = threading.Thread(target=threadfunc, args=(barrier, ret0 := [None], 'pars', True))
        thread1 = threading.Thread(target=threadfunc, args=(barrier, ret1 := [None], 'pars', False))

        thread0.start()
        thread1.start()
        thread0.join()
        thread1.join()

        self.assertEqual('auto', FST.get_option('pars'))
        self.assertEqual(True, ret0[0])
        self.assertEqual(False, ret1[0])

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
        o.a.elts[0] = UnaryOp(USub(), Constant(value=1))
        o.a.elts[1] = UnaryOp(USub(), Constant(value=2))
        o.a.elts[2] = UnaryOp(USub(), Constant(value=3))
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
        self.assertEqual('i = 1\nj = 2\nk = 3\nx = 4\ny = 5', f.src)
        f.verify()

        # other recurse slice FST

        m = (o := FST('[1]')).mark()
        o.a.elts.extend(FST('[2,#2\n3,#3\n4,#4\n]').a.elts)
        f = o.reconcile(m)
        self.assertEqual('[1, 2,#2\n 3,#3\n 4,#4\n]', f.src)
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
        self.assertEqual('if 1:\n  b = 5\n  c = 6\nelse:\n  i = 1\n  j = 2\n  k = 3\n  i = 1\n  j = 2\n  k = 3', f.src)
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
        self.assertEqual('[\n 2, # 2\n 1, # 1\n]', f.src)
        f.verify()

        m = (o := FST('[1,\n# 1and2\n2, 3,\n# 3and4\n4]')).mark()
        o.a = List(elts=[o.a.elts[2], o.a.elts[3], o.a.elts[0], o.a.elts[1]])
        f = o.reconcile(m)
        self.assertEqual('[3,\n # 3and4\n 4, 1,\n # 1and2\n 2]', f.src)
        f.verify()

        m = (o := FST('[1,#1\n]')).mark()
        o.a = List(elts=[o.a.elts[0]])
        o.a.elts.extend(FST('[2,#2\n3,#3\n4,#4\n]').a.elts)
        f = o.reconcile(m)
        self.assertEqual('[1, #1\n 2,#2\n 3,#3\n 4,#4\n]', f.src)
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
        self.assertEqual('[\n[\n [\n[\n [\n[\n [\n[\n x,#0\n],#1\n1\n],#2\n],#3\n3\n],#4\n],#5\n5\n],#6\n],#7\n7\n]', f.src)
        f.verify()

        a = (o := FST('[\n[\n[\n[\n[\n[\n[\n[\nx,#0\n0\n],#1\n1\n],#2\n2\n],#3\n3\n],#4\n4\n],#5\n5\n],#6\n6\n],#7\n7\n]')).a
        m = o.mark()
        o.a = List(elts=[a.elts[0]])
        a.elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0]])
        f = o.reconcile(m)
        self.assertEqual('[\n [\n[\n [\n[\n [\n[\n [\nx,#0\n0\n],#1\n],#2\n2\n],#3\n],#4\n4\n],#5\n],#6\n6\n],#7\n]', f.src)
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

            except (NodeError, ValueError) as exc:
                if not str(exc).startswith('cannot put slice to'):
                    raise

                getattr(f, field)[0] = put

            f.verify()

            return f

        self.assertEqual('a', test(FST('i\nj', 'exec'), 'body', 'a', fstview, 'i\nj').src)
        self.assertEqual('a', test(FST('i;j', 'single'), 'body', 'a', fstview, 'i;j').src)
        self.assertEqual('a', test(FST('i', 'eval'), 'body', 'a', FST, 'i').src)

        f = FST('@deco\ndef func(args) -> ret: pass')
        self.assertEqual('@deco\ndef func(args) -> ret: pass', test(f, 'decorator_list', '@deco', fstview,
                                                                    '<<FunctionDef ROOT 1,0..1,27>.decorator_list[0:1] [<Name 0,1..0,5>]>').src)
        self.assertEqual('@deco\ndef new(args) -> ret: pass', test(f, 'name', 'new', None, 'func').src)
        self.assertEqual('@deco\ndef new(nargs) -> ret: pass', test(f, 'args', 'nargs', FST, 'args').src)
        self.assertEqual('@deco\ndef new(nargs) -> int: pass', test(f, 'returns', 'int', FST, 'ret').src)
        self.assertEqual('@deco\ndef new(nargs) -> int:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('@deco\nasync def func(args) -> ret: pass')
        self.assertEqual('@deco\nasync def func(args) -> ret: pass', test(f, 'decorator_list', '@deco', fstview,
                                                                          '<<AsyncFunctionDef ROOT 1,0..1,33>.decorator_list[0:1] [<Name 0,1..0,5>]>').src)
        self.assertEqual('@deco\nasync def new(args) -> ret: pass', test(f, 'name', 'new', None, 'func').src)
        self.assertEqual('@deco\nasync def new(nargs) -> ret: pass', test(f, 'args', 'nargs', FST, 'args').src)
        self.assertEqual('@deco\nasync def new(nargs) -> int: pass', test(f, 'returns', 'int', FST, 'ret').src)
        self.assertEqual('@deco\nasync def new(nargs) -> int:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('@deco\nclass cls(base, meta=other): pass')
        self.assertEqual('@deco\nclass cls(base, meta=other): pass', test(f, 'decorator_list', '@deco', fstview,
                                                                          '<<ClassDef ROOT 1,0..1,33>.decorator_list[0:1] [<Name 0,1..0,5>]>').src)
        self.assertEqual('@deco\nclass new(base, meta=other): pass', test(f, 'name', 'new', None, 'cls').src)
        self.assertEqual('@deco\nclass new(bass, meta=other): pass', test(f, 'bases', 'bass,', fstview, '(base,)').src)
        self.assertEqual('@deco\nclass new(bass, moto=some): pass', test(f, 'keywords', 'moto=some', fstview,
                                                                         '<<ClassDef ROOT 1,0..1,33>.keywords[0:1] [<keyword 1,16..1,26>]>').src)
        self.assertEqual('@deco\nclass new(bass, moto=some):\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        self.assertEqual('return yup', test(FST('return yes'), 'value', 'yup', FST, 'yes').src)

        self.assertEqual('del zzz', test(FST('del a, b'), 'targets', 'zzz', fstview, 'a, b').src)

        self.assertEqual('zzz = c', test(FST('a, b = c'), 'targets', 'zzz', fstview, 'a, b =').src)
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
        self.assertEqual('for new in zzz:\n    return\nelse:\n    continue', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('async for a, b in c: pass\nelse: pass')
        self.assertEqual('async for new in c: pass\nelse: pass', test(f, 'target', 'new', FST, 'a, b').src)
        self.assertEqual('async for new in zzz: pass\nelse: pass', test(f, 'iter', 'zzz', FST, 'c').src)
        self.assertEqual('async for new in zzz:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('async for new in zzz:\n    return\nelse:\n    continue', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('while a: pass\nelse: pass')
        self.assertEqual('while new: pass\nelse: pass', test(f, 'test', 'new', FST, 'a').src)
        self.assertEqual('while new:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('while new:\n    return\nelse:\n    continue', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('if a: pass\nelse: pass')
        self.assertEqual('if new: pass\nelse: pass', test(f, 'test', 'new', FST, 'a').src)
        self.assertEqual('if new:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('if new:\n    return\nelse:\n    continue', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('with a as b: pass')
        self.assertEqual('with old as new: pass', test(f, 'items', 'old as new', fstview, 'a as b').src)
        self.assertEqual('with old as new:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('async with a as b: pass')
        self.assertEqual('async with old as new: pass', test(f, 'items', 'old as new', fstview, 'a as b').src)
        self.assertEqual('async with old as new:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('match a:\n    case _: pass')
        self.assertEqual('match new:\n    case _: pass', test(f, 'subject', 'new', FST, 'a').src)
        self.assertEqual('match new:\n    case 1: return', test(f, 'cases', 'case 1: return', fstview, 'case _: pass').src)

        f = FST('raise exc from cause')
        self.assertEqual('raise e from cause', test(f, 'exc', 'e', FST, 'exc').src)
        self.assertEqual('raise e from c', test(f, 'cause', 'c', FST, 'cause').src)

        f = FST('try: pass\nexcept: pass\nelse: pass\nfinally: pass')
        self.assertEqual('try:\n    return\nexcept: pass\nelse: pass\nfinally: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse: pass\nfinally: pass', test(f, 'handlers', 'except Exception as e: continue', fstview, 'except: pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse:\n    break\nfinally: pass', test(f, 'orelse', 'break', fstview, 'pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse:\n    break\nfinally:\n    f()', test(f, 'finalbody', 'f()', fstview, 'pass').src)

        f = FST('assert test, "msg"')
        self.assertEqual('assert toast, "msg"', test(f, 'test', 'toast', FST, 'test').src)
        self.assertEqual('assert toast, "sheep"', test(f, 'msg', '"sheep"', FST, '"msg"').src)

        self.assertEqual('import a, b, c', test(FST('import x, y'), 'names', 'a, b, c', fstview, 'x, y').src)

        f = FST('from .module import x, y')
        self.assertEqual('from .new import x, y', test(f, 'module', 'new', None, 'module').src)
        self.assertEqual('from .new import a, b, c', test(f, 'names', 'a, b, c', fstview, 'x, y').src)
        self.assertEqual('from ...new import a, b, c', test(f, 'level', 3, None, 1).src)

        self.assertEqual('global a, b, c', test(FST('global x, y'), 'names', 'a, b, c', fstview, 'x, y').src)

        self.assertEqual('nonlocal a, b, c', test(FST('nonlocal x, y'), 'names', 'a, b, c', fstview, 'x, y').src)

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
        self.assertEqual('call(a, b, kw=blah)', test(f, 'args', 'a, b', fstview, '(arg,)').src)
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
        self.assertEqual('except ValueError as blah:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

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
        self.assertEqual('case new if old:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

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
            self.assertEqual('try:\n    return\nexcept* Exception as e: continue\nelse:\n    break\nfinally:\n    f()', test(f, 'finalbody', 'f()', fstview, 'pass').src)

        if not PYLT12:
            self.assertEqual('def func[U](): pass', test(FST('def func[T](): pass'), 'type_params', 'U', fstview, 'T').src)

            self.assertEqual('async def func[U](): pass', test(FST('async def func[T](): pass'), 'type_params', 'U', fstview, 'T').src)

            self.assertEqual('class cls[U]: pass', test(FST('class cls[T]: pass'), 'type_params', 'U', fstview, 'T').src)

            f = FST('type t[T] = v')
            self.assertEqual('type new[T] = v', test(f, 'name', 'new', FST, 't').src)
            self.assertEqual('type new[U] = v', test(f, 'type_params', 'U', fstview, 'T').src)
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

    def test_precedence(self):
        data = iter(PRECEDENCE_DATA)

        for dst, *attrs in PRECEDENCE_DST_STMTS + PRECEDENCE_DST_EXPRS + PRECEDENCE_SRC_EXPRS:
            for src, *_ in PRECEDENCE_SRC_EXPRS:
                for attr in attrs:
                    d       = dst.copy()
                    s       = src.body[0].value.copy()
                    is_stmt = isinstance(d.a, stmt)
                    f       = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})
                    truth   = next(data)

                    try:
                        (parent := f.parent).put(s, idx := f.pfield.idx, name := f.pfield.name)

                    except Exception as exc:
                        is_exc = True
                        test   = str(exc)

                        if test == 'put inside JoinedStr not implemented on python < 3.12':
                            continue

                    else:
                        is_exc = False
                        test   = f.root.src

                        f.root.verify()

                    self.assertEqual(test, truth)

                    if is_exc:
                        continue

                    # vs. python

                    if attr == 'value' and isinstance(parent.a, NamedExpr):  # we explicitly parenthesize NamedExpr.value because by default we differ from python ast.unparse() and don't do this normally
                        test = parent.put(src.body[0].value.copy().par(), idx, name, pars=True).root.src

                    d            = dst.copy()
                    s            = src.body[0].value.copy()
                    f            = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})
                    is_unpar_tup = False if is_stmt else (d.body[0].value._is_parenthesized_tuple() is False)

                    if PYLT11 and isinstance(s.a, Tuple) and isinstance(d.a, (Assign, For, AsyncFor)):  # py 3.10 parenthesizes target tuples, we do not normally so we do it here explicitly for the compare
                        test = parent.put(src.body[0].value.copy().par(), idx, name, pars=True).root.src

                    f.pfield.set(f.parent.a, s.a)

                    py_truth = ast_unparse(f.root.a).replace('lambda :', 'lambda:')

                    if is_unpar_tup:
                        py_truth = py_truth[1:-1]

                    self.assertEqual(test, py_truth)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-pars', default=False, action='store_true', help="regenerate parentheses test data")
    parser.add_argument('--regen-put-src', default=False, action='store_true', help="regenerate put src test data")
    parser.add_argument('--regen-precedence', default=False, action='store_true', help="regenerate precedence test data")
    parser.add_argument('--regen-parse-autogen', default=False, action='store_true', help="regenerate autogenerated parse test data")

    args, _ = parser.parse_known_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT14:
            raise RuntimeError('cannot regenerate on python version < 3.14')

    if args.regen_pars or args.regen_all:
        print('Regenerating parentheses test data...')
        regen_pars_data()

    if args.regen_put_src or args.regen_all:
        print('Regenerating put raw test data...')
        regen_put_src()

    if args.regen_precedence or args.regen_all:
        print('Regenerating precedence test data...')
        regen_precedence_data()

    if args.regen_parse_autogen or args.regen_all:
        print('Regenerating autogenerated parse test data...')
        regen_parse_autogen_data()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
