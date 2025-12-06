"""Extended `AST` parse. Allows parsing bits and pieces of valid python `AST` trees which are not normally parsable
individually with `ast.parse()`.

The parse functions in this module are oriented towards parsing all valid elements which they name which may include
parsing things which are not those elements, common sense is applied liberally though. And just because an element is
parsed successfully doesn't mean it may not need parentheses if used in the way intended. Or that it needs a trailing
newline due to comment ending without an explicit trailing newline.
"""

from __future__ import annotations

import re
from ast import parse as ast_parse, unparse as ast_unparse, fix_missing_locations
from typing import Any, Callable, Literal, Mapping, get_args

from . import fst

from .asttypes import (
    AST,
    Add,
    And,
    Assign,
    BitOr,
    BitXor,
    BitAnd,
    BoolOp,
    ClassDef,
    Compare,
    Del,
    Div,
    Eq,
    ExceptHandler,
    Expr,
    Expression,
    FloorDiv,
    GeneratorExp,
    Gt,
    GtE,
    Interactive,
    In,
    Invert,
    Is,
    IsNot,
    LShift,
    List,
    ListComp,
    Load,
    Lt,
    LtE,
    MatMult,
    MatchSequence,
    Mod,
    Module,
    Mult,
    Name,
    Not,
    NotEq,
    NotIn,
    Or,
    Pass,
    Pow,
    RShift,
    Slice,
    Starred,
    Store,
    Sub,
    Tuple,
    UAdd,
    USub,
    alias,
    arg,
    arguments,
    boolop,
    cmpop,
    comprehension,
    expr,
    keyword,
    match_case,
    mod,
    operator,
    pattern,
    stmt,
    unaryop,
    withitem,
    type_param,
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

from .astutil import (
    pat_alnum,
    FIELDS,
    OPSTR2CLS_UNARY,
    OPSTR2CLS_BIN,
    OPSTR2CLS_CMP,
    OPSTR2CLS_BOOL,
    OPCLS2STR,
    bistr,
    walk,
    reduce_ast,
)

from .common import next_frag, shortstr

__all__ = [
    'Mode',
    'ParseError',
    'unparse',
    'parse',
    'parse_all',
    'parse_strict',
    'parse_Module',
    'parse_Expression',
    'parse_Interactive',
    'parse_stmt',
    'parse_stmts',
    'parse_ExceptHandler',
    'parse__ExceptHandlers',
    'parse_match_case',
    'parse__match_cases',
    'parse_expr',
    'parse_expr_all',
    'parse_expr_arglike',
    'parse_expr_slice',
    'parse_Tuple_elt',
    'parse_Tuple',
    'parse__Assign_targets',
    'parse_boolop',
    'parse_operator',
    'parse_unaryop',
    'parse_cmpop',
    'parse_comprehension',
    'parse__comprehensions',
    'parse__comprehension_ifs',
    'parse_arguments',
    'parse_arguments_lambda',
    'parse_arg',
    'parse_keyword',
    'parse_alias',
    'parse__aliases',
    'parse_Import_name',
    'parse__Import_names',
    'parse_ImportFrom_name',
    'parse__ImportFrom_names',
    'parse_withitem',
    'parse__withitems',
    'parse_pattern',
    'parse_type_param',
    'parse__type_params',
    'parse__expr_arglikes',
    'parse__BoolOp_dangling_left',
    'parse__BoolOp_dangling_right',
    'parse__Compare_dangling_left',
    'parse__Compare_dangling_right',
]


_re_non_lcont_newline  = re.compile(r'(?<!\\)\n')
_re_trailing_comma     = re.compile(r'(?: [)\s]* (?: (?: \\ | \#[^\n]* ) \n )? )* ,', re.VERBOSE)  # trailing comma search ignoring comments and line continuation backslashes
_re_first_src          = re.compile(r'^ ([^\S\n]*) ([^\s\\#]+)', re.VERBOSE | re.MULTILINE)  # search for non-comment non-linecont coding source code starting on a new line
_re_next_src_space     = re.compile(r'  ([^\S\n]+) ([^\s\\#]+)', re.VERBOSE | re.MULTILINE)  # match for non-comment non-linecont coding source code starting not necessarily on a new line but with at least one whitespace, meant for followup search for multiword code like 'is not'
_re_next_src_no_space  = re.compile(r'  ([^\S\n]*) ([^\s\\#]+)', re.VERBOSE | re.MULTILINE)  # match for non-comment non-linecont coding source code starting not necessarily on a new line and no whitespace constraint

_re_parse_all_category = re.compile(r'''
    (?P<stmt>                          (?: assert | break | class | continue | def | del | from | global | import | nonlocal | pass | raise | return | try | while | with ) \b ) |
    (?P<await_lambda_yield>            (?: await | lambda | yield ) \b ) |
    (?P<True_False_None>               (?: True | False | None ) \b ) |
    (?P<async_or_for>                  (?: async | for ) \b ) |
    (?P<if>                            (?: if ) \b ) |
    (?P<except>                        (?: except ) \b ) |
    (?P<case>                          (?: case ) \b ) |
    (?P<not>                           (?: not ) \b ) |
    (?P<boolop>                        (?: and | or ) \b ) |
    (?P<cmpop_w>                       (?: is | in ) \b ) |
    (?P<syntax_error>                  (?: elif | else | finally | as ) \b ) |
    (?P<match_type_identifier>         (?: match | type | [^\d\W][''' + pat_alnum + r''']* ) \b ) |
    (?P<stmt_or_expr_or_pat_or_witem>  (?: [(\[{"'.\d] ) ) |
    (?P<minus>                         (?: - ) ) |
    (?P<starstar>                      (?: \*\* ) ) |
    (?P<star>                          (?: \* ) ) |
    (?P<at>                            (?: @ ) ) |
    (?P<operator>                      (?: // | / | % | << | >> | \| | \^ | & ) ) |
    (?P<plus>                          (?: \+ ) ) |
    (?P<colon>                         (?: : ) ) |
    (?P<cmpop_o>                       (?: == | != | <= | < | >= | > ) ) |
    (?P<tilde>                         (?: ~ ) )
''', re.MULTILINE | re.VERBOSE)

Mode = Literal[
    'all',
    'strict',
    'exec',
    'eval',
    'single',
    'stmts',
    'stmt',
    'ExceptHandler',
    '_ExceptHandlers',
    'match_case',
    '_match_cases',
    'expr',
    'expr_all',
    'expr_arglike',
    'expr_slice',
    'Tuple_elt',
    'Tuple',
    '_Assign_targets',
    '_decorator_list',
    'boolop',
    'operator',
    'unaryop',
    'cmpop',
    'comprehension',
    '_comprehensions',
    '_comprehension_ifs',
    'arguments',
    'arguments_lambda',
    'arg',
    'keyword',
    'alias',
    '_aliases',
    'Import_name',
    '_Import_names',
    'ImportFrom_name',
    '_ImportFrom_names',
    'withitem',
    '_withitems',
    'pattern',
    'type_param',
    '_type_params',
    '_expr_arglikes',
] | type[AST]

"""Extended parse modes:
- `'all'`: Check all possible parse modes (from most likely to least). There is syntax overlap so certain types will
    never be returned, for example `TypeVar` is always shadowed by `AnnAssign`. Since this attempts many parses before
    failing it is slower to do so than other modes, though the most likely success is just as fast. Will never return an
    `Expression` or `Interactive`.
- `'strict'`: Attempt parse minumum valid parsable code. If only one statement then return the statement itself instead
    of the `Module`. If that statement is an `Expr` then return the expression instead of the statement. If nothing
    present then return empty `Module`. Doesn't attempt any of the other parse modes which would not normally be
    parsable by python, just anything that can be parsed natively by `ast.parse()`.
- `'exec'`: Parse to a `Module`. Same as passing `Module` type or `'stmts'`. Same as `ast.parse()` mode 'exec'.
- `'eval'`: Parse to an `Expression`. Same as passing `Expression` type. Same as `ast.parse()` mode 'eval'.
- `'single'`: Parse to an `Interactive`. Same as passing `Interactive` type. Same as `ast.parse()` mode 'single'.
- `'stmts'`: Parse zero or more `stmt`s returned in a `Module`. Same as passing `'exec'` or `Module`.
- `'stmt'`: Parse a single `stmt` returned as itself. Same as passing `stmt` type.
- `'ExceptHandler'`: Parse as a single `ExceptHandler` returned as itself. Same as passing `ExceptHandler` type.
- `'_ExceptHandlers'`: Parse zero or more `ExceptHandler`s returned in an `_ExceptHandlers` SPECIAL SLICE.
- `'match_case'`: Parse a single `match_case` returned as itself. Same as passing `match_case` type.
- `'_match_cases'`: Parse zero or more `match_case`s returned in a `_match_cases` SPECIAL SLICE.
- `'expr'`: "expression", parse a single `expr` returned as itself. This is differentiated from the following modes by
    the handling of slices and starred expressions. In this mode `a:b` and `*not v` are syntax errors. Same as passing
    `expr` type.
- `'expr_all'`: Parse to any kind of expression including `Slice`, `*not a` or `Tuple` of any of those combined (but
    unparenthesized in that case).
- `'expr_arglike'`: Accept special syntax for `Starred` (call argument, class base definition, slice implicit tuple),
    same as `'expr'` except that in this mode `a:b` is a syntax error and `*not v` parses to a starred expression
    `*(not v)`.
- `'expr_slice'`: "slice expression", same as `'expr'` except that in this mode `a:b` parses to a `Slice` and `*not v`
    parses to a single element tuple containing a starred expression `(*(not v),)`.
- `'Tuple_elt'`: "tuple element expression" as in a `Tuple` that can be anywhere including a `Subscript.slice`. Same
    as `'expr'` except that in this mode `a:b` parses to a `Slice` and `*not v` parses to a starred expression
    `*(not v)`. `Tuples` are parsed but cannot contain `Slice`s or arglike expressions.
- `'Tuple'`: Parse to a `Tuple` which may contain anything that a tuple can contain like multiple `Slice`s and arglike
    expressions. If it contains `Slice`s or arglikes then it must not be parenthesized (as per python syntax).
- `'_Assign_targets'`: Parse zero or more `Assign` targets returned in a `_Assign_targets` SPECIAL SLICE, with `=` as
    separators and an optional trailing `=`.
- `'_decorator_list'`: Parse zero or more decorators returned in a `_decorator_list` SPECIAL SLICE. Each decorator must
    have a leading `@`.
- `'boolop'`: Parse to a `boolop` operator.
- `'operator'`: Parse to an `operator` operator.
- `'unaryop'`: Parse to a `unaryop` operator.
- `'cmpop'`: Parse to a `cmpop` compare operator.
- `'comprehension'`: Parse a single `comprehension` returned as itself. Same as passing `comprehension` type.
- `'_comprehensions'`: Parse zero or more `comprehension`s returned in a `_comprehensions` SPECIAL SLICE.
- `'_comprehension_ifs'`: Parse zero or more `comprehension` `ifs` returned in a `_comprehension_ifs` SPECIAL SLICE.
- `'arguments'`: Parse as `arguments` for a `FunctionDef` or `AsyncFunctionDef` returned as itself. In this mode
    type annotations are allowed for the arguments. Same as passing `arguments` type.
- `'arguments_lambda'`: Parse as `arguments` for a `Lambda` returned as itself. In this mode type annotations
    are not allowed for the arguments.
- `'arg'`: Parse as a single `arg` returned as itself. Same as passing `arg` type.
- `'keyword'`: Parse as a single `keyword` returned as itself. Same as passing `keyword` type.
- `'alias'`: Parse as a single `alias` returned as itself. Either starred or dotted versions are accepted. Same
    as passing `alias` type.
- `'_aliases'`: Parse zero or more `alias`es returned in a `_aliases` SPECIAL SLICE. Either starred or dotted versions
    are accepted. Does not need trailing comma for a single element.
- `'Import_name'`: Parse as a single `alias` returned as itself, with starred version being a syntax error. This is the
    `alias` used in `Import.names`.
- `'_Import_names'`: Parse zero or more `alias` returned in a `_aliases` SPECIAL SLICE, with starred version being a
    syntax error. Does not need trailing comma for a single element. This is the `alias` used in `Import.names`.
- `'ImportFrom_name'`: Parse as a single `alias` returned as itself, with dotted version being a syntax error. This is
    the `alias` used in `ImportFrom.names`.
- `'_ImportFrom_names'`: Parse zero or more `alias` returned in a `_aliases` SPECIAL SLICE, with dotted version being a
    syntax error. Does not need trailing comma for a single element. This is the `alias` used in `ImportFrom.names`.
- `'withitem'`: Parse as a single `withitem` returned as itself. Same as passing `withitem` type.
- `'_withitems'`: Parse zero or more `withitem`s returned in a `_withitems` SPECIAL SLICE.
- `'pattern'`: Parse as a a single `pattern` returned as itself. Same as passing `pattern` type.
- `'type_param'`: Parse as a single `type_param` returned as itself, either `TypeVar`, `ParamSpec` or
    `TypeVarTuple`. Same as passing `type_param` type.
- `'_type_params'`: Parse zero or more `type_param`s returned in a `_type_params` SPECIAL SLICE. Does not need trailing
    comma for a single element.
- `type[AST]`: If an `AST` type is passed then will attempt to parse to this type. This can be used to narrow
    the scope of desired return, for example `Constant` will parse as an expression but fail if the expression
    is not a `Constant`. These overlap with the string specifiers to an extent but not all of them. For example
    `AST` type `expr` is the same as passing `'expr'`. Not all string specified modes are can be matched, for example
    `'arguments_lambda'`. Likewise `'exec'` and `'stmts'` specify the same parse mode. `Tuple` parse also allows parsing
    `Slice`s in the `Tuple` as well as otherwise invalid star notation `*not a`.
- `str(type[AST])`: Same as `type[AST]`.
"""


def _fixing_unparse(ast: AST) -> str:
    """"fixing" unparse because it will fix missing locations."""

    try:
        return ast_unparse(ast)

    except AttributeError as exc:
        if not str(exc).endswith("has no attribute 'lineno'"):
            raise

    fix_missing_locations(ast)

    return ast_unparse(ast)


def _unparse_Tuple(ast: AST) -> str:
    src = _fixing_unparse(ast)

    if (elts := ast.elts) and any(isinstance(e, Slice) for e in elts):  # tuples with Slices cannot have parentheses
        return src[1 : -1]

    return src


def _unparse__ExceptHandlers(ast: AST) -> str:
    return _fixing_unparse(Module(body=ast.handlers, type_ignores=[]))


def _unparse__match_cases(ast: AST) -> str:
    return _fixing_unparse(Module(body=ast.cases, type_ignores=[]))


def _unparse__Assign_targets(ast: AST) -> str:
    return _fixing_unparse(Assign(targets=ast.targets, value=Name(id='', ctx=Load(), lineno=1, col_offset=0,
                                                                  end_lineno=1, end_col_offset=0),
                                  lineno=1, col_offset=0, end_lineno=1, end_col_offset=0)).rstrip()


def _unparse__decorator_list(ast: AST) -> str:
    return _fixing_unparse(ClassDef(name='c', bases=[], keywords=[],
                                    body=[Pass(lineno=1, col_offset=0, end_lineno=1, end_col_offset=0)],
                                    decorator_list=ast.decorator_list,
                                    lineno=1, col_offset=0, end_lineno=1, end_col_offset=0))[:-18]  # [:.rindex('\nclass c:\n    pass')]


def _unparse__comprehensions(ast: AST) -> str:
    return _fixing_unparse(ListComp(elt=Name(id='_', ctx=Load(), lineno=1, col_offset=0,
                                             end_lineno=1, end_col_offset=0),
                                    generators=ast.generators, lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                           )[3:-1]


def _unparse__comprehension_ifs(ast: AST) -> str:
    return _fixing_unparse(ListComp(elt=Name(id='_', ctx=Load(), lineno=1, col_offset=0,
                                             end_lineno=1, end_col_offset=0),
                                    generators=[comprehension(target=Name(id='_', ctx=Store(), lineno=1, col_offset=0,
                                                                          end_lineno=1, end_col_offset=0),
                                                              iter=Name(id='_', ctx=Load(), lineno=1, col_offset=0,
                                                                        end_lineno=1, end_col_offset=0),
                                                              ifs=ast.ifs, is_async=0)]),
                           )[14:-1]


def _unparse__aliases(ast: AST) -> str:
    return _fixing_unparse(List(elts=ast.names, lineno=1, col_offset=0, end_lineno=1, end_col_offset=0))[1:-1]


def _unparse__withitems(ast: AST) -> str:
    return _fixing_unparse(List(elts=ast.items, lineno=1, col_offset=0, end_lineno=1, end_col_offset=0))[1:-1]


def _unparse__type_params(ast: AST) -> str:
    return _fixing_unparse(List(elts=ast.type_params, lineno=1, col_offset=0, end_lineno=1, end_col_offset=0))[1:-1]


_UNPARSE_FUNCS = {
    Tuple:              _unparse_Tuple,
    Invert:             lambda ast: '~',
    Not:                lambda ast: 'not',
    UAdd:               lambda ast: '+',
    USub:               lambda ast: '-',
    Add:                lambda ast: '+',
    Sub:                lambda ast: '-',
    Mult:               lambda ast: '*',
    MatMult:            lambda ast: '@',
    Div:                lambda ast: '/',
    Mod:                lambda ast: '%',
    LShift:             lambda ast: '<<',
    RShift:             lambda ast: '>>',
    BitOr:              lambda ast: '|',
    BitXor:             lambda ast: '^',
    BitAnd:             lambda ast: '&',
    FloorDiv:           lambda ast: '//',
    Pow:                lambda ast: '**',
    Eq:                 lambda ast: '==',
    NotEq:              lambda ast: '!=',
    Lt:                 lambda ast: '<',
    LtE:                lambda ast: '<=',
    Gt:                 lambda ast: '>',
    GtE:                lambda ast: '>=',
    Is:                 lambda ast: 'is',
    IsNot:              lambda ast: 'is not',
    In:                 lambda ast: 'in',
    NotIn:              lambda ast: 'not in',
    And:                lambda ast: 'and',
    Or:                 lambda ast: 'or',
    comprehension:      lambda ast: _fixing_unparse(ast).lstrip(),  # strip prefix space from this
    _ExceptHandlers:    _unparse__ExceptHandlers,
    _match_cases:       _unparse__match_cases,
    _Assign_targets:    _unparse__Assign_targets,
    _decorator_list:    _unparse__decorator_list,
    _comprehensions:    _unparse__comprehensions,
    _comprehension_ifs: _unparse__comprehension_ifs,
    _aliases:           _unparse__aliases,
    _withitems:         _unparse__withitems,
    _type_params:       _unparse__type_params,
}


def _ast_parse(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    if src.endswith('\\\n'):  # python doesn't like trailing line continuation (which we may actually want to parse like this)
        src += '\n'

    return ast_parse(src, **parse_params)


def _ast_parse1(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse a single statment."""

    if src.endswith('\\\n'):  # python doesn't like trailing line continuation (which we may actually want to parse like this)
        src += '\n'

    body = ast_parse(src, **parse_params).body

    if len(body) != 1:
        raise SyntaxError('unexpected multiple statements')

    return body[0]


def _ast_parse1_case(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse a single `match_case`."""

    if src.endswith('\\\n'):  # python doesn't like trailing line continuation (which we may actually want to parse like this)
        src += '\n'

    body = ast_parse(src, **parse_params).body

    if len(body) != 1 or len(cases := body[0].cases) != 1:
        raise SyntaxError('expecting single element')

    return cases[0]


def _astloc_from_src(src: str, lineno: int = 1) -> dict[str, int]:
    """Get whole `AST` location from whole source string, starting at `lineno`. Used to get location for SPECIAL SLICE
    custom `AST` containers."""

    last_line = src if (i := src.rfind('\n')) == -1 else src[i + 1:]

    return {
        'lineno': lineno,
        'col_offset': 0,
        'end_lineno': lineno + src.count('\n'),
        'end_col_offset': len(last_line.encode())
    }


def _offset_linenos(ast: AST, delta: int) -> AST:
    """Offset `AST` tree line numbers."""

    for a in walk(ast):
        if end_lineno := getattr(a, 'end_lineno', None):
            a.end_lineno = end_lineno + delta
            a.lineno += delta

    return ast


def _fix_unparenthesized_tuple_parsed_parenthesized(src: str, ast: AST) -> None:
    """Fix a parsed `Tuple` locations which had original source unparenthesized but which was parenthesized for the
    parse."""

    lines = src.split('\n')
    elts = ast.elts
    e0 = elts[0]
    en = elts[-1]
    ast.lineno = e0.lineno
    ast.col_offset = e0.col_offset
    end_ln = en.end_lineno - 2  # -2 because of extra line introduced in parse
    end_col = len(lines[end_ln].encode()[:en.end_col_offset].decode())  # bistr(lines[end_ln]).b2c(en.end_col_offset)

    if (not (frag := next_frag(lines, end_ln, end_col, ast.end_lineno - 3, 0x7fffffffffffffff))  # if nothing following then last element is ast end, -3 because end also had \n tacked on
        or not frag.src.startswith(',')  # if no comma then last element is ast end
    ):
        ast.end_lineno = en.end_lineno
        ast.end_col_offset = en.end_col_offset

    else:
        end_ln, end_col, _ = frag
        ast.end_lineno = end_ln + 2
        ast.end_col_offset = len(lines[end_ln][:end_col + 1].encode())


def _has_trailing_comma(src: str, end_lineno: int, end_col_offset: int) -> bool:
    """See if there is a trailing comma after `(end_lineno, end_col_offset)`."""

    pos = 0

    for _ in range(end_lineno - 1):  # skip leading lines
        pos = src.find('\n', pos) + 1  # assumed to all be there

    pos += len(src[pos : pos + end_col_offset].encode()[:end_col_offset].decode())

    return bool(_re_trailing_comma.match(src, pos))


def _parse_all__comprehensions(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse either a single `comprehension` preferentially or multiple `comprehensions`s returned in `_comprehensions`.
    Called from `parse_all()` on finding source which may parse to a `comprehension` so there may be at least one."""

    ast = parse__comprehensions(src, parse_params)

    return ast if len(ast.generators) != 1 else ast.generators[0]


def _parse_all__withitems(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse either a single `withitem` preferentially or multiple `withitems`s returned in `_withitems`.
    Called from `parse_all()` on finding source which may parse to a `withitem` so there may be at least one."""

    ast = parse__withitems(src, parse_params)

    return (ast if len(ast.items) != 1 or
                   _has_trailing_comma(src, (i0 := (i0 := ast.items[0]).optional_vars or i0.context_expr).end_lineno,
                                       i0.end_col_offset) else
            ast.items[0])


def _parse_all__type_params(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse either a single `type_param` preferentially or multiple `type_param`s returned in `_type_params`. Called
    from `parse_all()` on finding source which may parse to a `type_param` so there may be at least one."""

    ast = parse__type_params(src, parse_params)

    return (ast if len(ast.type_params) != 1 or
                   _has_trailing_comma(src, (tp0 := ast.type_params[0]).end_lineno, tp0.end_col_offset) else
            ast.type_params[0])


def _parse_all_multiple(src: str, parse_params: Mapping[str, Any], stmt: bool, rest: list[Callable]) -> AST:
    """Attempt to parse one at a time using functions from a list until one succeeds."""

    if stmt:
        try:
            return reduce_ast(parse_stmts(src, parse_params), True)
        except SyntaxError:
            pass

    for parse in rest:
        try:
            return parse(src, parse_params)
        except SyntaxError:
            pass

    raise ParseError('invalid syntax')


def _parse_op(src: str, type_name: str, opstr2cls: dict[str, type[AST]]) -> AST:
    '''"Parse" an operator, either simple or compound like 'is not' or 'not in'.'''

    if not (m := _re_first_src.search(src)):
        raise SyntaxError(f'expecting {type_name}, got nothing')

    op = m.group(2)

    if opstr2cls is OPSTR2CLS_CMP:  # this may be compound two-word operator
        if op == 'is':  # check for 'is not'
            end = m.end()

            if (n := (_re_next_src_space.match(src, end)) or _re_first_src.search(src, end)) and n.group(2) == 'not':
                op = 'is not'
                m = n

        elif op == 'not':  # check for 'not in'
            end = m.end()

            if (n := (_re_next_src_space.match(src, end)) or _re_first_src.search(src, end)) and n.group(2) == 'in':
                op = 'not in'
                m = n

    if not (kls := opstr2cls.get(op)):
        raise SyntaxError(f'expecting {type_name}, got {shortstr(op)!r}')

    end = m.end()

    if m := (_re_next_src_space.match(src, end) or _re_first_src.search(src, end)):
        raise SyntaxError(f'unexpected code after {type_name}, {shortstr(m.group(2))!r}')

    return kls()


# ----------------------------------------------------------------------------------------------------------------------

class ParseError(SyntaxError):
    """Not technically a syntax error but mostly not the code we were expecting."""


def unparse(ast: AST) -> str:
    """AST unparse that handles misc case of comprehension starting with a single space by stripping it as well as
    removing parentheses from `Tuple`s with `Slice`s. @private"""

    return _UNPARSE_FUNCS.get(ast.__class__, _fixing_unparse)(ast)


def parse(src: str, mode: Mode = 'all', parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse any source to an AST, including things which normal `ast.parse()` doesn't handle, like individual
    `comprehension`s. Can be given a target type to parse or else will try to various parse methods until it finds one
    that succeeds (if any).

    **WARNING!** Does not guarantee `src` can be plugged directly into a node of the type it is being parsed for without
    parentheses (especially for `Tuple`s).

    **Parameters**:
    - `src`: The source to parse.
    - `mode`: Either one of the standard `ast.parse()` modes `exec`, `eval` or `single` to parse to that type of module
        or one of our specific strings like `'_ExceptHandlers'` or an actual `AST` type to parse to. If the mode is
        provided and cannot parse to the specified target then an error is raised and no other parse types are tried.
        See `Mode`.
    - `parse_params`: Dictionary of optional parse parameters to pass to `ast.parse()`, can contain `filename`,
        `type_comments` and `feature_version`.

    @private
    """

    if parse := _PARSE_MODE_FUNCS.get(mode):
        ast = parse(src, parse_params)

        mode_type = _AST_TYPE_BY_NAME_OR_TYPE.get(mode)  # `expr` or expr -> expr, etc...

        if mode_type and not isinstance(ast, mode_type):
            raise ParseError(f'could not parse to {mode_type.__name__}, got {ast.__class__.__name__}')

        return ast

    if not isinstance(mode, type) or not issubclass(mode, AST):
        raise ValueError(f'invalid parse mode {mode!r}')

    raise ParseError(f'cannot parse to {mode.__name__}')


def parse_all(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """All parse modes. Get a hint from starting source and attempt parse according to that from most probable to least
    of what it could be. @private"""

    if not (first := _re_first_src.search(src)):
        return _ast_parse(src, parse_params)  # should return empty Module with src trivia

    if not (cat := _re_parse_all_category.match(first.group(2))):
        _ast_parse(src, parse_params)  # should raise SyntaxError

        raise RuntimeError('should not get here')

    groupdict = cat.groupdict()

    if groupdict['stmt_or_expr_or_pat_or_witem']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, _parse_all__withitems, parse__Assign_targets))  # parse_expr_all because could be Slice

    if groupdict['match_type_identifier']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, parse_arguments, parse_arguments_lambda,
                                    _parse_all__withitems, parse_arg, _parse_all__type_params, parse__Assign_targets))

    if groupdict['stmt']:
        return reduce_ast(parse_stmts(src, parse_params), True)

    if groupdict['True_False_None']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, _parse_all__withitems))

    if groupdict['async_or_for']:
        return _parse_all_multiple(src, parse_params, not first.group(1), (_parse_all__comprehensions,))

    if groupdict['await_lambda_yield']:
        return _parse_all_multiple(src, parse_params, not first.group(1), (parse_expr_all,))

    if groupdict['if']:
        return _parse_all_multiple(src, parse_params, True, (parse__comprehension_ifs,))

    if groupdict['except']:
        return reduce_ast(parse__ExceptHandlers(src, parse_params), True)

    if groupdict['case']:
        try:
            return reduce_ast(parse__match_cases(src, parse_params), True)
        except SyntaxError:
            pass

        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, parse_arguments, parse_arguments_lambda,
                                    _parse_all__withitems, parse_arg, _parse_all__type_params, parse__Assign_targets))

    if groupdict['at']:
        return _parse_all_multiple(src, parse_params, True, (parse__decorator_list,))

    if groupdict['star']:
        ast = _parse_all_multiple(src, parse_params, not first.group(1),
                                  (parse_expr_all, parse_pattern, parse_arguments, parse_arguments_lambda,
                                   _parse_all__type_params, parse_operator, parse__Assign_targets))

        if isinstance(ast, Assign) and len(targets := ast.targets) == 1 and isinstance(targets[0], Starred):  # '*T = ...' validly parses to Assign statement but is invalid compile, but valid type_param so reparse as that
            return _parse_all__type_params(src, parse_params)

        return ast

    if groupdict['minus']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, _parse_all__withitems, parse_operator))

    if groupdict['not']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, _parse_all__withitems, parse_unaryop, parse_cmpop))

    if groupdict['tilde']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, _parse_all__withitems, parse_unaryop))

    if groupdict['colon']:
        return _parse_all_multiple(src, parse_params, False, (parse_expr_all,))

    if groupdict['starstar']:
        return _parse_all_multiple(src, parse_params, False, (parse_arguments, parse_arguments_lambda,
                                                              _parse_all__type_params, parse_operator))

    if groupdict['plus']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, _parse_all__withitems, parse_operator))

    if groupdict['cmpop_w']:
        return parse_cmpop(src, parse_params)

    if groupdict['cmpop_o']:
        return parse_cmpop(src, parse_params)

    if groupdict['boolop']:
        return parse_boolop(src, parse_params)

    if groupdict['operator']:
        return parse_operator(src, parse_params)

    # groupdict['syntax_error'] or something else unrecognized

    _ast_parse(src, parse_params)  # should raise SyntaxError

    raise RuntimeError('should not get here')


