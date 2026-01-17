#!/usr/bin/env python

import os
import traceback
import types
import unittest
from ast import unparse as ast_unparse
from keyword import kwlist as keyword_kwlist

from fst import *

from fst.asttypes import (
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _arglikes,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from fst.astutil import (
    OPSTR2CLS_UNARY,
    OPSTR2CLS_BIN,
    OPSTR2CLS_CMP,
    OPSTR2CLS_BOOL,
    OPCLS2STR,
    copy_ast,
    compare_asts,
)

from fst.common import PYLT11, PYLT14, PYGE11, PYGE12, PYGE13

from fst.code import *

from fst import parsex as px, code

from support import BaseCases, ParseCases, CoerceCases


DIR_NAME = os.path.dirname(__file__)
FNM_PARSE_AUTOGEN = os.path.join(DIR_NAME, 'data/data_parse_autogen.py')
FNM_SYNTAX_ERRORS = os.path.join(DIR_NAME, 'data/data_syntax_errors.py')
FNM_PARSE_INVALID_SRC = os.path.join(DIR_NAME, 'data/data_parse_invalid_src.txt')

DATA_COERCE = CoerceCases(os.path.join(DIR_NAME, 'data/data_coerce.py'))

PARSE_TESTS = [
    ('all',                px.parse_stmts,              Module,                   '#'),
    ('all',                px.parse_stmts,              Module,                   'i: int = 1\nj'),
    ('all',                px.parse__ExceptHandlers,    _ExceptHandlers,          'except Exception: pass\nexcept: pass'),
    ('all',                px.parse__match_cases,       _match_cases,             'case None: pass\ncase 1: pass'),
    ('all',                px.parse_stmt,               AnnAssign,                'i: int = 1'),
    ('all',                px.parse_ExceptHandler,      ExceptHandler,            'except: pass'),
    ('all',                px.parse_match_case,         match_case,               'case None: pass'),
    ('all',                px.parse_stmts,              Module,                   'i: int = 1\nj'),
    ('all',                px.parse_stmt,               AnnAssign,                'i: int = 1'),
    ('all',                px.parse__ExceptHandlers,    _ExceptHandlers,          'except Exception: pass\nexcept: pass'),
    ('all',                px.parse_ExceptHandler,      ExceptHandler,            'except: pass'),
    ('all',                px.parse__match_cases,       _match_cases,             'case None: pass\ncase 1: pass'),
    ('all',                px.parse_match_case,         match_case,               'case None: pass'),
    ('all',                px.parse_expr,               Name,                     'j'),
    ('all',                px.parse_expr,               Starred,                  '*s'),
    ('all',                px.parse_expr_all,           Starred,                  '*not a'),
    ('all',                px.parse_stmt,               AnnAssign,                'a:b'),
    ('all',                px.parse_expr_all,           Slice,                    'a:b:c'),
    ('all',                px.parse_expr_all,           Slice,                    ':b:c'),
    ('all',                px.parse_expr_all,           Slice,                    '::'),
    ('all',                px.parse_expr_all,           Slice,                    ':'),
    ('all',                px.parse_pattern,            MatchAs,                  '1 as a'),
    ('all',                px.parse_arguments,          arguments,                'a: list[str], /, b: int = 1, *c, d=100, **e'),
    ('all',                px.parse_arguments_lambda,   arguments,                'a, /, b, *c, d=100, **e'),
    ('all',                px.parse_arguments,          arguments,                '**a: dict'),
    ('all',                px.parse_pattern,            MatchSequence,            '*a, b as c'),
    ('all',                px.parse_comprehension,      comprehension,            'for i in range(5) if i'),
    ('all',                px.parse__comprehensions,    _comprehensions,          'for j in k if j async for i in j if i'),
    ('all',                px.parse__comprehension_ifs, _comprehension_ifs,       'if u'),
    ('all',                px.parse__comprehension_ifs, _comprehension_ifs,       'if u if v'),
    ('all',                px.parse_withitem,           withitem,                 'f(**a) as b'),
    ('all',                px.parse__withitems,         _withitems,               'f(**a) as b,'),
    ('all',                px.parse__withitems,         _withitems,               'f(**a) as b, c as d'),
    ('all',                px.parse_operator,           Mult,                     '*'),
    ('all',                px.parse_cmpop,              Gt,                       '>'),
    ('all',                px.parse_boolop,             And,                      'and'),
    ('all',                px.parse_unaryop,            Invert,                   '~'),
    ('all',                px.parse_operator,           LShift,                   '<<'),
    ('all',                px.parse__Assign_targets,    _Assign_targets,          'a = '),
    ('all',                px.parse__Assign_targets,    _Assign_targets,          'a = b ='),
    ('all',                px.parse__decorator_list,    _decorator_list,          '@a'),
    ('all',                px.parse__decorator_list,    _decorator_list,          '@a\n@b'),
    ('all',                px.parse_stmt,               Assign,                   '_ = 1'),
    ('all',                px.parse_stmt,               Assign,                   'case = 1'),
    ('all',                px.parse_stmt,               Assign,                   'match = 1'),
    ('all',                px.parse_stmt,               Assign,                   'type = 1'),
    ('all',                px.parse_all,                SyntaxError,              'elif'),
    ('all',                px.parse_all,                SyntaxError,              'else'),
    ('all',                px.parse_all,                SyntaxError,              'finally'),
    ('all',                px.parse_all,                SyntaxError,              'as'),

    ('strict',             px.parse_stmts,              Module,                   '#'),
    ('strict',             px.parse_stmts,              Module,                   'i: int = 1\nj'),
    ('strict',             px.parse__ExceptHandlers,    SyntaxError,              'except Exception: pass\nexcept: pass'),
    ('strict',             px.parse__match_cases,       SyntaxError,              'case None: pass\ncase 1: pass'),
    ('strict',             px.parse_stmt,               AnnAssign,                'i: int = 1'),
    ('strict',             px.parse_ExceptHandler,      SyntaxError,              'except: pass'),
    ('strict',             px.parse_match_case,         SyntaxError,              'case None: pass'),
    ('strict',             px.parse_stmts,              Module,                   'i: int = 1\nj'),
    ('strict',             px.parse_stmt,               AnnAssign,                'i: int = 1'),
    ('strict',             px.parse__ExceptHandlers,    SyntaxError,              'except Exception: pass\nexcept: pass'),
    ('strict',             px.parse_ExceptHandler,      SyntaxError,              'except: pass'),
    ('strict',             px.parse__match_cases,       SyntaxError,              'case None: pass\ncase 1: pass'),
    ('strict',             px.parse_match_case,         SyntaxError,              'case None: pass'),
    ('strict',             px.parse_expr,               Name,                     'j'),
    ('strict',             px.parse_expr,               Starred,                  '*s'),
    ('strict',             px.parse_all,                SyntaxError,              '*not a'),
    ('strict',             px.parse_stmt,               AnnAssign,                'a:b'),
    ('strict',             px.parse_all,                SyntaxError,              'a:b:c'),
    ('strict',             px.parse_all,                SyntaxError,              '1 as a'),
    ('strict',             px.parse_all,                SyntaxError,              'a: list[str], /, b: int = 1, *c, d=100, **e'),
    ('strict',             px.parse_all,                SyntaxError,              'a, /, b, *c, d=100, **e'),
    ('strict',             px.parse_all,                SyntaxError,              '*not a'),
    ('strict',             px.parse_all,                SyntaxError,              'for i in range(5) if i'),
    ('strict',             px.parse_all,                SyntaxError,              'f(**a) as b'),
    ('strict',             px.parse_all,                SyntaxError,              '*'),
    ('strict',             px.parse_all,                SyntaxError,              '*='),
    ('strict',             px.parse_all,                SyntaxError,              '>'),
    ('strict',             px.parse_all,                SyntaxError,              'and'),
    ('strict',             px.parse_all,                SyntaxError,              '~'),

    ('exec',               px.parse_Module,             Module,                   '#'),
    ('exec',               px.parse_Module,             Module,                   'i: int = 1'),

    ('eval',               px.parse_Expression,         SyntaxError,              '#'),
    ('eval',               px.parse_Expression,         Expression,               'None'),

    ('single',             px.parse_Interactive,        SyntaxError,              '#'),
    ('single',             px.parse_Interactive,        Interactive,              'i: int = 1'),

    ('stmts',              px.parse_stmts,              Module,                   '#'),
    ('stmts',              px.parse_stmts,              Module,                   'i: int = 1\nj'),
    ('stmts',              px.parse_stmts,              SyntaxError,              'except Exception: pass\nexcept: pass'),
    ('stmt',               px.parse_stmt,               ParseError,               '#'),
    ('stmt',               px.parse_stmt,               AnnAssign,                'i: int = 1'),
    ('stmt',               px.parse_stmt,               Expr,                     'j'),
    ('stmt',               px.parse_stmt,               ParseError,               'i: int = 1\nj'),
    ('stmt',               px.parse_stmt,               SyntaxError,              'except: pass'),

    ('_ExceptHandlers',    px.parse__ExceptHandlers,    _ExceptHandlers,          '#'),
    ('_ExceptHandlers',    px.parse__ExceptHandlers,    _ExceptHandlers,          ''),
    ('_ExceptHandlers',    px.parse__ExceptHandlers,    _ExceptHandlers,          'except Exception: pass\nexcept: pass'),
    ('_ExceptHandlers',    px.parse__ExceptHandlers,    IndentationError,         ' except Exception: pass\nexcept: pass'),
    ('_ExceptHandlers',    px.parse__ExceptHandlers,    ParseError,               'except Exception: pass\nexcept: pass\nelse: pass'),
    ('_ExceptHandlers',    px.parse__ExceptHandlers,    ParseError,               'except Exception: pass\nexcept: pass\nfinally: pass'),
    ('_ExceptHandlers',    px.parse__ExceptHandlers,    SyntaxError,              'i: int = 1\nj'),
    ('ExceptHandler',      px.parse_ExceptHandler,      ParseError,               '#'),
    ('ExceptHandler',      px.parse_ExceptHandler,      ParseError,               ''),
    ('ExceptHandler',      px.parse_ExceptHandler,      ExceptHandler,            'except: pass'),
    ('ExceptHandler',      px.parse_ExceptHandler,      ParseError,               'except Exception: pass\nexcept: pass'),
    ('ExceptHandler',      px.parse_ExceptHandler,      IndentationError,         'except:\n  pass\n    pass'),
    ('ExceptHandler',      px.parse_ExceptHandler,      IndentationError,         '  except: pass'),
    ('ExceptHandler',      px.parse_ExceptHandler,      ParseError,               'finally: pass'),
    ('ExceptHandler',      px.parse_ExceptHandler,      SyntaxError,              'else: pass'),
    ('ExceptHandler',      px.parse_ExceptHandler,      SyntaxError,              'i: int = 1'),

    ('_match_cases',       px.parse__match_cases,       _match_cases,             '#'),
    ('_match_cases',       px.parse__match_cases,       _match_cases,             ''),
    ('_match_cases',       px.parse__match_cases,       _match_cases,             'case None: pass\ncase 1: pass'),
    ('_match_cases',       px.parse__match_cases,       IndentationError,         ' case None: pass\ncase 1: pass'),
    ('_match_cases',       px.parse__match_cases,       SyntaxError,              'i: int = 1'),
    ('match_case',         px.parse_match_case,         ParseError,               '#'),
    ('match_case',         px.parse_match_case,         ParseError,               ''),
    ('match_case',         px.parse_match_case,         match_case,               'case None: pass'),
    ('match_case',         px.parse_match_case,         ParseError,               'case None: pass\ncase 1: pass'),
    ('match_case',         px.parse_match_case,         SyntaxError,              'i: int = 1'),

    ('_Assign_targets',    px.parse__Assign_targets,    SyntaxError,              '#'),  # cannot be this because newlines not allowed
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          ''),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          'a'),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          'a ='),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          'a = b'),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          'a = b ='),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          '\\\na\\\n = \\\n'),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          ' a'),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          '\na'),
    ('_Assign_targets',    px.parse__Assign_targets,    SyntaxError,              '\n\na'),
    ('_Assign_targets',    px.parse__Assign_targets,    SyntaxError,              'a\n='),
    ('_Assign_targets',    px.parse__Assign_targets,    SyntaxError,              'a =  # tail'),
    ('_Assign_targets',    px.parse__Assign_targets,    SyntaxError,              '# head\na ='),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          'a,'),
    ('_Assign_targets',    px.parse__Assign_targets,    _Assign_targets,          'a, ='),
    ('_Assign_targets',    px.parse__Assign_targets,    SyntaxError,              'f()'),
    ('_Assign_targets',    px.parse__Assign_targets,    SyntaxError,              'pass'),
    ('_Assign_targets',    px.parse__Assign_targets,    SyntaxError,              'a; b'),

    ('_decorator_list',    px.parse__decorator_list,    _decorator_list,          '#'),
    ('_decorator_list',    px.parse__decorator_list,    _decorator_list,          ''),
    ('_decorator_list',    px.parse__decorator_list,    _decorator_list,          '@a'),
    ('_decorator_list',    px.parse__decorator_list,    _decorator_list,          '@a\n@b'),
    ('_decorator_list',    px.parse__decorator_list,    SyntaxError,              'pass'),
    ('_decorator_list',    px.parse__decorator_list,    SyntaxError,              'f()'),

    ('expr',               px.parse_expr,               Name,                     'j'),
    ('expr',               px.parse_expr,               Starred,                  '*s'),
    ('expr',               px.parse_expr,               Starred,                  '*\ns'),
    ('expr',               px.parse_expr,               Tuple,                    '*\ns,'),
    ('expr',               px.parse_expr,               SyntaxError,              '*not a'),
    ('expr',               px.parse_expr,               Tuple,                    '1\n,\n2\n,'),
    ('expr',               px.parse_expr,               SyntaxError,              '*not a'),
    ('expr',               px.parse_expr,               SyntaxError,              'a:b'),
    ('expr',               px.parse_expr,               SyntaxError,              'a:b:c'),
    ('expr',               px.parse_expr,               SyntaxError,              'i for i in j'),
    ('expr',               px.parse_expr,               SyntaxError,              '* *a'),
    ('expr',               px.parse_expr,               SyntaxError,              'pass'),
    ('expr',               px.parse_expr,               SyntaxError,              '#'),
    ('expr',               px.parse_expr,               SyntaxError,              ''),

    ('expr_all',           px.parse_expr_all,           Name,                     'j'),
    ('expr_all',           px.parse_expr_all,           Starred,                  '*s'),
    ('expr_all',           px.parse_expr_all,           Starred,                  '*\ns'),
    ('expr_all',           px.parse_expr_all,           Tuple,                    '*\ns,'),
    ('expr_all',           px.parse_expr_all,           Tuple,                    '1\n,\n2\n,'),
    ('expr_all',           px.parse_expr_all,           Slice,                    'a:b'),
    ('expr_all',           px.parse_expr_all,           Slice,                    'a:b:c'),
    ('expr_all',           px.parse_expr_all,           Tuple,                    'j, k'),
    ('expr_all',           px.parse_expr_all,           Tuple,                    'a:b:c, x:y:z'),
    ('expr_all',           px.parse_expr_all,           SyntaxError,              '* *a'),
    ('expr_all',           px.parse_expr_all,           SyntaxError,              'pass'),
    ('expr_all',           px.parse_expr_all,           SyntaxError,              '#'),
    ('expr_all',           px.parse_expr_all,           SyntaxError,              ''),

    ('expr_arglike',       px.parse_expr_arglike,       Name,                     'j'),
    ('expr_arglike',       px.parse_expr_arglike,       Starred,                  '*s'),
    ('expr_arglike',       px.parse_expr_arglike,       Tuple,                    '*s,'),
    ('expr_arglike',       px.parse_expr_arglike,       Starred,                  '*not a'),
    ('expr_arglike',       px.parse_expr_arglike,       SyntaxError,              '*not a,'),
    ('expr_arglike',       px.parse_expr_arglike,       Tuple,                    'j, k'),
    ('expr_arglike',       px.parse_expr_arglike,       ParseError,               'i=1'),
    ('expr_arglike',       px.parse_expr_arglike,       SyntaxError,              'a:b'),
    ('expr_arglike',       px.parse_expr_arglike,       SyntaxError,              'a:b:c'),
    ('expr_arglike',       px.parse_expr_arglike,       SyntaxError,              '* *a'),
    ('expr_arglike',       px.parse_expr_arglike,       SyntaxError,              'pass'),
    ('expr_arglike',       px.parse_expr_arglike,       SyntaxError,              '#'),
    ('expr_arglike',       px.parse_expr_arglike,       SyntaxError,              ''),

    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    ''),
    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    '#'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    'j'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    '*s'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    '*s,'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    '*not a'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    '*not a,'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    '*not a, *b or c'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     Tuple,                    'j, k'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     ParseError,               'i=1'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     SyntaxError,              'a:b'),
    ('_expr_arglikes',     px.parse__expr_arglikes,     SyntaxError,              'a:b:c'),

    ('expr_slice',         px.parse_expr_slice,         Name,                     'j'),
    ('expr_slice',         px.parse_expr_slice,         Slice,                    'a:b'),
    ('expr_slice',         px.parse_expr_slice,         Tuple,                    'j, k'),
    ('expr_slice',         px.parse_expr_slice,         Tuple,                    'a:b:c, x:y:z'),
    ('expr_slice',         px.parse_expr_slice,         SyntaxError,              ''),
    ('expr_slice',         px.parse_expr_slice,         SyntaxError,              'i for i in j'),
    ('expr_slice',         px.parse_expr_slice,         SyntaxError,              '* *a'),
    ('expr_slice',         px.parse_expr_slice,         SyntaxError,              'pass'),
    ('expr_slice',         px.parse_expr_slice,         SyntaxError,              '#'),
    ('expr_slice',         px.parse_expr_slice,         SyntaxError,              ''),

    ('Tuple_elt',          px.parse_Tuple_elt,          Name,                     'j'),
    ('Tuple_elt',          px.parse_Tuple_elt,          Starred,                  '*s'),
    ('Tuple_elt',          px.parse_Tuple_elt,          Slice,                    'a:b'),
    ('Tuple_elt',          px.parse_Tuple_elt,          Tuple,                    'j, k'),
    ('Tuple_elt',          px.parse_Tuple_elt,          SyntaxError,              'a:b:c, x:y:z'),
    ('Tuple_elt',          px.parse_Tuple_elt,          SyntaxError,              '* *a'),
    ('Tuple_elt',          px.parse_Tuple_elt,          SyntaxError,              'pass'),
    ('Tuple_elt',          px.parse_Tuple_elt,          SyntaxError,              '#'),
    ('Tuple_elt',          px.parse_Tuple_elt,          SyntaxError,              ''),

    ('Tuple',              px.parse_Tuple,              ParseError,               '1'),
    ('Tuple',              px.parse_Tuple,              ParseError,               '*st'),
    ('Tuple',              px.parse_Tuple,              SyntaxError,              '~'),
    ('Tuple',              px.parse_Tuple,              SyntaxError,              '* *a'),
    ('Tuple',              px.parse_Tuple,              SyntaxError,              'pass'),
    ('Tuple',              px.parse_Tuple,              SyntaxError,              '#'),
    ('Tuple',              px.parse_Tuple,              SyntaxError,              ''),

    ('_arglike' ,          px.parse__arglike,           ParseError,               ''),
    ('_arglike' ,          px.parse__arglike,           ParseError,               '#'),
    ('_arglike' ,          px.parse__arglike,           Name,                     'j'),
    ('_arglike' ,          px.parse__arglike,           Starred,                  '*s'),
    ('_arglike' ,          px.parse__arglike,           Starred,                  '*s,'),
    ('_arglike' ,          px.parse__arglike,           Starred,                  '*not a'),
    ('_arglike' ,          px.parse__arglike,           Starred,                  '*not a,'),
    ('_arglike' ,          px.parse__arglike,           ParseError,               '*not a, *b or c'),
    ('_arglike' ,          px.parse__arglike,           ParseError,               'j, k'),
    ('_arglike' ,          px.parse__arglike,           keyword,                  'i=1'),
    ('_arglike' ,          px.parse__arglike,           keyword,                  '**k'),
    ('_arglike' ,          px.parse__arglike,           ParseError,               'a, b=c'),
    ('_arglike' ,          px.parse__arglike,           ParseError,               'a, *not b, c=d, *e, f=g, **h'),
    ('_arglike' ,          px.parse__arglike,           ParseError,               '*a, **b'),
    ('_arglike' ,          px.parse__arglike,           SyntaxError,              'a=b, c'),
    ('_arglike' ,          px.parse__arglike,           SyntaxError,              '**a, *b'),
    ('_arglike' ,          px.parse__arglike,           SyntaxError,              'a:b'),
    ('_arglike' ,          px.parse__arglike,           SyntaxError,              'a:b:c'),

    ('_arglikes',          px.parse__arglikes,          _arglikes,                ''),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                '#'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                'j'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                '*s'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                '*s,'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                '*not a'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                '*not a,'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                '*not a, *b or c'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                'j, k'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                'i=1'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                '**k'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                'a, b=c'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                'a, *not b, c=d, *e, f=g, **h'),
    ('_arglikes',          px.parse__arglikes,          _arglikes,                '*a, **b'),
    ('_arglikes',          px.parse__arglikes,          SyntaxError,              'a=b, c'),
    ('_arglikes',          px.parse__arglikes,          SyntaxError,              '**a, *b'),
    ('_arglikes',          px.parse__arglikes,          SyntaxError,              'a:b'),
    ('_arglikes',          px.parse__arglikes,          SyntaxError,              'a:b:c'),

    ('boolop',             px.parse_boolop,             And,                      'and'),
    ('boolop',             px.parse_boolop,             SyntaxError,              'and 1'),
    ('boolop',             px.parse_boolop,             SyntaxError,              '*'),
    ('boolop',             px.parse_boolop,             SyntaxError,              ''),
    ('operator',           px.parse_operator,           Mult,                     '*'),
    ('operator',           px.parse_operator,           SyntaxError,              '* 1'),
    ('operator',           px.parse_operator,           SyntaxError,              '*='),
    ('operator',           px.parse_operator,           SyntaxError,              'and'),
    ('operator',           px.parse_operator,           SyntaxError,              ''),
    ('unaryop',            px.parse_unaryop,            UAdd,                     '+'),
    ('unaryop',            px.parse_unaryop,            SyntaxError,              '+ 1'),
    ('unaryop',            px.parse_unaryop,            SyntaxError,              'and'),
    ('unaryop',            px.parse_unaryop,            SyntaxError,              ''),
    ('cmpop',              px.parse_cmpop,              GtE,                      '>='),
    ('cmpop',              px.parse_cmpop,              IsNot,                    'is\nnot'),
    ('cmpop',              px.parse_cmpop,              SyntaxError,              '+='),
    ('cmpop',              px.parse_cmpop,              SyntaxError,              '>= a >='),
    ('cmpop',              px.parse_cmpop,              SyntaxError,              'and'),
    ('cmpop',              px.parse_cmpop,              SyntaxError,              ''),

    ('comprehension',      px.parse_comprehension,      comprehension,            'for u in v'),
    ('comprehension',      px.parse_comprehension,      comprehension,            'async for u in v'),
    ('comprehension',      px.parse_comprehension,      comprehension,            'for u in v if w'),
    ('comprehension',      px.parse_comprehension,      ParseError,               'for u in v async for s in t'),
    ('comprehension',      px.parse_comprehension,      SyntaxError,              '#'),
    ('comprehension',      px.parse_comprehension,      SyntaxError,              ']+['),

    ('_comprehensions',    px.parse__comprehensions,    _comprehensions,          ''),
    ('_comprehensions',    px.parse__comprehensions,    _comprehensions,          '#'),
    ('_comprehensions',    px.parse__comprehensions,    _comprehensions,          'for u in v'),
    ('_comprehensions',    px.parse__comprehensions,    _comprehensions,          'async for u in v'),
    ('_comprehensions',    px.parse__comprehensions,    _comprehensions,          'for u in v if w async for s in t'),
    ('_comprehensions',    px.parse__comprehensions,    ParseError,               'if i'),
    ('_comprehensions',    px.parse__comprehensions,    SyntaxError,              ']+['),

    ('_comprehension_ifs', px.parse__comprehension_ifs, _comprehension_ifs,       ''),
    ('_comprehension_ifs', px.parse__comprehension_ifs, _comprehension_ifs,       '#'),
    ('_comprehension_ifs', px.parse__comprehension_ifs, _comprehension_ifs,       'if u'),
    ('_comprehension_ifs', px.parse__comprehension_ifs, _comprehension_ifs,       'if u if v'),
    ('_comprehension_ifs', px.parse__comprehension_ifs, SyntaxError,              'if 1 else 2'),
    ('_comprehension_ifs', px.parse__comprehension_ifs, ParseError,               '(a)'),
    ('_comprehension_ifs', px.parse__comprehension_ifs, ParseError,               '.b'),
    ('_comprehension_ifs', px.parse__comprehension_ifs, ParseError,               '+b'),
    ('_comprehension_ifs', px.parse__comprehension_ifs, SyntaxError,              ']+['),
    ('_comprehension_ifs', px.parse__comprehension_ifs, ParseError,               'for _ in _'),

    ('arguments',          px.parse_arguments,          arguments,                ''),
    ('arguments',          px.parse_arguments,          arguments,                '#'),
    ('arguments',          px.parse_arguments,          arguments,                'a: list[str], /, b: int = 1, *c, d=100, **e'),

    ('arguments_lambda',   px.parse_arguments_lambda,   arguments,                ''),
    ('arguments_lambda',   px.parse_arguments_lambda,   arguments,                '#'),
    ('arguments_lambda',   px.parse_arguments_lambda,   arguments,                'a, /, b, *c, d=100, **e'),
    ('arguments_lambda',   px.parse_arguments_lambda,   arguments,                'a,\n/,\nb,\n*c,\nd=100,\n**e'),
    ('arguments_lambda',   px.parse_arguments_lambda,   SyntaxError,              'a: list[str], /, b: int = 1, *c, d=100, **e'),

    ('arg',                px.parse_arg,                arg,                      'a: b'),
    ('arg',                px.parse_arg,                ParseError,               'a: b = c'),
    ('arg',                px.parse_arg,                ParseError,               'a, b'),
    ('arg',                px.parse_arg,                ParseError,               'a, /'),
    ('arg',                px.parse_arg,                ParseError,               ', a'),
    ('arg',                px.parse_arg,                ParseError,               '*, a'),
    ('arg',                px.parse_arg,                ParseError,               '*a'),
    ('arg',                px.parse_arg,                ParseError,               '**a'),
    ('arg',                px.parse_arg,                SyntaxError,              ','),
    ('arg',                px.parse_arg,                SyntaxError,              ')'),

    ('keyword',            px.parse_keyword,            keyword,                  'a=1'),
    ('keyword',            px.parse_keyword,            keyword,                  '**a'),
    ('keyword',            px.parse_keyword,            ParseError,               '1'),
    ('keyword',            px.parse_keyword,            ParseError,               'a'),
    ('keyword',            px.parse_keyword,            ParseError,               'a=1, b=2'),

    ('alias',              px.parse_alias,              SyntaxError,              ''),
    ('alias',              px.parse_alias,              alias,                    'a'),
    ('alias',              px.parse_alias,              alias,                    'a.b'),
    ('alias',              px.parse_alias,              alias,                    '*'),
    ('alias',              px.parse_alias,              ParseError,               'a, b'),
    ('alias',              px.parse_alias,              alias,                    'a as c'),
    ('alias',              px.parse_alias,              alias,                    'a.b as c'),
    ('alias',              px.parse_alias,              SyntaxError,              '* as c'),
    ('alias',              px.parse_alias,              ParseError,               'a as x, b as y'),
    ('alias',              px.parse_alias,              ParseError,               'a as x, a.b as y'),

    ('_aliases',           px.parse__aliases,           _aliases,                 ''),
    ('_aliases',           px.parse__aliases,           _aliases,                 'a'),
    ('_aliases',           px.parse__aliases,           _aliases,                 'a.b'),
    ('_aliases',           px.parse__aliases,           _aliases,                 '*'),
    ('_aliases',           px.parse__aliases,           _aliases,                 'a, b'),
    ('_aliases',           px.parse__aliases,           _aliases,                 'a as c'),
    ('_aliases',           px.parse__aliases,           _aliases,                 'a.b as c'),
    ('_aliases',           px.parse__aliases,           SyntaxError,              '* as c'),
    ('_aliases',           px.parse__aliases,           _aliases,                 'a as x, b as y'),
    ('_aliases',           px.parse__aliases,           _aliases,                 'a as x, a.b as y'),

    ('Import_name',        px.parse_Import_name,        SyntaxError,              ''),
    ('Import_name',        px.parse_Import_name,        alias,                    'a'),
    ('Import_name',        px.parse_Import_name,        alias,                    'a.b'),
    ('Import_name',        px.parse_Import_name,        SyntaxError,              '*'),
    ('Import_name',        px.parse_Import_name,        ParseError,               'a, b'),
    ('Import_name',        px.parse_Import_name,        alias,                    'a as c'),
    ('Import_name',        px.parse_Import_name,        alias,                    'a.b as c'),
    ('Import_name',        px.parse_Import_name,        SyntaxError,              '* as c'),
    ('Import_name',        px.parse_Import_name,        ParseError,               'a as x, b as y'),
    ('Import_name',        px.parse_Import_name,        ParseError,               'a as x, a.b as y'),
    ('Import_name',        px.parse_Import_name,        SyntaxError,              '(a)'),
    ('Import_name',        px.parse_Import_name,        SyntaxError,              ')'),
    ('Import_name',        px.parse_Import_name,        SyntaxError,              ','),

    ('_Import_names',      px.parse__Import_names,      _aliases,                 ''),
    ('_Import_names',      px.parse__Import_names,      _aliases,                 'a'),
    ('_Import_names',      px.parse__Import_names,      _aliases,                 'a.b'),
    ('_Import_names',      px.parse__Import_names,      SyntaxError,              '*'),
    ('_Import_names',      px.parse__Import_names,      _aliases,                 'a, b'),
    ('_Import_names',      px.parse__Import_names,      _aliases,                 'a as c'),
    ('_Import_names',      px.parse__Import_names,      _aliases,                 'a.b as c'),
    ('_Import_names',      px.parse__Import_names,      SyntaxError,              '* as c'),
    ('_Import_names',      px.parse__Import_names,      _aliases,                 'a as x, b as y'),
    ('_Import_names',      px.parse__Import_names,      _aliases,                 'a as x, a.b as y'),
    ('_Import_names',      px.parse__Import_names,      _aliases,                 'a,\nb'),
    ('_Import_names',      px.parse__Import_names,      SyntaxError,              '(a, b)'),
    ('_Import_names',      px.parse__Import_names,      SyntaxError,              ')'),
    ('_Import_names',      px.parse__Import_names,      SyntaxError,              ','),

    ('ImportFrom_name',    px.parse_ImportFrom_name,    SyntaxError,              ''),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    alias,                    'a'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    SyntaxError,              'a.b'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    alias,                    '*'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    ParseError,               'a, b'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    alias,                    'a as c'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    SyntaxError,              'a.b as c'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    SyntaxError,              '* as c'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    ParseError,               'a as x, b as y'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    SyntaxError,              'a as x, a.b as y'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    SyntaxError,              '(a)'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    SyntaxError,              ')'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    SyntaxError,              ','),

    ('_ImportFrom_names',  px.parse__ImportFrom_names,  _aliases,                 ''),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  _aliases,                 'a'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  SyntaxError,              'a.b'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  _aliases,                 '*'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  _aliases,                 'a, b'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  _aliases,                 'a as c'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  SyntaxError,              'a.b as c'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  SyntaxError,              '* as c'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  _aliases,                 'a as x, b as y'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  SyntaxError,              'a as x, a.b as y'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  _aliases,                 'a,\nb'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  SyntaxError,              '(a, b)'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  SyntaxError,              ')'),
    ('_ImportFrom_names',  px.parse__ImportFrom_names,  SyntaxError,              ','),

    ('withitem',           px.parse_withitem,           SyntaxError,              ''),
    ('withitem',           px.parse_withitem,           withitem,                 'a'),
    ('withitem',           px.parse_withitem,           SyntaxError,              '*a'),
    ('withitem',           px.parse_withitem,           withitem,                 'a, b'),
    ('withitem',           px.parse_withitem,           withitem,                 '(a, b)'),
    ('withitem',           px.parse_withitem,           withitem,                 '()'),
    ('withitem',           px.parse_withitem,           withitem,                 'a as b'),
    ('withitem',           px.parse_withitem,           withitem,                 '(a) as (b)'),
    ('withitem',           px.parse_withitem,           ParseError,               'a, b as c'),
    ('withitem',           px.parse_withitem,           ParseError,               'a as b, x as y'),
    ('withitem',           px.parse_withitem,           withitem,                 '(a)'),
    ('withitem',           px.parse_withitem,           SyntaxError,              '(a as b)'),
    ('withitem',           px.parse_withitem,           SyntaxError,              '(a as b, x as y)'),
    ('withitem',           px.parse_withitem,           SyntaxError,              ')'),
    ('withitem',           px.parse_withitem,           SyntaxError,              ','),

    ('_withitems',         px.parse__withitems,         _withitems,               ''),
    ('_withitems',         px.parse__withitems,         _withitems,               'a'),
    ('_withitems',         px.parse__withitems,         SyntaxError,              '*a'),
    ('_withitems',         px.parse__withitems,         _withitems,               'a, b'),
    ('_withitems',         px.parse__withitems,         _withitems,               '(a, b)'),
    ('_withitems',         px.parse__withitems,         _withitems,               '()'),
    ('_withitems',         px.parse__withitems,         _withitems,               'a as b'),
    ('_withitems',         px.parse__withitems,         _withitems,               '(a) as (b)'),
    ('_withitems',         px.parse__withitems,         _withitems,               'a, b as c'),
    ('_withitems',         px.parse__withitems,         _withitems,               'a as b, x as y'),
    ('_withitems',         px.parse__withitems,         _withitems,               '(a)'),
    ('_withitems',         px.parse__withitems,         SyntaxError,              '(a as b)'),
    ('_withitems',         px.parse__withitems,         SyntaxError,              '(a as b, x as y)'),
    ('_withitems',         px.parse__withitems,         SyntaxError,              'i for i in j'),
    ('_withitems',         px.parse__withitems,         SyntaxError,              ')'),
    ('_withitems',         px.parse__withitems,         SyntaxError,              ','),

    ('pattern',            px.parse_pattern,            MatchValue,               '42'),
    ('pattern',            px.parse_pattern,            MatchSingleton,           'None'),
    ('pattern',            px.parse_pattern,            MatchSequence,            '[a, *_]'),
    ('pattern',            px.parse_pattern,            MatchSequence,            '[]'),
    ('pattern',            px.parse_pattern,            MatchSequence,            'a,'),
    ('pattern',            px.parse_pattern,            MatchSequence,            'a\n,'),
    ('pattern',            px.parse_pattern,            MatchMapping,             '{"key": _}'),
    ('pattern',            px.parse_pattern,            MatchMapping,             '{}'),
    ('pattern',            px.parse_pattern,            MatchClass,               'SomeClass()'),
    ('pattern',            px.parse_pattern,            MatchClass,               'SomeClass(attr=val)'),
    ('pattern',            px.parse_pattern,            MatchAs,                  'as_var'),
    ('pattern',            px.parse_pattern,            MatchAs,                  '1 as as_var'),
    ('pattern',            px.parse_pattern,            MatchOr,                  '1 | 2 | 3'),
    ('pattern',            px.parse_pattern,            MatchAs,                  '_'),
    ('pattern',            px.parse_pattern,            MatchStar,                '*a'),
    ('pattern',            px.parse_pattern,            SyntaxError,              ''),
    ('pattern',            px.parse_pattern,            SyntaxError,              ')'),
    ('pattern',            px.parse_pattern,            SyntaxError,              ','),
    ('pattern',            px.parse_pattern,            SyntaxError,              'i: pass\n case 2'),

    ('expr',               px.parse_expr,               BoolOp,                   '\na\nor\nb\n'),
    ('expr',               px.parse_expr,               NamedExpr,                '\na\n:=\nb\n'),
    ('expr',               px.parse_expr,               BinOp,                    '\na\n|\nb\n'),
    ('expr',               px.parse_expr,               BinOp,                    '\na\n**\nb\n'),
    ('expr',               px.parse_expr,               UnaryOp,                  '\nnot\na\n'),
    ('expr',               px.parse_expr,               UnaryOp,                  '\n~\na\n'),
    ('expr',               px.parse_expr,               Lambda,                   '\nlambda\n:\nNone\n'),
    ('expr',               px.parse_expr,               IfExp,                    '\na\nif\nb\nelse\nc\n'),
    ('expr',               px.parse_expr,               Dict,                     '\n{\na\n:\nb\n}\n'),
    ('expr',               px.parse_expr,               Set,                      '\n{\na\n,\nb\n}\n'),
    ('expr',               px.parse_expr,               ListComp,                 '\n[\na\nfor\na\nin\nb\n]\n'),
    ('expr',               px.parse_expr,               SetComp,                  '\n{\na\nfor\na\nin\nb\n}\n'),
    ('expr',               px.parse_expr,               DictComp,                 '\n{\na\n:\nc\nfor\na\n,\nc\nin\nb\n}\n'),
    ('expr',               px.parse_expr,               GeneratorExp,             '\n(\na\nfor\na\nin\nb\n)\n'),
    ('expr',               px.parse_expr,               Await,                    '\nawait\na\n'),
    ('expr',               px.parse_expr,               Yield,                    '\nyield\n'),
    ('expr',               px.parse_expr,               Yield,                    '\nyield\na\n'),
    ('expr',               px.parse_expr,               YieldFrom,                '\nyield\nfrom\na\n'),
    ('expr',               px.parse_expr,               Compare,                  '\na\n<\nb\n'),
    ('expr',               px.parse_expr,               Call,                     '\nf\n(\na\n)\n'),
    ('expr',               px.parse_expr,               JoinedStr,                "\nf'{a}'\n"),
    ('expr',               px.parse_expr,               JoinedStr,                '\nf"{a}"\n'),
    ('expr',               px.parse_expr,               JoinedStr,                "\nf'''\n{\na\n}\n'''\n"),
    ('expr',               px.parse_expr,               JoinedStr,                '\nf"""\n{\na\n}\n"""\n'),
    ('expr',               px.parse_expr,               Constant,                 '\n...\n'),
    ('expr',               px.parse_expr,               Constant,                 '\nNone\n'),
    ('expr',               px.parse_expr,               Constant,                 '\nTrue\n'),
    ('expr',               px.parse_expr,               Constant,                 '\nFalse\n'),
    ('expr',               px.parse_expr,               Constant,                 '\n1\n'),
    ('expr',               px.parse_expr,               Constant,                 '\n1.0\n'),
    ('expr',               px.parse_expr,               Constant,                 '\n1j\n'),
    ('expr',               px.parse_expr,               Constant,                 "\n'a'\n"),
    ('expr',               px.parse_expr,               Constant,                 '\n"a"\n'),
    ('expr',               px.parse_expr,               Constant,                 "\n'''\na\n'''\n"),
    ('expr',               px.parse_expr,               Constant,                 '\n"""\na\n"""\n'),
    ('expr',               px.parse_expr,               Constant,                 "\nb'a'\n"),
    ('expr',               px.parse_expr,               Constant,                 '\nb"a"\n'),
    ('expr',               px.parse_expr,               Constant,                 "\nb'''\na\n'''\n"),
    ('expr',               px.parse_expr,               Constant,                 '\nb"""\na\n"""\n'),
    ('expr',               px.parse_expr,               Attribute,                '\na\n.\nb\n'),
    ('expr',               px.parse_expr,               Subscript,                '\na\n[\nb\n]\n'),
    ('expr',               px.parse_expr,               Starred,                  '\n*\na\n'),
    ('expr',               px.parse_expr,               List,                     '\n[\na\n,\nb\n]\n'),
    ('expr',               px.parse_expr,               Tuple,                    '\n(\na\n,\nb\n)\n'),
    ('expr',               px.parse_expr,               Tuple,                    '\na\n,\n'),
    ('expr',               px.parse_expr,               Tuple,                    '\na\n,\nb\n'),

    ('pattern',            px.parse_pattern,            MatchValue,               '\n42\n'),
    ('pattern',            px.parse_pattern,            MatchSingleton,           '\nNone\n'),
    ('pattern',            px.parse_pattern,            MatchSequence,            '\n[\na\n,\n*\nb\n]\n'),
    ('pattern',            px.parse_pattern,            MatchSequence,            '\n\na\n,\n*\nb\n\n'),
    ('pattern',            px.parse_pattern,            MatchMapping,             '\n{\n"key"\n:\n_\n}\n'),
    ('pattern',            px.parse_pattern,            MatchClass,               '\nSomeClass\n(\nattr\n=\nval\n)\n'),
    ('pattern',            px.parse_pattern,            MatchAs,                  '\nas_var\n'),
    ('pattern',            px.parse_pattern,            MatchAs,                  '\n1\nas\nas_var\n'),
    ('pattern',            px.parse_pattern,            MatchOr,                  '\n1\n|\n2\n'),

    ('expr',               px.parse_expr,               BoolOp,                   '\n a\n or\n b\n         '),
    ('expr',               px.parse_expr,               NamedExpr,                '\n a\n :=\n b\n         '),
    ('expr',               px.parse_expr,               BinOp,                    '\n a\n |\n b\n         '),
    ('expr',               px.parse_expr,               BinOp,                    '\n a\n **\n b\n         '),
    ('expr',               px.parse_expr,               UnaryOp,                  '\n not\n a\n         '),
    ('expr',               px.parse_expr,               UnaryOp,                  '\n ~\n a\n         '),
    ('expr',               px.parse_expr,               Lambda,                   '\n lambda\n :\n None\n         '),
    ('expr',               px.parse_expr,               IfExp,                    '\n a\n if\n b\n else\n c\n         '),
    ('expr',               px.parse_expr,               Dict,                     '\n {\n a\n :\n b\n }\n         '),
    ('expr',               px.parse_expr,               Set,                      '\n {\n a\n ,\n b\n }\n         '),
    ('expr',               px.parse_expr,               ListComp,                 '\n [\n a\n for\n a\n in\n b\n ]\n         '),
    ('expr',               px.parse_expr,               SetComp,                  '\n {\n a\n for\n a\n in\n b\n }\n         '),
    ('expr',               px.parse_expr,               DictComp,                 '\n {\n a\n :\n c\n for\n a\n ,\n c\n in\n b\n }\n         '),
    ('expr',               px.parse_expr,               GeneratorExp,             '\n (\n a\n for\n a\n in\n b\n )\n         '),
    ('expr',               px.parse_expr,               Await,                    '\n await\n a\n         '),
    ('expr',               px.parse_expr,               Yield,                    '\n yield\n         '),
    ('expr',               px.parse_expr,               Yield,                    '\n yield\n a\n         '),
    ('expr',               px.parse_expr,               YieldFrom,                '\n yield\n from\n a\n         '),
    ('expr',               px.parse_expr,               Compare,                  '\n a\n <\n b\n         '),
    ('expr',               px.parse_expr,               Call,                     '\n f\n (\n a\n )\n         '),
    ('expr',               px.parse_expr,               JoinedStr,                "\n f'{a}'\n "),
    ('expr',               px.parse_expr,               JoinedStr,                '\n f"{a}"\n         '),
    ('expr',               px.parse_expr,               JoinedStr,                "\n f'''\n {\n a\n }\n         '''\n "),
    ('expr',               px.parse_expr,               JoinedStr,                '\n f"""\n {\n a\n }\n """\n         '),
    ('expr',               px.parse_expr,               Constant,                 '\n ...\n         '),
    ('expr',               px.parse_expr,               Constant,                 '\n None\n         '),
    ('expr',               px.parse_expr,               Constant,                 '\n True\n         '),
    ('expr',               px.parse_expr,               Constant,                 '\n False\n         '),
    ('expr',               px.parse_expr,               Constant,                 '\n 1\n         '),
    ('expr',               px.parse_expr,               Constant,                 '\n 1.0\n         '),
    ('expr',               px.parse_expr,               Constant,                 '\n 1j\n         '),
    ('expr',               px.parse_expr,               Constant,                 "\n         'a'\n "),
    ('expr',               px.parse_expr,               Constant,                 '\n "a"\n         '),
    ('expr',               px.parse_expr,               Constant,                 "\n         '''\n a\n         '''\n "),
    ('expr',               px.parse_expr,               Constant,                 '\n """\n a\n """\n         '),
    ('expr',               px.parse_expr,               Constant,                 "\n b'a'\n "),
    ('expr',               px.parse_expr,               Constant,                 '\n b"a"\n         '),
    ('expr',               px.parse_expr,               Constant,                 "\n b'''\n a\n         '''\n "),
    ('expr',               px.parse_expr,               Constant,                 '\n b"""\n a\n """\n         '),
    ('expr',               px.parse_expr,               Attribute,                '\n a\n .\n b\n         '),
    ('expr',               px.parse_expr,               Subscript,                '\n a\n [\n b\n ]\n         '),
    ('expr',               px.parse_expr,               Starred,                  '\n *\n a\n         '),
    ('expr',               px.parse_expr,               List,                     '\n [\n a\n ,\n b\n ]\n         '),
    ('expr',               px.parse_expr,               Tuple,                    '\n (\n a\n ,\n b\n )\n         '),
    ('expr',               px.parse_expr,               Tuple,                    '\n a\n ,\n         '),
    ('expr',               px.parse_expr,               Tuple,                    '\n a\n ,\n b\n         '),

    ('pattern',            px.parse_pattern,            MatchValue,               '\n 42\n         '),
    ('pattern',            px.parse_pattern,            MatchSingleton,           '\n None\n         '),
    ('pattern',            px.parse_pattern,            MatchSequence,            '\n [\n a\n ,\n *\n b\n ]\n         '),
    ('pattern',            px.parse_pattern,            MatchSequence,            '\n \n a\n ,\n *\n b\n \n         '),
    ('pattern',            px.parse_pattern,            MatchMapping,             '\n {\n "key"\n :\n _\n }\n         '),
    ('pattern',            px.parse_pattern,            MatchClass,               '\n SomeClass\n (\n attr\n =\n val\n )\n         '),
    ('pattern',            px.parse_pattern,            MatchAs,                  '\n as_var\n         '),
    ('pattern',            px.parse_pattern,            MatchAs,                  '\n 1\n as\n as_var\n         '),
    ('pattern',            px.parse_pattern,            MatchOr,                  '\n 1\n |\n 2\n         '),

    (mod,                  px.parse_Module,             Module,                   'j'),
    (Module,               px.parse_Module,             Module,                   'j'),
    (Expression,           px.parse_Expression,         Expression,               'None'),
    (Interactive,          px.parse_Interactive,        Interactive,              'j'),

    (stmt,                 px.parse_stmt,               AnnAssign,                'i: int = 1'),
    (stmt,                 px.parse_stmt,               Expr,                     'j'),
    (stmt,                 px.parse_stmt,               ParseError,               'i: int = 1\nj'),
    (stmt,                 px.parse_stmt,               SyntaxError,              'except: pass'),
    (AnnAssign,            px.parse_stmt,               AnnAssign,                'i: int = 1'),
    (Expr,                 px.parse_stmt,               Expr,                     'j'),

    (ExceptHandler,        px.parse_ExceptHandler,      ExceptHandler,            'except: pass'),
    (ExceptHandler,        px.parse_ExceptHandler,      ParseError,               'except Exception: pass\nexcept: pass'),
    (ExceptHandler,        px.parse_ExceptHandler,      SyntaxError,              'i: int = 1'),

    (match_case,           px.parse_match_case,         match_case,               'case None: pass'),
    (match_case,           px.parse_match_case,         ParseError,               'case None: pass\ncase 1: pass'),
    (match_case,           px.parse_match_case,         SyntaxError,              'i: int = 1'),

    (expr,                 px.parse_expr,               Name,                     'j'),
    (expr,                 px.parse_expr,               Starred,                  '*s'),
    (expr,                 px.parse_expr,               Starred,                  '*\ns'),
    (expr,                 px.parse_expr,               Tuple,                    '*\ns,'),
    (expr,                 px.parse_expr,               Tuple,                    '1\n,\n2\n,'),
    (expr,                 px.parse_expr,               SyntaxError,              '*not a'),
    (expr,                 px.parse_expr,               SyntaxError,              'a:b'),
    (expr,                 px.parse_expr,               SyntaxError,              'a:b:c'),
    (Name,                 px.parse_expr,               Name,                     'j'),
    (Starred,              px.parse_expr,               Starred,                  '*s'),

    (Starred,              px.parse_expr_arglike,       Starred,                  '*not a'),

    (Slice,                px.parse_expr_slice,         Slice,                    'a:b'),

    (boolop,               px.parse_boolop,             And,                      'and'),
    (boolop,               px.parse_boolop,             SyntaxError,              '*'),
    (operator,             px.parse_operator,           Mult,                     '*'),
    (operator,             px.parse_operator,           SyntaxError,              '*='),
    (operator,             px.parse_operator,           SyntaxError,              'and'),
    (unaryop,              px.parse_unaryop,            UAdd,                     '+'),
    (unaryop,              px.parse_unaryop,            SyntaxError,              'and'),
    (cmpop,                px.parse_cmpop,              GtE,                      '>='),
    (cmpop,                px.parse_cmpop,              IsNot,                    'is\nnot'),
    (cmpop,                px.parse_cmpop,              SyntaxError,              '>= a >='),
    (cmpop,                px.parse_cmpop,              SyntaxError,              'and'),

    (comprehension,        px.parse_comprehension,      comprehension,            'for u in v'),
    (comprehension,        px.parse_comprehension,      comprehension,            'for u in v if w'),
    (comprehension,        px.parse_comprehension,      SyntaxError,              '()'),

    (arguments,            px.parse_arguments,          arguments,                ''),
    (arguments,            px.parse_arguments,          arguments,                'a: list[str], /, b: int = 1, *c, d=100, **e'),
    (arguments,            px.parse_arguments_lambda,   arguments,                'a, /, b, *c, d=100, **e'),

    (arg,                  px.parse_arg,                arg,                      'a: b'),
    (arg,                  px.parse_arg,                ParseError,               'a: b = c'),
    (arg,                  px.parse_arg,                ParseError,               'a, b'),
    (arg,                  px.parse_arg,                ParseError,               'a, /'),
    (arg,                  px.parse_arg,                ParseError,               '*, a'),
    (arg,                  px.parse_arg,                ParseError,               '*a'),
    (arg,                  px.parse_arg,                ParseError,               '**a'),

    (keyword,              px.parse_keyword,            keyword,                  'a=1'),
    (keyword,              px.parse_keyword,            keyword,                  '**a'),
    (keyword,              px.parse_keyword,            ParseError,               '1'),
    (keyword,              px.parse_keyword,            ParseError,               'a'),
    (keyword,              px.parse_keyword,            ParseError,               'a=1, b=2'),

    (alias,                px.parse_alias,              alias,                    'a'),
    (alias,                px.parse_alias,              alias,                    'a.b'),
    (alias,                px.parse_alias,              alias,                    '*'),
    (alias,                px.parse_alias,              ParseError,               'a, b'),
    (alias,                px.parse_alias,              alias,                    'a as c'),
    (alias,                px.parse_alias,              alias,                    'a.b as c'),
    (alias,                px.parse_alias,              SyntaxError,              '* as c'),

    (withitem,             px.parse_withitem,           withitem,                 'a'),
    (withitem,             px.parse_withitem,           withitem,                 'a, b'),
    (withitem,             px.parse_withitem,           withitem,                 '(a, b)'),
    (withitem,             px.parse_withitem,           withitem,                 'a as b'),
    (withitem,             px.parse_withitem,           ParseError,               'a as b, x as y'),
    (withitem,             px.parse_withitem,           withitem,                 '(a)'),
    (withitem,             px.parse_withitem,           SyntaxError,              '(a as b)'),
    (withitem,             px.parse_withitem,           SyntaxError,              '(a as b, x as y)'),

    (pattern,              px.parse_pattern,            MatchValue,               '42'),
    (pattern,              px.parse_pattern,            MatchSingleton,           'None'),
    (pattern,              px.parse_pattern,            MatchSequence,            '[a, *_]'),
    (pattern,              px.parse_pattern,            MatchSequence,            '[]'),
    (pattern,              px.parse_pattern,            MatchSequence,            'a,'),
    (pattern,              px.parse_pattern,            MatchSequence,            'a\n,'),
    (pattern,              px.parse_pattern,            MatchMapping,             '{"key": _}'),
    (pattern,              px.parse_pattern,            MatchMapping,             '{}'),
    (pattern,              px.parse_pattern,            MatchClass,               'SomeClass()'),
    (pattern,              px.parse_pattern,            MatchClass,               'SomeClass(attr=val)'),
    (pattern,              px.parse_pattern,            MatchAs,                  'as_var'),
    (pattern,              px.parse_pattern,            MatchAs,                  '1 as as_var'),
    (pattern,              px.parse_pattern,            MatchOr,                  '1 | 2 | 3'),
    (pattern,              px.parse_pattern,            MatchAs,                  '_'),
    (pattern,              px.parse_pattern,            MatchStar,                '*a'),
    (pattern,              px.parse_pattern,            SyntaxError,              ''),

    (MatchValue,           px.parse_pattern,            MatchValue,               '42'),
    (MatchSingleton,       px.parse_pattern,            MatchSingleton,           'None'),
    (MatchSequence,        px.parse_pattern,            MatchSequence,            '[a, *_]'),
    (MatchSequence,        px.parse_pattern,            MatchSequence,            '[]'),
    (MatchSequence,        px.parse_pattern,            MatchSequence,            'a,'),
    (MatchSequence,        px.parse_pattern,            MatchSequence,            'a\n,'),
    (MatchMapping,         px.parse_pattern,            MatchMapping,             '{"key": _}'),
    (MatchMapping,         px.parse_pattern,            MatchMapping,             '{}'),
    (MatchClass,           px.parse_pattern,            MatchClass,               'SomeClass()'),
    (MatchClass,           px.parse_pattern,            MatchClass,               'SomeClass(attr=val)'),
    (MatchAs,              px.parse_pattern,            MatchAs,                  'as_var'),
    (MatchAs,              px.parse_pattern,            MatchAs,                  '1 as as_var'),
    (MatchOr,              px.parse_pattern,            MatchOr,                  '1 | 2 | 3'),
    (MatchAs,              px.parse_pattern,            MatchAs,                  '_'),
    (MatchStar,            px.parse_pattern,            MatchStar,                '*a'),

    ('expr',               px.parse_expr,               Tuple,                    ' *a,  # tail'),
    ('expr_arglike',       px.parse_expr_arglike,       Starred,                  ' *not a  # tail'),
    ('expr_slice',         px.parse_expr_slice,         Slice,                    ' a:b:c  # tail'),
    ('expr_slice',         px.parse_expr_slice,         Yield,                    ' yield  # tail'),
    ('boolop',             px.parse_boolop,             And,                      ' and  # tail'),
    ('operator',           px.parse_operator,           RShift,                   ' >>  # tail'),
    ('unaryop',            px.parse_unaryop,            Invert,                   ' ~  # tail'),
    ('cmpop',              px.parse_cmpop,              GtE,                      ' >=  # tail'),
    ('comprehension',      px.parse_comprehension,      comprehension,            ' for i in j  # tail'),
    ('arguments',          px.parse_arguments,          arguments,                ' a: list[str], /, b: int = 1, *c, d=100, **e  # tail'),
    ('arguments_lambda',   px.parse_arguments_lambda,   arguments,                ' a, /, b, *c, d=100, **e  # tail'),
    ('arg',                px.parse_arg,                arg,                      ' a: b  # tail'),
    ('keyword',            px.parse_keyword,            keyword,                  ' a=1  # tail'),
    ('Import_name',        px.parse_Import_name,        alias,                    ' a.b  # tail'),
    ('ImportFrom_name',    px.parse_ImportFrom_name,    alias,                    ' *  # tail'),
    ('withitem',           px.parse_withitem,           withitem,                 ' a as b,  # tail'),
    ('pattern',            px.parse_pattern,            MatchOr,                  ' 1 | 2 | 3  # tail'),
    ('pattern',            px.parse_pattern,            MatchStar,                ' *a  # tail'),
  ]

