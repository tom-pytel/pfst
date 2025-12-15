#!/usr/bin/env python

from fst.astutil import *
from fst import *
from fst.astutil import FIELDS, AST_FIELDS

_FIELD_CARDINALITY = {
    (kls, field): t if (t := typ[-1:]) in ('?*') else ''
    for kls, fields in FIELDS.items()
    for field, typ in (('END', ''),) + fields + ((None, ''),)
}

print(r'''
from typing import Union

from . import fst

from .asttypes import (
    AST,
    Add,
    And,
    AnnAssign,
    Assert,
    Assign,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    Attribute,
    AugAssign,
    Await,
    BinOp,
    BitAnd,
    BitOr,
    BitXor,
    BoolOp,
    Break,
    Call,
    ClassDef,
    Compare,
    Constant,
    Continue,
    Del,
    Delete,
    Dict,
    DictComp,
    Div,
    Eq,
    ExceptHandler,
    Expr,
    Expression,
    FloorDiv,
    For,
    FormattedValue,
    FunctionDef,
    FunctionType,
    GeneratorExp,
    Global,
    Gt,
    GtE,
    If,
    IfExp,
    Import,
    ImportFrom,
    In,
    Interactive,
    Invert,
    Is,
    IsNot,
    JoinedStr,
    LShift,
    Lambda,
    List,
    ListComp,
    Load,
    Lt,
    LtE,
    MatMult,
    Match,
    MatchAs,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    MatchSingleton,
    MatchStar,
    MatchValue,
    Mod,
    Module,
    Mult,
    Name,
    NamedExpr,
    Nonlocal,
    Not,
    NotEq,
    NotIn,
    Or,
    Pass,
    Pow,
    RShift,
    Raise,
    Return,
    Set,
    SetComp,
    Slice,
    Starred,
    Store,
    Sub,
    Subscript,
    Try,
    Tuple,
    TypeIgnore,
    UAdd,
    USub,
    UnaryOp,
    While,
    With,
    Yield,
    YieldFrom,
    alias,
    arg,
    arguments,
    comprehension,
    keyword,
    match_case,
    withitem,
    TryStar,
    TypeAlias,
    TypeVar,
    ParamSpec,
    TypeVarTuple,
    TemplateStr,
    Interpolation,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

__all__ = ['PREV_FUNCS']


_NextPrevRet = Union['fst.FST', None, tuple[str, int | None]]
'''.strip())

PREV_FUNCS = {}

