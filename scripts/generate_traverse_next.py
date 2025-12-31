#!/usr/bin/env python

from fst.astutil import *
from fst import *
from fst.astutil import FIELDS, AST_FIELDS

PRUNE_EMPTY_FUNCS = True

_FIELD_CARDINALITY = {
    (kls, field): t if (t := typ[-1:]) in ('?*') else ''
    for kls, fields in FIELDS.items()
    for field, typ in (('START', ''),) + fields + ((None, ''),)
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
    _arglikes,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

__all__ = ['NEXT_FUNCS']


_NextPrevRet = Union['fst.FST', None, tuple[str, int | None]]


def _next_None(ast: AST, idx: int | None) -> _NextPrevRet:
      return None
'''.strip())

NEXT_FUNCS = {}

for ast_cls, fields in AST_FIELDS.items():
    def ret_next(next_idx):
        if next_idx >= len(fields):
            return None

        next_field = fields[next_idx] or 'START'

        return (next_field, -1 if _FIELD_CARDINALITY[(ast_cls, next_field)] == '*' else None)

    cls_name = func_cls = ast_cls.__name__
    fields = (None,) + fields
    special = True

    if ast_cls is Dict:
        print(r'''

def _next_Dict_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.keys:
        if a := a[0]:  # key may be None
            return a.f

        return ast.values[0].f

    return None


def _next_Dict_keys(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.values[idx].f


def _next_Dict_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.keys):
        if a := a[idx]:  # key may be None
            return a.f

        return ast.values[idx].f

    return None
'''.rstrip())

    elif ast_cls is Compare:
        print(r'''

def _next_Compare_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.left.f


def _next_Compare_left(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.ops:
        return a[0].f

    return None


def _next_Compare_ops(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.comparators[idx].f


def _next_Compare_comparators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.ops):
        return a[idx].f

    return None
'''.rstrip())

    elif ast_cls is MatchMapping:
        print(r'''

def _next_MatchMapping_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.keys:
        return a[0].f

    return None


def _next_MatchMapping_keys(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.patterns[idx].f


def _next_MatchMapping_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.keys):
        if a := a[idx]:  # OUR OWN SPECIAL CASE: MatchMapping.keys cannot normally be None but we make use of this temporarily in some operations
            return a.f

        return ast.patterns[idx].f

    return None
'''.rstrip())

    elif ast_cls is Call:
        print(r'''

def _next_Call_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.func.f


def _next_Call_func(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    kws = ast.keywords

    if not kws:
        if args:
            return args[0].f

        return None

    kw0 = kws[0]

    if (not args
        or (
            (arg0 := args[0]).__class__ is Starred
            and (arg0.lineno, arg0.col_offset) > (kw0.lineno, kw0.col_offset)
    )):
        return kw0.f

    return arg0.f


def _next_Call_args(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    last_arg = args[-1]  # we know there is at least one .args because otherwise we wouldn't be in this function

    if last_arg.__class__ is not Starred:  # if no Starred then can't be mixed with keywords, unchecked walk forward
        if (idx := idx + 1) < len(args):
            return args[idx].f

        if a := ast.keywords:
            return a[0].f

        return None

    arg = args[idx]
    arg_pos = (arg.lineno, arg.col_offset)

    if arg is last_arg:  # only need to find first keyword after this arg
        for kw in ast.keywords:
            if (kw.lineno, kw.col_offset) > arg_pos:
                return kw.f

        return None

    next_arg = args[idx + 1]
    next_arg_pos = (next_arg.lineno, next_arg.col_offset)

    for kw in ast.keywords:
        kw_pos = (kw.lineno, kw.col_offset)

        if kw_pos > next_arg_pos:
            return next_arg.f
        if kw_pos > arg_pos:
            return kw.f

    return next_arg.f


def _next_Call_keywords(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    kws = ast.keywords

    if (not args
        or (last_arg := args[-1]).__class__ is not Starred  # if no args or no Starred then can't be mixed with keywords, unchecked walk forward
        or (last_arg_pos := (last_arg.lineno, last_arg.col_offset))
            < (kw_pos := ((kw := kws[idx]).lineno, kw.col_offset))  # last Starred arg before this kw (likely case)
    ):
        if (idx := idx + 1) < len(kws):
            return kws[idx].f

        return None

    if kw is kws[-1]:  # no more kws, just find first arg past this kw if any (will be Starred)
        for arg in args[-2::-1]:  # we search backwards because more likely to be shorter search
            if (arg.lineno, arg.col_offset) < kw_pos:
                break

            last_arg = arg

        return last_arg.f

    next_kw = kws[idx + 1]
    next_kw_pos = (next_kw.lineno, next_kw.col_offset)

    for arg in args[-2::-1]:
        arg_pos = (arg.lineno, arg.col_offset)

        if arg_pos < kw_pos:
            break

        last_arg = arg
        last_arg_pos = arg_pos

    return (next_kw if next_kw_pos < last_arg_pos else last_arg).f
'''.rstrip())

    elif ast_cls is ClassDef:
        print(r'''

def _next_ClassDef_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.decorator_list:
        return a[0].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[0].f

    return _next_ClassDef_bases_or_keywords_start(ast)


def _next_ClassDef_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.decorator_list):
        return a[idx].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[0].f

    return _next_ClassDef_bases_or_keywords_start(ast)


def _next_ClassDef_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.type_params):  # if we got into this function then the AST has this
        return a[idx].f

    return _next_ClassDef_bases_or_keywords_start(ast)


def _next_ClassDef_bases_or_keywords_start(ast: AST) -> _NextPrevRet:  # SPECIAL
    bases = ast.bases
    kws = ast.keywords

    if not kws:
        if bases:
            return bases[0].f

        if a := ast.body:
            return a[0].f

        return None

    if (not bases
        or (
            (base0 := bases[0]).__class__ is Starred
            and (base0.lineno, base0.col_offset) > ((kw0 := kws[0]).lineno, kw0.col_offset)
    )):
        return kws[0].f

    return base0.f


def _next_ClassDef_bases(ast: AST, idx: int | None) -> _NextPrevRet:
    bases = ast.bases
    last = bases[-1]  # we know there is at least one .bases because otherwise we wouldn't be in this function

    if last.__class__ is not Starred:  # if no Starred then can't be mixed with keywords, unchecked walk forward
        if (idx := idx + 1) < len(bases):
            return bases[idx].f

        if a := ast.keywords:
            return a[0].f

        if a := ast.body:
            return a[0].f

        return None

    base = bases[idx]
    base_pos = (base.lineno, base.col_offset)

    if base is last:  # only need to find first keyword after this base
        for kw in ast.keywords:
            if (kw.lineno, kw.col_offset) > base_pos:
                return kw.f

        if a := ast.body:
            return a[0].f

        return None

    next_base = bases[idx + 1]
    next_base_pos = (next_base.lineno, next_base.col_offset)

    for kw in ast.keywords:
        kw_pos = (kw.lineno, kw.col_offset)

        if kw_pos > next_base_pos:
            return next_base.f
        if kw_pos > base_pos:
            return kw.f

    return next_base.f


def _next_ClassDef_keywords(ast: AST, idx: int | None) -> _NextPrevRet:
    bases = ast.bases
    kws = ast.keywords

    if (not bases
        or (last_base := bases[-1]).__class__ is not Starred  # if no bases or no Starred then can't be mixed with keywords, unchecked walk forward
        or (last_base_pos := (last_base.lineno, last_base.col_offset))
            < (kw_pos := ((kw := kws[idx]).lineno, kw.col_offset))  # last Starred base before this kw (likely case)
    ):
        if (idx := idx + 1) < len(kws):
            return kws[idx].f

        if a := ast.body:
            return a[0].f

        return None

    if kw is kws[-1]:  # no more kws, just find first base past this kw if any (will be Starred)
        for base in bases[-2::-1]:  # we search backwards because more likely to be shorter search
            if (base.lineno, base.col_offset) < kw_pos:
                break

            last_base = base

        return last_base.f

    next_kw = kws[idx + 1]
    next_kw_pos = (next_kw.lineno, next_kw.col_offset)

    for base in bases[-2::-1]:
        base_pos = (base.lineno, base.col_offset)

        if base_pos < kw_pos:
            break

        last_base = base
        last_base_pos = base_pos

    return (next_kw if next_kw_pos < last_base_pos else last_base).f


def _next_ClassDef_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None
'''.rstrip())

    elif ast_cls is AsyncFunctionDef:
        func_cls = 'FunctionDef'

    elif ast_cls is FunctionDef:
        print(r'''

def _next_FunctionDef_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.decorator_list:
        return a[0].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[0].f

    return ast.args.f


def _next_FunctionDef_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.decorator_list):
        return a[idx].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[0].f

    return ast.args.f


def _next_FunctionDef_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.type_params):  # if we got into this function then the AST has this
        return a[idx].f

    return ast.args.f


def _next_FunctionDef_args(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.returns:
        return a.f

    if a := ast.body:
        return a[0].f

    return None


def _next_FunctionDef_returns(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    return None


def _next_FunctionDef_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None
'''.rstrip())

    elif ast_cls is arguments:
        print(r'''

def _next_arguments_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.posonlyargs:
        return a[0].f
    if a := ast.args:
        return a[0].f
    if a := ast.vararg:
        return a.f
    if a := ast.kwonlyargs:
        return a[0].f
    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_posonlyargs(ast: AST, idx: int | None) -> _NextPrevRet:
    posonlyargs = ast.posonlyargs
    nposonlyargs = len(posonlyargs)
    defaults = ast.defaults

    if defaults:
        idefault = len(defaults) - nposonlyargs - len(ast.args) + idx

        if idefault >= 0:
            return defaults[idefault].f

    if (idx := idx + 1) < nposonlyargs:
        return posonlyargs[idx].f

    if a := ast.args:
        return a[0].f
    if a := ast.vararg:
        return a.f
    if a := ast.kwonlyargs:
        return a[0].f
    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_args(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    nargs = len(args)
    defaults = ast.defaults

    if defaults:
        idefault = len(defaults) - nargs + idx

        if idefault >= 0:
            return defaults[idefault].f

    if (idx := idx + 1) < nargs:
        return args[idx].f

    if a := ast.vararg:
        return a.f
    if a := ast.kwonlyargs:
        return a[0].f
    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_defaults(ast: AST, idx: int | None) -> _NextPrevRet:
    ndefaults = len(ast.defaults)
    idx += 1

    if idx == ndefaults:  # end of defaults
        if a := ast.vararg:
            return a.f
        if a := ast.kwonlyargs:
            return a[0].f
        if a := ast.kwarg:
            return a.f

        return None

    args = ast.args
    iarg = len(args) - ndefaults + idx

    if iarg >= 0:
        return args[iarg].f

    return ast.posonlyargs[iarg].f


def _next_arguments_vararg(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.kwonlyargs:
        return a[0].f
    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_kwonlyargs(ast: AST, idx: int | None) -> _NextPrevRet:
    kw_default = ast.kw_defaults[idx]

    if kw_default:
        return kw_default.f

    if (idx := idx + 1) < len(a := ast.kwonlyargs):
        return a[idx].f

    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_kw_defaults(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.kwonlyargs):
        return a[idx].f

    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_kwarg(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    elif ast_cls is TypeVar:
        print(r'''

def _next_TypeVar_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.bound:
        return a.f

    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _next_TypeVar_bound(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _next_TypeVar_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    elif ast_cls is ParamSpec:
        print(r'''

def _next_ParamSpec_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _next_ParamSpec_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    elif ast_cls is TypeVarTuple:
        print(r'''

def _next_TypeVarTuple_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _next_TypeVarTuple_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None
'''.rstrip())

    elif PRUNE_EMPTY_FUNCS and len(fields) == 1:  # if no fields then doesn't need its own functions
        NEXT_FUNCS[(cls_name, None)] = '_next_None'

        continue

    else:
        special = False

    for i, field in enumerate(fields):
        func_name = f'_next_{func_cls}_{field or "START"}'

        NEXT_FUNCS[(cls_name, field)] = func_name

        if special:
            continue

        body = []
        cur_card = _FIELD_CARDINALITY[(ast_cls, field)]  # this node already returned, just need to see if have to keep iterating it or move on to next field

        if cur_card == '*':
            body.append(f'    if (idx := idx + 1) < len(a := ast.{field}):\n        return a[idx].f')

        for next_field in fields[i + 1:]:
            next_card = _FIELD_CARDINALITY[(ast_cls, next_field)]

            if next_card == '*':
                body.append(f'    if a := ast.{next_field}:\n        return a[0].f')
            elif next_card == '?':
                body.append(f'    if a := ast.{next_field}:\n        return a.f')

            else:
                body.append(f'    return ast.{next_field}.f')

                break

        else:
            if PRUNE_EMPTY_FUNCS and field is fields[-1] and not body:  # if last field and nothing in body then doesn't need its own function
                NEXT_FUNCS[(cls_name, field)] = '_next_None'

                continue

            body.append('    return None')

        comment = '  # pragma: no cover' if ast_cls is FunctionType else ''

        print(f'\n\ndef {func_name}(ast: AST, idx: int | None) -> _NextPrevRet:{comment}\n' + '\n\n'.join(body))


print('\n\nNEXT_FUNCS = {')

for key, val in NEXT_FUNCS.items():
    print(f'    ({key[0]}, {key[1]!r}): {val},')

print('}')