PARSE_TESTS_10 = PARSE_TESTS.copy()

if PYGE11:
    PARSE_TESTS.extend(PARSE_TESTS_11 := [
        ('ExceptHandler',      px.parse_ExceptHandler,      ExceptHandler,          'except* Exception: pass'),

        ('expr_all',           px.parse_expr_all,           Starred,                '*not a'),
        ('expr_all',           px.parse_expr_all,           Tuple,                  '*not a,'),

        ('expr_slice',         px.parse_expr_slice,         Tuple,                  '*s'),
        ('expr_slice',         px.parse_expr_slice,         Tuple,                  '*not a'),
        ('expr_slice',         px.parse_expr_slice,         Tuple,                  'a:b:c, *st'),

        ('Tuple_elt',          px.parse_Tuple_elt,          Starred,                '*not a'),
        ('Tuple_elt',          px.parse_Tuple_elt,          SyntaxError,            '*not a, *b or c'),

        (ExceptHandler,        px.parse_ExceptHandler,      ExceptHandler,          'except* Exception: pass'),

        ('arg',                px.parse_arg,                arg,                    ' a: *()'),
        ('arg',                px.parse_arg,                arg,                    ' a: *b  # tail'),
        ('arg',                px.parse_arg,                SyntaxError,            'a: *(,)'),
        ('arg',                px.parse_arg,                SyntaxError,            'a: *+'),
    ])