for ast_cls, fields in AST_FIELDS.items():
    def ret_next(next_idx):
        if next_idx >= len(fields):
            return None

        next_field = fields[next_idx] or 'END'

        return (next_field, -1 if _FIELD_CARDINALITY[(ast_cls, next_field)] == '*' else None)

    cls_name = func_cls = ast_cls.__name__
    fields = (None,) + fields[::-1]
    special = True

    if ast_cls is Dict:
        print(r'''

def _prev_Dict_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.values:
        return a[-1].f

    return None


def _prev_Dict_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.keys[idx]:
        return a.f

    if (idx := idx - 1) >= 0:
        return ast.values[idx].f

    return None


def _prev_Dict_keys(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return ast.values[idx].f

    return None
'''.rstrip())

    elif ast_cls is Compare:
        print(r'''

def _prev_Compare_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.comparators:
        return a[-1].f

    return ast.left.f


def _prev_Compare_comparators(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ops[idx].f


def _prev_Compare_ops(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.comparators[idx].f

    return ast.left.f


def _prev_Compare_left(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    elif ast_cls is MatchMapping:
        print(r'''

def _prev_MatchMapping_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.patterns:
        return a[-1].f

    return None


def _prev_MatchMapping_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.keys[idx]:  # OUR OWN SPECIAL CASE: MatchMapping.keys cannot normally be None but we make use of this temporarily in some operations
        return a.f

    if (idx := idx - 1) >= 0:
        return  ast.patterns[idx].f

    return None


def _prev_MatchMapping_keys(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.patterns[idx].f

    return None
'''.rstrip())

    elif ast_cls is Call:
        print(r'''

def _prev_Call_END(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    kws = ast.keywords

    if not kws:
        if args:
            return args[-1].f

        return ast.func.f

    kwn = kws[-1]

    if (not args
        or (argn := args[-1]).__class__ is not Starred
        or (argn.lineno, argn.col_offset) < (kwn.lineno, kwn.col_offset)
    ):
        return kwn.f

    return argn.f


def _prev_Call_keywords(ast: AST, idx: int | None) -> _NextPrevRet:
    kws = ast.keywords
    args = ast.args
    idx_ = idx - 1

    if not args:
        if idx_ >= 0:
            return kws[idx_].f

        return ast.func.f

    if (last_arg := args[-1]).__class__ is not Starred:  # if no Starred then can't be mixed with keywords, unchecked walk backward
        if idx_ >= 0:
            return kws[idx_].f

        return last_arg.f

    last_arg_pos = (last_arg.lineno, last_arg.col_offset)

    if idx_ < 0:
        if (kw_pos := ((kw := kws[0]).lineno, kw.col_offset)) > last_arg_pos:
            return last_arg.f

        for arg in args[-2::-1]:  # only need to find last arg (if any) before first keyword
            if (arg.lineno, arg.col_offset) < kw_pos:
                return arg.f

        return ast.func.f

    if (kw_pos := ((kw := kws[idx_]).lineno, kw.col_offset)) > last_arg_pos:
        return kw.f

    if (kw_plus1_pos := ((kw_plus1 := kws[idx]).lineno, kw_plus1.col_offset)) > last_arg_pos:
        return last_arg.f

    for arg in args[-2::-1]:  # need to find last arg (if any) between next and last keywords
        arg_pos = (arg.lineno, arg.col_offset)

        if arg_pos < kw_pos:
            break
        if arg_pos < kw_plus1_pos:
            return arg.f

    return kw.f


def _prev_Call_args(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    kws = ast.keywords

    if (not kws
        or args[-1].__class__ is not Starred  # if no kws or last arg is not Starred then can't be mixed with keywords, unchecked walk backward
        or (arg_pos := ((arg := args[idx]).lineno, arg.col_offset))
            < (first_kw_pos := ((first_kw := kws[0]).lineno, first_kw.col_offset))  # this arg before first keyword so all args from here
    ):
        if (idx := idx - 1) >= 0:
            return args[idx].f

        return ast.func.f

    if not idx:  # no more args, just find last kw before this arg if any
        for kw in kws[1:]:  # from start likely shorter search, we already checked kws[0]
            if (kw.lineno, kw.col_offset) > arg_pos:
                break

            first_kw = kw

        return first_kw.f

    prev_arg = args[idx - 1]
    prev_arg_pos = (prev_arg.lineno, prev_arg.col_offset)

    for kw in kws[1:]:
        kw_pos = (kw.lineno, kw.col_offset)

        if kw_pos > arg_pos:
            break

        first_kw = kw
        first_kw_pos = kw_pos

    return (prev_arg if prev_arg_pos > first_kw_pos else first_kw).f


def _prev_Call_func(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    elif ast_cls is ClassDef:
        print(r'''

def _prev_ClassDef_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    if a := ast.keywords:
        kwn = a[-1]

        if (not (b := ast.bases)
            or (basen := b[-1]).__class__ is not Starred
            or (basen.lineno, basen.col_offset) < (kwn.lineno, kwn.col_offset)
        ):
            return kwn.f

        return basen.f

    if a := ast.bases:
        return a[-1].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[-1].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_ClassDef_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    if a := ast.keywords:
        kwn = a[-1]

        if (not (b := ast.bases)
            or (basen := b[-1]).__class__ is not Starred
            or (basen.lineno, basen.col_offset) < (kwn.lineno, kwn.col_offset)
        ):
            return kwn.f

        return basen.f

    if a := ast.bases:
        return a[-1].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[-1].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_ClassDef_keywords(ast: AST, idx: int | None) -> _NextPrevRet:
    kws = ast.keywords
    bases = ast.bases
    idx_ = idx - 1

    if not bases:
        if idx_ >= 0:
            return kws[idx_].f

    else:
        if (last_base := bases[-1]).__class__ is not Starred:  # if no Starred then can't be mixed with keywords, unchecked walk backward
            if idx_ >= 0:
                return kws[idx_].f

            return last_base.f

        last_base_pos = (last_base.lineno, last_base.col_offset)

        if idx_ < 0:
            if (kw_pos := ((kw := kws[0]).lineno, kw.col_offset)) > last_base_pos:
                return last_base.f

            for base in bases[-2::-1]:  # only need to find last base (if any) before first keyword
                if (base.lineno, base.col_offset) < kw_pos:
                    return base.f

        else:
            if (kw_pos := ((kw := kws[idx_]).lineno, kw.col_offset)) > last_base_pos:
                return kw.f

            if (kw_plus1_pos := ((kw_plus1 := kws[idx]).lineno, kw_plus1.col_offset)) > last_base_pos:
                return last_base.f

            for base in bases[-2::-1]:  # need to find last base (if any) between next and last keywords
                base_pos = (base.lineno, base.col_offset)

                if base_pos < kw_pos:
                    break
                if base_pos < kw_plus1_pos:
                    return base.f

            return kw.f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[-1].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_ClassDef_bases(ast: AST, idx: int | None) -> _NextPrevRet:
    bases = ast.bases
    kws = ast.keywords

    if (not kws
        or bases[-1].__class__ is not Starred  # if no kws or last base is not Starred then can't be mixed with keywords, unchecked walk backward
        or (base_pos := ((base := bases[idx]).lineno, base.col_offset))
            < (first_kw_pos := ((first_kw := kws[0]).lineno, first_kw.col_offset))  # this base before first keyword so all bases from here
    ):
        if (idx := idx - 1) >= 0:
            return bases[idx].f

        if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
            return a[-1].f

        if a := ast.decorator_list:
            return a[-1].f

        return None

    if not idx:  # no more bases, just find last kw before this base if any
        for kw in kws[1:]:  # from start likely shorter search, we already checked kws[0]
            if (kw.lineno, kw.col_offset) > base_pos:
                break

            first_kw = kw

        return first_kw.f

    prev_base = bases[idx - 1]
    prev_base_pos = (prev_base.lineno, prev_base.col_offset)

    for kw in kws[1:]:
        kw_pos = (kw.lineno, kw.col_offset)

        if kw_pos > base_pos:
            break

        first_kw = kw
        first_kw_pos = kw_pos

    return (prev_base if prev_base_pos > first_kw_pos else first_kw).f


def _prev_ClassDef_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:  # if we got into this function then the AST has this
        return  ast.type_params[idx].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_ClassDef_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.decorator_list[idx].f

    return None
'''.rstrip())

    elif ast_cls is AsyncFunctionDef:
        func_cls = 'FunctionDef'

    elif ast_cls is FunctionDef:
        print(r'''

def _prev_FunctionDef_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    if a := ast.returns:
        return a.f

    return ast.args.f


def _prev_FunctionDef_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    if a := ast.returns:
        return a.f

    return ast.args.f


def _prev_FunctionDef_returns(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.args.f


def _prev_FunctionDef_args(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[-1].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_FunctionDef_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:  # if we got into this function then the AST has this
        return  ast.type_params[idx].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_FunctionDef_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.decorator_list[idx].f

    return None
'''.rstrip())

    elif ast_cls is arguments:
        print(r'''

def _prev_arguments_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.kwarg:
        return a.f

    if a := ast.kw_defaults:
        if a := a[-1]:
            return a.f

    if a := ast.kwonlyargs:
        return a[-1].f

    if a := ast.vararg:
        return a.f

    if a := ast.defaults:
        return a[-1].f

    if a := ast.args:
        return a[-1].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_kwarg(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.kw_defaults:
        if a := a[-1]:
            return a.f

    if a := ast.kwonlyargs:
        return a[-1].f

    if a := ast.vararg:
        return a.f

    if a := ast.defaults:
        return a[-1].f

    if a := ast.args:
        return a[-1].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_kw_defaults(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.kwonlyargs[idx].f


def _prev_arguments_kwonlyargs(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        if a := ast.kw_defaults[idx]:
            return a.f

        return ast.kwonlyargs[idx].f

    if a := ast.vararg:
        return a.f

    if a := ast.defaults:
        return a[-1].f

    if a := ast.args:
        return a[-1].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_vararg(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.defaults:
        return a[-1].f

    if a := ast.args:
        return a[-1].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_defaults(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    iarg = len(args) - len(ast.defaults) + idx

    if iarg >= 0:
        return args[iarg].f

    return ast.posonlyargs[iarg].f


def _prev_arguments_args(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    defaults = ast.defaults
    idx -= 1

    if defaults:
        idefault = len(defaults) - len(args) + idx

        if idefault >= 0:
            return defaults[idefault].f

    if idx >= 0:
        return args[idx].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_posonlyargs(ast: AST, idx: int | None) -> _NextPrevRet:
    posonlyargs = ast.posonlyargs
    defaults = ast.defaults
    idx -= 1

    if defaults:
        idefault = len(defaults) - len(ast.args) - len(posonlyargs) + idx

        if idefault >= 0:
            return defaults[idefault].f

    if idx >= 0:
        return posonlyargs[idx].f

    return None
'''.rstrip())

    elif ast_cls is TypeVar:
        print(r'''

def _prev_TypeVar_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    if a := ast.bound:
        return a.f

    return None


def _prev_TypeVar_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.bound:
        return a.f

    return None


def _prev_TypeVar_bound(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    elif ast_cls is ParamSpec:
        print(r'''

def _prev_ParamSpec_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _prev_ParamSpec_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    elif ast_cls is TypeVarTuple:
        print(r'''

def _prev_TypeVarTuple_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _prev_TypeVarTuple_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    else:
        special = False

    for i, field in enumerate(fields):
        func_name = f'_prev_{func_cls}_{field or "END"}'

        PREV_FUNCS[(cls_name, field)] = func_name

        if special:
            continue

        body = []
        cur_card = _FIELD_CARDINALITY[(ast_cls, field)]  # this node already returned, just need to see if have to keep iterating it or move on to next field

        if cur_card == '*':
            body.append(f'    if (idx := idx - 1) >= 0:\n        return  ast.{field}[idx].f')

        for next_field in fields[i + 1:]:
            next_card = _FIELD_CARDINALITY[(ast_cls, next_field)]

            if next_card == '*':
                body.append(f'    if a := ast.{next_field}:\n        return a[-1].f')
            elif next_card == '?':
                body.append(f'    if a := ast.{next_field}:\n        return a.f')

            else:
                body.append(f'    return ast.{next_field}.f')

                break

        else:
            body.append('    return None')

        print(f'\n\ndef {func_name}(ast: AST, idx: int | None) -> _NextPrevRet:\n' + '\n\n'.join(body))



print('\n\nPREV_FUNCS = {')
for key, val in PREV_FUNCS.items():
    print(f'    ({key[0]}, {key[1]!r}): {val},')
print('}')