def parse_strict(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Attempt to parse valid parsable statements and then reduce to a single statement or expressing if possible. Only
    parses what `ast.parse()` can, no funny stuff. @private"""

    return reduce_ast(_ast_parse(src, parse_params), True)


def parse_Module(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Module`, ast.parse(mode='exec')'. @private"""

    return _ast_parse(src, {**parse_params, 'mode': 'exec'})


def parse_Expression(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Expression`, `ast.parse(mode='eval'). @private"""

    return _ast_parse(src, {**parse_params, 'mode': 'eval'})


def parse_Interactive(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Interactive`. @private"""

    if not src.endswith('\n'):  # because otherwise error for block statement on single line like `if a: b`
        src = src + '\n'

    return _ast_parse(src, {**parse_params, 'mode': 'single'})


def parse_stmts(src: str, parse_params: Mapping[str, Any] = {}) -> AST:  # same as parse_Module() but I want the IDE context coloring
    """Parse zero or more `stmt`s and return them in a `Module` `body` (just `ast.parse()` basically). @private"""

    return _ast_parse(src, parse_params)


def parse_stmt(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `stmt` and return as itself. @private"""

    body = _ast_parse(src, parse_params).body

    if len(body) != 1:
        raise ParseError('expecting single stmt')

    return body[0]


def parse_ExceptHandler(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `ExceptHandler` and return as itself. @private"""

    handlers = parse__ExceptHandlers(src, parse_params).handlers

    if len(handlers) != 1:
        raise ParseError('expecting single ExceptHandler')

    return handlers[0]


def parse__ExceptHandlers(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `ExceptHandler`s and return them in an `_ExceptHandlers` SPECIAL SLICE. @private"""

    try:
        ast = _ast_parse1(f'try: pass\n{src}\nfinally: pass', parse_params)
    except IndentationError:
        raise

    except SyntaxError:
        if (m := _re_first_src.search(src)) and m.group(1):
            raise IndentationError('unexpected indent') from None

        try:
            ast = _ast_parse(f'try: pass\n{src}', parse_params)  # just reparse without our finally block to confirm if that was the error
        except SyntaxError:
            pass

        else:
            if len(ast.body) == 1:
                raise ParseError("not expecting 'finally' block") from None
            else:
                raise ParseError('expecting only exception handlers`') from None

        raise

    if ast.orelse:
        raise ParseError("not expecting 'else' block")

    ast = _ExceptHandlers(handlers=ast.handlers, **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


def parse_match_case(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `match_case` and return as itself. @private"""

    cases = parse__match_cases(src, parse_params).cases

    if len(cases) != 1:
        raise ParseError('expecting single match_case')

    return cases[0]


def parse__match_cases(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `match_case`s and return them in a `_match_cases` SPECIAL SLICE. @private"""

    lines = [bistr('match x:'),
             bistr(' case None: pass'),
             *[bistr(' ' + l) for l in src.split('\n')]]

    ast = _ast_parse1('\n'.join(lines), parse_params)

    if not (cases := ast.cases[1:]):
        return _match_cases(cases=[], **_astloc_from_src(src, 1))

    fst_ = fst.FST(ast, lines, None, parse_params=parse_params, lcopy=False)
    lns = fst_._get_indentable_lns(2, docstr=False)

    if len(lns) != len(lines) - 2:  # if there are multiline strings then we need to dedent them and reparse, because of f-strings, TODO: optimize out second reparse if no f-strings
        strlns = set(range(2, len(lines)))

        strlns.difference_update(lns)

        for ln in strlns:
            lines[ln] = bistr(lines[ln][1:])

        ast = _ast_parse1('\n'.join(lines), parse_params)
        fst_ = fst.FST(ast, lines, None, parse_params=parse_params, lcopy=False)

    a0 = cases[0]
    an = cases[-1]
    lineno = a0.f.lineno
    end_lineno = an.f.end_lineno

    lns_ = set()

    for ln in lns:
        lines[ln] = bistr(lines[ln][1:])

        lns_.add(ln - 1)

    for a in walk(ast):
        del a.f  # remove all trace of FST

        if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
            a.lineno = lineno = a.lineno - 2
            a.end_lineno = end_lineno = a.end_lineno - 2

            if lineno in lns_:
                a.col_offset -= 1

            if end_lineno in lns_:
                a.end_col_offset = end_col_offset - 1

    return _match_cases(cases=ast.cases[1:], **_astloc_from_src(src, 1))


def parse_expr(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a "standard" `expr`, only things which are normally valid in an `expr` location, no `Slices` or
    `Starred` expressions which are only valid as a `Call` arg (`*not a`). @private"""

    try:
        body = _ast_parse(src, parse_params).body
    except SyntaxError:
        pass
    else:
        if len(body) == 1 and isinstance(b0 := body[0], Expr):  # if parsed to single expression then done
            return b0.value

    try:
        ast = _ast_parse1(f'(\n{src}\n)', parse_params).value  # has newlines or indentation

    except SyntaxError:
        try:
            elts = _ast_parse1(f'(\n{src}\n,)', parse_params).value.elts  # Starred expression with newlines or indentation
        except SyntaxError:
            raise SyntaxError('invalid expression (standard)') from None

        ast = elts[0]

        assert isinstance(ast, Starred) and len(elts) == 1

    else:
        if isinstance(ast, GeneratorExp) and ast.lineno == 1 and ast.col_offset == 0:  # wrapped something that looks like a GeneratorExp and turned it into that, bad
            raise SyntaxError('expecting expression, got unparenthesized GeneratorExp')

        if isinstance(ast, Tuple) and ast.lineno == 1:  # tuple with newlines included grouping pars which are not in source, fix
            if not ast.elts:
                raise SyntaxError('expecting expression')

            _fix_unparenthesized_tuple_parsed_parenthesized(src, ast)  # we have to do some work to find a possible comma

    return _offset_linenos(ast, -1)


def parse_expr_all(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to any kind of expression including `Slice`, `*not a` or `Tuple` of any of those combined. Lone `*a`
    `Starred` is returned as a `Starred` and not `Tuple` as would be in a slice. @private"""

    try:
        ast = parse_expr_slice(src, parse_params)

    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11
        try:
            ast = parse_expr_arglike(src, parse_params)  # expr_arglike instead of expr because py 3.10 won't pick up `*not a` in a slice above
        except SyntaxError:
            raise SyntaxError('invalid expression (all types)') from None

    else:
        if (isinstance(ast, Tuple)
            and len(elts := ast.elts) == 1
            and isinstance(e0 := elts[0], Starred)  # check for '*starred' acting as '*starred,'
            and e0.end_col_offset == ast.end_col_offset
            and e0.end_lineno == ast.end_lineno
        ):
            return e0

    return ast


def parse_expr_arglike(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `expr` in the context of a `Call.args` which treats `Starred` differently. @private"""

    try:
        return parse_expr(src, parse_params)
    except SyntaxError:  # stuff like '*not a'
        pass

    try:
        value = _ast_parse1(f'f(\n{src}\n,)', parse_params).value
    except SyntaxError:
        raise SyntaxError('invalid argument-like expression') from None

    args = value.args

    if len(args) != 1 or value.keywords:
        raise ParseError('expecting single argumnent-like expression')

    ast = args[0]

    # if isinstance(ast, GeneratorExp):  # wrapped something that looks like a GeneratorExp and turned it into that, bad
    #     raise ParseError('expecting argumnent-like expression, got unparenthesized GeneratorExp')

    return _offset_linenos(ast, -1)


def parse_expr_slice(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `Slice` or anything else that can go into `Subscript.slice` (`expr`), e.g. "start:stop:step" or "name"
    or even "a:b, c:d:e, g". Using this, naked `Starred` expressions parse to single element `Tuple` with the `Starred`
    as the only element (on py 3.11, py 3.10 is an error in this case). @private"""

    try:
        ast = _ast_parse1(f'a[\n{src}\n]', parse_params).value.slice

    except SyntaxError:  # maybe 'yield', also could be unparenthesized 'tuple' containing 'Starred' on py 3.10
        try:
            ast = _ast_parse1(f'a[(\n{src}\n)]', parse_params).value.slice
        except SyntaxError:
            raise SyntaxError('invalid slice expression') from None

        if isinstance(ast, GeneratorExp):  # wrapped something that looks like a GeneratorExp and turned it into that, bad
            raise SyntaxError('expecting slice expression, got unparenthesized GeneratorExp') from None

        if isinstance(ast, Tuple):  # only py 3.10 because otherwise the parse above would have gotten it
            if ast.elts:
                raise SyntaxError('cannot have unparenthesized tuple containing Starred in slice') from None

            raise SyntaxError('expecting slice expression') from None

    return _offset_linenos(ast, -1)


def parse_Tuple_elt(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to any `expr` which can be an element of a `Tuple` anywhere, including `Slice` and arglike expressions like
    `*not a` on py 3.11+ (both in a `Tuple` in `Subscript.slice`).

    Naked `Starred` expression parses to just the `Starred` and not a `Tuple` like in `parse_expr_slice()`.

    Does not allow a `Tuple` with `Slice` in it as it is expected that this expression is already in a slice `Tuple` and
    nested `Tuple`s with `Slice`s are not allowed.

    @private
    """

    try:
        ast = parse_expr_slice(src, parse_params)
    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11
        pass

    else:
        if not isinstance(ast, Tuple):
            return ast

        if (len(elts := ast.elts) == 1
            and isinstance(e0 := elts[0], Starred)  # check for '*starred' acting as '*starred,' due to py 3.11 'a[*starred]' sneaky tuple syntax
            and e0.end_col_offset == ast.end_col_offset
            and e0.end_lineno == ast.end_lineno
        ):
            return e0

    return parse_expr(src, parse_params)


def parse_Tuple(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `Tuple` which may or may not contain `Slice`s and otherwise invalid syntax in normal `Tuple`s like
    `*not a` (if not parenthesized). @private"""

    try:
        ast = parse_expr_slice(src, parse_params)
        from_slice = True

    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11
        try:
            ast = parse_expr(src, parse_params)
        except SyntaxError:
            raise SyntaxError('invalid tuple') from None

        from_slice = False

    if not isinstance(ast, Tuple):
        raise ParseError(f'expecting Tuple, got {ast.__class__.__name__}')

    if (from_slice
        and len(elts := ast.elts) == 1
        and isinstance(e0 := elts[0], Starred)  # check for '*starred' acting as '*starred,' due to py 3.11 'a[*starred]' sneaky tuple syntax
        and e0.end_col_offset == ast.end_col_offset
        and e0.end_lineno == ast.end_lineno
    ):
        raise ParseError('expecting Tuple, got Starred')

    return ast


def parse__Assign_targets(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `Assign` targets and return them in a `_Assign_targets` SPECIAL SLICE. Takes `=` as separators
    and accepts an optional trailing `=`. @private"""

    src_ = '\\' + src if src.startswith('\n') else src  # we allow an initial non-line-continued newline because that is a slice indicator to start on new line and will have line continuation added in slice put to Assign

    try:
        ast = _ast_parse1(f'_=\\\n{src_}  _', parse_params)  # try assuming src has trailing equals

    except SyntaxError:
        try:
            ast = _ast_parse1(f'_=\\\n{src_} =_', parse_params)  # now check assuming src does not have trailing equals
        except SyntaxError:
            raise SyntaxError('invalid Assign targets slice') from None

    if not isinstance(ast, Assign):
        raise ParseError(f'expecting Assign targets, got {ast.__class__.__name__}')

    name = ast.value

    if not isinstance(name, Name):
        raise ParseError(f'unexpected value type parsing Assign targets, {name.__class__.__name__}')
    elif name.id != '_':
        raise ParseError(f'unexpected value id parsing Assign targets, {name.value!r}')

    targets = ast.targets

    del targets[0]  # remove syntax check dummy target `_`

    # if targets and targets[0].col_offset:
    #     raise IndentationError('unexpected indent')

    ast = _Assign_targets(targets=targets, **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


def parse__decorator_list(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more decorators and return them in a `_decorator_list` SPECIAL SLICE. Each decorator must have a
    leading `@`. @private"""

    ast = _ast_parse1(f'{src}\nclass c: pass', parse_params)

    return _decorator_list(decorator_list=ast.decorator_list, **_astloc_from_src(src, 1))


def parse_boolop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `boolop`. We do it manually. We refuse to do equivalent of `ast.parse('or')` on principle. @private"""

    return _parse_op(src, 'boolop', OPSTR2CLS_BOOL)


def parse_operator(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `operator`. We do it manually. We refuse to do equivalent of `ast.parse('+')` on principle.
    @private"""

    return _parse_op(src, 'operator', OPSTR2CLS_BIN)


def parse_unaryop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `unaryop`. We do it manually. We refuse to do equivalent of `ast.parse('~')` on principle.
    @private"""

    return _parse_op(src, 'unaryop', OPSTR2CLS_UNARY)


def parse_cmpop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `cmpop`. We do it manually. We refuse to do equivalent of `ast.parse('==')` on principle. @private"""

    return _parse_op(src, 'cmpop', OPSTR2CLS_CMP)


def parse_comprehension(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `comprehension`, e.g. "async for i in something() if i". @private"""

    ast = _ast_parse1(f'[_ \n{src}\n]', parse_params).value

    if not isinstance(ast, ListComp):
        raise ParseError('expecting comprehension')

    generators = ast.generators

    if len(generators) != 1:
        raise ParseError('expecting single comprehension')

    return _offset_linenos(generators[0], -1)


def parse__comprehensions(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `comprehension`s, returned as a `_comprehensions` SPECIAL SLICE. @private"""

    ast = _ast_parse1(f'[_ for _ in _\n{src}\n]', parse_params).value

    if not isinstance(ast, ListComp):
        raise ParseError('expecting comprehensions')

    generators = ast.generators

    if generators[0].ifs:
        raise ParseError('expecting comprehensions, got comprehension ifs')

    ast = _comprehensions(generators=generators[1:], **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


def parse__comprehension_ifs(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `comprehension` `if`s (including the `if`), returned as a `_comprehension_ifs` SPECIAL
    SLICE. @private"""

    ast = _ast_parse1(f'[_ for _ in _\n{src}\n]', parse_params).value

    if not isinstance(ast, ListComp) or len(ast.generators) != 1 or not isinstance(ast.generators[0].iter, Name):
        raise ParseError('expecting comprehension ifs')

    ast = _comprehension_ifs(ifs=ast.generators[0].ifs, **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


def parse_arguments(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `arguments`, e.g. "a: list[str], /, b: int = 1, *c, d=100, **e". @private"""

    ast = _ast_parse1(f'def f(\n{src}\n): pass', parse_params).args

    return _offset_linenos(ast, -1)


def parse_arguments_lambda(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `arguments` for a `Lambda`, e.g. "a, /, b, *c, d=100, **e". @private"""

    ast = _ast_parse1(f'(lambda \n{src}\n: None)', parse_params).value.args

    return _offset_linenos(ast, -1)


def parse_arg(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `arg`, e.g. "var: list[int]". @private"""

    try:
        args = _ast_parse1(f'def f(\n{src}\n): pass', parse_params).args

    except SyntaxError:  # may be '*vararg: *starred'
        try:
            args = _ast_parse1(f'def f(*\n{src}\n): pass', parse_params).args
        except SyntaxError:
            raise SyntaxError('invalid arg') from None

        if args.posonlyargs or args.args or args.kwonlyargs or args.defaults or args.kw_defaults or args.kwarg:
            ast = None
        else:
            ast = args.vararg

    else:
        if (args.posonlyargs
            or args.vararg
            or args.kwonlyargs
            or args.defaults
            or args.kw_defaults
            or args.kwarg
            or len(args := args.args) != 1
        ):
            ast = None
        else:
            ast = args[0]

    if ast is None:
        raise ParseError('expecting single argument without default')

    return _offset_linenos(ast, -1)


def parse_keyword(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `keyword`, e.g. "var=val". @private"""

    keywords = _ast_parse1(f'f(\n{src}\n)', parse_params).value.keywords

    if len(keywords) != 1:
        raise ParseError('expecting single keyword')

    return _offset_linenos(keywords[0], -1)


def parse_alias(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `alias`, allowing star or dotted notation or star, e.g. "name as alias". @private"""

    if '*' in src:
        try:
            return parse_ImportFrom_name(src, parse_params)
        except SyntaxError:  # '*' could have been in a comment
            pass

    return parse_Import_name(src, parse_params)


def parse__aliases(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `_aliases` of `alias` SPECIAL SLICE, allowing star or dotted, e.g. "name as alias". @private"""

    if '*' in src:
        try:
            return parse__ImportFrom_names(src, parse_params)
        except SyntaxError:  # '*' could have been in a comment
            pass

    return parse__Import_names(src, parse_params)


def parse_Import_name(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `alias`, allowing dotted notation but not star (not all aliases are created equal), e.g.
    "name as alias". @private"""

    try:
        names = _ast_parse1(f'import \\\n{src}', parse_params).names

    except SyntaxError as first_exc:
        try:
            src = _re_non_lcont_newline.sub('\\\n', src)
            names = _ast_parse1(f'import \\\n{src}', parse_params).names  # multiline?

        except SyntaxError:
            raise first_exc from None

    if len(names) != 1:
        raise ParseError('expecting single name')

    return _offset_linenos(names[0], -1)


def parse__Import_names(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `_aliases` of `alias` SPECIAL SLICE, allowing dotted notation but not star. @private"""

    try:
        names = _ast_parse1(f'import \\\n{src}', parse_params).names

    except SyntaxError as first_exc:
        if not _re_first_src.search(src):  # empty?
            names = []

        else:
            try:
                src = _re_non_lcont_newline.sub('\\\n', src)
                names = _ast_parse1(f'import \\\n{src}', parse_params).names  # multiline?

            except SyntaxError:
                raise first_exc from None

    ast = _aliases(names=names, **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


def parse_ImportFrom_name(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `alias`, allowing star but not dotted. @private"""

    try:
        names = _ast_parse1(f'from . import \\\n{src}', parse_params).names  # this instead of parentheses because could be '*' which doesn't like parentheses

    except SyntaxError as first_exc:
        try:
            src = _re_non_lcont_newline.sub('\\\n', src)
            names = _ast_parse1(f'from . import \\\n{src}', parse_params).names  # multiline?

        except SyntaxError:
            raise first_exc from None

    if len(names) != 1:
        raise ParseError('expecting single name')

    return _offset_linenos(names[0], -1)


def parse__ImportFrom_names(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `_aliases` of `alias` SPECIAL SLICE, allowing star but not dotted. @private"""

    try:
        names = _ast_parse1(f'from . import \\\n{src}', parse_params).names  # this instead of parentheses because could be '*' which doesn't like parentheses

    except SyntaxError as first_exc:
        if not _re_first_src.search(src):  # empty?
            names = []

        else:
            try:
                src = _re_non_lcont_newline.sub('\\\n', src)
                names = _ast_parse1(f'from . import \\\n{src}', parse_params).names  # multiline?

            except SyntaxError:
                raise first_exc from None

    ast = _aliases(names=names, **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


def parse_withitem(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `withitem`, e.g. "something() as var". @private"""

    items = _ast_parse1(f'with (\n{src}\n): pass', parse_params).items

    if len(items) == 1:
        ast = items[0].context_expr

        if isinstance(ast, GeneratorExp):  # wrapped something that looks like a GeneratorExp and turned it into that, bad
            raise SyntaxError('expecting withitem, got unparenthesized GeneratorExp')

        if isinstance(ast, Tuple) and not ast.elts and ast.col_offset == 5:
            raise SyntaxError('expecting withitem')

    else:  # unparenthesized Tuple
        if all(i.optional_vars is None for i in items):
            items = _ast_parse1(f'with ((\n{src}\n)): pass', parse_params).items

        if len(items) != 1:
            raise ParseError('expecting single withitem')

        ast = items[0].context_expr

        assert isinstance(ast, Tuple)

        _fix_unparenthesized_tuple_parsed_parenthesized(src, ast)

    return _offset_linenos(items[0], -1)


def parse__withitems(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to zero or more `withitem`s, returned as a `_withitems` SPECIAL SLICE. @private"""

    items = _ast_parse1(f'with (\n{src}\n): pass', parse_params).items

    if len(items) == 1:
        ast = items[0].context_expr

        if isinstance(ast, GeneratorExp):  # wrapped something that looks like a GeneratorExp and turned it into that, bad
            raise SyntaxError('expecting withitem, got unparenthesized GeneratorExp')

        if isinstance(ast, Tuple) and not ast.elts and ast.col_offset == 5:
            items = []

    ast = _withitems(items=items, **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


def parse_pattern(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `pattern`, e.g. "{a.b: i, **rest}". @private"""

    try:
        ast = _ast_parse1_case(f'match _:\n case \\\n{src}: pass', parse_params).pattern

    except SyntaxError:  # first in case needs to be enclosed
        try:
            ast = _ast_parse1_case(f'match _:\n case (\\\n{src}\n): pass', parse_params).pattern

        except SyntaxError:  # now just the case of a lone MatchStar
            try:
                patterns = _ast_parse1_case(f'match _:\n case [\\\n{src}\n]: pass', parse_params).pattern.patterns
            except SyntaxError:
                raise SyntaxError('invalid pattern') from None

            if len(patterns) != 1:
                raise ParseError('expecting single pattern') from None

            ast = patterns[0]

        else:
            if ast.lineno < 3 and isinstance(ast, MatchSequence):
                if not (patterns := ast.patterns):
                    raise SyntaxError('empty pattern') from None

                ast.lineno = 3  # remove our delimiters from location
                ast.col_offset = 0
                ast.end_lineno = (p_1 := patterns[-1]).end_lineno
                ast.end_col_offset = p_1.end_col_offset

    return _offset_linenos(ast, -2)


def parse_type_param(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `type_param`, e.g. "t: Base = Subclass". @private"""

    type_params = _ast_parse1(f'type t[\n{src}\n] = None', parse_params).type_params

    if len(type_params) != 1:
        raise ParseError('expecting single type_param')

    ast = type_params[0]

    if _has_trailing_comma(src, ast.end_lineno - 1, ast.end_col_offset):
        raise ParseError('expecting single type_param, has trailing comma')

    return _offset_linenos(ast, -1)


def parse__type_params(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `type_param`s and return them in a `_type_params` SPECIAL SLICE. @private"""

    try:
        type_params = _ast_parse1(f'type t[\n{src}\n] = None', parse_params).type_params

    except SyntaxError:  # maybe empty
        if _re_first_src.search(src):  # if not empty then error
            raise

        type_params = []

    ast = _type_params(type_params=type_params, **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


# ......................................................................................................................
# internal parse stuff, not meant for direct user use

def parse__expr_arglikes(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `Tuple` of zero or more arglike expressions as would be seen as a sequence of `Call.args`. If there
    are parentheses then they belong to the elements as the `Tuple` itself cannot have any. If there is a single element
    it does not need to have a trailing comma.

    **WARNING!** The `Tuple` that is returned may be an invalid python `Tuple` as it may be an empty `Tuple` `AST` with
    source having no parentheses or an unparenthesized `Tuple` with incorrect start and stop locations. Intended as a
    convenience for putting slices.

    @private
    """

    try:
        value = _ast_parse1(f'f(\n{src}\n)', parse_params).value
    except SyntaxError:
        raise SyntaxError('invalid argument-like expression(s)') from None

    if value.keywords:
        raise ParseError('expecting only argumnent-like expression(s), got keyword')

    ast = Tuple(elts=value.args, ctx=Load(), **_astloc_from_src(src, 2))

    return _offset_linenos(ast, -1)


def parse__BoolOp_dangling_left(src: str, parse_params: Mapping[str, Any] = {}, *, loc_whole: bool = False) -> AST:
    """Parse to a `BoolOp` expecting an explicit dangling operator on left side, e.g. 'and b and c' or `or x'.

    **Parameters:**
    - `loc_whole': Whether the location of the root `BoolOp` should be the full source or just the `BoolOp` starting at
        the left dangling op.

    @private
    """

    try:
        ast = _ast_parse1(f'(_\n{src}\n)', parse_params).value
    except SyntaxError:
        raise SyntaxError('expecting BoolOp with dangling operator on left side') from None

    if not isinstance(ast, BoolOp):
        raise ParseError('expecting BoolOp with dangling operator on left side')

    del ast.values[0]

    ast = _offset_linenos(ast, -1)

    if loc_whole:
        loc = _astloc_from_src(src)
        ast.lineno = 1
        ast.col_offset = 0
        ast.end_lineno = loc['end_lineno']
        ast.end_col_offset = loc['end_col_offset']

    else:
        m = _re_first_src.search(src)  # left dangling operator, needs to become start position of BoolOp

        ast.lineno = src.count('\n', 0, m.start()) + 1
        ast.col_offset = len(m.group(1).encode())

    return ast


def parse__BoolOp_dangling_right(src: str, parse_params: Mapping[str, Any] = {}, *, loc_whole: bool = False) -> AST:
    """Parse to a `BoolOp` expecting an explicit dangling operator on right side, e.g. 'b and c and' or `x or'.

    **Parameters:**
    - `loc_whole': Whether the location of the root `BoolOp` should be the full source or just the `BoolOp` ending past
        the right dangling op.

    @private
    """

    try:
        ast = _ast_parse1(f'(\n{src}\n_)', parse_params).value
    except SyntaxError:
        raise SyntaxError('expecting BoolOp with dangling operator on right side') from None

    if not isinstance(ast, BoolOp):
        raise ParseError('expecting BoolOp with dangling operator on right side')

    values = ast.values

    del values[-1]

    ast = _offset_linenos(ast, -1)

    if loc_whole:
        loc = _astloc_from_src(src)
        ast.lineno = 1
        ast.col_offset = 0
        ast.end_lineno = loc['end_lineno']
        ast.end_col_offset = loc['end_col_offset']

    else:  # search for dangling op from end of last value
        valn = values[-1]
        end_lineno = valn.end_lineno
        end_col_offset = valn.end_col_offset
        pos = 0

        for _ in range(end_lineno - 1):  # find start of line of node
            pos = src.index('\n', pos) + 1

        op_len = 3 if isinstance(ast.op, And) else 2
        end_col = len(src[pos : pos + end_col_offset].encode()[:end_col_offset].decode())  # convert byte column to char column
        pos += end_col

        m = (_re_next_src_no_space.match(src, pos) or _re_first_src.search(src, pos))  # right dangling operator, needs to become end position of BoolOp

        if extra_lines := src.count('\n', pos, m.start()):
            ast.end_lineno = end_lineno + extra_lines
            ast.end_col_offset = len(m.group(1).encode()) + op_len

        else:
            ast.end_lineno = end_lineno
            ast.end_col_offset = end_col_offset + len(m.group(1).encode()) + op_len

    return ast


def parse__Compare_dangling_left(src: str, parse_params: Mapping[str, Any] = {}, *, loc_whole: bool = False) -> AST:
    """Parse to a `Compare` expecting an explicit dangling operator on left side, e.g. '< b == c' or `> x'.

    **Parameters:**
    - `loc_whole': Whether the location of the root `Compare` should be the full source or just the `Compare` starting
        at the left dangling op.

    **Returns:**
    - `Compare`: The operators and comparators will be in the `ops` and `comparators` fields and the `left` field will
        be a placeholder `AST` with location at the start of the left dangling operator, regardless of `loc_whole`.

    @private
    """

    try:
        ast = _ast_parse1(f'(_\n{src}\n)', parse_params).value
    except SyntaxError:
        raise SyntaxError('expecting Compare with dangling operator on left side') from None

    if not isinstance(ast, Compare):
        raise ParseError('expecting Compare with dangling operator on left side')

    ast.left = None  # no need to offset this

    ast = _offset_linenos(ast, -1)

    m = _re_first_src.search(src)  # left dangling operator, needs to become start position of `left`

    lineno = src.count('\n', 0, m.start()) + 1
    col_offset = len(m.group(1).encode())

    ast.left = Pass(lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset)  # placeholder AST

    if loc_whole:
        loc = _astloc_from_src(src)
        ast.lineno = 1
        ast.col_offset = 0
        ast.end_lineno = loc['end_lineno']
        ast.end_col_offset = loc['end_col_offset']

    else:
        ast.lineno = lineno
        ast.col_offset = col_offset

    return ast


def parse__Compare_dangling_right(src: str, parse_params: Mapping[str, Any] = {}, *, loc_whole: bool = False) -> AST:
    """Parse to a `Compare` expecting an explicit dangling operator on right side, e.g. 'b < c ==' or `x >'.

    **Parameters:**
    - `loc_whole': Whether the location of the root `Compare` should be the full source or just the `Compare` ending
        past the right dangling op.

    **Returns:**
    - `Compare`: The operators and comparators will be in the `ops`, `left` and `comparators` fields and the last
        `comparator` field will be a placeholder `AST` with location at the end of the right dangling operator,
        regardless of `loc_whole`.

    @private
    """

    try:
        ast = _ast_parse1(f'(\n{src}\n_)', parse_params).value
    except SyntaxError:
        raise SyntaxError('expecting Compare with dangling operator on right side') from None

    if not isinstance(ast, Compare):
        raise ParseError('expecting Compare with dangling operator on right side')

    comparators = ast.comparators
    comparators[-1] = None  # no need to offset this

    ast = _offset_linenos(ast, -1)

    valn = comparators[-2] if len(comparators) > 1 else ast.left  # search for dangling op from end of last comparator
    end_lineno = valn.end_lineno
    end_col_offset = valn.end_col_offset
    pos = 0

    for _ in range(end_lineno - 1):  # find start of line of node
        pos = src.index('\n', pos) + 1

    end_col = len(src[pos : pos + end_col_offset].encode()[:end_col_offset].decode())  # convert byte column to char column
    pos += end_col

    m = (_re_next_src_no_space.match(src, pos) or _re_first_src.search(src, pos))  # right dangling operator, needs to become end position of placeholder AST and maybe Compare

    if (op_cls := ast.ops[-1].__class__) not in (IsNot, NotIn):  # if not two-part operator then done searching
        op_len = len(OPCLS2STR[op_cls])

    else:  # two-part operator, find second part
        p = m.end()
        m = (_re_next_src_no_space.match(src, p) or _re_first_src.search(src, p))
        op_len = 3 if op_cls is IsNot else 2

    if extra_lines := src.count('\n', pos, m.start()):
        end_lineno = end_lineno + extra_lines
        end_col_offset = len(m.group(1).encode()) + op_len

    else:
        end_lineno = end_lineno
        end_col_offset = end_col_offset + len(m.group(1).encode()) + op_len

    comparators[-1] = Pass(lineno=end_lineno, col_offset=end_col_offset,
                           end_lineno=end_lineno, end_col_offset=end_col_offset)  # placeholder AST

    if loc_whole:
        loc = _astloc_from_src(src)
        ast.lineno = 1
        ast.col_offset = 0
        ast.end_lineno = loc['end_lineno']
        ast.end_col_offset = loc['end_col_offset']

    else:
        ast.end_lineno = end_lineno
        ast.end_col_offset = end_col_offset

    return ast


# ......................................................................................................................

_AST_TYPE_BY_NAME_OR_TYPE = {}  # {Module: Module, 'Module': Module, ...}  - filled out below

_PARSE_MODE_FUNCS = {  # these do not all guarantee will parse ONLY to that type but that will parse ALL of those types without error, not all parsed in desired but all desired in parsed
    'all':                    parse_all,
    'strict':                 parse_strict,
    'exec':                   parse_Module,
    'eval':                   parse_Expression,
    'single':                 parse_Interactive,
    'stmts':                  parse_stmts,
    'stmt':                   parse_stmt,
    'ExceptHandler':          parse_ExceptHandler,
    '_ExceptHandlers':        parse__ExceptHandlers,
    'match_case':             parse_match_case,
    '_match_cases':           parse__match_cases,
    'expr':                   parse_expr,
    'expr_all':               parse_expr_all,       # `a:b:c`, `*not c`, `*st`, `a,`, `a, b`, `a:b:c,`, `a:b:c, x:y:x, *st`, `*not c`
    'expr_arglike':           parse_expr_arglike,   # `*a or b`, `*not c`
    'expr_slice':             parse_expr_slice,     # `a:b:c`, `*not c`, `a:b:c, x:y:z`, `*st` -> `*st,` (py 3.11+)
    'Tuple_elt':              parse_Tuple_elt,      # `a:b:c`, `*not c`, `*st`
    'Tuple':                  parse_Tuple,          # `a,`, `a, b`, `a:b:c,`, `a:b:c, x:y:x, *st`, `*not a,` (py 3.11+)
    '_Assign_targets':        parse__Assign_targets,
    '_decorator_list':        parse__decorator_list,
    'boolop':                 parse_boolop,
    'operator':               parse_operator,
    'unaryop':                parse_unaryop,
    'cmpop':                  parse_cmpop,
    'comprehension':          parse_comprehension,
    '_comprehensions':        parse__comprehensions,
    '_comprehension_ifs':     parse__comprehension_ifs,
    'arguments':              parse_arguments,
    'arguments_lambda':       parse_arguments_lambda,
    'arg':                    parse_arg,
    'keyword':                parse_keyword,
    'alias':                  parse_alias,
    '_aliases':               parse__aliases,
    'Import_name':            parse_Import_name,
    '_Import_names':          parse__Import_names,
    'ImportFrom_name':        parse_ImportFrom_name,
    '_ImportFrom_names':      parse__ImportFrom_names,
    'withitem':               parse_withitem,
    '_withitems':             parse__withitems,
    'pattern':                parse_pattern,
    'type_param':             parse_type_param,
    '_type_params':           parse__type_params,
    mod:                      parse_Module,    # parsing with an AST type doesn't mean it will be parsable by ast module
    Expression:               parse_Expression,
    Interactive:              parse_Interactive,
    stmt:                     parse_stmt,
    ExceptHandler:            parse_ExceptHandler,
    match_case:               parse_match_case,
    expr:                     parse_expr,          # not _expr_all because those cases are handled in Starred, Slice and Tuple
    Starred:                  parse_expr_arglike,  # because could have form '*a or b' and we want to parse any form of Starred here
    Slice:                    parse_expr_slice,    # because otherwise would be parse_expr which doesn't do slice by default, parses '*a' to '*a,' on py 3.11+
    Tuple:                    parse_Tuple,         # because could have slice in it and we are parsing all forms including '*not a'
    boolop:                   parse_boolop,
    operator:                 parse_operator,
    unaryop:                  parse_unaryop,
    cmpop:                    parse_cmpop,
    comprehension:            parse_comprehension,
    arguments:                parse_arguments,
    arg:                      parse_arg,
    keyword:                  parse_keyword,
    alias:                    parse_alias,
    withitem:                 parse_withitem,
    pattern:                  parse_pattern,
    type_param:               parse_type_param,
    Load:                     lambda src, parse_params = {}: Load(),  # HACKS for verify() and other similar stuff
    Store:                    lambda src, parse_params = {}: Store(),
    Del:                      lambda src, parse_params = {}: Del(),
    _ExceptHandlers:          parse__ExceptHandlers,
    _match_cases:             parse__match_cases,
    _Assign_targets:          parse__Assign_targets,
    _decorator_list:          parse__decorator_list,
    _comprehensions:          parse__comprehensions,
    _comprehension_ifs:       parse__comprehension_ifs,
    _aliases:                 parse__aliases,
    _withitems:               parse__withitems,
    _type_params:             parse__type_params,
    '_expr_arglikes':         parse__expr_arglikes,
}  # automatically filled out with all AST types and their names derived from these

assert not set(get_args(get_args(Mode)[0])).symmetric_difference(k for k in _PARSE_MODE_FUNCS if isinstance(k, str)), \
    'Mode string modes do not match _PARSE_MODE_FUNCS table'

for ast_type in FIELDS:  # fill out _PARSE_MODE_FUNCS with all supported AST types and their class names as parse modes
    ast_name = ast_type.__name__

    _AST_TYPE_BY_NAME_OR_TYPE[ast_type] = _AST_TYPE_BY_NAME_OR_TYPE[ast_name] = ast_type

    if parse_func := _PARSE_MODE_FUNCS.get(ast_type):
        if ast_name not in _PARSE_MODE_FUNCS:  # for top level types already in table name is probably in table as well (and may be different in future?)
            _PARSE_MODE_FUNCS[ast_name] = parse_func

    else:
        base = ast_type

        while (base := base.__bases__[0]) is not AST:
            if parse_func := _PARSE_MODE_FUNCS.get(base):
                _PARSE_MODE_FUNCS[ast_type] = _PARSE_MODE_FUNCS[ast_name] = parse_func  # base ASTs not in table will not have name in table either

                break