if PYGE12:
    PARSE_TESTS.extend(PARSE_TESTS_12 := [
        ('all',                px.parse__type_params,       _type_params,           '*U, **V, **Z'),
        ('all',                px.parse__type_params,       _type_params,           'T: int, *U, **V, **Z'),

        ('type_param',         px.parse_type_param,         TypeVar,                'a: int'),
        ('type_param',         px.parse_type_param,         ParamSpec,              '**a'),
        ('type_param',         px.parse_type_param,         TypeVarTuple,           '*a'),
        ('type_param',         px.parse_type_param,         ParseError,             'a: int,'),
        ('type_param',         px.parse_type_param,         ParseError,             'T, U'),

        ('_type_params',       px.parse__type_params,       _type_params,           ''),
        ('_type_params',       px.parse__type_params,       _type_params,           'a: int'),
        ('_type_params',       px.parse__type_params,       _type_params,           'a: int,'),
        ('_type_params',       px.parse__type_params,       _type_params,           'a: int, *b, **c'),

        (type_param,           px.parse_type_param,         TypeVar,                'a: int'),
        (TypeVar,              px.parse_type_param,         TypeVar,                'a: int'),
        (type_param,           px.parse_type_param,         ParamSpec,              '**a'),
        (ParamSpec,            px.parse_type_param,         ParamSpec,              '**a'),
        (type_param,           px.parse_type_param,         TypeVarTuple,           '*a'),
        (TypeVarTuple,         px.parse_type_param,         TypeVarTuple,           '*a'),

        ('type_param',         px.parse_type_param,         TypeVar,                ' a: int  # tail'),
        ('_type_params',       px.parse__type_params,       _type_params,           ' a: int, *b, **c  # tail'),
    ])

if PYGE13:
    PARSE_TESTS.extend(PARSE_TESTS_13 := [
        ('all',                px.parse_type_param,         ParamSpec,              '**a = {T: int, U: str}'),
        ('all',                px.parse_type_param,         TypeVarTuple,           '*a = (int, str)'),
        ('all',                px.parse__type_params,       _type_params,           '**a = {T: int, U: str},'),
        ('all',                px.parse__type_params,       _type_params,           '**a = {T: int, U: str}, *b'),

        ('type_param',         px.parse_type_param,         TypeVar,                'a: int = int'),
        ('type_param',         px.parse_type_param,         ParamSpec,              '**a = {T: int, U: str}'),
        ('type_param',         px.parse_type_param,         TypeVarTuple,           '*a = (int, str)'),

        (type_param,           px.parse_type_param,         TypeVar,                'a: int = int'),
        (TypeVar,              px.parse_type_param,         TypeVar,                'a: int = int'),
        (type_param,           px.parse_type_param,         ParamSpec,              '**a = {T: int, U: str}'),
        (ParamSpec,            px.parse_type_param,         ParamSpec,              '**a = {T: int, U: str}'),
        (type_param,           px.parse_type_param,         TypeVarTuple,           '*a = (int, str)'),
        (TypeVarTuple,         px.parse_type_param,         TypeVarTuple,           '*a = (int, str)'),
    ])


def read(fnm):
    with open(fnm) as f:
        return f.read()


def parse_invalid_src_data():
    funcs = []  # [('name', func), ...]
    data = []  # ['line', ...]

    for name in sorted(dir(px)):
        if name.startswith('parse_') and isinstance(func := getattr(px, name), types.FunctionType):
            funcs.append((name, func))

    for src in [
        ')+(',
        '),(',
        'a)(',
        'a)(b',
        'a),(b',
        'a),(*b',
        'a,)(b',
        'a,),(b',
        'a,b)(b',
        'a)=(',
        'a,)if(',
        ')->(',

        ' #0 ) \\\n + \\\n (',
        ' #0 ) \\\n, \\\n (',
        ' #0\n a #1\n ) \\\n(',
        ' #0\n a #1\n ) \\\n( #2\n b',
        ' #0\n a #1\n ) \\\n ,( \n b',
        ' #0\n a #1\n ) \\\n ,( \n * \n b',
        ' #0\n a #1\n ) \\\n , \\\n ( #2\n b',
        ' #0\n a #1\n , #2\n ) \\\n ( #3\n b',
        ' #0\n a #1\n , #2\n ) \\\n , \\\n ( #3\n b',
        ' #0\n a #1\n , #2\n b #3\n ) \\\n ( #4\n b',
        ' #0\n a #1\n ) \\\n = \\\n (',
        ' #0\n a #1\n , #2\n ) \\\n if \\\n ( #3\n b',

        ']+[',
        '],[',
        'a][',
        'a][b',
        'a],[b',
        'a,][b',
        'a,],[b',
        'a,b][b',
        'a]=[',
        'a,]if[b',

        ' #0 ] \\\n + \\\n [',
        ' #0 ] \\\n, \\\n [',
        ' #0\n a #1\n ] \\\n[',
        ' #0\n a #1\n ] \\\n[ #2\n b',
        ' #0\n a #1\n ] \\\n ,[ \n b',
        ' #0\n a #1\n ] \\\n ,[ \n * \n b',
        ' #0\n a #1\n ] \\\n , \\\n [ #2\n b',
        ' #0\n a #1\n , #2\n ] \\\n [ #3\n b',
        ' #0\n a #1\n , #2\n ] \\\n , \\\n [ #3\n b',
        ' #0\n a #1\n , #2\n b #3\n ] \\\n [ #4\n b',
        ' #0\n a #1\n ] \\\n = \\\n [',
        ' #0\n a #1\n , #2\n ] \\\n if \\\n [ #3\n b',
    ]:
        for name, func in funcs:
            try:
                res = func(src)
            except SyntaxError as exc:
                res = '**SyntaxError**' if len(exc.args) > 1 else f'**{exc!r}**'
            except Exception as exc:
                res = f'**{exc!r}**'
            else:
                res = f'{res.__class__.__name__}  - TODO: FIX THIS!!! TODO: FIX THIS!!! TODO: FIX THIS!!! TODO: FIX THIS!!!'

            data.append(f'{src!r:<12} {name:<32} {res}')

    return data


def regen_coerce_data():
    DATA_COERCE.generate()
    DATA_COERCE.write()


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

            lines.extend(('\n', f'({func.__name__!r}, 0, 0, {res.__name__!r}, {options}, ({mode_str}, {src!r})),\n'))  # need the extra leading newline for lineno counting in support.py

    lines.append(']}\n')

    with open(FNM_PARSE_AUTOGEN, 'w') as f:
        f.writelines(lines)

    DATA_PARSE_AUTOGEN = ParseCases(FNM_PARSE_AUTOGEN)

    DATA_PARSE_AUTOGEN.generate()
    DATA_PARSE_AUTOGEN.write()


def regen_syntax_errors_data():
    out = ['DATA_SYNTAX_ERRORS = {']

    for mode, _, res, src in PARSE_TESTS:
        if not (res is SyntaxError and isinstance(mode, str)):
            continue

        try:
            px.parse(src, mode)

        except SyntaxError as exc:
            lines = traceback.format_exception(exc)

            for i in range(len(lines) - 1, -1, -1):
                if lines[i].startswith('  File'):
                    break
            else:
                continue

            out.append(f'\n{(mode, src)}: [')
            out.extend(f'    {l.rstrip()!r},' for l in lines[i + 1:])
            out.append(f'],')

    out.append('}')

    with open(FNM_SYNTAX_ERRORS, 'w') as fp:
        fp.write('\n'.join(out))


def regen_parse_invalid_src_data():
    data = parse_invalid_src_data()

    with open(FNM_PARSE_INVALID_SRC, 'w') as fp:
        fp.write('\n'.join(data))


class TestParse(unittest.TestCase):
    """Genral parse and unparse and `Code` conversions."""

    maxDiff = None

    def test_coerce(self):
        for case, rest in DATA_COERCE.iterate(True):
            for rest_idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                self.assertEqual(c, r, f'{case.id()}, rest idx = {rest_idx}')

    def test_parse_autogen(self):
        DATA_PARSE_AUTOGEN = ParseCases(FNM_PARSE_AUTOGEN)

        for case, rest in DATA_PARSE_AUTOGEN.iterate(True):
            for rest_idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                if not (c.startswith('**SyntaxError(') and r.startswith('**SyntaxError(')):  # because we will get different texts for different py versions
                    self.assertEqual(c, r, f'{case.id()}, rest idx = {rest_idx}')

    def test_parse_invalid_src(self):
        cur_data = '\n'.join(parse_invalid_src_data())

        with open(FNM_PARSE_INVALID_SRC) as fp:
            old_data = fp.read()

        self.assertEqual(old_data, cur_data)

    def test_parse_invalid_src_selected(self):
        self.assertRaises(SyntaxError, px.parse_expr, '),(')
        self.assertRaises(SyntaxError, px.parse_expr, 'a,)(b')
        self.assertRaises(SyntaxError, px.parse_expr, 'a,),(b')
        self.assertRaises(SyntaxError, px.parse_expr, 'a,b)(')

        self.assertRaises(SyntaxError, px.parse__withitems, 'a),(b')
        self.assertRaises(SyntaxError, px.parse__withitems, 'a) as c,(b')
        self.assertRaises(SyntaxError, px.parse_expr, 'a),(b')
        self.assertRaises(SyntaxError, px.parse__withitems, 'a),(b')
        self.assertRaises(SyntaxError, px.parse_expr, '#0\n a #1\n) \\\n, \\\n( #4')

        self.assertRaises(SyntaxError, px.parse_expr_slice, 'a][b')

        self.assertRaises(SyntaxError, px.parse_expr_arglike, '#0\n a #1\n) \\\n, \\\n( #4\n b')

        self.assertRaises(SyntaxError, px.parse_expr, ' #0\n a #1\n ) \\\n , \\\n ( #4\n b')
        self.assertRaises(SyntaxError, px.parse_expr, ' #0\n a #1\n ) , ( #4\n b')
        self.assertRaises(SyntaxError, px.parse_expr, ' #0\n a #1\n ) , ( b')

        self.assertRaises(SyntaxError, px.parse__arglikes, 'a)(')
        self.assertRaises(SyntaxError, px.parse__arglikes, 'a,b)(b')
        self.assertRaises(SyntaxError, px.parse__expr_arglikes, 'a)(')
        self.assertRaises(SyntaxError, px.parse_expr_arglike, 'a)(b')
        self.assertRaises(SyntaxError, px.parse_expr_arglike, 'a,)(b')

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

                if ((src or func not in (px.parse__aliases, px.parse__Import_names, px.parse__ImportFrom_names))  # these unparse to '()' which can't be reparsed as these
                    and not (src.endswith(',') and func in (px.parse__withitems, px.parse__type_params))  # special case of singletons list containers that can with a trailing comma, which unparse from AST without the comma so reparse to a single element of the type
                ):
                    test = 'reparse'
                    unp  = ((s := px.unparse(ast)) and s.lstrip()) or src  # 'lstrip' because comprehension has leading space, 'or src' because unparse of operators gives nothing
                    ast2 = px.parse(unp, mode)

                    compare_asts(ast, ast2, raise_=True)

                # trailing newline

                if func != px.parse__Assign_targets:  # this can't take trailing newline
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

        self.assertRaises(SyntaxError, px.parse_arguments_lambda, ': lambda')

        self.assertRaises(SyntaxError, px.parse_withitem, 'i for i in j')
        self.assertRaises(SyntaxError, px.parse_withitem, '')

        # parenthesized elements of unparenthesized multiline tuple

        a = px.parse_expr('(a),\n(b)')
        self.assertEqual((1, 0, 2, 3), (a.lineno, a.col_offset, a.end_lineno, a.end_col_offset))

        a = px.parse_expr('( a),\n(b )')
        self.assertEqual((1, 0, 2, 4), (a.lineno, a.col_offset, a.end_lineno, a.end_col_offset))

        a = px.parse_expr(' (a),\n(b) ')
        self.assertEqual((1, 1, 2, 3), (a.lineno, a.col_offset, a.end_lineno, a.end_col_offset))

        # prefer TypeVarTuple over invalid Assign

        if PYGE13:
            self.assertIsInstance(px.parse_all('*T = (int,)'), TypeVarTuple)

    def test_parse__BoolOp_dangling(self):
        # left

        src = '\n# comment\n \\\n and # line\n x # line\n \\\n'
        f = FST(px.parse__BoolOp_dangling_left(src, loc_whole=False), src.split('\n'), None)
        self.assertEqual((3, 1, 4, 2), f.loc)

        f = FST(px.parse__BoolOp_dangling_left(src, loc_whole=True), src.split('\n'), None)
        self.assertEqual((0, 0, 6, 0), f.loc)

        self.assertRaises(ParseError, px.parse__BoolOp_dangling_left, '+ 1')

        # right

        src = '\n# comment\n \\\n x # comment\n \\\n and # line\n \\\n'
        f = FST(px.parse__BoolOp_dangling_right(src, loc_whole=False), src.split('\n'), None)
        self.assertEqual((3, 1, 5, 4), f.loc)

        f = FST(px.parse__BoolOp_dangling_right(src, loc_whole=True), src.split('\n'), None)
        self.assertEqual((0, 0, 7, 0), f.loc)

        src = '\na and\n'

        f = FST(px.parse__BoolOp_dangling_right(src, loc_whole=False), src.split('\n'), None)
        self.assertEqual((1, 0, 1, 5), f.loc)

        self.assertRaises(ParseError, px.parse__BoolOp_dangling_right, '1 +')

    def test_parse__Compare_dangling(self):
        # left

        src = '\n# comment\n \\\n < # line\n x # line\n \\\n'
        f = FST(px.parse__Compare_dangling_left(src, loc_whole=False), src.split('\n'), None)
        self.assertEqual((3, 1, 4, 2), f.loc)

        f = FST(px.parse__Compare_dangling_left(src, loc_whole=True), src.split('\n'), None)
        self.assertEqual((0, 0, 6, 0), f.loc)

        src = '\n# comment\n \\\n is \\\n not \\\n # line\n x # line\n \\\n'
        f = FST(px.parse__Compare_dangling_left(src, loc_whole=False), src.split('\n'), None)
        self.assertEqual((3, 1, 6, 2), f.loc)

        f = FST(px.parse__Compare_dangling_left(src, loc_whole=True), src.split('\n'), None)
        self.assertEqual((0, 0, 8, 0), f.loc)

        self.assertRaises(ParseError, px.parse__Compare_dangling_left, '+ 1')

        # right

        src = '\n# comment\n \\\n x # comment\n \\\n > # line\n \\\n'
        f = FST(px.parse__Compare_dangling_right(src, loc_whole=False), src.split('\n'), None)
        self.assertEqual((3, 1, 5, 2), f.loc)

        f = FST(px.parse__Compare_dangling_right(src, loc_whole=True), src.split('\n'), None)
        self.assertEqual((0, 0, 7, 0), f.loc)

        src = '\n# comment\n \\\n x # comment\n \\\n is \\\n not \\\n # line\n \\\n'
        f = FST(px.parse__Compare_dangling_right(src, loc_whole=False), src.split('\n'), None)
        self.assertEqual((3, 1, 6, 4), f.loc)

        f = FST(px.parse__Compare_dangling_right(src, loc_whole=True), src.split('\n'), None)
        self.assertEqual((0, 0, 9, 0), f.loc)

        src = '\n# comment\n \\\n x # comment\n \\\n not \\\n in \\\n # line\n \\\n'
        f = FST(px.parse__Compare_dangling_right(src, loc_whole=False), src.split('\n'), None)
        self.assertEqual((3, 1, 6, 3), f.loc)

        f = FST(px.parse__Compare_dangling_right(src, loc_whole=True), src.split('\n'), None)
        self.assertEqual((0, 0, 9, 0), f.loc)

        self.assertRaises(ParseError, px.parse__Compare_dangling_right, '1 +')

    def test_parse_by_ast_name_from_get_one_data(self):
        # make sure parsing by name of `AST` class is same as parsing by `AST` class

        cases_found = False

        for case in BaseCases(os.path.join(DIR_NAME, 'data/data_get_one.py')).iterate():
            if case.key != 'all_basic':
                break

            cases_found = True

            if isinstance(code := case.code, tuple) and isinstance(code[0], type) and issubclass(code[0], AST):
                try:
                    a = px.parse(code[1], code[0])
                except Exception as exc:
                    pass

                else:
                    b = px.parse(code[1], code[0].__name__)

                    compare_asts(a, b, locs=True, raise_=True)

        if not cases_found:
            raise RuntimeError("'all_basic' cases not found at start of DATA_GET_ONE")

    @unittest.skipUnless(PYGE13, 'only valid for py >= 3.13')
    def test_parse_syntax_errors(self):
        with open(FNM_SYNTAX_ERRORS) as fp:
            src = fp.read()

        globs = {}

        exec(src, globs)

        syntax_errors = globs['DATA_SYNTAX_ERRORS']

        for mode, _, res, src in PARSE_TESTS:
            if not (res is SyntaxError and isinstance(mode, str)):
                continue

            try:
                px.parse(src, mode)

            except SyntaxError as exc:
                lines = traceback.format_exception(exc)

                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].startswith('  File'):
                        break
                else:
                    continue

            old = syntax_errors.get((mode, src))

            if not old:
                raise ValueError(f'case not found in data: {(mode, src)}')

            old = '\n'.join(old)
            new = '\n'.join(l.rstrip() for l in lines[i + 1:])

            self.assertEqual(old, new)

    def test_parse_unsupported(self):
        self.assertRaises(ParseError, px.parse, '', FunctionType)
        self.assertRaises(ParseError, px.parse, '', FormattedValue)
        self.assertRaises(ParseError, px.parse, '', Interpolation)
        self.assertRaises(ParseError, px.parse, '', TypeIgnore)

        self.assertRaises(ValueError, px.parse, '', 'FunctionType')
        self.assertRaises(ValueError, px.parse, '', 'FormattedValue')
        self.assertRaises(ValueError, px.parse, '', 'Interpolation')
        self.assertRaises(ValueError, px.parse, '', 'TypeIgnore')

    def test_parse_coverage(self):
        # for test coverage

        self.assertRaises(ParseError, px.parse, 'pass', Assign)
        self.assertRaises(ParseError, px.parse, 'call()', BinOp)
        self.assertRaises(ParseError, px.parse, '*st', MatchSequence)

        self.assertRaises(ParseError, px.parse, '', TypeIgnore)
        self.assertRaises(ValueError, px.parse, '', list)

        self.assertRaises(SyntaxError, px.parse_all, '!')

        self.assertRaises(SyntaxError, px.parse_expr_slice, ']')

        if PYLT11:
            self.assertRaises(SyntaxError, px.parse_expr_slice, '*st')
            self.assertIsInstance(px.parse_Tuple_elt('*st'), Starred)
            self.assertRaises(SyntaxError, px.parse_Tuple, '')

        if PYGE11:
            self.assertRaises(ParseError, px.parse_arg, 'arg: *st, b')

    def test_code_as_simple(self):
        # stmts

        f = FST(r'''
if 1:
    pass

call(a)
'''.strip(), 'exec')

        h = code_as_stmts(f.copy(), coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.src, coerce=True)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.a, coerce=True)
        self.assertTrue(compare_asts(h.a, f.a, locs=False, raise_=True))

        f0 = f.body[0].copy()
        h = code_as_stmts(f0.a, coerce=True)
        self.assertEqual(ast_unparse(f0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f0.a, locs=False, raise_=True))

        f1 = f.body[1].copy()
        h = code_as_stmts(f1.a, coerce=True)
        self.assertEqual(ast_unparse(f1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f1.a, locs=False, raise_=True))

        g = FST('from a import b', 'exec').body[0].names[0]
        self.assertRaises(ValueError, code_as_stmts, f.body[0].test)
        self.assertRaises(NodeError, code_as_stmts, g.copy())
        self.assertRaises(NodeError, code_as_stmts, g.a)
        self.assertRaises(SyntaxError, code_as_stmts, 'except Exception: pass')

        f = FST('f(a)', 'exec')
        h = code_as_stmts(f.body[0].value.copy(), coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.src, coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.a, coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        # expr

        f = FST('a if b else {"c": f()}', 'eval')

        h = code_as_expr(f.copy(), coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body.a, locs=True, raise_=True))

        f = FST('a if b else {"c": f()}', 'single')

        h = code_as_expr(f.copy(), coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        f = FST('a if b else {"c": f()}', 'exec')

        h = code_as_expr(f.copy(), coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        h = code_as_expr(f.body[0].copy(), coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.body[0].value.a, locs=True, raise_=True))

        h = code_as_expr(f.body[0].value.copy(), coerce=True)
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

        h = code_as__ExceptHandlers(g.copy(), coerce=True)
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = code_as__ExceptHandlers(g.src, coerce=True)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.handlers[0].copy()
        h = code_as__ExceptHandlers(g0.a, coerce=True)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.handlers[0].a, g0.a, locs=False, raise_=True))

        g1 = g.handlers[1].copy()
        h = code_as__ExceptHandlers(g1.a, coerce=True)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.handlers[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as__ExceptHandlers, f.body[0].handlers[0])

        self.assertEqual(0, len(code_as__ExceptHandlers('', coerce=True).handlers))  # make sure we can parse zero ExceptHandlers

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

        h = code_as__match_cases(g.copy(), coerce=True)
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = code_as__match_cases(g.src, coerce=True)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.cases[0].copy()
        h = code_as__match_cases(g0.a, coerce=True)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.cases[0].a, g0.a, locs=False, raise_=True))

        g1 = g.cases[1].copy()
        h = code_as__match_cases(g1.a, coerce=True)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.cases[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as__match_cases, f.body[0].cases[0])

        self.assertEqual(0, len(code_as__match_cases('', coerce=True).cases))  # make sure we can parse zero match_cases

        # boolop

        f = FST(And(), ['and'], None)

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
            (code_as_operator, 'body[0].value.op', 'a + b'),
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

        h = code_as_stmts(f.copy(), coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.src, coerce=True)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.a, coerce=True)
        self.assertTrue(compare_asts(h.a, f.a, locs=False, raise_=True))

        f0 = f.body[0].copy()
        h = code_as_stmts(f0.a, coerce=True)
        self.assertEqual(ast_unparse(f0.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f0.a, locs=False, raise_=True))

        f1 = f.body[1].copy()
        h = code_as_stmts(f1.a, coerce=True)
        self.assertEqual(ast_unparse(f1.a), h.src)
        self.assertTrue(compare_asts(h.body[0].a, f1.a, locs=False, raise_=True))

        g = FST('from a import b', 'exec').body[0].names[0]
        self.assertRaises(ValueError, code_as_stmts, f.body[0].test)
        self.assertRaises(NodeError, code_as_stmts, g.copy())
        self.assertRaises(NodeError, code_as_stmts, g.a)

        f = FST('f(a)', 'exec')
        h = code_as_stmts(f.body[0].value.copy(), coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.src, coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

        h = code_as_stmts(f.a, coerce=True)
        self.assertEqual(h.src, f.src)
        self.assertTrue(compare_asts(h.a, f.a, locs=True, raise_=True))

    def test_code_as__ExceptHandlers(self):
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

        h = code_as__ExceptHandlers(g.copy(), coerce=True)
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = code_as__ExceptHandlers(g.src, coerce=True)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.handlers[0].copy()
        h = code_as__ExceptHandlers(g0.a, coerce=True)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.handlers[0].a, g0.a, locs=False, raise_=True))

        g1 = g.handlers[1].copy()
        h = code_as__ExceptHandlers(g1.a, coerce=True)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.handlers[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as__ExceptHandlers, f.body[0].handlers[0])

    def test_code_as__match_cases(self):
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

        h = code_as__match_cases(g.copy(), coerce=True)
        self.assertEqual(h.src, g.src)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        h = code_as__match_cases(g.src, coerce=True)
        self.assertTrue(compare_asts(h.a, g.a, locs=True, raise_=True))

        g0 = g.cases[0].copy()
        h = code_as__match_cases(g0.a, coerce=True)
        self.assertEqual(ast_unparse(g0.a), h.src)
        self.assertTrue(compare_asts(h.cases[0].a, g0.a, locs=False, raise_=True))

        g1 = g.cases[1].copy()
        h = code_as__match_cases(g1.a, coerce=True)
        self.assertEqual(ast_unparse(g1.a), h.src)
        self.assertTrue(compare_asts(h.cases[0].a, g1.a, locs=False, raise_=True))

        self.assertRaises(ValueError, code_as__match_cases, f.body[0].cases[0])

        # special 'case' non-keyword

        self.assertIsInstance(code_as__match_cases('case 1: pass', coerce=True).cases[0].a, match_case)
        self.assertRaises(SyntaxError, code_as__match_cases, 'case = 1')
        self.assertRaises(SyntaxError, code_as__match_cases, 'case.b = 1')

    def test_code_as_op(self):
        for code_as, opstr2cls in [
            (code_as_unaryop, OPSTR2CLS_UNARY),
            (code_as_operator, OPSTR2CLS_BIN),
            (code_as_cmpop, OPSTR2CLS_CMP),
            (code_as_boolop, OPSTR2CLS_BOOL)
        ]:
            for op, kls in opstr2cls.items():
                self.assertEqual(op, code_as(op).src)
                self.assertEqual(f'# pre\n{op} # line\n# post', code_as(f'# pre\n{op} # line\n# post').src)
                self.assertEqual(op, code_as(f'# pre\n{op} # line\n# post', sanitize=True).src)
                self.assertEqual(op, code_as([op]).src)
                self.assertEqual(f'# pre\n{op} # line\n# post', code_as(['# pre', f'{op} # line', '# post']).src)
                self.assertEqual(op, code_as(['# pre', f'{op} # line', '# post'], sanitize=True).src)
                self.assertEqual(op, code_as(FST(op, kls)).src)
                self.assertEqual(f'# pre\n{op} # line\n# post', code_as(FST(f'# pre\n{op} # line\n# post', kls)).src)
                self.assertEqual(op, code_as(FST(f'# pre\n{op} # line\n# post', kls), sanitize=True).src)
                self.assertEqual(op, code_as(kls()).src)
                self.assertEqual(op, code_as(kls(), sanitize=True).src)

    def test_code_as_identifier(self):
        self.assertEqual('name', code_as_identifier('name'))
        self.assertEqual('name', code_as_identifier(['name']))
        self.assertEqual('name', code_as_identifier(FST('name', 'Name')))
        self.assertEqual('name', code_as_identifier(FST('name', 'Expr')))
        self.assertEqual('name', code_as_identifier(FST('name', 'exec')))
        self.assertEqual('name', code_as_identifier(FST('# pre\nname # line\n# post', 'Name')))
        self.assertEqual('name', code_as_identifier(Name('name')))
        self.assertEqual('name', code_as_identifier(Expr(Name('name'))))
        self.assertEqual('name', code_as_identifier(Module([Expr(Name('name'))], [])))

        self.assertRaises(ParseError, code_as_identifier, 'a.b')
        self.assertRaises(ParseError, code_as_identifier, '*')

        self.assertEqual('a.b', code_as_identifier_dotted('a.b'))
        self.assertEqual('a.b', code_as_identifier_dotted(['a.b']))
        self.assertEqual('a.b', code_as_identifier_dotted(FST('a.b', 'Attribute')))
        self.assertEqual('a.b', code_as_identifier_dotted(FST('a.b', 'Expr')))
        self.assertEqual('a.b', code_as_identifier_dotted(FST('a.b', 'exec')))
        self.assertEqual('a.b', code_as_identifier_dotted(FST('# pre\na.b # line\n# post', 'Attribute')))
        self.assertEqual('a.b', code_as_identifier_dotted(Attribute(Name('a'), 'b')))
        self.assertEqual('a.b', code_as_identifier_dotted(Expr(Attribute(Name('a'), 'b'))))
        self.assertEqual('a.b', code_as_identifier_dotted(Module([Expr(Attribute(Name('a'), 'b'))], [])))
        self.assertEqual('name', code_as_identifier_dotted('name'))
        self.assertEqual('name', code_as_identifier_dotted(['name']))
        self.assertEqual('name', code_as_identifier_dotted(FST('name', 'Name')))
        self.assertEqual('name', code_as_identifier_dotted(FST('name', 'Expr')))
        self.assertEqual('name', code_as_identifier_dotted(FST('name', 'exec')))
        self.assertEqual('name', code_as_identifier_dotted(FST('# pre\nname # line\n# post', 'Name')))
        self.assertEqual('name', code_as_identifier_dotted(Name('name')))
        self.assertEqual('name', code_as_identifier_dotted(Expr(Name('name'))))
        self.assertEqual('name', code_as_identifier_dotted(Module([Expr(Name('name'))], [])))

        self.assertRaises(ParseError, code_as_identifier_dotted, '*')

        self.assertEqual('*', code_as_identifier_star('*'))
        self.assertEqual('*', code_as_identifier_star(['*']))
        self.assertEqual('*', code_as_identifier_star(FST('*', 'alias')))
        self.assertEqual('*', code_as_identifier_star(FST('* # line', 'alias')))
        self.assertEqual('*', code_as_identifier_star(alias('*')))
        self.assertEqual('name', code_as_identifier_star('name'))
        self.assertEqual('name', code_as_identifier_star(['name']))
        self.assertEqual('name', code_as_identifier_star(FST('name', 'Name')))
        self.assertEqual('name', code_as_identifier_star(FST('name', 'Expr')))
        self.assertEqual('name', code_as_identifier_star(FST('name', 'exec')))
        self.assertEqual('name', code_as_identifier_star(FST('# pre\nname # line\n# post', 'Name')))
        self.assertEqual('name', code_as_identifier_star(Name('name')))
        self.assertEqual('name', code_as_identifier_star(Expr(Name('name'))))
        self.assertEqual('name', code_as_identifier_star(Module([Expr(Name('name'))], [])))

        self.assertRaises(ParseError, code_as_identifier_star, 'a.b')

        self.assertEqual('*', code_as_identifier_alias('*'))
        self.assertEqual('*', code_as_identifier_alias(['*']))
        self.assertEqual('*', code_as_identifier_alias(FST('*', 'alias')))
        self.assertEqual('*', code_as_identifier_alias(FST('* # line', 'alias')))
        self.assertEqual('*', code_as_identifier_alias(alias('*')))
        self.assertEqual('name', code_as_identifier_alias('name'))
        self.assertEqual('name', code_as_identifier_alias(['name']))
        self.assertEqual('name', code_as_identifier_alias(FST('name', 'Name')))
        self.assertEqual('name', code_as_identifier_alias(FST('name', 'Expr')))
        self.assertEqual('name', code_as_identifier_alias(FST('name', 'exec')))
        self.assertEqual('name', code_as_identifier_alias(FST('# pre\nname # line\n# post', 'Name')))
        self.assertEqual('name', code_as_identifier_alias(Name('name')))
        self.assertEqual('name', code_as_identifier_alias(Expr(Name('name'))))
        self.assertEqual('name', code_as_identifier_alias(Module([Expr(Name('name'))], [])))
        self.assertEqual('a.b', code_as_identifier_alias('a.b'))
        self.assertEqual('a.b', code_as_identifier_alias(['a.b']))
        self.assertEqual('a.b', code_as_identifier_alias(FST('a.b', 'Attribute')))
        self.assertEqual('a.b', code_as_identifier_alias(FST('a.b', 'Expr')))
        self.assertEqual('a.b', code_as_identifier_alias(FST('a.b', 'exec')))
        self.assertEqual('a.b', code_as_identifier_alias(FST('# pre\na.b # line\n# post', 'Attribute')))
        self.assertEqual('a.b', code_as_identifier_alias(Attribute(Name('a'), 'b')))
        self.assertEqual('a.b', code_as_identifier_alias(Expr(Attribute(Name('a'), 'b'))))
        self.assertEqual('a.b', code_as_identifier_alias(Module([Expr(Attribute(Name('a'), 'b'))], [])))

        for keyword in keyword_kwlist:
            self.assertRaises(ParseError, code_as_identifier, keyword)
            self.assertRaises(ParseError, code_as_identifier_dotted, keyword)
            self.assertRaises(ParseError, code_as_identifier_star, keyword)
            self.assertRaises(ParseError, code_as_identifier_alias, keyword)

    def test_code_as_sanitize_exprlike(self):
        CODE_ASES = [
            (code_as_expr, 'f(a)'),
            (code_as_expr_slice, 'b:c:d'),
            (code_as_expr_slice, 'b:c:d, e:f'),
            (code_as_Tuple, '1, 2, 3'),
            (code_as_boolop, 'and'),
            (code_as_operator, '+'),
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
            self.assertEqual(src, code_as(f'  {src}  ', sanitize=True).src)

            if code_as in (code_as_expr, code_as_pattern):  # parenthesizable things so lets abuse
                srcp = f'(\n# pre\n{src} # post\n# post2\n)'

                self.assertEqual(srcp, code_as(srcp).src)
                self.assertEqual(src, code_as(srcp[1:-1], sanitize=True).src)

    def test_code_as_all_from_ast(self):
        for mode, func, res, src in PARSE_TESTS:
            if issubclass(res, Exception):
                continue

            ast = None

            try:
                ast  = px.parse(src, mode)
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
                    test    = 'src'
                    fst     = code_as(src)

                    compare_asts(ref_ast, fst.a, locs=True, raise_=True)

                    if fst._get_parse_mode() not in ('_ExceptHandlers', '_match_cases'):  # this tells us if it is a SPECIAL SLICE, which can not be unparsed  TODO: remove this check once ExceptHandler and match_case special slices moved from Module to their own _slice AST classes
                        test    = 'ast'
                        ast_fst = code_as(fst.a)

                        compare_asts(ref_ast, ast_fst.a, locs=False, raise_=True)

                    test    = 'fst'
                    fst_src = fst.src
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

        self.assertRaises(NodeError, code_as__ImportFrom_names, FST('*', '_aliases').names.append('*').base)
        self.assertRaises(NodeError, code_as__ImportFrom_names, FST('a', '_aliases').names.append('*').base)
        self.assertEqual('*', code_as__ImportFrom_names(FST('*', '_aliases')).src)

        # lambda arguments from FST

        self.assertIs(f := FST('a=1, /, b=2, *c, d=3, **e', 'arguments'), code_as_arguments_lambda(f))

        self.assertRaises(NodeError, code_as_arguments_lambda, FST('a: int = 1, /, b=2, *c, d=3, **e', 'arguments'))
        self.assertRaises(NodeError, code_as_arguments_lambda, FST('a=1, /, b: int = 2, *c, d=3, **e', 'arguments'))
        self.assertRaises(NodeError, code_as_arguments_lambda, FST('a=1, /, b=2, *c: tuple, d=3, **e', 'arguments'))
        self.assertRaises(NodeError, code_as_arguments_lambda, FST('a=1, /, b=2, *c, d: int = 3, **e', 'arguments'))
        self.assertRaises(NodeError, code_as_arguments_lambda, FST('a=1, /, b=2, *c, d=3, **e: dict', 'arguments'))

        # expr from FST

        self.assertRaises(NodeError, code_as_expr, FST('a:b:c', 'Slice'))
        self.assertRaises(NodeError, code_as_expr, FST('a:b:c, d:e', 'expr_slice'))

        self.assertIs(f := FST('a:b:c', 'Slice'), code_as_expr_all(f))
        self.assertIs(f := FST('a:b:c, d:e', 'expr_slice'), code_as_expr_all(f))

        self.assertRaises(NodeError, code_as_expr_arglike, FST('a:b:c', 'Slice'))
        self.assertRaises(NodeError, code_as_expr_arglike, FST('a:b:c, d:e', 'expr_slice'))

        self.assertIs(f := FST('a:b:c', 'Slice'), code_as_expr_slice(f))
        self.assertIs(f := FST('a:b:c, d:e', 'expr_slice'), code_as_expr_slice(f))

        self.assertIs(f := FST('a:b:c', 'Slice'), code_as_Tuple_elt(f))
        self.assertRaises(NodeError, code_as_Tuple_elt, FST('a:b:c, d:e', 'expr_slice'))

        self.assertRaises(NodeError, code_as_Tuple, FST('a:b:c', 'Slice'))
        self.assertIs(f := FST('a:b:c, d:e', 'expr_slice'), code_as_Tuple(f))

        # expr_arglikes

        self.assertRaises(NodeError, code_as__expr_arglikes, FST('a:b:c'))
        self.assertRaises(NodeError, code_as__expr_arglikes, FST('a:b:c,'))

        # disallowed Starred

        self.assertRaises(NodeError, code_as_withitem, FST('*a'))
        self.assertRaises(NodeError, code_as__withitems, FST('*a'))
        self.assertRaises(ParseError, code_as__comprehension_ifs, '*a', coerce=True)
        self.assertRaises(NodeError, code_as__comprehension_ifs, FST('*a'), coerce=True)

    def test_code_as_coerce(self):
        def test(code, res):
            try:
                f = code_as(code, coerce=True)
            except Exception as exc:
                r = f'**SyntaxError**' if exc.__class__ is SyntaxError else f'**{exc!r}**'

            else:
                if code_as is not code_as__expr_arglikes:  # this one is special and unverifiable
                    f.verify()

                r = (f.a.__class__, f.src)

            try:
                self.assertEqual(res, r)  # old, new
            except Exception:
                print(f'\nold={res}\nnew={r}')
                raise

        cases = [
            (code_as_expr, (Module, 'a'), (Name, 'a')),
            (code_as_expr, (Module, 'a\nb'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got Module, could not coerce, multiple statements')**",  # FST
                "**NodeError('expecting expression (standard), got Module, could not coerce, multiple statements')**"),  # AST
            (code_as_expr, (Module, 'a = b'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got Module, could not coerce, uncoercible type Assign')**",  # FST
                "**NodeError('expecting expression (standard), got Module, could not coerce, uncoercible type Assign')**"),  # AST
            (code_as_expr, (Interactive, 'a'), (Name, 'a')),
            (code_as_expr, (Interactive, 'a; b'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got Interactive, could not coerce, multiple statements')**",  # FST
                "**NodeError('expecting expression (standard), got Interactive, could not coerce, multiple statements')**"),  # AST
            (code_as_expr, (Interactive, 'a = b'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got Interactive, could not coerce, uncoercible type Assign')**",  # FST
                "**NodeError('expecting expression (standard), got Interactive, could not coerce, uncoercible type Assign')**"),  # AST
            (code_as_expr, (Expression, 'a'), (Name, 'a')),
            (code_as_expr, (Expr, 'a'), (Name, 'a')),
            (code_as_expr, (arguments, 'a'),
                (Name, 'a'),
                (Tuple, 'a,'),
                (Tuple, '(a,)')),
            (code_as_expr, (arguments, 'a, *b, c'),
                (Tuple, 'a, *b, c'),
                (Tuple, 'a, *b, c'),
                (Tuple, '(a, *b, c)')),
            (code_as_expr, (arguments, '\n*\nb\n,\nc\n,\n'),
                (Tuple, '\n*\nb\n,\nc\n,\n'),
                (Tuple, '\n*\nb\n,\nc\n,\n'),
                (Tuple, '(*b, c)')),
            (code_as_expr, (arguments, '#0'),
                "**SyntaxError**",  # src
                (Tuple, '(#0\n)'),
                (Tuple, '()')),
            (code_as_expr, (arguments, '#0\n#1'),
                "**SyntaxError**",  # src
                (Tuple, '(#0\n#1\n)'),
                (Tuple, '()')),
            (code_as_expr, (arguments, '\\'),
                "**SyntaxError**",  # src
                (Tuple, '()'),
                (Tuple, '()')),
            (code_as_expr, (arg, 'a'), (Name, 'a')),
            (code_as_expr, (arg, 'a: int'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got arg, could not coerce, has annotation')**",  # FST
                "**NodeError('expecting expression (standard), got arg, could not coerce, has annotation')**"),  # AST
            (code_as_expr, (alias, 'a'), (Name, 'a')),
            (code_as_expr, (alias, 'a as b'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got alias, could not coerce, has asname')**",  # FST
                "**NodeError('expecting expression (standard), got alias, could not coerce, has asname')**"),  # AST
            (code_as_expr, (alias, '*'),
                "**SyntaxError**",  # src
                "**NodeError(\"expecting expression (standard), got alias, could not coerce, star '*' alias\")**",  # FST
                "**NodeError(\"expecting expression (standard), got alias, could not coerce, star '*' alias\")**"),  # AST
            (code_as_expr, (alias, 'a.b'), (Attribute, 'a.b')),
            (code_as_expr, (alias, 'a\\\n.\\\nb'), (Attribute, 'a\\\n.\\\nb'), (Attribute, 'a.b')),
            (code_as_expr, (_aliases, ''),
                "**SyntaxError**",  # src
                (Tuple, '()'),  # FST
                (Tuple, '()')),  # AST
            (code_as_expr, (_aliases, 'a'),
                (Name, 'a'),  # src
                (Tuple, 'a,'),  # FST
                (Tuple, '(a,)')),  # AST
            (code_as_expr, (_aliases, 'a, b as c'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got _aliases, could not coerce, alias has asname')**",  # FST
                "**NodeError('expecting expression (standard), got _aliases, could not coerce, alias has asname')**"),  # AST
            (code_as_expr, (_aliases, '*'),
                "**SyntaxError**",  # src
                "**NodeError(\"expecting expression (standard), got _aliases, could not coerce, star '*' alias\")**",  # FST
                "**NodeError(\"expecting expression (standard), got _aliases, could not coerce, star '*' alias\")**"),  # AST
            (code_as_expr, (_aliases, 'a, b.c'),
                (Tuple, 'a, b.c'),  # src
                (Tuple, 'a, b.c'),  # FST
                (Tuple, '(a, b.c)')),  # AST
            (code_as_expr, (_aliases, ' a, b\\\n.\\\nc '),
                (Tuple, ' a, b\\\n.\\\nc '),  # src
                (Tuple, ' a, b\\\n.\\\nc '),  # FST
                (Tuple, '(a, b.c)')),  # AST
            (code_as_expr, (withitem, 'a'), (Name, 'a')),
            (code_as_expr, (withitem, 'a as b'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got withitem, could not coerce, has optional_vars')**",  # FST
                "**NodeError('expecting expression (standard), got withitem, could not coerce, has optional_vars')**"),  # AST
            (code_as_expr, (MatchValue, '1'), (Constant, '1')),
            (code_as_expr, (MatchSingleton, 'True'), (Constant, 'True')),
            (code_as_expr, (MatchSingleton, 'False'), (Constant, 'False')),
            (code_as_expr, (MatchSingleton, 'None'), (Constant, 'None')),
            (code_as_expr, (MatchStar, '*s'), (Starred, '*s')),
            (code_as_expr, (MatchAs, 'a'), (Name, 'a')),
            (code_as_expr, (MatchAs, 'a as b'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got MatchAs, could not coerce, has pattern')**",  # FST
                "**NodeError('expecting expression (standard), got MatchAs, could not coerce, has pattern')**"),  # AST
            (code_as_expr, (MatchSequence, 'x, 1, True, *y'), (Tuple, 'x, 1, True, *y'), (List, '[x, 1, True, *y]')),
            (code_as_expr, (MatchSequence, '(x, 1, True, *y)'), (Tuple, '(x, 1, True, *y)'), (List, '[x, 1, True, *y]')),
            (code_as_expr, (MatchSequence, '[x, 1, True, *y]'), (List, '[x, 1, True, *y]')),
            (code_as_expr, (MatchSequence, '[([x, 1, True, *y],)]'), (List, '[([x, 1, True, *y],)]'), (List, '[[[x, 1, True, *y]]]')),
            (code_as_expr, (MatchMapping, '{1: a, b.c: d, **e}'), (Dict, '{1: a, b.c: d, **e}')),
            (code_as_expr, (MatchClass, 'cls(a, b=c)'), (Call, 'cls(a, b=c)')),
            (code_as_expr, (MatchOr, 'a | b'), (BinOp, 'a | b')),
            (code_as_expr, (MatchOr, 'a | b | c'), (BinOp, 'a | b | c')),
            (code_as_expr, (MatchOr, '(a | b) | c'),
                (BinOp, '(a | b) | c'),
                (BinOp, '(a | b) | c'),
                (BinOp, 'a | b | c')),
            (code_as_expr, (MatchOr, 'a | (b | c)'), (BinOp, 'a | (b | c)')),
            (code_as_expr, (MatchOr, '(a | (b | c)) | d'),
                (BinOp, '(a | (b | c)) | d'),
                (BinOp, '(a | (b | c)) | d'),
                (BinOp, 'a | (b | c) | d')),
            (code_as_expr, (MatchOr, 'a | ((b | c) | d)'),
                (BinOp, 'a | ((b | c) | d)'),
                (BinOp, 'a | ((b | c) | d)'),
                (BinOp, 'a | (b | c | d)')),
            (code_as_expr, (MatchOr, '(a | b | c) | d'),
                (BinOp, '(a | b | c) | d'),
                (BinOp, '(a | b | c) | d'),
                (BinOp, 'a | b | c | d')),
            (code_as_expr, (MatchOr, 'a | (b | c | d)'), (BinOp, 'a | (b | c | d)')),
            (code_as_expr, (MatchOr, 'a | (b | c) | d'), (BinOp, 'a | (b | c) | d')),
            (code_as_expr, (MatchOr, 'a | (b | (c | d) | e) | f'), (BinOp, 'a | (b | (c | d) | e) | f')),
            (code_as_expr, (_Assign_targets, 'a = b = c ='),
                "**SyntaxError**",  # src
                (Tuple, 'a, b, c'),  # FST
                (Tuple, '(a, b, c)')),  # AST
            (code_as_expr, (_decorator_list, '@a\n@b\n@c'),
                "**SyntaxError**",  # src
                (Tuple, '(a,\nb,\nc)'),  # FST
                (Tuple, '(a, b, c)')),  # AST
            (code_as_expr, (_comprehension_ifs, 'if a if b if c'),
                "**SyntaxError**",  # src
                (Tuple, 'a, b, c'),  # AST
                (Tuple, '(a, b, c)')),  # AST
            (code_as_expr, (_arglikes, ''),
                "**SyntaxError**",  # src
                (Tuple, '()'),  # FST
                (Tuple, '()')),  # AST
            (code_as_expr, (_arglikes, 'a'),
                (Name, 'a'),  # src
                (Tuple, 'a,'),  # FST
                (Tuple, '(a,)')),  # AST
            (code_as_expr, (_arglikes, 'a, b=c'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got _arglikes, could not coerce, cannot have keyword')**",  # FST
                "**NodeError('expecting expression (standard), got _arglikes, could not coerce, cannot have keyword')**"),  # AST
            (code_as_expr, (_arglikes, 'a, *b'),
                (Tuple, 'a, *b'),  # src
                (Tuple, 'a, *b'),  # FST
                (Tuple, '(a, *b)')),  # AST
            (code_as_expr, (_arglikes, ' a, *b '),
                (Tuple, ' a, *b '),  # src
                (Tuple, 'a, *b'),  # FST
                (Tuple, '(a, *b)')),  # AST
            (code_as_expr, (_arglikes, ' *not a, *b or c '),
                "**SyntaxError**",  # src
                (Tuple, '*(not a), *(b or c)'),  # FST
                (Tuple, '(*(not a), *(b or c))')),  # AST
            (code_as_expr, (_withitems, ''),
                "**SyntaxError**",  # src
                (Tuple, '()'),  # FST
                (Tuple, '()')),  # AST
            (code_as_expr, (_withitems, 'a'),
                (Name, 'a'),  # src
                (Tuple, 'a,'),  # FST
                (Tuple, '(a,)')),  # AST
            (code_as_expr, (_withitems, 'a as b'),
                "**SyntaxError**",  # src
                "**NodeError('expecting expression (standard), got _withitems, could not coerce, withitem has optional_vars')**",  # FST
                "**NodeError('expecting expression (standard), got _withitems, could not coerce, withitem has optional_vars')**"),  # AST
            (code_as_expr, (_withitems, 'a, b'),
                (Tuple, 'a, b'),  # src
                (Tuple, 'a, b'),  # FST
                (Tuple, '(a, b)')),  # AST
            (code_as_expr, (_withitems, ' a, b '),
                (Tuple, ' a, b '),  # src
                (Tuple, 'a, b'),  # FST
                (Tuple, '(a, b)')),  # AST

            (code_as__Assign_targets, (Name, 'a'), (_Assign_targets, 'a')),
            (code_as__Assign_targets, (Attribute, 'a.b'), (_Assign_targets, 'a.b')),
            (code_as__Assign_targets, (Subscript, 'a[b]'), (_Assign_targets, 'a[b]')),
            (code_as__Assign_targets, (Tuple, 'a, b'),
                (_Assign_targets, 'a, b'),  # src
                (_Assign_targets, 'a = b ='),  # FST
                (_Assign_targets, 'a = b =')),  # AST
            (code_as__Assign_targets, (Tuple, '(a, b)'),
                (_Assign_targets, '(a, b)'),  # src
                (_Assign_targets, 'a = b ='),  # FST
                (_Assign_targets, 'a = b =')),  # AST
            (code_as__Assign_targets, (List, '[a, b]'),
                (_Assign_targets, '[a, b]'),  # src
                (_Assign_targets, 'a = b ='),  # FST
                (_Assign_targets, 'a = b =')),  # AST
            (code_as__Assign_targets, (Starred, '*a'), (_Assign_targets, '*a')),
            (code_as__Assign_targets, (Call, 'f()'),
                "**SyntaxError**",  # src
                "**NodeError('expecting _Assign_targets, got Call, could not coerce')**",  # FST
                "**NodeError('expecting _Assign_targets, got Call, could not coerce')**"),  # AST
            (code_as__Assign_targets, (Name, '#0\n ( a ) #1\n#2'),
                "**SyntaxError**",
                (_Assign_targets, '( a )'),
                (_Assign_targets, 'a')),
            (code_as__Assign_targets, (Tuple, 'a,b,c'),
                (_Assign_targets, 'a,b,c'),
                (_Assign_targets, 'a =b =c ='),
                (_Assign_targets, 'a = b = c =')),
            (code_as__Assign_targets, (Tuple, '(a) , \\\n # 0\n(b) # 1\n,\n(c) \\'),
                "**SyntaxError**",  # src
                (_Assign_targets, '(a) = \\\n \\\n(b) = \\\n\\\n(c) ='),
                (_Assign_targets, 'a = b = c =')),
            (code_as__Assign_targets, (Tuple, 'a,'),
                (_Assign_targets, 'a,'),
                (_Assign_targets, 'a ='),
                (_Assign_targets, 'a =')),
            (code_as__Assign_targets, (Tuple, '(a,)'),
                (_Assign_targets, '(a,)'),
                (_Assign_targets, 'a ='),
                (_Assign_targets, 'a =')),
            (code_as__Assign_targets, (arguments, '\nb\n,\nc\n,\n'),
                '**SyntaxError**',
                (_Assign_targets, '\\\nb = \\\n\\\nc = \\\n\\\n'),
                (_Assign_targets, 'b = c =')),
            (code_as__Assign_targets, (Tuple, 'a:b, c:d:e'),
                "**SyntaxError**",  # src
                "**NodeError('expecting _Assign_targets, got Tuple, could not coerce')**",
                "**NodeError('expecting _Assign_targets, got Tuple, could not coerce')**"),
            (code_as__Assign_targets, (Tuple, 'a\n,\nb'),
                "**SyntaxError**",  # src
                (_Assign_targets, 'a = \\\n\\\nb ='),
                (_Assign_targets, 'a = b =')),
            (code_as__Assign_targets, (Tuple, '(a)\n,\n(b)'),
                "**SyntaxError**",  # src
                (_Assign_targets, '(a) = \\\n\\\n(b) ='),
                (_Assign_targets, 'a = b =')),
            (code_as__Assign_targets, (List, '[a]'),
                (_Assign_targets, '[a]'),
                (_Assign_targets, 'a ='),
                (_Assign_targets, 'a =')),
            (code_as__Assign_targets, (List, '[\na\n,\nb\n]'),
                (_Assign_targets, '[\na\n,\nb\n]'),
                (_Assign_targets, '\\\na = \\\n\\\nb = \\\n'),
                (_Assign_targets, 'a = b =')),
            (code_as__Assign_targets, (Set, '{a}'),
                "**SyntaxError**",  # src
                (_Assign_targets, 'a ='),
                (_Assign_targets, 'a =')),
            (code_as__Assign_targets, (Set, '{\na\n,\nb\n}'),
                "**SyntaxError**",  # src
                (_Assign_targets, '\\\na = \\\n\\\nb = \\\n'),
                (_Assign_targets, 'a = b =')),
            # (code_as__Assign_targets, (_Assign_targets, 'a = \\\nb ='),
            #     "**ParseError('expecting _Assign_targets, could not parse or coerce')**",
            #     (_Assign_targets, '@a\n@b'),
            #     (_Assign_targets, '@a\n@b')),
            # (code_as__Assign_targets, (_Assign_targets, '\n@a\n@b\n'),
            #     "**ParseError('expecting _Assign_targets, could not parse or coerce')**",
            #     (_Assign_targets, '\n@a\n@b\n'),
            #     (_Assign_targets, '@a\n@b')),
            (code_as__Assign_targets, (_arglikes, '\na\n,\nb\n'),
                "**SyntaxError**",  # src
                (_Assign_targets, '\\\na = \\\n\\\nb = \\\n'),
                (_Assign_targets, 'a = b =')),
            (code_as__Assign_targets, (_arglikes, '\na\n,\n*b\n'),
                "**SyntaxError**",  # src
                (_Assign_targets, '\\\na = \\\n\\\n*b = \\\n'),
                (_Assign_targets, 'a = *b =')),
            (code_as__Assign_targets, (_arglikes, '\na\n,\n*not b\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting _Assign_targets, got _arglikes, could not coerce')**",
                "**NodeError('expecting _Assign_targets, got _arglikes, could not coerce')**"),
            (code_as__Assign_targets, (_arglikes, '\na\n,\nb=c\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting _Assign_targets, got _arglikes, could not coerce')**",
                "**NodeError('expecting _Assign_targets, got _arglikes, could not coerce')**"),
            (code_as__Assign_targets, (_arglikes, '\na\n,\nb=c\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting _Assign_targets, got _arglikes, could not coerce')**",
                "**NodeError('expecting _Assign_targets, got _arglikes, could not coerce')**"),
            # (code_as__Assign_targets, (_Assign_targets, '\nif\na\nif\nb\n'),
            #     '**SyntaxError**',
            #     (_Assign_targets, '\na,\nb\n'),
            #     (_Assign_targets, 'a, b')),
            (code_as__Assign_targets, (_aliases, '\na\n,\nb\n'),
                "**SyntaxError**",  # src
                (_Assign_targets, '\\\na = \\\n\\\nb = \\\n'),
                (_Assign_targets, 'a = b =')),
            (code_as__Assign_targets, (_aliases, 'a as b, c as d'),
                "**SyntaxError**",  # src
                "**NodeError('expecting _Assign_targets, got _aliases, could not coerce')**",
                "**NodeError('expecting _Assign_targets, got _aliases, could not coerce')**"),
            # (code_as__Assign_targets, (_Assign_targets, '\na\n,\nb\n'),
            #     (_Assign_targets, '\na\n,\nb\n'),
            #     (_Assign_targets, '\na\n,\nb\n'),
            #     (_Assign_targets, 'a, b')),
            # (code_as__Assign_targets, (_Assign_targets, 'a as b, c as d'),
            #     (_Assign_targets, 'a as b, c as d'),
            #     "**NodeError('expecting _Assign_targets, got _Assign_targets, could not coerce')**",
            #     "**NodeError('expecting _Assign_targets, got _Assign_targets, could not coerce')**"),
            (code_as__Assign_targets, (MatchSequence, '\na\n,\nb\n'),
                "**SyntaxError**",  # src
                (_Assign_targets, '\\\na = \\\n\\\nb = \\\n'),
                (_Assign_targets, 'a = b =')),
            (code_as__Assign_targets, (MatchSequence, 'a as b, c as d'),
                "**SyntaxError**",  # src
                "**NodeError('expecting _Assign_targets, got MatchSequence, could not coerce')**",
                "**NodeError('expecting _Assign_targets, got MatchSequence, could not coerce')**"),

            (code_as_Tuple, (Tuple, 'a, b'),
                (Tuple, 'a, b'),  # src, FST
                (Tuple, '(a, b)')),  # AST
            (code_as_Tuple, (Tuple, '(a, b)'),
                (Tuple, '(a, b)'),  # src, FST
                (Tuple, '(a, b)')),  # AST
            (code_as_Tuple, (List, '[a, b]'),
                "**ParseError('expecting Tuple, got List')**",  # src
                (Tuple, '(a, b)'),  # FST
                (Tuple, '(a, b)')),  # AST
            (code_as_Tuple, (Starred, '*a'),
                "**ParseError('expecting Tuple, got Starred')**",
                "**NodeError('expecting Tuple, got Starred, could not coerce')**",
                "**NodeError('expecting Tuple, got Starred, could not coerce')**"),
            (code_as_Tuple, (Call, 'f()'),
                "**ParseError('expecting Tuple, got Call')**",  # src
                "**NodeError('expecting Tuple, got Call, could not coerce')**",  # FST
                "**NodeError('expecting Tuple, got Call, could not coerce')**"),  # AST
            (code_as_Tuple, (Name, '#0\n ( a ) #1\n#2'),
                "**ParseError('expecting Tuple, got Name')**",
                "**NodeError('expecting Tuple, got Name, could not coerce')**",  # FST
                "**NodeError('expecting Tuple, got Name, could not coerce')**"),  # AST
            (code_as_Tuple, (Tuple, 'a,b,c'),
                (Tuple, 'a,b,c'),
                (Tuple, '(a, b, c)')),
            (code_as_Tuple, (Tuple, '(a) , \\\n # 0\n(b) # 1\n,\n(c) \\'),
                (Tuple, '(a) , \\\n # 0\n(b) # 1\n,\n(c) \\'),
                (Tuple, '(a, b, c)')),
            (code_as_Tuple, (Tuple, 'a,'),
                (Tuple, 'a,'),
                (Tuple, '(a,)')),
            (code_as_Tuple, (Tuple, '(a,)'),
                (Tuple, '(a,)')),
            (code_as_Tuple, (arguments, '\nb\n,\nc\n,\n'),
                (Tuple, '\nb\n,\nc\n,\n'),
                (Tuple, '(b, c)')),
            (code_as_Tuple, (Tuple, 'a:b, c:d:e'),
                (Tuple, 'a:b, c:d:e')),
            (code_as_Tuple, (Tuple, 'a\n,\nb'),
                (Tuple, 'a\n,\nb'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (Tuple, '(a)\n,\n(b)'),
                (Tuple, '(a)\n,\n(b)'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (List, '[a]'),
                "**ParseError('expecting Tuple, got List')**",
                (Tuple, '(a,)'),
                (Tuple, '(a,)')),
            (code_as_Tuple, (List, '[\na\n,\nb\n]'),
                "**ParseError('expecting Tuple, got List')**",
                (Tuple, '(\na\n,\nb\n)'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (Set, '{a}'),
                "**ParseError('expecting Tuple, got Set')**",
                (Tuple, '(a,)'),
                (Tuple, '(a,)')),
            (code_as_Tuple, (Set, '{\na\n,\nb\n}'),
                "**ParseError('expecting Tuple, got Set')**",
                (Tuple, '(\na\n,\nb\n)'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (_Assign_targets, 'a = \\\nb ='),
                "**SyntaxError**",
                (Tuple, 'a, \\\nb'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (_decorator_list, '\n@a\n@b\n'),
                "**SyntaxError**",
                (Tuple, '(\na,\nb\n)'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (_arglikes, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, '(\na\n,\nb\n)'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (_arglikes, '\na\n,\n*b\n'),
                (Tuple, '\na\n,\n*b\n'),
                (Tuple, '(\na\n,\n*b\n)'),
                (Tuple, '(a, *b)')),
            # (code_as_Tuple, (_arglikes, '\na\n,\n*not b\n'),
            #     (Tuple, '\na\n,\n*not b\n'),
            #     (Tuple, '(\na\n,\n*(not b)\n)'),
            #     (Tuple, '(a, *(not b))')),
            (code_as_Tuple, (_arglikes, '\na\n,\nb=c\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Tuple, got _arglikes, could not coerce, cannot have keyword')**",
                "**NodeError('expecting Tuple, got _arglikes, could not coerce, cannot have keyword')**"),
            (code_as_Tuple, (_arglikes, '\na\n,\nb=c\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Tuple, got _arglikes, could not coerce, cannot have keyword')**",
                "**NodeError('expecting Tuple, got _arglikes, could not coerce, cannot have keyword')**"),
            (code_as_Tuple, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                '**SyntaxError**',
                (Tuple, '(\na,\nb\n)'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (_aliases, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, '(\na\n,\nb\n)'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (_aliases, 'a as b, c as d'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Tuple, got _aliases, could not coerce, alias has asname')**",
                "**NodeError('expecting Tuple, got _aliases, could not coerce, alias has asname')**"),
            # (code_as_Tuple, (Tuple, '\na\n,\nb\n'),
            #     (Tuple, '\na\n,\nb\n'),
            #     (Tuple, '\na\n,\nb\n'),
            #     (Tuple, 'a, b')),
            (code_as_Tuple, (_withitems, 'a as b, c as d'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Tuple, got _withitems, could not coerce, withitem has optional_vars')**",
                "**NodeError('expecting Tuple, got _withitems, could not coerce, withitem has optional_vars')**"),
            (code_as_Tuple, (MatchSequence, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, '(a, b)')),
            (code_as_Tuple, (MatchSequence, 'a as b, c as d'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Tuple, got MatchSequence, could not coerce, has pattern')**",
                "**NodeError('expecting Tuple, got MatchSequence, could not coerce, has pattern')**"),

            (code_as_List, (Tuple, 'a, b'),
                "**SyntaxError**",
                (List, '[a, b]'),
                (List, '[a, b]')),
            (code_as_List, (Tuple, '(a, b)'),
                "**SyntaxError**",
                (List, '[a, b]'),
                (List, '[a, b]')),
            (code_as_List, (List, '[a, b]'),
                (List, '[a, b]')),
            (code_as_List, (Starred, '*a'),
                "**SyntaxError**",
                "**NodeError('expecting List, got Starred, could not coerce')**",
                "**NodeError('expecting List, got Starred, could not coerce')**"),
            (code_as_List, (Call, 'f()'),
                "**SyntaxError**",  # src
                "**NodeError('expecting List, got Call, could not coerce')**",  # FST
                "**NodeError('expecting List, got Call, could not coerce')**"),  # AST
            (code_as_List, (Name, '#0\n ( a ) #1\n#2'),
                "**SyntaxError**",
                "**NodeError('expecting List, got Name, could not coerce')**",  # FST
                "**NodeError('expecting List, got Name, could not coerce')**"),  # AST
            (code_as_List, (Tuple, 'a,b,c'),
                "**SyntaxError**",
                (List, '[a,b,c]'),
                (List, '[a, b, c]')),
            (code_as_List, (Tuple, '(a) , \\\n # 0\n(b) # 1\n,\n(c) \\'),
                "**SyntaxError**",
                (List, '[(a) , \\\n # 0\n(b) # 1\n,\n(c)]'),
                (List, '[a, b, c]')),
            (code_as_List, (Tuple, 'a,'),
                "**SyntaxError**",
                (List, '[a,]'),
                (List, '[a]')),
            (code_as_List, (Tuple, '(a,)'),
                "**SyntaxError**",
                (List, '[a,]'),
                (List, '[a]')),
            (code_as_List, (arguments, '\nb\n,\nc\n,\n'),
                "**SyntaxError**",
                (List, '[\nb\n,\nc\n,\n]'),
                (List, '[b, c]')),
            (code_as_List, (Tuple, 'a:b, c:d:e'),
                "**SyntaxError**",
                "**NodeError('expecting List, got Tuple, could not coerce')**",
                "**NodeError('expecting List, got Tuple, could not coerce')**"),
            (code_as_List, (Tuple, 'a\n,\nb'),
                "**SyntaxError**",
                (List, '[a\n,\nb]'),
                (List, '[a, b]')),
            (code_as_List, (Tuple, '(a)\n,\n(b)'),
                "**SyntaxError**",
                (List, '[(a)\n,\n(b)]'),
                (List, '[a, b]')),
            (code_as_List, (List, '[a]'),
                (List, '[a]')),
            (code_as_List, (List, '[\na\n,\nb\n]'),
                (List, '[\na\n,\nb\n]'),
                (List, '[a, b]')),
            (code_as_List, (Set, '{a}'),
                "**SyntaxError**",
                (List, '[a]'),
                (List, '[a]')),
            (code_as_List, (Set, '{\na\n,\nb\n}'),
                "**SyntaxError**",
                (List, '[\na\n,\nb\n]'),
                (List, '[a, b]')),
            (code_as_List, (_Assign_targets, 'a = \\\nb ='),
                "**SyntaxError**",
                (List, '[a, \\\nb]'),
                (List, '[a, b]')),
            (code_as_List, (_decorator_list, '\n@a\n@b\n'),
                "**SyntaxError**",
                (List, '[\na,\nb\n]'),
                (List, '[a, b]')),
            (code_as_List, (_arglikes, '\na\n,\nb\n'),
                "**SyntaxError**",
                (List, '[\na\n,\nb\n]'),
                (List, '[a, b]')),
            (code_as_List, (_arglikes, '\na\n,\n*b\n'),
                "**SyntaxError**",
                (List, '[\na\n,\n*b\n]'),
                (List, '[a, *b]')),
            (code_as_List, (_arglikes, '\na\n,\n*not b\n'),
                '**SyntaxError**',
                (List, '[\na\n,\n*(not b)\n]'),
                (List, '[a, *(not b)]')),
            (code_as_List, (_arglikes, '\na\n,\nb=c\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting List, got _arglikes, could not coerce')**",
                "**NodeError('expecting List, got _arglikes, could not coerce')**"),
            (code_as_List, (_arglikes, '\na\n,\nb=c\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting List, got _arglikes, could not coerce')**",
                "**NodeError('expecting List, got _arglikes, could not coerce')**"),
            (code_as_List, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                '**SyntaxError**',
                (List, '[\na,\nb\n]'),
                (List, '[a, b]')),
            (code_as_List, (_aliases, '\na\n,\nb\n'),
                '**SyntaxError**',
                (List, '[\na\n,\nb\n]'),
                (List, '[a, b]')),
            (code_as_List, (_aliases, 'a as b, c as d'),
                "**SyntaxError**",  # src
                "**NodeError('expecting List, got _aliases, could not coerce')**",
                "**NodeError('expecting List, got _aliases, could not coerce')**"),
            # (code_as_List, (Tuple, '\na\n,\nb\n'),
            #     (Tuple, '\na\n,\nb\n'),
            #     (Tuple, '\na\n,\nb\n'),
            #     (Tuple, 'a, b')),
            (code_as_List, (_withitems, 'a as b, c as d'),
                "**SyntaxError**",
                "**NodeError('expecting List, got _withitems, could not coerce')**",
                "**NodeError('expecting List, got _withitems, could not coerce')**"),
            (code_as_List, (MatchSequence, '\na\n,\nb\n'),
                "**SyntaxError**",
                (List, '[\na\n,\nb\n]'),
                (List, '[a, b]')),
            (code_as_List, (MatchSequence, 'a as b, c as d'),
                "**SyntaxError**",
                "**NodeError('expecting List, got MatchSequence, could not coerce')**",
                "**NodeError('expecting List, got MatchSequence, could not coerce')**"),

            (code_as_Set, (Tuple, 'a, b'),
                "**SyntaxError**",
                (Set, '{a, b}'),
                (Set, '{a, b}')),
            (code_as_Set, (Tuple, '(a, b)'),
                "**SyntaxError**",
                (Set, '{a, b}'),
                (Set, '{a, b}')),
            (code_as_Set, (List, '[a, b]'),
                "**SyntaxError**",
                (Set, '{a, b}'),
                (Set, '{a, b}')),
            (code_as_Set, (Starred, '*a'),
                "**SyntaxError**",
                "**NodeError('expecting Set, got Starred, could not coerce')**",
                "**NodeError('expecting Set, got Starred, could not coerce')**"),
            (code_as_Set, (Call, 'f()'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Set, got Call, could not coerce')**",  # FST
                "**NodeError('expecting Set, got Call, could not coerce')**"),  # AST
            (code_as_Set, (Name, '#0\n ( a ) #1\n#2'),
                "**SyntaxError**",
                "**NodeError('expecting Set, got Name, could not coerce')**",  # FST
                "**NodeError('expecting Set, got Name, could not coerce')**"),  # AST
            (code_as_Set, (Tuple, 'a,b,c'),
                "**SyntaxError**",
                (Set, '{a,b,c}'),
                (Set, '{a, b, c}')),
            (code_as_Set, (Tuple, '(a) , \\\n # 0\n(b) # 1\n,\n(c) \\'),
                "**SyntaxError**",
                (Set, '{(a) , \\\n # 0\n(b) # 1\n,\n(c)}'),
                (Set, '{a, b, c}')),
            (code_as_Set, (Tuple, 'a,'),
                "**SyntaxError**",
                (Set, '{a,}'),
                (Set, '{a}')),
            (code_as_Set, (Tuple, '(a,)'),
                "**SyntaxError**",
                (Set, '{a,}'),
                (Set, '{a}')),
            (code_as_Set, (arguments, '\nb\n,\nc\n,\n'),
                "**SyntaxError**",
                (Set, '{\nb\n,\nc\n,\n}'),
                (Set, '{b, c}')),
            (code_as_Set, (Tuple, 'a:b, c:d:e'),
                "**SyntaxError**",
                "**NodeError('expecting Set, got Tuple, could not coerce')**",
                "**NodeError('expecting Set, got Tuple, could not coerce')**"),
            (code_as_Set, (Tuple, 'a\n,\nb'),
                "**SyntaxError**",
                (Set, '{a\n,\nb}'),
                (Set, '{a, b}')),
            (code_as_Set, (Tuple, '(a)\n,\n(b)'),
                "**SyntaxError**",
                (Set, '{(a)\n,\n(b)}'),
                (Set, '{a, b}')),
            (code_as_Set, (List, '[a]'),
                "**SyntaxError**",
                (Set, '{a}'),
                (Set, '{a}')),
            (code_as_Set, (List, '[\na\n,\nb\n]'),
                "**SyntaxError**",
                (Set, '{\na\n,\nb\n}'),
                (Set, '{a, b}')),
            (code_as_Set, (Set, '{a}'),
                (Set, '{a}')),
            (code_as_Set, (Set, '{\na\n,\nb\n}'),
                (Set, '{\na\n,\nb\n}'),
                (Set, '{a, b}')),
            (code_as_Set, (_Assign_targets, 'a = \\\nb ='),
                "**SyntaxError**",
                (Set, '{a, \\\nb}'),
                (Set, '{a, b}')),
            (code_as_Set, (_decorator_list, '\n@a\n@b\n'),
                "**SyntaxError**",
                (Set, '{\na,\nb\n}'),
                (Set, '{a, b}')),
            (code_as_Set, (_arglikes, '\na\n,\nb\n'),
                "**SyntaxError**",
                (Set, '{\na\n,\nb\n}'),
                (Set, '{a, b}')),
            (code_as_Set, (_arglikes, '\na\n,\n*b\n'),
                "**SyntaxError**",
                (Set, '{\na\n,\n*b\n}'),
                (Set, '{a, *b}')),
            (code_as_Set, (_arglikes, '\na\n,\n*not b\n'),
                '**SyntaxError**',
                (Set, '{\na\n,\n*(not b)\n}'),
                (Set, '{a, *(not b)}')),
            (code_as_Set, (_arglikes, '\na\n,\nb=c\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Set, got _arglikes, could not coerce')**",
                "**NodeError('expecting Set, got _arglikes, could not coerce')**"),
            (code_as_Set, (_arglikes, '\na\n,\nb=c\n'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Set, got _arglikes, could not coerce')**",
                "**NodeError('expecting Set, got _arglikes, could not coerce')**"),
            (code_as_Set, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                '**SyntaxError**',
                (Set, '{\na,\nb\n}'),
                (Set, '{a, b}')),
            (code_as_Set, (_aliases, '\na\n,\nb\n'),
                '**SyntaxError**',
                (Set, '{\na\n,\nb\n}'),
                (Set, '{a, b}')),
            (code_as_Set, (_aliases, 'a as b, c as d'),
                "**SyntaxError**",  # src
                "**NodeError('expecting Set, got _aliases, could not coerce')**",
                "**NodeError('expecting Set, got _aliases, could not coerce')**"),
            # (code_as_Set, (Tuple, '\na\n,\nb\n'),
            #     (Tuple, '\na\n,\nb\n'),
            #     (Tuple, '\na\n,\nb\n'),
            #     (Tuple, 'a, b')),
            (code_as_Set, (_withitems, 'a as b, c as d'),
                "**SyntaxError**",
                "**NodeError('expecting Set, got _withitems, could not coerce')**",
                "**NodeError('expecting Set, got _withitems, could not coerce')**"),
            (code_as_Set, (MatchSequence, '\na\n,\nb\n'),
                "**SyntaxError**",
                (Set, '{\na\n,\nb\n}'),
                (Set, '{a, b}')),
            (code_as_Set, (MatchSequence, 'a as b, c as d'),
                "**SyntaxError**",
                "**NodeError('expecting Set, got MatchSequence, could not coerce')**",
                "**NodeError('expecting Set, got MatchSequence, could not coerce')**"),

            (code_as__decorator_list, (Name, 'a'), (_decorator_list, '@a')),
            (code_as__decorator_list, (Call, 'f()'), (_decorator_list, '@f()')),
            (code_as__decorator_list, (Name, '#0\n ( a ) #1\n#2'),
                (_decorator_list, '#0\n@ ( a ) #1\n#2'),
                (_decorator_list, '@a')),
            (code_as__decorator_list, (Tuple, 'a,b,c'),
                (_decorator_list, '@(a,b,c)'),
                (_decorator_list, '@a\n@b\n@c'),
                (_decorator_list, '@a\n@b\n@c')),
            (code_as__decorator_list, (Starred, '*a'),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                "**NodeError('expecting _decorator_list, got Starred, could not coerce')**",
                "**NodeError('expecting _decorator_list, got Starred, could not coerce')**"),
            (code_as__decorator_list, (Tuple, '(a) , \\\n # 0\n(b) # 1\n,\n(c) \\'),
                (_decorator_list, '@((a) , \\\n # 0\n(b) # 1\n,\n(c))'),
                (_decorator_list, '@(a)  \\\n # 0\n@(b) # 1\n\n@(c)'),
                (_decorator_list, '@a\n@b\n@c')),
            (code_as__decorator_list, (Tuple, 'a,'),
                (_decorator_list, '@(a,)'),
                (_decorator_list, '@a'),
                (_decorator_list, '@a')),
            (code_as__decorator_list, (Tuple, '(a,)'),
                (_decorator_list, '@(a,)'),
                (_decorator_list, '@a'),
                (_decorator_list, '@a')),
            (code_as__decorator_list, (arguments, '\nb\n,\nc\n,\n'),
                (_decorator_list, '@(\nb\n,\nc\n,\n)'),
                (_decorator_list, '\n@b\n\n@c\n\n'),
                (_decorator_list, '@b\n@c')),
            (code_as__decorator_list, (Tuple, 'a:b, c:d:e'),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                "**NodeError('expecting _decorator_list, got Tuple, could not coerce')**",
                "**NodeError('expecting _decorator_list, got Tuple, could not coerce')**"),
            (code_as__decorator_list, (Tuple, 'a\n,\nb'),
                (_decorator_list, '@(a\n,\nb)'),
                (_decorator_list, '@a\n\n@b'),
                (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (Tuple, '(a)\n,\n(b)'),
                (_decorator_list, '@((a)\n,\n(b))'),
                (_decorator_list, '@(a)\n\n@(b)'),
                (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (List, '[a]'),
                (_decorator_list, '@[a]'),
                (_decorator_list, '@a'),
                (_decorator_list, '@a')),
            (code_as__decorator_list, (List, '[\na\n,\nb\n]'),
                (_decorator_list, '@[\na\n,\nb\n]'),
                (_decorator_list, '\n@a\n\n@b\n'),
                (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (Set, '{a}'),
                (_decorator_list, '@{a}'),
                (_decorator_list, '@a'),
                (_decorator_list, '@a')),
            (code_as__decorator_list, (Set, '{\na\n,\nb\n}'),
                (_decorator_list, '@{\na\n,\nb\n}'),
                (_decorator_list, '\n@a\n\n@b\n'),
                (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (_Assign_targets, 'a = \\\nb ='),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                (_decorator_list, '@a\n@b'),
                (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (_Assign_targets, 'x, y ='),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                (_decorator_list, '@(x, y)'),
                (_decorator_list, '@(x, y)')),
            (code_as__decorator_list, (_Assign_targets, '\\\na = x, y = b ='),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                (_decorator_list, '@a\n@(x, y)\n@b'),
                (_decorator_list, '@a\n@(x, y)\n@b')),
            # (code_as__decorator_list, (_decorator_list, '\n@a\n@b\n'),
            #     "**ParseError('expecting _decorator_list, could not parse or coerce')**",
            #     (_decorator_list, '\n@a\n@b\n'),
            #     (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (_arglikes, '\na\n,\nb\n'),
                (_decorator_list, '@(\na\n,\nb\n)'),
                (_decorator_list, '\n@a\n\n@b\n'),
                (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (_arglikes, '\na\n,\n*b\n'),
                (_decorator_list, '@(\na\n,\n*b\n)'),
                "**NodeError('expecting _decorator_list, got _arglikes, could not coerce')**",
                "**NodeError('expecting _decorator_list, got _arglikes, could not coerce')**"),
            (code_as__decorator_list, (_arglikes, '\na\n,\n*not b\n'),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                "**NodeError('expecting _decorator_list, got _arglikes, could not coerce')**",
                "**NodeError('expecting _decorator_list, got _arglikes, could not coerce')**"),
            (code_as__decorator_list, (_arglikes, '\na\n,\nb=c\n'),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                "**NodeError('expecting _decorator_list, got _arglikes, could not coerce')**",
                "**NodeError('expecting _decorator_list, got _arglikes, could not coerce')**"),
            (code_as__decorator_list, (_arglikes, '\na\n,\nb=c\n'),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                "**NodeError('expecting _decorator_list, got _arglikes, could not coerce')**",
                "**NodeError('expecting _decorator_list, got _arglikes, could not coerce')**"),
            # (code_as__decorator_list, (_decorator_list, '\nif\na\nif\nb\n'),
            #     '**SyntaxError**',
            #     (_decorator_list, '\na,\nb\n'),
            #     (_decorator_list, 'a, b')),
            (code_as__decorator_list, (_aliases, '\na\n,\nb\n'),
                (_decorator_list, '@(\na\n,\nb\n)'),
                (_decorator_list, '\n@a\n\n@b\n'),
                (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (_aliases, 'a as b, c as d'),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                "**NodeError('expecting _decorator_list, got _aliases, could not coerce')**",
                "**NodeError('expecting _decorator_list, got _aliases, could not coerce')**"),
            # (code_as__decorator_list, (_decorator_list, '\na\n,\nb\n'),
            #     (_decorator_list, '\na\n,\nb\n'),
            #     (_decorator_list, '\na\n,\nb\n'),
            #     (_decorator_list, 'a, b')),
            # (code_as__decorator_list, (_decorator_list, 'a as b, c as d'),
            #     (_decorator_list, 'a as b, c as d'),
            #     "**NodeError('expecting _decorator_list, got _decorator_list, could not coerce')**",
            #     "**NodeError('expecting _decorator_list, got _decorator_list, could not coerce')**"),
            (code_as__decorator_list, (MatchSequence, '\na\n,\nb\n'),
                (_decorator_list, '@(\na\n,\nb\n)'),
                (_decorator_list, '\n@a\n\n@b\n'),
                (_decorator_list, '@a\n@b')),
            (code_as__decorator_list, (MatchSequence, 'a as b, c as d'),
                "**ParseError('expecting _decorator_list, could not parse or coerce')**",
                "**NodeError('expecting _decorator_list, got MatchSequence, could not coerce')**",
                "**NodeError('expecting _decorator_list, got MatchSequence, could not coerce')**"),

            (code_as__arglikes, (Name, 'a'), (_arglikes, 'a')),
            (code_as__arglikes, (Call, 'f()'), (_arglikes, 'f()')),
            (code_as__arglikes, (Name, '#0\n ( a ) #1\n#2'),
                (_arglikes, '#0\n ( a ) #1\n#2'),
                (_arglikes, 'a')),
            (code_as__arglikes, (Tuple, 'a,'),
                (_arglikes, 'a,'),
                (_arglikes, 'a,'),
                (_arglikes, 'a')),
            (code_as__arglikes, (Tuple, '(a,)'),
                (_arglikes, '(a,)'),
                (_arglikes, 'a,'),
                (_arglikes, 'a')),
            (code_as__arglikes, (arguments, '\n*\nb\n,\nc\n,\n'),
                (_arglikes, '\n*\nb\n,\nc\n,\n'),
                (_arglikes, '\n*\nb\n,\nc\n,\n'),
                (_arglikes, '*b, c')),
            (code_as__arglikes, (Tuple, '(((a).b).c), d'),
                (_arglikes, '(((a).b).c), d'),
                (_arglikes, '(((a).b).c), d'),
                (_arglikes, 'a.b.c, d')),
            (code_as__arglikes, (Tuple, 'a:b, c:d:e'),
                "**SyntaxError**",
                "**NodeError('expecting _arglikes, got Tuple, could not coerce')**",
                "**NodeError('expecting _arglikes, got Tuple, could not coerce')**"),
            (code_as__arglikes, (Tuple, 'a\n,\nb'),
                (_arglikes, 'a\n,\nb'),
                (_arglikes, 'a\n,\nb'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (List, '[a]'),
                (_arglikes, '[a]'),
                (_arglikes, 'a'),
                (_arglikes, 'a')),
            (code_as__arglikes, (List, '[\na\n,\nb\n]'),
                (_arglikes, '[\na\n,\nb\n]'),
                (_arglikes, '\na\n,\nb\n'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (Set, '{a}'),
                (_arglikes, '{a}'),
                (_arglikes, 'a'),
                (_arglikes, 'a')),
            (code_as__arglikes, (Set, '{\na\n,\nb\n}'),
                (_arglikes, '{\na\n,\nb\n}'),
                (_arglikes, '\na\n,\nb\n'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (_Assign_targets, 'a = \\\nb ='),
                '**SyntaxError**',
                (_arglikes, 'a, \\\nb'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (_decorator_list, '\n@a\n@b\n'),
                '**SyntaxError**',
                (_arglikes, '\na,\nb\n'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                '**SyntaxError**',
                (_arglikes, '\na,\nb\n'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (_aliases, '\na\n,\nb\n'),
                (_arglikes, '\na\n,\nb\n'),
                (_arglikes, '\na\n,\nb\n'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (_aliases, 'a as b, c as d'),
                '**SyntaxError**',
                "**NodeError('expecting _arglikes, got _aliases, could not coerce')**",
                "**NodeError('expecting _arglikes, got _aliases, could not coerce')**"),
            (code_as__arglikes, (_withitems, '\na\n,\nb\n'),
                (_arglikes, '\na\n,\nb\n'),
                (_arglikes, '\na\n,\nb\n'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (_withitems, 'a as b, c as d'),
                '**SyntaxError**',
                "**NodeError('expecting _arglikes, got _withitems, could not coerce')**",
                "**NodeError('expecting _arglikes, got _withitems, could not coerce')**"),
            (code_as__arglikes, (MatchSequence, '\na\n,\nb\n'),
                (_arglikes, '\na\n,\nb\n'),
                (_arglikes, '\na\n,\nb\n'),
                (_arglikes, 'a, b')),
            (code_as__arglikes, (MatchSequence, 'a as b, c as d'),
                '**SyntaxError**',
                "**NodeError('expecting _arglikes, got MatchSequence, could not coerce')**",
                "**NodeError('expecting _arglikes, got MatchSequence, could not coerce')**"),

            (code_as__comprehensions, (comprehension, 'for a in a'), (_comprehensions, 'for a in a')),
            (code_as__comprehensions, (comprehension, '#0\n for a in a #1\n#2'),
                (_comprehensions, '#0\n for a in a #1\n#2'),
                (_comprehensions, 'for a in a')),

            (code_as__comprehension_ifs, (Name, 'a'), (_comprehension_ifs, 'if a')),
            (code_as__comprehension_ifs, (Call, 'f()'), (_comprehension_ifs, 'if f()')),
            (code_as__comprehension_ifs, (Name, '#0\n ( a ) #1\n#2'),
                (_comprehension_ifs, '#0\n if ( a ) #1\n#2'),
                (_comprehension_ifs, 'if a')),
            (code_as__comprehension_ifs, (Tuple, '# test\na, # 0\nb, \\\nc'),
                (_comprehension_ifs, 'if (# test\na, # 0\nb, \\\nc)'),
                (_comprehension_ifs, '# test\nif a # 0\nif b \\\nif c'),
                (_comprehension_ifs, 'if a if b if c')),
            (code_as__comprehension_ifs, (Tuple, 'a,b,c'),
                (_comprehension_ifs, 'if (a,b,c)'),
                (_comprehension_ifs, 'if a if b if c'),
                (_comprehension_ifs, 'if a if b if c')),
            (code_as__comprehension_ifs, (Starred, '*a'),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                "**NodeError('expecting _comprehension_ifs, got Starred, could not coerce')**",
                "**NodeError('expecting _comprehension_ifs, got Starred, could not coerce')**"),
            (code_as__comprehension_ifs, (Tuple, 'a,'),
                (_comprehension_ifs, 'if (a,)'),
                (_comprehension_ifs, 'if a'),
                (_comprehension_ifs, 'if a')),
            (code_as__comprehension_ifs, (Tuple, '(a,)'),
                (_comprehension_ifs, 'if (a,)'),
                (_comprehension_ifs, 'if a'),
                (_comprehension_ifs, 'if a')),
            (code_as__comprehension_ifs, (arguments, '\nb\n,\nc\n,\n'),
                (_comprehension_ifs, 'if (\nb\n,\nc\n,\n)'),
                (_comprehension_ifs, '\nif b\n\nif c\n\n'),
                (_comprehension_ifs, 'if b if c')),
            (code_as__comprehension_ifs, (Tuple, 'a:b, c:d:e'),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                "**NodeError('expecting _comprehension_ifs, got Tuple, could not coerce')**",
                "**NodeError('expecting _comprehension_ifs, got Tuple, could not coerce')**"),
            (code_as__comprehension_ifs, (Tuple, 'a\n,\nb'),
                (_comprehension_ifs, 'if (a\n,\nb)'),
                (_comprehension_ifs, 'if a\n\nif b'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (Tuple, '(a)\n,\n(b)'),
                (_comprehension_ifs, 'if ((a)\n,\n(b))'),
                (_comprehension_ifs, 'if (a)\n\nif (b)'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (List, '[a]'),
                (_comprehension_ifs, 'if [a]'),
                (_comprehension_ifs, 'if a'),
                (_comprehension_ifs, 'if a')),
            (code_as__comprehension_ifs, (List, '[\na\n,\nb\n]'),
                (_comprehension_ifs, 'if [\na\n,\nb\n]'),
                (_comprehension_ifs, '\nif a\n\nif b\n'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (Set, '{a}'),
                (_comprehension_ifs, 'if {a}'),
                (_comprehension_ifs, 'if a'),
                (_comprehension_ifs, 'if a')),
            (code_as__comprehension_ifs, (Set, '{\na\n,\nb\n}'),
                (_comprehension_ifs, 'if {\na\n,\nb\n}'),
                (_comprehension_ifs, '\nif a\n\nif b\n'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (_Assign_targets, 'a = \\\nb ='),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                (_comprehension_ifs, 'if a \\\nif b'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (_decorator_list, '\n@a\n@b\n'),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                (_comprehension_ifs, '\nif a\nif b\n'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (_arglikes, '\na\n,\nb\n'),
                (_comprehension_ifs, 'if (\na\n,\nb\n)'),
                (_comprehension_ifs, '\nif a\n\nif b\n'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (_arglikes, '\na\n,\n*b\n'),
                (_comprehension_ifs, 'if (\na\n,\n*b\n)'),
                "**NodeError('expecting _comprehension_ifs, got _arglikes, could not coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _arglikes, could not coerce')**"),
            (code_as__comprehension_ifs, (_arglikes, '\na\n,\n*not b\n'),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _arglikes, could not coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _arglikes, could not coerce')**"),
            (code_as__comprehension_ifs, (_arglikes, '\na\n,\nb=c\n'),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _arglikes, could not coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _arglikes, could not coerce')**"),
            (code_as__comprehension_ifs, (_arglikes, '\na\n,\nb=c\n'),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _arglikes, could not coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _arglikes, could not coerce')**"),
            # (code_as__comprehension_ifs, (_comprehension_ifs, '\nif\na\nif\nb\n'),
            #     '**SyntaxError**',
            #     (_comprehension_ifs, '\na,\nb\n'),
            #     (_comprehension_ifs, 'a, b')),
            (code_as__comprehension_ifs, (_aliases, '\na\n,\nb\n'),
                (_comprehension_ifs, 'if (\na\n,\nb\n)'),
                (_comprehension_ifs, '\nif a\n\nif b\n'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (_aliases, 'a as b, c as d'),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _aliases, could not coerce')**",
                "**NodeError('expecting _comprehension_ifs, got _aliases, could not coerce')**"),
            # (code_as__comprehension_ifs, (_comprehension_ifs, '\na\n,\nb\n'),
            #     (_comprehension_ifs, '\na\n,\nb\n'),
            #     (_comprehension_ifs, '\na\n,\nb\n'),
            #     (_comprehension_ifs, 'a, b')),
            # (code_as__comprehension_ifs, (_comprehension_ifs, 'a as b, c as d'),
            #     (_comprehension_ifs, 'a as b, c as d'),
            #     "**NodeError('expecting _comprehension_ifs, got _comprehension_ifs, could not coerce')**",
            #     "**NodeError('expecting _comprehension_ifs, got _comprehension_ifs, could not coerce')**"),
            (code_as__comprehension_ifs, (MatchSequence, '\na\n,\nb\n'),
                (_comprehension_ifs, 'if (\na\n,\nb\n)'),
                (_comprehension_ifs, '\nif a\n\nif b\n'),
                (_comprehension_ifs, 'if a if b')),
            (code_as__comprehension_ifs, (MatchSequence, 'a as b, c as d'),
                "**ParseError('expecting _comprehension_ifs, could not parse or coerce')**",
                "**NodeError('expecting _comprehension_ifs, got MatchSequence, could not coerce')**",
                "**NodeError('expecting _comprehension_ifs, got MatchSequence, could not coerce')**"),

            (code_as_arguments, (Tuple, 'a,'),
                (arguments, 'a,'),
                (arguments, 'a,'),
                (arguments, 'a,')),
            (code_as_arguments, (Tuple, 'a, b'),
                (arguments, 'a, b'),
                (arguments, 'a, b'),
                (arguments, 'a, b')),
            (code_as_arguments, (Tuple, 'a, b.c.d.e'),
                "**SyntaxError**",
                "**NodeError('expecting arguments, got Tuple, could not coerce')**",
                "**NodeError('expecting arguments, got Tuple, could not coerce')**"),
            (code_as_arguments, (Tuple, '(a,)'),
                "**SyntaxError**",
                (arguments, 'a,'),
                (arguments, 'a,')),
            (code_as_arguments, (arguments, '\nb\n,\nc\n,\n'),
                (arguments, '\nb\n,\nc\n,\n'),
                (arguments, '\nb\n,\nc\n,\n'),
                (arguments, 'b, c')),
            (code_as_arguments, (Tuple, 'a:b, c:d:e'),
                "**SyntaxError**",
                "**NodeError('expecting arguments, got Tuple, could not coerce')**",
                "**NodeError('expecting arguments, got Tuple, could not coerce')**"),
            (code_as_arguments, (Tuple, 'a\n,\nb'),
                (arguments, 'a\n,\nb'),
                (arguments, 'a\n,\nb'),
                (arguments, 'a, b')),
            (code_as_arguments, (Tuple, '(a)\n,\n(b)'),
                "**SyntaxError**",
                (arguments, 'a\n,\nb'),
                (arguments, 'a, b')),
            (code_as_arguments, (List, '[a]'),
                "**SyntaxError**",
                (arguments, 'a'),
                (arguments, 'a,')),
            (code_as_arguments, (List, '[\na\n,\nb\n]'),
                "**SyntaxError**",
                (arguments, '\na\n,\nb\n'),
                (arguments, 'a, b')),
            (code_as_arguments, (Set, '{a}'),
                "**SyntaxError**",
                (arguments, 'a'),
                (arguments, 'a,')),
            (code_as_arguments, (Set, '{\na\n,\nb\n}'),
                "**SyntaxError**",
                (arguments, '\na\n,\nb\n'),
                (arguments, 'a, b')),
            (code_as_arguments, (_Assign_targets, 'a = \\\nb ='),
                '**SyntaxError**',
                (arguments, 'a, \\\nb'),
                (arguments, 'a, b')),
            (code_as_arguments, (_decorator_list, '\n@a\n@b\n'),
                '**SyntaxError**',
                (arguments, '\na,\nb\n'),
                (arguments, 'a, b')),
            (code_as_arguments, (_arglikes, '\na\n,\nb\n'),
                (arguments, '\na\n,\nb\n'),
                (arguments, '\na\n,\nb\n'),
                (arguments, 'a, b')),
            (code_as_arguments, (_arglikes, '\na\n,\n*b\n'),
                (arguments, '\na\n,\n*b\n'),
                (arguments, '\na\n,\n*b\n'),
                (arguments, 'a, *b')),
            (code_as_arguments, (_arglikes, '\na\n,\n*not b\n'),
                '**SyntaxError**',
                "**NodeError('expecting arguments, got _arglikes, could not coerce')**",
                "**NodeError('expecting arguments, got _arglikes, could not coerce')**"),
            (code_as_arguments, (_arglikes, '\na\n,\nb=c\n'),
                (arguments, '\na\n,\nb=c\n'),
                "**NodeError('expecting arguments, got _arglikes, could not coerce')**",
                "**NodeError('expecting arguments, got _arglikes, could not coerce')**"),
            (code_as_arguments, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                '**SyntaxError**',
                (arguments, '\na,\nb\n'),
                (arguments, 'a, b')),
            # (code_as_arguments, (arguments, '\na\n,\nb\n'),
            #     (arguments, '\na\n,\nb\n'),
            #     (arguments, '\na\n,\nb\n'),
            #     (arguments, 'a, b')),
            # (code_as_arguments, (arguments, 'a as b, c as d'),
            #     (arguments, 'a as b, c as d'),
            #     "**NodeError('expecting arguments, got arguments, could not coerce')**",
            #     "**NodeError('expecting arguments, got arguments, could not coerce')**"),
            # (code_as_arguments, (arguments, '\na\n,\nb\n'),
            #     (arguments, '\na\n,\nb\n'),
            #     (arguments, '\na\n,\nb\n'),
            #     (arguments, 'a, b')),
            # (code_as_arguments, (arguments, 'a as b, c as d'),
            #     (arguments, 'a as b, c as d'),
            #     "**NodeError('expecting arguments, got arguments, could not coerce')**",
            #     "**NodeError('expecting arguments, got arguments, could not coerce')**"),
            (code_as_arguments, (MatchSequence, '\na\n,\nb\n'),
                (arguments, '\na\n,\nb\n'),
                (arguments, '\na\n,\nb\n'),
                (arguments, 'a, b')),
            (code_as_arguments, (MatchSequence, 'a as b, c as d'),
                '**SyntaxError**',
                "**NodeError('expecting arguments, got MatchSequence, could not coerce')**",
                "**NodeError('expecting arguments, got MatchSequence, could not coerce')**"),

            (code_as_alias, (Name, 'a'), (alias, 'a')),
            (code_as_alias, (Attribute, 'a.b'), (alias, 'a.b')),
            (code_as_alias, (Mult, '*'),
                (alias, '*'),
                "**NodeError('expecting alias, got Mult, could not coerce')**",
                "**NodeError('expecting alias, got Mult, could not coerce')**"),
            (code_as_alias, (Subscript, 'a[b]'),
                "**SyntaxError**",
                "**NodeError('expecting alias, got Subscript, could not coerce')**",
                "**NodeError('expecting alias, got Subscript, could not coerce')**"),
            # (code_as_alias, (Name, '#0\n ( a ) #1\n#2'), (alias, 'a')),
            (code_as_alias, (Name, '#0\n ( a ) #1\n#2'),
                '**SyntaxError**',
                (alias, 'a'),
                (alias, 'a')),

            (code_as__aliases, (Name, 'a'), (_aliases, 'a')),
            (code_as__aliases, (Attribute, 'a.b'), (_aliases, 'a.b')),
            (code_as__aliases, (Mult, '*'),
                (_aliases, '*'),
                "**NodeError('expecting _aliases, got Mult, could not coerce')**",
                "**NodeError('expecting _aliases, got Mult, could not coerce')**"),
            (code_as__aliases, (Subscript, 'a[b]'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got Subscript, could not coerce')**",
                "**NodeError('expecting _aliases, got Subscript, could not coerce')**"),
            # (code_as__aliases, (Name, '#0\n ( a ) #1\n#2'), (_aliases, 'a')),
            (code_as__aliases, (Name, '#0\n ( a ) #1\n#2'),
                '**SyntaxError**',
                (_aliases, 'a'),
                (_aliases, 'a')),
            (code_as__aliases, (alias, 'a'), (_aliases, 'a')),
            (code_as__aliases, (alias, 'a as b'), (_aliases, 'a as b')),
            (code_as__aliases, (alias, 'a.b'), (_aliases, 'a.b')),
            (code_as__aliases, (alias, 'a.b as c'), (_aliases, 'a.b as c')),
            (code_as__aliases, (alias, '*'), (_aliases, '*')),
            (code_as__aliases, (Tuple, 'a,'),
                "**SyntaxError**",
                (_aliases, 'a'),
                (_aliases, 'a')),
            (code_as__aliases, (Tuple, 'a, b'),
                (_aliases, 'a, b'),
                (_aliases, 'a, b'),
                (_aliases, 'a, b')),
            (code_as__aliases, (Tuple, 'a, b.c.d.e'),
                (_aliases, 'a, b.c.d.e'),
                (_aliases, 'a, b.c.d.e'),
                (_aliases, 'a, b.c.d.e')),
            (code_as__aliases, (Tuple, '(((a).b).c), d'),
                "**SyntaxError**",
                (_aliases, 'a.b.c, d'),
                (_aliases, 'a.b.c, d')),
            (code_as__aliases, (Tuple, 'a, b().c.d.e'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got Tuple, could not coerce')**",
                "**NodeError('expecting _aliases, got Tuple, could not coerce')**"),
            (code_as__aliases, (Tuple, '(a,)'),
                "**SyntaxError**",
                (_aliases, 'a'),
                (_aliases, 'a')),
            (code_as__aliases, (arguments, '\nb\n,\nc\n,\n'),
                "**SyntaxError**",
                (_aliases, '\nb\n,\nc\n\n'),
                (_aliases, 'b, c')),
            (code_as__aliases, (Tuple, 'a:b, c:d:e'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got Tuple, could not coerce')**",
                "**NodeError('expecting _aliases, got Tuple, could not coerce')**"),
            (code_as__aliases, (Tuple, 'a\n,\nb'),
                (_aliases, 'a\n,\nb'),
                (_aliases, 'a\n,\nb'),
                (_aliases, 'a, b')),
            (code_as__aliases, (Tuple, '(a)\n,\n(b)'),
                "**SyntaxError**",
                (_aliases, 'a\n,\nb'),
                (_aliases, 'a, b')),
            (code_as__aliases, (List, '[a]'),
                "**SyntaxError**",
                (_aliases, 'a'),
                (_aliases, 'a')),
            (code_as__aliases, (List, '[\na\n,\nb\n]'),
                "**SyntaxError**",
                (_aliases, '\na\n,\nb\n'),
                (_aliases, 'a, b')),
            (code_as__aliases, (Set, '{a}'),
                "**SyntaxError**",
                (_aliases, 'a'),
                (_aliases, 'a')),
            (code_as__aliases, (Set, '{\na\n,\nb\n}'),
                "**SyntaxError**",
                (_aliases, '\na\n,\nb\n'),
                (_aliases, 'a, b')),
            (code_as__aliases, (_Assign_targets, 'a = \\\nb ='),
                '**SyntaxError**',
                (_aliases, 'a, \\\nb'),
                (_aliases, 'a, b')),
            (code_as__aliases, (_decorator_list, '\n@a\n@b\n'),
                '**SyntaxError**',
                (_aliases, '\na,\nb\n'),
                (_aliases, 'a, b')),
            (code_as__aliases, (_arglikes, '\na\n,\nb\n'),
                (_aliases, '\na\n,\nb\n'),
                (_aliases, '\na\n,\nb\n'),
                (_aliases, 'a, b')),
            (code_as__aliases, (_arglikes, '\na\n,\n*b\n'),
                '**SyntaxError**',
                "**NodeError('expecting _aliases, got _arglikes, could not coerce')**",
                "**NodeError('expecting _aliases, got _arglikes, could not coerce')**"),
            # (code_as__aliases, (_arglikes, '\na\n,\n*not b\n'),
            #     '**SyntaxError**',
            #     (_aliases, '\na\n,\n*(not b)\n'),
            #     (_aliases, 'a, *(not b)')),
            (code_as__aliases, (_arglikes, '\na\n,\nb=c\n'),
                '**SyntaxError**',
                "**NodeError('expecting _aliases, got _arglikes, could not coerce')**",
                "**NodeError('expecting _aliases, got _arglikes, could not coerce')**"),
            (code_as__aliases, (_arglikes, '\na\n,\nb=c\n'),
                '**SyntaxError**',
                "**NodeError('expecting _aliases, got _arglikes, could not coerce')**",
                "**NodeError('expecting _aliases, got _arglikes, could not coerce')**"),
            (code_as__aliases, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                '**SyntaxError**',
                (_aliases, '\na,\nb\n'),
                (_aliases, 'a, b')),
            # (code_as__aliases, (_aliases, '\na\n,\nb\n'),
            #     (_aliases, '\na\n,\nb\n'),
            #     (_aliases, '\na\n,\nb\n'),
            #     (_aliases, 'a, b')),
            # (code_as__aliases, (_aliases, 'a as b, c as d'),
            #     (_aliases, 'a as b, c as d'),
            #     "**NodeError('expecting _aliases, got _aliases, could not coerce')**",
            #     "**NodeError('expecting _aliases, got _aliases, could not coerce')**"),
            # (code_as__aliases, (_aliases, '\na\n,\nb\n'),
            #     (_aliases, '\na\n,\nb\n'),
            #     (_aliases, '\na\n,\nb\n'),
            #     (_aliases, 'a, b')),
            # (code_as__aliases, (_aliases, 'a as b, c as d'),
            #     (_aliases, 'a as b, c as d'),
            #     "**NodeError('expecting _aliases, got _aliases, could not coerce')**",
            #     "**NodeError('expecting _aliases, got _aliases, could not coerce')**"),
            (code_as__aliases, (MatchSequence, '\na\n,\nb\n'),
                (_aliases, '\na\n,\nb\n'),
                (_aliases, '\na\n,\nb\n'),
                (_aliases, 'a, b')),
            (code_as__aliases, (MatchSequence, 'a as b, c as d'),
                (_aliases, 'a as b, c as d'),
                "**NodeError('expecting _aliases, got MatchSequence, could not coerce')**",
                "**NodeError('expecting _aliases, got MatchSequence, could not coerce')**"),

            (code_as_Import_name, (Name, 'a'), (alias, 'a')),
            (code_as_Import_name, (Attribute, 'a.b'), (alias, 'a.b')),
            (code_as_Import_name, (Mult, '*'),
                "**SyntaxError**",
                "**NodeError('expecting alias, got Mult, could not coerce')**",
                "**NodeError('expecting alias, got Mult, could not coerce')**"),
            (code_as_Import_name, (Subscript, 'a[b]'),
                "**SyntaxError**",
                "**NodeError('expecting alias, got Subscript, could not coerce')**",
                "**NodeError('expecting alias, got Subscript, could not coerce')**"),
            # (code_as_Import_name, (Name, '#0\n ( a ) #1\n#2'), (alias, 'a')),
            (code_as_Import_name, (Name, '#0\n ( a ) #1\n#2'),
                '**SyntaxError**',
                (alias, 'a'),
                (alias, 'a')),

            (code_as__Import_names, (Name, 'a'), (_aliases, 'a')),
            (code_as__Import_names, (Attribute, 'a.b'), (_aliases, 'a.b')),
            (code_as__Import_names, (Mult, '*'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got Mult, could not coerce')**",
                "**NodeError('expecting _aliases, got Mult, could not coerce')**"),
            (code_as__Import_names, (Subscript, 'a[b]'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got Subscript, could not coerce')**",
                "**NodeError('expecting _aliases, got Subscript, could not coerce')**"),
            # (code_as__Import_names, (Name, '#0\n ( a ) #1\n#2'), (_aliases, 'a')),
            (code_as__Import_names, (Name, '#0\n ( a ) #1\n#2'),
                '**SyntaxError**',
                (_aliases, 'a'),
                (_aliases, 'a')),
            (code_as__Import_names, (alias, 'a'), (_aliases, 'a')),
            (code_as__Import_names, (alias, 'a as b'), (_aliases, 'a as b')),
            (code_as__Import_names, (alias, 'a.b'), (_aliases, 'a.b')),
            (code_as__Import_names, (alias, 'a.b as c'), (_aliases, 'a.b as c')),
            (code_as__Import_names, (alias, '*'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got alias, could not coerce')**",
                "**NodeError('expecting _aliases, got alias, could not coerce')**"),
            (code_as__Import_names, (Tuple, 'a, b'),
                (_aliases, 'a, b'),
                (_aliases, 'a, b'),
                (_aliases, 'a, b')),
            (code_as__Import_names, (Tuple, 'a, b.c'),
                (_aliases, 'a, b.c'),
                (_aliases, 'a, b.c'),
                (_aliases, 'a, b.c')),

            (code_as_ImportFrom_name, (Name, 'a'), (alias, 'a')),
            (code_as_ImportFrom_name, (Attribute, 'a.b'),
                "**SyntaxError**",
                "**NodeError('expecting alias, got Attribute, could not coerce')**",
                "**NodeError('expecting alias, got Attribute, could not coerce')**"),
            (code_as_ImportFrom_name, (Mult, '*'),
                (alias, '*'),
                "**NodeError('expecting alias, got Mult, could not coerce')**",
                "**NodeError('expecting alias, got Mult, could not coerce')**"),
            (code_as_ImportFrom_name, (Subscript, 'a[b]'),
                "**SyntaxError**",
                "**NodeError('expecting alias, got Subscript, could not coerce')**",
                "**NodeError('expecting alias, got Subscript, could not coerce')**"),
            # (code_as_ImportFrom_name, (Name, '#0\n ( a ) #1\n#2'), (alias, 'a')),
            (code_as_ImportFrom_name, (Name, '#0\n ( a ) #1\n#2'),
                '**SyntaxError**',
                (alias, 'a'),
                (alias, 'a')),

            (code_as__ImportFrom_names, (Name, 'a'), (_aliases, 'a')),
            (code_as__ImportFrom_names, (Attribute, 'a.b'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got Attribute, could not coerce')**",
                "**NodeError('expecting _aliases, got Attribute, could not coerce')**"),
            (code_as__ImportFrom_names, (Mult, '*'),
                (_aliases, '*'),
                "**NodeError('expecting _aliases, got Mult, could not coerce')**",
                "**NodeError('expecting _aliases, got Mult, could not coerce')**"),
            (code_as__ImportFrom_names, (Subscript, 'a[b]'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got Subscript, could not coerce')**",
                "**NodeError('expecting _aliases, got Subscript, could not coerce')**"),
            # (code_as__ImportFrom_names, (Name, '#0\n ( a ) #1\n#2'), (_aliases, 'a')),
            (code_as__ImportFrom_names, (Name, '#0\n ( a ) #1\n#2'),
                '**SyntaxError**',
                (_aliases, 'a'),
                (_aliases, 'a')),
            (code_as__ImportFrom_names, (alias, 'a'), (_aliases, 'a')),
            (code_as__ImportFrom_names, (alias, 'a as b'), (_aliases, 'a as b')),
            (code_as__ImportFrom_names, (alias, 'a.b'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got alias, could not coerce')**",
                "**NodeError('expecting _aliases, got alias, could not coerce')**"),
            (code_as__ImportFrom_names, (alias, '*'), (_aliases, '*')),
            (code_as__ImportFrom_names, (Tuple, 'a, b'),
                (_aliases, 'a, b'),
                (_aliases, 'a, b'),
                (_aliases, 'a, b')),
            (code_as__ImportFrom_names, (Tuple, 'a, b.c'),
                "**SyntaxError**",
                "**NodeError('expecting _aliases, got Tuple, could not coerce')**",
                "**NodeError('expecting _aliases, got Tuple, could not coerce')**"),

            (code_as_withitem, (Name, 'a'), (withitem, 'a')),
            (code_as_withitem, (Call, 'f()'), (withitem, 'f()')),
            (code_as_withitem, (Slice, 'a:b:c'),
                "**SyntaxError**",
                "**NodeError('expecting withitem, got Slice, could not coerce')**",
                "**NodeError('expecting withitem, got Slice, could not coerce')**"),
            (code_as_withitem, (Name, '#0\n ( a ) #1\n#2'),
                (withitem, '#0\n ( a ) #1\n#2'),
                (withitem, 'a')),

            (code_as__withitems, (Name, 'a'), (_withitems, 'a')),
            (code_as__withitems, (Call, 'f()'), (_withitems, 'f()')),
            (code_as__withitems, (Slice, 'a:b:c'),
                "**SyntaxError**",
                "**NodeError('expecting _withitems, got Slice, could not coerce')**",
                "**NodeError('expecting _withitems, got Slice, could not coerce')**"),
            (code_as__withitems, (Name, '#0\n ( a ) #1\n#2'),
                (_withitems, '#0\n ( a ) #1\n#2'),
                (_withitems, 'a')),
            (code_as__withitems, (withitem, 'a'), (_withitems, 'a')),
            (code_as__withitems, (withitem, 'a as b'), (_withitems, 'a as b')),
            (code_as__withitems, (Tuple, 'a,'),
                (_withitems, 'a,'),
                (_withitems, 'a,'),
                (_withitems, 'a')),
            (code_as__withitems, (Tuple, '(a,)'),
                (_withitems, '(a,)'),
                (_withitems, 'a,'),
                (_withitems, 'a')),
            (code_as__withitems, (arguments, '\nb\n,\nc\n,\n'),
                (_withitems, '\nb\n,\nc\n,\n'),
                (_withitems, '\nb\n,\nc\n,\n'),
                (_withitems, 'b, c')),
            (code_as__withitems, (Tuple, '(((a).b).c), d'),
                (_withitems, '(((a).b).c), d'),
                (_withitems, '(((a).b).c), d'),
                (_withitems, 'a.b.c, d')),
            (code_as__withitems, (Tuple, 'a:b, c:d:e'),
                "**SyntaxError**",
                "**NodeError('expecting _withitems, got Tuple, could not coerce')**",
                "**NodeError('expecting _withitems, got Tuple, could not coerce')**"),
            (code_as__withitems, (Tuple, 'a\n,\nb'),
                (_withitems, 'a\n,\nb'),
                (_withitems, 'a\n,\nb'),
                (_withitems, 'a, b')),
            (code_as__withitems, (Tuple, '(a)\n,\n(b)'),
                (_withitems, '(a)\n,\n(b)'),
                (_withitems, '(a)\n,\n(b)'),
                (_withitems, 'a, b')),
            (code_as__withitems, (List, '[a]'),
                (_withitems, '[a]'),
                (_withitems, 'a'),
                (_withitems, 'a')),
            (code_as__withitems, (List, '[\na\n,\nb\n]'),
                (_withitems, '[\na\n,\nb\n]'),
                (_withitems, '\na\n,\nb\n'),
                (_withitems, 'a, b')),
            (code_as__withitems, (Set, '{a}'),
                (_withitems, '{a}'),
                (_withitems, 'a'),
                (_withitems, 'a')),
            (code_as__withitems, (Set, '{\na\n,\nb\n}'),
                (_withitems, '{\na\n,\nb\n}'),
                (_withitems, '\na\n,\nb\n'),
                (_withitems, 'a, b')),
            (code_as__withitems, (_Assign_targets, 'a = \\\nb ='),
                '**SyntaxError**',
                (_withitems, 'a, \\\nb'),
                (_withitems, 'a, b')),
            (code_as__withitems, (_decorator_list, '\n@a\n@b\n'),
                '**SyntaxError**',
                (_withitems, '\na,\nb\n'),
                (_withitems, 'a, b')),
            (code_as__withitems, (_arglikes, '\na\n,\nb\n'),
                (_withitems, '\na\n,\nb\n'),
                (_withitems, '\na\n,\nb\n'),
                (_withitems, 'a, b')),
            (code_as__withitems, (_arglikes, '\na\n,\n*b\n'),
                '**SyntaxError**',
                "**NodeError('expecting _withitems, got _arglikes, could not coerce')**",
                "**NodeError('expecting _withitems, got _arglikes, could not coerce')**"),
            # (code_as__withitems, (_arglikes, '\na\n,\n*not b\n'),
            #     '**SyntaxError**',
            #     (_withitems, '\na\n,\n*(not b)\n'),
            #     (_withitems, 'a, *(not b)')),
            (code_as__withitems, (_arglikes, '\na\n,\nb=c\n'),
                '**SyntaxError**',
                "**NodeError('expecting _withitems, got _arglikes, could not coerce')**",
                "**NodeError('expecting _withitems, got _arglikes, could not coerce')**"),
            (code_as__withitems, (_arglikes, '\na\n,\nb=c\n'),
                '**SyntaxError**',
                "**NodeError('expecting _withitems, got _arglikes, could not coerce')**",
                "**NodeError('expecting _withitems, got _arglikes, could not coerce')**"),
            (code_as__withitems, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                '**SyntaxError**',
                (_withitems, '\na,\nb\n'),
                (_withitems, 'a, b')),
            (code_as__withitems, (_aliases, '\na\n,\nb\n'),
                (_withitems, '\na\n,\nb\n'),
                (_withitems, '\na\n,\nb\n'),
                (_withitems, 'a, b')),
            (code_as__withitems, (_aliases, 'a as b, c as d'),
                (_withitems, 'a as b, c as d'),
                "**NodeError('expecting _withitems, got _aliases, could not coerce')**",
                "**NodeError('expecting _withitems, got _aliases, could not coerce')**"),
            # (code_as__withitems, (_withitems, '\na\n,\nb\n'),
            #     (_withitems, '\na\n,\nb\n'),
            #     (_withitems, '\na\n,\nb\n'),
            #     (_withitems, 'a, b')),
            # (code_as__withitems, (_withitems, 'a as b, c as d'),
            #     (_withitems, 'a as b, c as d'),
            #     "**NodeError('expecting _withitems, got _withitems, could not coerce')**",
            #     "**NodeError('expecting _withitems, got _withitems, could not coerce')**"),
            (code_as__withitems, (MatchSequence, '\na\n,\nb\n'),
                (_withitems, '\na\n,\nb\n'),
                (_withitems, '\na\n,\nb\n'),
                (_withitems, 'a, b')),
            (code_as__withitems, (MatchSequence, 'a as b, c as d'),
                (_withitems, 'a as b, c as d'),
                "**NodeError('expecting _withitems, got MatchSequence, could not coerce')**",
                "**NodeError('expecting _withitems, got MatchSequence, could not coerce')**"),

            (code_as_pattern, (Module, '( a )'),
                (MatchAs, '( a )'),
                (MatchAs, 'a')),
            (code_as_pattern, (Interactive, '( a )'),
                (MatchAs, '( a )'),
                (MatchAs, 'a')),
            (code_as_pattern, (Expression, '( a )'),
                (MatchAs, '( a )'),
                (MatchAs, 'a')),
            (code_as_pattern, (Expr, '( a )'),
                (MatchAs, '( a )'),
                (MatchAs, 'a')),
            (code_as_pattern, (Name, ' ( a ) '),
                (MatchAs, ' ( a ) '),
                (MatchAs, 'a')),
            (code_as_pattern, (Constant, ' ( 1 ) '),
                (MatchValue, ' ( 1 ) '),
                (MatchValue, '1')),
            (code_as_pattern, (Constant, ' ( ... ) '),
                "**SyntaxError**",
                "**NodeError('expecting pattern, got Constant, could not coerce')**",
                "**NodeError('expecting pattern, got Constant, could not coerce')**",),
            (code_as_pattern, (Constant, ' ( True ) '),
                (MatchSingleton, ' ( True ) '),
                (MatchSingleton, 'True')),
            (code_as_pattern, (Constant, ' ( False ) '),
                (MatchSingleton, ' ( False ) '),
                (MatchSingleton, 'False')),
            (code_as_pattern, (Constant, ' ( None ) '),
                (MatchSingleton, ' ( None ) '),
                (MatchSingleton, 'None')),
            (code_as_pattern, (Constant, '...'),
                "**SyntaxError**",
                "**NodeError('expecting pattern, got Constant, could not coerce')**",
                "**NodeError('expecting pattern, got Constant, could not coerce')**"),
            (code_as_pattern, (Attribute, ' ( ( a )\n.\nb ) '),
                "**SyntaxError**",
                (MatchValue, ' ( a\n.\nb ) '),
                (MatchValue, 'a.b')),
            (code_as_pattern, (Starred, ' *\na '),
                (MatchStar, ' *\na '),
                (MatchStar, '*a')),
            (code_as_pattern, (Starred, ' *(\na) '),
                "**SyntaxError**",
                (MatchStar, ' *a '),
                (MatchStar, '*a')),
            (code_as_pattern, (arg, ' a '),
                (MatchAs, ' a '),
                (MatchAs, 'a')),
            (code_as_pattern, (alias, ' a '),
                (MatchAs, ' a '),
                (MatchAs, 'a')),
            (code_as_pattern, (withitem, ' ( a ) '),
                (MatchAs, ' ( a ) '),
                (MatchAs, 'a')),
            (code_as_pattern, (Dict, '{((a).b): c, **r}'),
                "**SyntaxError**",
                (MatchMapping, '{a.b: c, **r}'),
                (MatchMapping, '{a.b: c, **r}')),
            (code_as_pattern, (Call, '((u).v)((a), b=(c))'),
                "**SyntaxError**",
                (MatchClass, 'u.v((a), b=(c))'),
                (MatchClass, 'u.v(a, b=c)')),
            (code_as_pattern, (BinOp, 'a | b'), (MatchOr, 'a | b')),
            (code_as_pattern, (BinOp, 'a | b | c'), (MatchOr, 'a | b | c')),
            (code_as_pattern, (BinOp, '(a | b) | c'),
                (MatchOr, '(a | b) | c'),
                (MatchOr, '(a | b) | c'),
                (MatchOr, 'a | b | c')),
            (code_as_pattern, (BinOp, 'a | (b | c)'), (MatchOr, 'a | (b | c)')),
            (code_as_pattern, (BinOp, '(a | (b | c)) | d'),
                (MatchOr, '(a | (b | c)) | d'),
                (MatchOr, '(a | (b | c)) | d'),
                (MatchOr, 'a | (b | c) | d')),
            (code_as_pattern, (BinOp, 'a | ((b | c) | d)'),
                (MatchOr, 'a | ((b | c) | d)'),
                (MatchOr, 'a | ((b | c) | d)'),
                (MatchOr, 'a | (b | c | d)')),
            (code_as_pattern, (BinOp, '(a | b | c) | d'),
                (MatchOr, '(a | b | c) | d'),
                (MatchOr, '(a | b | c) | d'),
                (MatchOr, 'a | b | c | d')),
            (code_as_pattern, (BinOp, 'a | (b | c | d)'), (MatchOr, 'a | (b | c | d)')),
            (code_as_pattern, (BinOp, 'a | (b | c) | d'), (MatchOr, 'a | (b | c) | d')),
            (code_as_pattern, (BinOp, 'a | (b | (c | d) | e) | f'), (MatchOr, 'a | (b | (c | d) | e) | f')),
            (code_as_pattern, (BinOp, 'a + b'),
                "**SyntaxError**",
                "**NodeError('expecting pattern, got BinOp, could not coerce')**",
                "**NodeError('expecting pattern, got BinOp, could not coerce')**"),

            (code_as_pattern, (Tuple, ' a\n, '),
                (MatchSequence, ' a\n, '),
                (MatchSequence, '[a]')),
            (code_as_pattern, (List, ' [\na\n] '),
                (MatchSequence, ' [\na\n] '),
                (MatchSequence, '[a]')),
            (code_as_pattern, (Set, ' {\na\n} '),
                "**SyntaxError**",
                (MatchSequence, ' [\na\n] '),
                (MatchSequence, '[a]')),
            (code_as_pattern, (_Assign_targets, ' a \\\n= '),
                "**SyntaxError**",
                (MatchSequence, '[ a ]'),
                (MatchSequence, '[a]')),
            (code_as_pattern, (_decorator_list, '@ \\\n a '),
                "**SyntaxError**",
                (MatchSequence, '[a ]'),
                (MatchSequence, '[a]')),
            (code_as_pattern, (_comprehension_ifs, ' \nif\n a '),
                "**SyntaxError**",
                (MatchSequence, '[ \na ]'),
                (MatchSequence, '[a]')),
            (code_as_pattern, (arguments, ' \n*\n a '),
                (MatchStar, ' \n*\n a '),
                (MatchSequence, '[ \n*\n a ]'),
                (MatchSequence, '[*a]')),
            (code_as_pattern, (_aliases, ' \n a\n '),
                (MatchAs, ' \n a\n '),
                (MatchSequence, '[ \n a\n ]'),
                (MatchSequence, '[a]')),
            (code_as_pattern, (_withitems, ' \n a\n '),
                (MatchAs, ' \n a\n '),
                (MatchSequence, '[ \n a\n ]'),
                (MatchSequence, '[a]')),

            (code_as__expr_arglikes, (Name, 'a'), (Tuple, 'a')),
            (code_as__expr_arglikes, (Call, 'f()'), (Tuple, 'f()')),
            (code_as__expr_arglikes, (Name, '#0\n ( a ) #1\n#2'),
                (Tuple, '#0\n ( a ) #1\n#2'),
                (Tuple, 'a')),
            (code_as__expr_arglikes, (Tuple, 'a,'),
                (Tuple, 'a,'),
                (Tuple, 'a,'),
                (Tuple, 'a,')),
            (code_as__expr_arglikes, (Tuple, '(a,)'),
                (Tuple, '(a,)'),
                (Tuple, 'a,'),
                (Tuple, 'a,')),
            (code_as__expr_arglikes, (arguments, '\n*\nb\n,\nc\n,\n'),
                (Tuple, '\n*\nb\n,\nc\n,\n'),
                (Tuple, '\n*\nb\n,\nc\n,\n'),
                (Tuple, '*b, c')),
            (code_as__expr_arglikes, (Tuple, '(((a).b).c), d'),
                (Tuple, '(((a).b).c), d'),
                (Tuple, '(((a).b).c), d'),
                (Tuple, 'a.b.c, d')),
            (code_as__expr_arglikes, (Tuple, 'a:b, c:d:e'),
                "**SyntaxError**",
                "**NodeError('expecting non-Slice expressions (arglike), found Slice')**",
                "**SyntaxError**"),
            (code_as__expr_arglikes, (Tuple, 'a\n,\nb'),
                (Tuple, 'a\n,\nb'),
                (Tuple, 'a\n,\nb'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (List, '[a]'),
                (Tuple, '[a]'),
                (Tuple, 'a'),
                (Tuple, 'a')),
            (code_as__expr_arglikes, (List, '[\na\n,\nb\n]'),
                (Tuple, '[\na\n,\nb\n]'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (Set, '{a}'),
                (Tuple, '{a}'),
                (Tuple, 'a'),
                (Tuple, 'a')),
            (code_as__expr_arglikes, (Set, '{\na\n,\nb\n}'),
                (Tuple, '{\na\n,\nb\n}'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (_Assign_targets, 'a = \\\nb ='),
                '**SyntaxError**',
                (Tuple, 'a, \\\nb'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (_Assign_targets, '\\\na = x, y = b ='),
                "**SyntaxError**",
                (Tuple, '\\\na, (x, y), b'),
                (Tuple, 'a, (x, y), b')),
            (code_as__expr_arglikes, (_decorator_list, '\n@a\n@b\n'),
                '**SyntaxError**',
                (Tuple, '\na,\nb\n'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (_arglikes, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (_arglikes, '\na\n,\n*b\n'),
                (Tuple, '\na\n,\n*b\n'),
                (Tuple, '\na\n,\n*b\n'),
                (Tuple, 'a, *b')),
            (code_as__expr_arglikes, (_arglikes, '\na\n,\n*not b\n'),
                (Tuple, '\na\n,\n*not b\n'),
                (Tuple, '\na\n,\n*not b\n'),
                (Tuple, 'a, *(not b)')),
            (code_as__expr_arglikes, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                '**SyntaxError**',
                (Tuple, '\na,\nb\n'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (_aliases, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (_aliases, 'a as b, c as d'),
                '**SyntaxError**',
                "**NodeError('expecting Tuple, got _aliases, could not coerce')**",
                "**NodeError('expecting Tuple, got _aliases, could not coerce')**"),
            (code_as__expr_arglikes, (_withitems, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (_withitems, 'a as b, c as d'),
                '**SyntaxError**',
                "**NodeError('expecting Tuple, got _withitems, could not coerce')**",
                "**NodeError('expecting Tuple, got _withitems, could not coerce')**"),
            (code_as__expr_arglikes, (MatchSequence, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, '\na\n,\nb\n'),
                (Tuple, 'a, b')),
            (code_as__expr_arglikes, (MatchSequence, 'a as b, c as d'),
                '**SyntaxError**',
                "**NodeError('expecting Tuple, got MatchSequence, could not coerce')**",
                "**NodeError('expecting Tuple, got MatchSequence, could not coerce')**"),
        ]

        if PYGE11:
            cases.extend([
                (code_as_Tuple, (_arglikes, '\na\n,\n*not b\n'),
                    (Tuple, '\na\n,\n*not b\n'),  # SyntaxError on py 3.10
                    (Tuple, '(\na\n,\n*(not b)\n)'),
                    (Tuple, '(a, *(not b))')),
            ])

        if PYGE12:
            cases.extend([
                (code_as_expr, (TypeVar, 'T'), (Name, 'T')),
                (code_as_expr, (TypeVar, 'T: int'),
                    "**SyntaxError**",  # src
                    "**NodeError('expecting expression (standard), got TypeVar, could not coerce, has bound')**",  # FST
                    "**NodeError('expecting expression (standard), got TypeVar, could not coerce, has bound')**"),  # AST
                (code_as_expr, (TypeVarTuple, '*T'), (Starred, '*T')),
                (code_as_expr, (_type_params, ''),
                    "**SyntaxError**",  # src
                    (Tuple, '()'),  # FST
                    (Tuple, '()')),  # AST
                (code_as_expr, (_type_params, 'T'),
                    (Name, 'T'),  # src
                    (Tuple, 'T,'),  # FST
                    (Tuple, '(T,)')),  # AST
                (code_as_expr, (_type_params, 'T, *U'),
                    (Tuple, 'T, *U'),  # src
                    (Tuple, 'T, *U'),  # FST
                    (Tuple, '(T, *U)')),  # AST
                (code_as_expr, (_type_params, 'T, *U, **V'),
                    "**SyntaxError**",  # src
                    "**NodeError('expecting expression (standard), got _type_params, could not coerce, incompatible type ParamSpec')**",  # FST
                    "**NodeError('expecting expression (standard), got _type_params, could not coerce, incompatible type ParamSpec')**"),  # AST
                (code_as_expr, (_type_params, 'T: int, *U'),
                    "**SyntaxError**",  # src
                    "**NodeError('expecting expression (standard), got _type_params, could not coerce, TypeVar has bound')**",  # FST
                    "**NodeError('expecting expression (standard), got _type_params, could not coerce, TypeVar has bound')**"),  # AST

                (code_as__arglikes, (_type_params, '\na\n,\nb\n'),
                    (_arglikes, '\na\n,\nb\n'),
                    (_arglikes, '\na\n,\nb\n'),
                    (_arglikes, 'a, b')),
                (code_as__arglikes, (_type_params, 'a: int, c: str'),
                    '**SyntaxError**',
                    "**NodeError('expecting _arglikes, got _type_params, could not coerce')**",
                    "**NodeError('expecting _arglikes, got _type_params, could not coerce')**"),

                (code_as__aliases, (_type_params, '\na\n,\nb\n'),
                    (_aliases, '\na\n,\nb\n'),
                    (_aliases, '\na\n,\nb\n'),
                    (_aliases, 'a, b')),
                (code_as__aliases, (_type_params, 'a: int, c: str'),
                    '**SyntaxError**',
                    "**NodeError('expecting _aliases, got _type_params, could not coerce')**",
                    "**NodeError('expecting _aliases, got _type_params, could not coerce')**"),

                (code_as__withitems, (_type_params, '\na\n,\nb\n'),
                    (_withitems, '\na\n,\nb\n'),
                    (_withitems, '\na\n,\nb\n'),
                    (_withitems, 'a, b')),
                (code_as__withitems, (_type_params, 'a: int, c: str'),
                    '**SyntaxError**',
                    "**NodeError('expecting _withitems, got _type_params, could not coerce')**",
                    "**NodeError('expecting _withitems, got _type_params, could not coerce')**"),

                (code_as_pattern, (TypeVar, ' a '),
                    (MatchAs, ' a '),
                    (MatchAs, 'a')),
                (code_as_pattern, (TypeVarTuple, ' *\na '),
                    (MatchStar, ' *\na '),
                    (MatchStar, '*a')),
                (code_as_pattern, (_type_params, ' \n a\n '),
                    (MatchAs, ' \n a\n '),
                    (MatchSequence, '[ \n a\n ]'),
                    (MatchSequence, '[a]')),

                (code_as__type_params, (type_param, '**X'), (_type_params, '**X')),
                (code_as__type_params, (type_param, '#0\n **X #1\n#2'),
                    (_type_params, '#0\n **X #1\n#2'),
                    (_type_params, '**X')),
                (code_as__type_params, (Name, 'a'), (_type_params, 'a')),
                (code_as__type_params, (Call, 'f()'),
                    "**SyntaxError**",
                    "**NodeError('expecting _type_params, got Call, could not coerce')**",
                    "**NodeError('expecting _type_params, got Call, could not coerce')**"),
                (code_as__type_params, (Slice, 'a:b:c'),
                    "**SyntaxError**",
                    "**NodeError('expecting _type_params, got Slice, could not coerce')**",
                    "**NodeError('expecting _type_params, got Slice, could not coerce')**"),
                (code_as__type_params, (Name, '#0\n ( a ) #1\n#2'),
                    "**SyntaxError**",
                    (_type_params, '#0\n a #1\n#2'),
                    (_type_params, 'a')),
                (code_as__type_params, (withitem, 'a'), (_type_params, 'a')),
                (code_as__type_params, (withitem, 'a as b'),
                    "**SyntaxError**",
                    "**NodeError('expecting _type_params, got withitem, could not coerce')**",
                    "**NodeError('expecting _type_params, got withitem, could not coerce')**"),
                (code_as__type_params, (Tuple, 'a,'),
                    (_type_params, 'a,'),
                    (_type_params, 'a,'),
                    (_type_params, 'a')),
                (code_as__type_params, (Tuple, '(a,)'),
                    "**SyntaxError**",
                    (_type_params, 'a,'),
                    (_type_params, 'a')),
                (code_as__type_params, (arguments, '\nb\n,\nc\n,\n'),
                    (_type_params, '\nb\n,\nc\n,\n'),
                    (_type_params, '\nb\n,\nc\n,\n'),
                    (_type_params, 'b, c')),
                (code_as__type_params, (Tuple, '(a), *(b)'),
                    "**SyntaxError**",
                    (_type_params, 'a, *b'),
                    (_type_params, 'a, *b')),
                (code_as__type_params, (Tuple, 'a:b, c:d:e'),
                    "**SyntaxError**",
                    "**NodeError('expecting _type_params, got Tuple, could not coerce')**",
                    "**NodeError('expecting _type_params, got Tuple, could not coerce')**"),
                (code_as__type_params, (Tuple, 'a\n,\nb'),
                    (_type_params, 'a\n,\nb'),
                    (_type_params, 'a\n,\nb'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (Tuple, '(a)\n,\n(b)'),
                    "**SyntaxError**",
                    (_type_params, 'a\n,\nb'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (List, '[a]'),
                    "**SyntaxError**",
                    (_type_params, 'a'),
                    (_type_params, 'a')),
                (code_as__type_params, (List, '[\na\n,\nb\n]'),
                    "**SyntaxError**",
                    (_type_params, '\na\n,\nb\n'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (Set, '{a}'),
                    "**SyntaxError**",
                    (_type_params, 'a'),
                    (_type_params, 'a')),
                (code_as__type_params, (Set, '{\na\n,\nb\n}'),
                    "**SyntaxError**",
                    (_type_params, '\na\n,\nb\n'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (_Assign_targets, 'a = \\\nb ='),
                    '**SyntaxError**',
                    (_type_params, 'a, \\\nb'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (_decorator_list, '\n@a\n@b\n'),
                    '**SyntaxError**',
                    (_type_params, '\na,\nb\n'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (_arglikes, '\na\n,\nb\n'),
                    (_type_params, '\na\n,\nb\n'),
                    (_type_params, '\na\n,\nb\n'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (_arglikes, '\na\n,\n*b\n'),
                    (_type_params, '\na\n,\n*b\n'),
                    (_type_params, '\na\n,\n*b\n'),
                    (_type_params, 'a, *b')),
                (code_as__type_params, (_arglikes, '\na\n,\n*not b\n'),
                    '**SyntaxError**',
                    "**NodeError('expecting _type_params, got _arglikes, could not coerce')**",
                    "**NodeError('expecting _type_params, got _arglikes, could not coerce')**"),
                (code_as__type_params, (_comprehension_ifs, '\nif\na\nif\nb\n'),
                    '**SyntaxError**',
                    (_type_params, '\na,\nb\n'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (_aliases, '\na\n,\nb\n'),
                    (_type_params, '\na\n,\nb\n'),
                    (_type_params, '\na\n,\nb\n'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (_aliases, 'a as b, c as d'),
                    '**SyntaxError**',
                    "**NodeError('expecting _type_params, got _aliases, could not coerce')**",
                    "**NodeError('expecting _type_params, got _aliases, could not coerce')**"),
                (code_as__type_params, (MatchSequence, '\na\n,\nb\n'),
                    (_type_params, '\na\n,\nb\n'),
                    (_type_params, '\na\n,\nb\n'),
                    (_type_params, 'a, b')),
                (code_as__type_params, (MatchSequence, 'a as b, c as d'),
                    '**SyntaxError**',
                    "**NodeError('expecting _type_params, got MatchSequence, could not coerce')**",
                    "**NodeError('expecting _type_params, got MatchSequence, could not coerce')**"),
            ])

        if PYGE13:
            cases.extend([
                (code_as_expr, (TypeVar, 'T = int'),
                    "**SyntaxError**",  # src
                    "**NodeError('expecting expression (standard), got TypeVar, could not coerce, has default_value')**",  # FST
                    "**NodeError('expecting expression (standard), got TypeVar, could not coerce, has default_value')**"),  # AST
                (code_as_expr, (TypeVarTuple, '*T = ()'),
                    "**SyntaxError**",  # src
                    "**NodeError('expecting expression (standard), got TypeVarTuple, could not coerce, has default_value')**",  # FST
                    "**NodeError('expecting expression (standard), got TypeVarTuple, could not coerce, has default_value')**"),  # AST
                (code_as_expr, (_type_params, 'T = int, *U'),
                    "**SyntaxError**",  # src
                    "**NodeError('expecting expression (standard), got _type_params, could not coerce, TypeVar has default_value')**",  # FST
                    "**NodeError('expecting expression (standard), got _type_params, could not coerce, TypeVar has default_value')**"),  # AST

                (code_as__type_params, (_arglikes, '\na\n,\nb=c\n'),
                    (_type_params, '\na\n,\nb=c\n'),
                    "**NodeError('expecting _type_params, got _arglikes, could not coerce')**",
                    "**NodeError('expecting _type_params, got _arglikes, could not coerce')**"),
            ])

        for case in cases:
            try:
                code_as, (mode, src), *ress = case

                if (l := len(ress)) == 1:
                    res_src = res_fst = res_ast = ress[0]

                elif l == 2:
                    res_src = res_fst = ress[0]
                    res_ast = ress[1]

                else:
                    res_src, res_fst, res_ast = ress

                fst_ = FST(src, mode)

                test(src, res_src)
                test(fst_.a, res_ast)
                test(fst_, res_fst)

            except Exception:
                print(f'\nCase: {case}')

                raise

    def test_unmake__ast_coerce_to_expr(self):
        mode_and_src = [
            (Module, 'a'),
            (Interactive, 'a'),
            (Expression, 'a'),
            (Expr, 'a'),
            (_Assign_targets, 'a ='),
            (_decorator_list, '@a'),
            (_arglikes, 'a'),
            (_comprehension_ifs, 'if a'),
            (arguments, 'a'),
            (arg, 'a'),
            (alias, 'a'),
            (_aliases, 'a'),
            (withitem, 'a'),
            (_withitems, 'a'),
            (MatchValue, '1'),
            (MatchSingleton, 'True'),
            (MatchSequence, '[a]'),
            (MatchMapping, '{1: a}'),
            (MatchClass, 'cls()'),
            (MatchStar, '*a'),
            (MatchAs, 'a'),
            (MatchOr, 'a | b'),
        ]

        if PYGE12:
            mode_and_src.extend([
                (TypeVar, 'a'),
                (TypeVarTuple, '*a'),
                (_type_params, 'a'),
            ])

        for mode, src in mode_and_src:
            fst_ = FST(src, mode)

            code._coerce_to_expr_ast(fst_.a, True, {}, {}, 'test')

            self.assertIsNone(fst_.a)

    def test_unmake__ast_coerce_to_pattern(self):
        mode_and_src = [
            (Module, 'a'),
            (Interactive, 'a'),
            (Expression, 'a'),
            (Expr, 'a'),
            (Constant, '1'),
            (Starred, '*a'),
            (Name, 'a'),
            (arg, 'a'),
            (alias, 'a'),
            (withitem, 'a'),
            (Dict, '{1: b}'),
            (Call, 'f()'),
            (BinOp, 'a | b'),
            (Tuple, 'a,'),
            (List, '[a]'),
            (Set, '{a}'),
            (Set, '{a}'),
            (_Assign_targets, 'a ='),
            (_decorator_list, '@a'),
            (_arglikes, 'a'),
            (_comprehension_ifs, 'if a'),
            (arguments, '*a'),
            (_aliases, 'a'),
            (_withitems, 'a'),
        ]

        if PYGE12:
            mode_and_src.extend([
                (TypeVar, 'a'),
                (TypeVarTuple, '*a'),
                (_type_params, 'a'),
            ])

        for mode, src in mode_and_src:
            fst_ = FST(src, mode)

            code._coerce_to_pattern(fst_)

            self.assertIsNone(fst_.a)

    def test_fst_parse_non_str(self):
        self.assertEqual('if 1: pass', parse(b'if 1: pass').f.src)
        self.assertEqual('if 1: pass', parse(memoryview(b'if 1: pass')).f.src)

        self.assertEqual('if 1:\n    pass', parse(FST('if 1: pass').a).f.src)
        self.assertEqual('a:b:c', parse(FST('a:b:c').a).f.src)
        self.assertEqual('except:\n    pass', parse(FST('except: pass').a).f.src)

    def test_parse_coverage(self):
        self.assertRaises(SyntaxError, px.parse_expr, ')+(')
        self.assertRaises(SyntaxError, px.parse_withitem, ')+(')
        self.assertRaises(SyntaxError, px.parse__withitems, ')+(')

    def test_code_coverage(self):
        # misc stuff to fill out test coverage

        self.assertRaises(NodeError, FST('import a').put, FST('x', 'Name').a, 0, coerce=False)

        self.assertRaises(NodeError, FST('a = b').put, FST('a as b', 'withitem'))
        self.assertRaises(NodeError, FST('a = b').put, FST('a as b', 'withitem').a)

        self.assertRaises(ValueError, code.code_as_lines, FST('a = b').value)
        self.assertRaises(ValueError, code.code_as_all, FST('a = b').value)

        self.assertEqual('a\nb', code.code_as_all(['a', 'b']).src)

        self.assertRaises(NodeError, code.code_as__ExceptHandlers, FST('a'))
        self.assertRaises(NodeError, code.code_as__ExceptHandlers, FST('a').a)

        self.assertEqual('except:\n    pass', code.code_as__ExceptHandlers(FST('except: pass', '_ExceptHandlers', coerce=True).a).src)
        self.assertEqual('except:\n  pass', code.code_as__ExceptHandlers(['except:', '  pass'], coerce=True).src)

        self.assertRaises(NodeError, code.code_as__match_cases, FST('a'))
        self.assertRaises(NodeError, code.code_as__match_cases, FST('a').a)

        self.assertEqual('case _:\n  pass', code.code_as__match_cases(['case _:', '  pass'], coerce=True).src)

        self.assertRaises(NodeError, code.code_as_Tuple, FST('a'))

        self.assertRaises(NodeError, code.code_as__ImportFrom_names, FST('a.b', '_aliases'))

        f = FST('a, b', '_aliases')
        f.names[0] = '*'
        self.assertRaises(NodeError, code.code_as__ImportFrom_names, f)

        f = FST('a.b')
        self.assertRaises(ValueError, code.code_as_identifier, f.value)
        self.assertRaises(ValueError, code.code_as_identifier_dotted, f.value)
        self.assertRaises(ValueError, code.code_as_identifier_star, f.value)
        self.assertRaises(ValueError, code.code_as_identifier_alias, f.value)

        self.assertRaises(ValueError, code.code_as_constant, f.value)
        self.assertRaises(NodeError, code.code_as_constant, f.a)
        self.assertRaises(NodeError, code.code_as_constant, Constant(value=-1))
        self.assertRaises(NodeError, code.code_as_constant, Constant(value=1+1j))
        self.assertRaises(NodeError, code.code_as_constant, Constant(value=-1j))
        self.assertRaises(NodeError, code.code_as_constant, {})

        self.assertEqual('a\nb', code.code_as_constant(['a', 'b']))

        self.assertRaises(ParseError, code.code_as__comprehension_ifs, '**z', coerce=True)

        self.assertEqual('if a', code.code_as__comprehension_ifs(FST('a,'), coerce=True).src)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-coerce', default=False, action='store_true', help="regenerate coerce test data")
    parser.add_argument('--regen-parse-autogen', default=False, action='store_true', help="regenerate autogenerated parse test data")
    parser.add_argument('--regen-syntax-errors', default=False, action='store_true', help="regenerate detailed syntax errors")
    parser.add_argument('--regen-parse-invalid-src', default=False, action='store_true', help="regenerate parse invalid source")

    args, _ = parser.parse_known_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT14:
            raise RuntimeError('cannot regenerate on python version < 3.14')

    if args.regen_coerce or args.regen_all:
        print('Regenerating coerce test data...')
        regen_coerce_data()

    if args.regen_parse_autogen or args.regen_all:
        print('Regenerating autogenerated parse test data...')
        regen_parse_autogen_data()

    if args.regen_syntax_errors or args.regen_all:
        print('Regenerating detailed parse syntax error data...')
        regen_syntax_errors_data()

    if args.regen_parse_invalid_src or args.regen_all:
        print('Regenerating parse invalid source data...')
        regen_parse_invalid_src_data()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
