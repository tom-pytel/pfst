"""Convert `Code` to `FST`, coercion happens here."""

from __future__ import annotations

from typing import Any, Callable, Literal, Mapping, Union
from unicodedata import normalize

from . import fst

from .asttypes import (
    ASTS_LEAF_EXPR,
    ASTS_LEAF_STMT,
    ASTS_LEAF_EXPR_STMT_OR_MOD,
    ASTS_LEAF_FTSTR_FMT_OR_SLICE,
    AST,
    Attribute,
    Constant,
    Dict,
    ExceptHandler,
    Expr,
    Expression,
    Interactive,
    List,
    Load,
    MatchAs,
    MatchMapping,
    MatchOr,
    MatchSequence,
    MatchSingleton,
    MatchStar,
    MatchValue,
    Module,
    Name,
    Pass,
    Set,
    Slice,
    Starred,
    Store,
    Try,
    TryStar,
    TypeVar,
    TypeVarTuple,
    Tuple,
    alias,
    arg,
    arguments,
    boolop,
    cmpop,
    comprehension,
    expr,
    keyword,
    match_case,
    operator,
    pattern,
    unaryop,
    withitem,
    type_param,
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

from .astutil import (
    constant,
    OPCLS2STR,
    is_valid_identifier,
    is_valid_identifier_dotted,
    is_valid_identifier_star,
    is_valid_identifier_alias,
    is_valid_target,
)

from .common import NodeError, pyver, shortstr, next_frag

from .parsex import (
    _fixing_unparse,
    ParseError,
    unparse,
    parse,
    parse_stmts,
    parse__ExceptHandlers,
    parse__match_cases,
    parse_expr,
    parse_expr_all,
    parse_expr_arglike,
    parse_expr_slice,
    parse_Tuple_elt,
    parse_Tuple,
    parse__Assign_targets,
    parse__decorator_list,
    parse__arglike,
    parse__arglikes,
    parse_boolop,
    parse_operator,
    parse_unaryop,
    parse_cmpop,
    parse_comprehension,
    parse__comprehensions,
    parse__comprehension_ifs,
    parse_arguments,
    parse_arguments_lambda,
    parse_arg,
    parse_keyword,
    parse_alias,
    parse__aliases,
    parse_Import_name,
    parse__Import_names,
    parse_ImportFrom_name,
    parse__ImportFrom_names,
    parse_withitem,
    parse__withitems,
    parse_pattern,
    parse_type_param,
    parse__type_params,
    parse__expr_arglikes,
)

__all__ = [
    'Code',
    'code_as_lines',
    'code_as_all',
    'code_as_stmts',
    'code_as__ExceptHandlers',
    'code_as__match_cases',
    'code_as_expr',
    'code_as_expr_all',
    'code_as_expr_arglike',
    'code_as_expr_slice',
    'code_as_Tuple_elt',
    'code_as_Tuple',
    'code_as__Assign_targets',
    'code_as__decorator_list',
    'code_as__arglike',
    'code_as__arglikes',
    'code_as_boolop',
    'code_as_operator',
    'code_as_unaryop',
    'code_as_cmpop',
    'code_as_comprehension',
    'code_as__comprehensions',
    'code_as__comprehension_ifs',
    'code_as_arguments',
    'code_as_arguments_lambda',
    'code_as_arg',
    'code_as_keyword',
    'code_as_alias',
    'code_as__aliases',
    'code_as_Import_name',
    'code_as__Import_names',
    'code_as_ImportFrom_name',
    'code_as__ImportFrom_names',
    'code_as_withitem',
    'code_as__withitems',
    'code_as_pattern',
    'code_as_type_param',
    'code_as__type_params',
    'code_as_identifier',
    'code_as_identifier_dotted',
    'code_as_identifier_star',
    'code_as_identifier_alias',
    'code_as_constant',
    'code_as__expr_arglikes',
]


Code = Union['fst.FST', AST, list[str], str]  ; """Code types accepted for put to `FST`."""
CodeAs = Callable[[Code, Mapping[str, Any]], 'fst.FST']  # + kwargs: *, sanitize: bool = False, coerce: bool = False

_ASTS_LEAF_EXPRISH_SEQ = frozenset([Tuple, List, Set, MatchSequence, _Assign_targets, _decorator_list, _arglikes,
                                    _comprehension_ifs, _aliases, _withitems, _type_params])

_EXPR_PARSE_FUNC_TO_NAME = {
    parse_Tuple:        'Tuple',
    parse_Tuple_elt:    'expression (tuple element)',
    parse_expr_slice:   'expression (slice)',
    parse_expr_arglike: 'expression (arglike)',
    parse_expr_all:     'expression (all types)',
    parse_expr:         'expression (standard)',
}


def _ast_coerce_to_ret_empty_str(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """These are the individual `AST` coerce functions.

    **Parameters:**
    - `ast`: The `AST` node to coerce, can be part of an `FST` tree.
    - `is_FST`: Whether the `ast` node is part of an `FST` tree, meaning it has source for any possible reparse which
        should be done in that case to get the correct locations.

    **Returns:**
    - `str`: An error string indicating why a coercion could not happen. Empty string for general uncoercability.
    - `(AST, is_nonstandard_tuple, unmake_which)`:
        - `AST`: The `AST` is the new node to use, it is either a child of the original node passed in or a completely
            new node created based on the node passed in.
        - `is_nonstandard_tuple`: This only has meaning if the node is an `FST`. Indicates that the `AST` it is a
            nonstandard `Tuple` which needs to be fixed with `_fix_tuple()` for `is_FST=True` because is unparenthesized
            and may be empty and may not have trailing comma on singleton, also start and stop locations may be
            incorrect. **WARNING!** This can only be used for top-level nodes like `_arglikes` because it is not handled
            recursively.
        - `unmake_which`: This only has meaning if the node is an `FST`. Indicates what kind of unmake should be done on
            the original tree. In reality the whole tree can always be unmade and in this case all that will happen is
            that new `FST` nodes will be created for it, but it may be more efficient to only unmake a part of the
            original tree if we know we will need the already-created `FST` node for some children, which saves some
            class instantiations.
            - `0`: Unmake the returned `AST` parents.
            - `1`: Unmake just the original `FST` root node, no children.
            - `2`: Unmake the entire original `FST`.
    """

    return ''

def _ast_coerce_to_expr_value(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    return ast.value, False, 0

def _ast_coerce_to_expr_stmtmod(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if len(body := ast.body) != 1:
        return 'multiple statements'

    if (ast := body[0]).__class__ is not Expr:
        return f'uncoercable type {ast.__class__.__name__}'

    return ast.value, False, 0

def _ast_coerce_to_expr_Expression(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    return ast.body, False, 0

def _ast_coerce_to_expr__Assign_targets(
    ast: AST, is_FST: bool, parse_params: Mapping[str, Any]
) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if is_FST:
        return 'FST has incompatible source'

    return Tuple(elts=ast.targets), False, 1

def _ast_coerce_to_expr__decorator_list(
    ast: AST, is_FST: bool, parse_params: Mapping[str, Any]
) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if is_FST:
        return 'FST has incompatible source'

    return Tuple(elts=ast.decorator_list), False, 1

def _ast_coerce_to_expr__arglikes(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    arglikes = ast.arglikes

    if any(a.__class__ is keyword for a in arglikes):
        return '_arglikes has a keyword'

    return Tuple(elts=arglikes, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                 end_col_offset=ast.end_col_offset), True, 1

def _ast_coerce_to_expr__comprehension_ifs(
    ast: AST, is_FST: bool, parse_params: Mapping[str, Any]
) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if is_FST:
        return 'FST has incompatible source'

    return Tuple(elts=ast.ifs), False, 1

def _ast_coerce_to_expr_arg(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    if ast.annotation:
        return 'arg has annotation'

    return Name(id=ast.arg, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                end_col_offset=ast.end_col_offset), False, 2

def _ast_coerce_to_expr_alias(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if ast.asname:
        return 'alias has asname'
    if ast.name == '*':
        return "star '*' alias"

    if '.' not in (name := ast.name):
        ast = Name(id=name, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                   end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    elif not is_FST:  # or (f := ast.f).end_ln != f.ln or f.end_col != f.col + len(name):  # NOTE: could calculate locations but parse_expr() is probably faster
        parts = name.split('.')[::-1]
        ast = Attribute(value=Name(id=parts.pop()), attr=parts.pop())  # no locations needed because we know this will be reparsed when not is_FST

        while parts:
            ast = Attribute(value=ast, attr=parts.pop())

    else:  # reparse is cheap and lazy for the locations, which are needed if is_FST
        try:
            ast = parse_expr(ast.f.src, parse_params)
        except Exception as exc:  # pragma: no cover  # sanity check, this shouldn't fail
            return str(exc)

        if ast.__class__ is not Attribute:
            return 'failed reparse to Attribute'  # pragma: no cover  # sanity

    return ast, False, 2

def _ast_coerce_to_expr__aliases(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    names = ast.names
    elts = []

    if names:
        for a in names:
            if a.asname:
                return 'alias has asname'
            if a.name == '*':
                return "star '*' alias"


        if not is_FST:
            for a in ast.names:
                res = _ast_coerce_to_expr_alias(a, is_FST, parse_params)

                if res.__class__ is str:
                    return res

                elts.append(res[0])

        else:  # reparse is cheap and lazy for the locations if there are any Attributes, which are needed if is_FST
            try:
                ast = parse_expr(ast.f.src, parse_params)
            except Exception as exc:  # pragma: no cover  # sanity check, this shouldn't fail
                return str(exc)

            if (ast_cls := ast.__class__) is Tuple:
                elts = ast.elts
            elif ast_cls in (Name, Attribute):
                elts = [ast]
            else:
                return 'failed reparse to Attribute'  # pragma: no cover  # sanity

    return Tuple(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                 end_col_offset=ast.end_col_offset), True, 2

def _ast_coerce_to_expr_withitem(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if ast.optional_vars:
        return 'withitem has optional_vars'

    return ast.context_expr, False, 1  # if coerce from withitem can reuse its AST

def _ast_coerce_to_expr__withitems(
    ast: AST, is_FST: bool, parse_params: Mapping[str, Any]
) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    elts = []

    for a in ast.items:
        if a.optional_vars:
            return 'withitem has optional_vars'

        elts.append(a.context_expr)

    return Tuple(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                 end_col_offset=ast.end_col_offset), True, 2

def _ast_coerce_to_expr_MatchSingleton(
    ast: AST, is_FST: bool, parse_params: Mapping[str, Any]
) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    return Constant(value=ast.value, lineno=ast.lineno, col_offset=ast.col_offset,
                    end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset), False, 2

def _ast_coerce_to_expr_MatchStar(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    name = ast.name
    lineno = ast.lineno
    end_lineno = ast.end_lineno
    col_offset = ast.col_offset
    end_col_offset = ast.end_col_offset

    return Starred(value=Name(id=name, ctx=Load(), lineno=end_lineno, col_offset=end_col_offset - len(name),
                              end_lineno=end_lineno, end_col_offset=end_col_offset),
                   ctx=Load(), lineno=lineno, col_offset=col_offset, end_lineno=end_lineno,
                   end_col_offset=end_col_offset), False, 2

def _ast_coerce_to_expr_MatchAs(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if ast.pattern:
        return 'MatchAs has pattern'

    return Name(id=ast.name, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset), False, 2

def _ast_coerce_to_expr_MatchSequence(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if not is_FST:
        ast_cls = List
    else:
        ast_cls = List if ast.f.is_delimited_matchseq() == '[]' else Tuple

    elts = []
    ret = ast_cls(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                  end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    for pat in ast.patterns:
        pat = _AST_COERCE_TO_EXPR_FUNCS.get(pat.__class__, _ast_coerce_to_ret_empty_str)(pat, is_FST, parse_params)

        if (pat_cls := pat.__class__) is str:
            return pat
        elif pat_cls is tuple:
            pat = pat[0]

        elts.append(pat)

    return ret, False, 2  # we do not unmake trees here for subpatterns because this return signals that the whole tree needs to be unmade (FST nodes will be recreated)

def _ast_coerce_to_expr_MatchMapping(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    keys = []
    values = []
    ret = Dict(keys=keys, values=values, lineno=ast.lineno, col_offset=ast.col_offset,
               end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    for key, pat in zip(ast.keys, ast.patterns, strict=True):
        pat = _AST_COERCE_TO_EXPR_FUNCS.get(pat.__class__, _ast_coerce_to_ret_empty_str)(pat, is_FST, parse_params)

        if (pat_cls := pat.__class__) is str:
            return pat
        elif pat_cls is tuple:
            pat = pat[0]

        keys.append(key)
        values.append(pat)

    if rest := ast.rest:
        keys.append(None)

        if not is_FST:
            values.append(Name(id=rest))

        else:
            f = ast.f
            lines = f.root._lines
            ln, col, end_ln, end_col = f._loc_MatchMapping_rest()

            values.append(Name(id=rest, ctx=Load(), lineno=ln + 1, col_offset=lines[ln].c2b(col), end_lineno=end_ln + 1,
                               end_col_offset=lines[end_ln].c2b(end_col)))

    return ret, False, 2

def _ast_coerce_to_expr_TypeVar(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if ast.bound:
        return 'TypeVar has bound'
    if getattr(ast, 'default_value', None):
        return 'TypeVar has default_value'

    return Name(id=ast.name, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset), False, 2

def _ast_coerce_to_expr_TypeVarTuple(ast: AST, is_FST: bool, parse_params: Mapping[str, Any]) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    if getattr(ast, 'default_value', None):
        return 'TypeVarTuple has default_value'

    name = ast.name
    lineno = ast.lineno
    end_lineno = ast.end_lineno
    col_offset = ast.col_offset
    end_col_offset = ast.end_col_offset

    return Starred(value=Name(id=name, ctx=Load(), lineno=end_lineno, col_offset=end_col_offset - len(name),
                              end_lineno=end_lineno, end_col_offset=end_col_offset),
                   ctx=Load(), lineno=lineno, col_offset=col_offset, end_lineno=end_lineno,
                   end_col_offset=end_col_offset), False, 2

def _ast_coerce_to_expr__type_params(
    ast: AST, is_FST: bool, parse_params: Mapping[str, Any]
) -> tuple[AST, bool, int]:
    """See `_ast_coerce_to_ret_empty_str()`."""

    elts = []

    for a in ast.type_params:
        if getattr(a, 'bound', None):
            return 'type_param has bound'
        if getattr(a, 'default_value', None):
            return 'type_param has default_value'

        ast_cls = a.__class__

        if ast_cls is TypeVar:
            a = Name(id=a.name, ctx=Load(), lineno=a.lineno, col_offset=a.col_offset,
                     end_lineno=a.end_lineno, end_col_offset=a.end_col_offset)

        elif ast_cls is TypeVarTuple:
            name = a.name
            lineno = a.lineno
            end_lineno = a.end_lineno
            col_offset = a.col_offset
            end_col_offset = a.end_col_offset

            a = Starred(value=Name(id=name, ctx=Load(), lineno=end_lineno, col_offset=end_col_offset - len(name),
                                   end_lineno=end_lineno, end_col_offset=end_col_offset),
                        ctx=Load(), lineno=lineno, col_offset=col_offset, end_lineno=end_lineno,
                        end_col_offset=end_col_offset)

        else:
            return f'incompatible type {ast_cls.__name__}'

        elts.append(a)

    return Tuple(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                 end_col_offset=ast.end_col_offset), True, 2

_AST_COERCE_TO_EXPR_FUNCS = {
    Module:             _ast_coerce_to_expr_stmtmod,
    Interactive:        _ast_coerce_to_expr_stmtmod,
    Expression:         _ast_coerce_to_expr_Expression,
    Expr:               _ast_coerce_to_expr_value,
    _Assign_targets:    _ast_coerce_to_expr__Assign_targets,
    _decorator_list:    _ast_coerce_to_expr__decorator_list,
    _arglikes:          _ast_coerce_to_expr__arglikes,
    _comprehension_ifs: _ast_coerce_to_expr__comprehension_ifs,
    arg:                _ast_coerce_to_expr_arg,
    alias:              _ast_coerce_to_expr_alias,  # can reparse in case of FST
    _aliases:           _ast_coerce_to_expr__aliases,  # TODO? to Tuple, has Name or Attribute
    withitem:           _ast_coerce_to_expr_withitem,
    _withitems:         _ast_coerce_to_expr__withitems,
    MatchValue:         _ast_coerce_to_expr_value,
    MatchSingleton:     _ast_coerce_to_expr_MatchSingleton,
    MatchSequence:      _ast_coerce_to_expr_MatchSequence,
    MatchMapping:       _ast_coerce_to_expr_MatchMapping,
    # MatchClass:         _ast_coerce_to_expr_MatchClass,  # TODO?  how to handle parentheses for locations, "a | (b | c)", "(a | (b | c)) | d"
    MatchStar:          _ast_coerce_to_expr_MatchStar,
    MatchAs:            _ast_coerce_to_expr_MatchAs,
    # MatchOr:            _ast_coerce_to_expr_MatchOr,  # TODO?  need locations of kwd_attrs identifiers
    TypeVar:            _ast_coerce_to_expr_TypeVar,
    TypeVarTuple:       _ast_coerce_to_expr_TypeVarTuple,
    _type_params:       _ast_coerce_to_expr__type_params,  # TODO? to Tuple, has Name or Starred
}


def _coerce_to_expr_ast(
    ast: AST, is_FST: bool, parse_params: Mapping[str, Any], expecting: str
) -> tuple[AST, bool]:
    """This is not like the `_coerce_to_?()` functions below, it just tries to coerce an `AST` to an expression `AST`,
    mostly by taking a contained expression `AST` but maybe by creating a new one from a string. Parsing is a possible
    action in case of `is_FST=True`. If is not an `FST` then it is assumed the node will be unparsed and reparsed so
    node creation in that case is just targetted at the `unparse()` and may not have locations or other things a full
    node would.

    This function will unmake the source `FST` if is one.

    **WARNING!** Can not assume any `AST` nodes returned from here have valid `FST` nodes even if `is_FST=True`. They
    must always be recreated.

    **Parameters:**
    - `ast`: The `AST` node to coerce, can be part of an `FST` tree.
    - `is_FST`: Whether the `ast` node is part of an `FST` tree, meaning it has source for any possible reparse which
        should be done in that case to get the correct locations.

    **Returns:**
    - `(AST, is_nonstandard_tuple)`: The coerced `AST` and a bool indicating whether it is a nonstandard tuple, which
        means it needs to be fixed with `_fix_tuple()` because is unparenthesized and may be empty and may not have
        trailing comma on singleton, also start and stop locations may be incorrect. Ignore nonstandard bool if is not
        `FST`.
    """

    ret = _AST_COERCE_TO_EXPR_FUNCS.get(ast.__class__, _ast_coerce_to_ret_empty_str)(ast, is_FST, parse_params)

    if ret.__class__ is str:
        raise NodeError(f'expecting {expecting}, got {ast.__class__.__name__}'
                        f', could not coerce{", " + ret if ret else ""}', rawable=True)  # ret here is reason str

    ret, is_nonstd_tuple, unmake_which = ret

    if is_FST:
        if not unmake_which:  # WARNING! make sure ast is only child of parent and whole parent chain is only-children if coerced!!!
            ret.f._unmake_fst_parents()
        elif unmake_which == 1:  # just the root node
            ast.f._unmake_fst_parents(self_=True)
        else:  # node was completely regenerated, unmake whole original (e.g. arg.arg coerced to new Name node, or complicated MatchSequence with nested stuff)
            ast.f._unmake_fst_tree()

    return ret, is_nonstd_tuple


def _coerce_to__slice_with_commas(
    code: Code,
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    to_cls: type[AST],
    always_reparse: bool = False,
) -> fst.FST | list[AST] | None:
    """Attempt coerce given code if is sequence type to one of our own SPECIAL SLICE types that has commas: `_arglikes`,
    `_aliases`, `_withitems` or _type_params`.

    **Returns:**
    - `FST`: Coerced tree ready for return.
    - `list[AST]`: Came from an `FST` so wasn't parsed so may need to coerce the individual elements, they are all valid
        `FST` `AST` nodes so need to unmake them if recreating nodes.
    - `None`: Coercion doesn't apply, try others.
    """

    ast = code
    ast_cls = code.__class__
    is_FST = False

    if not (ast_cls in _ASTS_LEAF_EXPRISH_SEQ
        or (is_FST := (ast_cls is fst.FST and (ast_cls := (ast := code.a).__class__) in _ASTS_LEAF_EXPRISH_SEQ))
    ):
        return None

    # if is_FST and (last_child := code.last_child()):  # remove trailing comma if present, needed for _aliases, preferred for the others
    #     _, _, ln, col = last_child.pars()
    #     _, _, end_ln, end_col = code.loc

    #     if (frag := next_frag(code._lines, ln, col, end_ln, end_col)) and frag.src.startswith(','):
    #         ln, col, _ = frag

    #         code._put_src(None, ln, col, ln, col + 1, True)

    if ast_cls not in (Tuple, List, Set):
        if is_FST:
            if ast_cls is _arglikes:  # if this is true then we are coercing to something other than _arglikes which will need this fix
                code._fix_arglikes(field='arglikes')
            elif ast_cls is MatchSequence and code.is_delimited_matchseq():
                code._trim_delimiters()

        ast, _ = _coerce_to_expr_ast(ast, is_FST, parse_params, to_cls.__name__)

    else:
        if ast_cls is Tuple:
            if any(e.__class__ is Slice for e in ast.elts):
                raise NodeError(f'expecting {to_cls.__name__}, got Tuple with a Slice in it, could not coerce',
                                rawable=True)

        if is_FST:
            if code.is_parenthesized_tuple() is not False:
                code._trim_delimiters()

            code._unmake_fst_parents(True)

    if is_FST:
        if not always_reparse:
            return ast.elts

        code._unmake_fst_tree(ast.elts)

        ast = parse(code.src, parse_params)

        assert ast.__class__ is to_cls  # sanity check

        return fst.FST(ast, code._lines, None, lcopy=False)

    trim_end = -2 if ast_cls is Tuple and len(ast.elts) == 1 else -1  # singleton tuple trim should remove trailing comma
    src = unparse(ast)[1 : trim_end]  # need to strip Tuple or List or Set unparsed delimiters
    lines = src.split('\n')
    ast = parse(src, parse_params)

    assert ast.__class__ is to_cls  # sanity check

    return fst.FST(ast, lines, None)


def _coerce_to__aliases_common(
    code: Code,
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    expecting: str,
    sanitize: bool,
    allow_dotted: bool,
) -> fst.FST | None:
    """Common to `_aliases`, `Import_names` and `ImportFrom_names`."""

    codea = getattr(code, 'a', None)

    fst_ = _coerce_to__slice_with_commas(code, parse_params, parse, _aliases)

    if fst_ is None:  # sequence as sequence?
        return None

    if fst_.__class__ is list:  # this means code is an FST
        elts = fst_
        ast = Tuple(elts=elts, ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                    end_col_offset=ls[-1].lenbytes)
        tmp = fst.FST(ast, ls, None, from_=code, lcopy=False)  # temporary Tuple so that we can unparenthesize everything
        names = []

        for e in elts:
            e.f._unparenthesize_grouping()  # names can't have pars

            if (e_cls := e.__class__) is Name:
                a = alias(name=e.id, lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                          end_col_offset=e.end_col_offset)

            elif e_cls is Attribute and allow_dotted:
                lineno = e.lineno
                col_offset = e.col_offset
                end_lineno = e.end_lineno
                end_col_offset = e.end_col_offset
                attr = e.attr

                while (e_cls := (e := e.value).__class__) is Attribute:
                    e.f._unparenthesize_grouping()

                    attr = f'{e.attr}.{attr}'

                if e_cls is not Name:
                    raise NodeError(f'expecting {expecting}, got {codea.__class__.__name__}'
                                    f', could not coerce, found {e_cls.__name__}')

                a = alias(name=f'{e.id}.{attr}', lineno=lineno, col_offset=col_offset, end_lineno=end_lineno,
                          end_col_offset=end_col_offset)

            else:
                raise NodeError(f'expecting {expecting}, got {codea.__class__.__name__}'
                                f', could not coerce, found {e_cls.__name__}')

            names.append(a)

        tmp._unmake_fst_tree()

        ast = _aliases(names=names, lineno=1, col_offset=0, end_lineno=tmp.end_lineno,
                       end_col_offset=tmp.end_col_offset)
        fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

    if names := fst_.a.names:  # remove trailing comma if present, not legal in Import/From names mostly (except parenthesized ImportFrom.names)
        _, _, ln, col = names[-1].f.loc
        _, _, end_ln, end_col = fst_.loc

        if (frag := next_frag(fst_._lines, ln, col, end_ln, end_col)) and frag.src.startswith(','):
            ln, col, _ = frag

            fst_._put_src(None, ln, col, ln, col + 1, True)

    return fst_._sanitize() if sanitize else fst_


# ......................................................................................................................

def _coerce_to__Assign_targets(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """These are coerce functions which attempt to convert to a specific type of node. For the most part and unless
    explicitly permitted, they only guarantee attempted coercion from an `AST` of `FST`, not source, even if that might
    work as a side-effect of how they coerce.

    If a coerce function can handle source (because we want to be able to parse a different source representation of the
    node than the one the default parse function for the type handles), then the attribute `coerce_src=True` should be
    set on the function. Most should have this False (or not present) as the parse attempt should already have given a
    definitive answer. Exists for stuff like `_decorator_names` and `_comprehension_ifs` where those parse functions
    expect a prefix like `@` or `if` but we want to allow expressions without the prefixes as well.
    """

    fst_ = code_as_expr(code, parse_params, sanitize=True, coerce=True)  # sanitize=True because Assign.targets can't have comments or other things that may break a logical line
    ast_ = fst_.a

    if not is_valid_target(ast_):
        raise NodeError(f'expecting Assign target, got {ast_.__class__.__name__}, could not coerce')

    fst_._set_ctx(Store)

    ast = _Assign_targets(targets=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                          end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([ast_], 'targets', True, False)  # _set_field() is alternative to putting ast_ in the ast.targets to begin with, this won't walk existing valid FST tree unnecessarily


def _coerce_to__decorator_list(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`. This function can coerce source."""

    fst_ = code_as_expr(code, parse_params, sanitize=sanitize, coerce=True)
    ln = fst_.pars().ln

    fst_._put_src('@', ln, 0, ln, 0, False)  # prepend '@' to expression on line of expression at start to make it a _decorator_list slice

    ast = _decorator_list(decorator_list=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                          end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'decorator_list', True, False)

_coerce_to__decorator_list.coerce_src = True


def _coerce_to__arglike(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    code_cls = code.__class__

    if code_cls is keyword or (code_cls is fst.FST and code.a.__class__ is keyword):
        return code_as_keyword(code, parse_params, sanitize=sanitize)  # pragma: no cover  # can't get here normally because _code_as() will see the keyword first and accept it

    fst_ = code_as_expr_arglike(code, parse_params, sanitize=sanitize, coerce=True)

    if fst_.is_parenthesized_tuple() is False:
        fst_._delimit_node()

    return fst_


def _coerce_to__arglikes(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = _coerce_to__slice_with_commas(code, parse_params, parse__arglikes, _arglikes)

    if fst_ is not None:  # sequence as sequence?
        if fst_.__class__ is list:  # this means code is an FST
            ast = _arglikes(arglikes=fst_, lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                            end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

        return fst_._sanitize() if sanitize else fst_

    # single element as sequence

    fst_ = code_as__arglike(code, parse_params, sanitize=sanitize, coerce=True)

    if fst_.is_parenthesized_tuple() is False:
        fst_._delimit_node()

    ast = _arglikes(arglikes=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                    end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'arglikes', True, False)


def _coerce_to__comprehensions(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = code_as_comprehension(code, parse_params, sanitize=sanitize, coerce=True)

    ast = _comprehensions(generators=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                          end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'generators', True, False)


def _coerce_to__comprehension_ifs(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`. This function can coerce source."""

    fst_ = code_as_expr(code, parse_params, sanitize=sanitize, coerce=True)

    if fst_.is_parenthesized_tuple() is False:
        fst_._delimit_node()

    ln, col, _, _ = fst_.pars()

    fst_._put_src('if ', ln, col, ln, col, False)  # prepend 'if' to expression to make it a _comprehension_ifs slice, we do it before the container because the container will have to start at 0, 0

    ast = _comprehension_ifs(ifs=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                             end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'ifs', True, False)

_coerce_to__comprehension_ifs.coerce_src = True


def _coerce_to_arg(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = code_as_expr(code, parse_params, sanitize=sanitize, coerce=True)
    ast_ = fst_.a

    if ast_.__class__ is not Name:
        raise NodeError(f'cannot coerce {ast_.__class__.__name__} to arg, must be Name')

    if fst_.pars().n:  # args can't have pars
        fst_._unparenthesize_grouping(False)

    ast = arg(arg=ast_.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
              end_col_offset=ast_.end_col_offset)

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_to_alias(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce "with a as b" items[0] -> "import a as b"?

    fst_ = code_as_expr(code, parse_params, sanitize=True, coerce=True)  # sanitize because where aliases are used then generally can't have junk, comments specifically would break Import.names aliases
    ast_ = a = fst_.a
    name = ''

    while a.__class__ is Attribute:
        name = f'.{a.attr}{name}'  # we build it up like this because there can be whitespace, line continuations and newlines in the source
        a = a.value

        if a.f.pars().n:  # aliases can't have pars
            a.f._unparenthesize_grouping(False)

    if a.__class__ is not Name:
        raise NodeError(f'cannot coerce {a.__class__.__name__} to alias, must be Name or Attribute')

    if fst_.pars().n:  # aliases can't have pars
        fst_._unparenthesize_grouping(False)

    ast = alias(name=a.id + name, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                end_col_offset=ast_.end_col_offset)

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_to__aliases(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce _withitems specially for the "a as b" format?

    if fst_ := _coerce_to__aliases_common(code, parse_params, parse__aliases, '_aliases', sanitize, True):  # sequence as sequence?
        return fst_

    # single element as sequence

    fst_ = code_as_alias(code, parse_params, sanitize=sanitize, coerce=True)

    ast = _aliases(names=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                   end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'names', True, False)


_coerce_to__Import_name = _coerce_to_alias


def _coerce_to__Import_names(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce _withitems specially for the "a as b" format?

    if fst_ := _coerce_to__aliases_common(code, parse_params, parse__Import_names, 'Import names', sanitize, True):  # sequence as sequence?
        return fst_

    # single element as sequence

    fst_ = code_as_Import_name(code, parse_params, sanitize=sanitize, coerce=True)

    ast = _aliases(names=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                   end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'names', True, False)


def _coerce_to__ImportFrom_name(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = code_as_expr(code, parse_params, sanitize=True, coerce=True)  # sanitize because where aliases are used then generally can't have junk, comments specifically would break Import.names aliases
    ast_ = fst_.a

    if ast_.__class__ is not Name:
        raise NodeError(f'cannot coerce {ast_.__class__.__name__} to ImportFrom.names alias, must be Name')

    if fst_.pars().n:  # aliases can't have pars
        fst_._unparenthesize_grouping(False)

    ast = alias(name=ast_.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                end_col_offset=ast_.end_col_offset)

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_to__ImportFrom_names(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce _withitems specially for the "a as b" format?

    if fst_ := _coerce_to__aliases_common(code, parse_params, parse__ImportFrom_names, 'ImportFrom names', sanitize,
                                          False):  # sequence as sequence?
        return fst_

    # single element as sequence

    fst_ = code_as_ImportFrom_name(code, parse_params, sanitize=sanitize, coerce=True)

    ast = _aliases(names=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                   end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'names', True, False)


def _coerce_to_arguments(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = code_as_arg(code, parse_params, sanitize=sanitize, coerce=True)

    ast = arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'args', True, False)


def _coerce_to_arguments_lambda(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = code_as_arg(code, parse_params, sanitize=sanitize, coerce=True)
    ast_ = fst_.a

    if ast_.annotation:
        raise NodeError('lambda arguments cannot have annotations')

    ast = arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'args', True, False)


def _coerce_to_withitem(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce "import a as b" names[0] -> "with a as b"?

    fst_ = code_as_expr(code, parse_params, sanitize=sanitize, coerce=True)

    if fst_.is_parenthesized_tuple() is False:
        fst_._delimit_node()

    ast = withitem(context_expr=None)

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)._set_field(fst_.a, 'context_expr', True, False)


def _coerce_to__withitems(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce _aliases specially for the "a as b" format?

    fst_ = _coerce_to__slice_with_commas(code, parse_params, parse__withitems, _withitems, always_reparse=True)  # list[AST] is never returned with always_reparse=True

    if fst_ is not None:  # sequence as sequence? always_reparse=True because otherwise it would be a pain to get individual withitem locations because of possible group pars around context_exprs
        return fst_._sanitize() if sanitize else fst_

    # single element as sequence

    fst_ = code_as_withitem(code, parse_params, sanitize=sanitize, coerce=True)

    ast = _withitems(items=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                     end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'items', True, False)


@pyver(lt=12)
def _coerce_to_type_param(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    raise RuntimeError('type_params do not exist on python < 3.12')


@pyver(ge=12)
def _coerce_to_type_param(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce keyword (default value)? AnnAssign (bound and maybe default value)? Assign (default value)?

    fst_ = code_as_expr(code, parse_params, sanitize=sanitize, coerce=True)
    ast_ = fst_.a

    if ast_.__class__ is Name:
        if fst_.pars().n:  # type_params can't have pars
            fst_._unparenthesize_grouping(False)

        ast = TypeVar(name=ast_.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                      end_col_offset=ast_.end_col_offset)

    elif ast_.__class__ is Starred:
        if (value := fst_.a.value).__class__ is not Name:
            raise NodeError(f'cannot coerce {value.__class__.__name__} to TypeVarTuple name, must be Name')

        if (valuef := value.f).pars().n:  # type_params can't have pars
            valuef._unparenthesize_grouping(False)

        ast = TypeVarTuple(name=value.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                           end_col_offset=ast_.end_col_offset)

    else:
        raise NodeError(f'cannot coerce {ast_.__class__.__name__} to type_param, must be Name or Starred Name')

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)


@pyver(ge=12, else_=_coerce_to_type_param)
def _coerce_to__type_params(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = getattr(code, 'a', None)

    fst_ = _coerce_to__slice_with_commas(code, parse_params, parse__type_params, _type_params)  # sequence as sequence?

    if fst_ is not None:  # sequence as sequence?
        if fst_.__class__ is list:  # this means code is an FST
            elts = fst_
            ast = Tuple(elts=elts, ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                        end_col_offset=ls[-1].lenbytes)

            tmp = fst.FST(ast, ls, None, from_=code, lcopy=False)  # temporary Tuple so that we can unparenthesize everything

            type_params = []

            for e in elts:
                e.f._unparenthesize_grouping()  # type_params can't have pars

                if (e_cls := e.__class__) is Name:
                    tp = TypeVar(name=e.id, lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                                 end_col_offset=e.end_col_offset)

                elif e_cls is Starred:
                    if (v := e.value).__class__ is Name:
                        tp = TypeVarTuple(name=v.id, lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                                          end_col_offset=e.end_col_offset)
                    else:
                        raise NodeError(f'expecting _type_params, got {codea.__class__.__name__}'
                                        f', could not coerce, found Starred {v.__class__.__name__}')

                else:
                    raise NodeError(f'expecting _type_params, got {codea.__class__.__name__}'
                                    f', could not coerce, found {e_cls.__name__}')

                type_params.append(tp)

            tmp._unmake_fst_tree()

            ast = _type_params(type_params=type_params, lineno=1, col_offset=0, end_lineno=tmp.end_lineno,
                               end_col_offset=tmp.end_col_offset)

            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

        return fst_._sanitize() if sanitize else fst_

    # single element as sequence

    fst_ = code_as_type_param(code, parse_params, sanitize=sanitize, coerce=True)

    ast = _type_params(type_params=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                       end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'type_params', True, False)


def _coerce_to__expr_arglikes(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = code_as_expr_arglike(code, parse_params, sanitize=sanitize, coerce=True)

    if fst_.is_parenthesized_tuple() is False:  # can't have unparenthesized tuple as sole element, will look like multiple elements
        fst_._delimit_node()

    ast = Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'elts', True, False)


# ......................................................................................................................

def _code_as(
    code: Code,
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    ast_cls: type[AST] | tuple[type[AST], ...],
    sanitize: bool,
    coerce_to: CodeAs | Literal[False] | None = None,
    *,
    name: str | None = None,
) -> fst.FST:
    """Generic handler for this."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if not isinstance(codea, ast_cls):
            if not coerce_to:
                raise NodeError(f'expecting {name or ast_cls.__name__}, got {codea.__class__.__name__}'
                                f'{", coerce disabled" if coerce_to is False else ""}', rawable=True)

            try:
                return coerce_to(code, parse_params, sanitize=sanitize)
            except Exception as exc:
                raise NodeError(f'expecting {name or ast_cls.__name__}, got {codea.__class__.__name__}, '
                                'could not coerce', rawable=True) from exc

    else:
        if isinstance(code, AST):
            if not isinstance(code, ast_cls):
                if not coerce_to:
                    raise NodeError(f'expecting {name or ast_cls.__name__}, got {code.__class__.__name__}'
                                    f'{", coerce disabled" if coerce_to is False else ""}', rawable=True)

                try:
                    return coerce_to(code, parse_params, sanitize=sanitize)
                except Exception as exc:
                    raise NodeError(f'expecting {name or ast_cls.__name__}, got {code.__class__.__name__}, '
                                    'could not coerce', rawable=True) from exc

            src = unparse(code)
            lines = src.split('\n')

            ast = parse(src, parse_params)

            if ast.__class__ is not code.__class__:  # sanity check
                raise ParseError(f'could not reparse AST to {code.__class__.__name__}, got {ast.__class__.__name__}')  # pragma: no cover

        else:
            if isinstance(code, list):
                src = '\n'.join(lines := code)
            else:  # str
                lines = (src := code).split('\n')

            try:
                ast = parse(src, parse_params)

            except Exception:
                if not (coerce_to and getattr(coerce_to, 'coerce_src', False)):  # if there is a coerce function and it supports coerce source (by "supports" we also mean if it makes sense)
                    raise

                try:
                    fst_ = coerce_to(code, parse_params, sanitize=sanitize)
                except Exception as exc:
                    raise ParseError(f'expecting {name or ast_cls.__name__}, could not parse or coerce') from exc

                return fst_

            if not isinstance(ast, ast_cls):  # sanity check, parse func should guarantee what we want but maybe in future is used to get a specific subset of what parse func returns
                raise ParseError(f'expecting {name or ast_cls.__name__}, got {code.__class__.__name__}')  # pragma: no cover

        code = fst.FST(ast, lines, None, parse_params=parse_params)

    return code._sanitize() if sanitize else code


def _code_as_expr(
    code: Code,
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    allow_Slice: bool,
    allow_Tuple_of_Slice: bool,
    sanitize: bool,
    coerce: bool,
) -> fst.FST:
    """General convert `code` to `expr`. Meant to handle any type of expression including `Slice`, `Tuple` of `Slice`s,
    `Tuple` of `Slice` elements and arglikes."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        ast = code.a
        ast_cls = ast.__class__
        fix_coerced_tuple = False  # coerced tuples from the likes of _arglikes FST source may not be in standard source format

        if ast_cls not in ASTS_LEAF_EXPR:  # if not an expr then try coerce if allowed
            if not coerce:
                raise NodeError(f'expecting {_EXPR_PARSE_FUNC_TO_NAME[parse]}, got {ast_cls.__name__}, coerce disabled',
                                rawable=True)

            old_ast = ast
            ast, fix_coerced_tuple = _coerce_to_expr_ast(ast, True, parse_params, _EXPR_PARSE_FUNC_TO_NAME[parse])
            ast_cls = ast.__class__

            code = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

        if ast_cls is Slice:
            if not allow_Slice:
                raise NodeError(f'expecting {_EXPR_PARSE_FUNC_TO_NAME[parse]}, got Slice', rawable=True)

        elif ast_cls is Tuple:
            if not allow_Tuple_of_Slice and any(e.__class__ is Slice for e in ast.elts):
                raise NodeError(f'expecting {_EXPR_PARSE_FUNC_TO_NAME[parse]}, got Tuple with a Slice in it',
                                rawable=True)

            if fix_coerced_tuple:
                code._fix_tuple(False)  # it is not be parenthesized

                if old_ast.__class__ is _arglikes:  # these will need arglike-only expressions parenthesized to be a valid expr
                    code._fix_arglikes()

            elif parse is not parse_expr_slice:  # specifically for lone '*starred' as a `Tuple` without comma from `Subscript.slice`, doesn't happen organically but can be created with FST('*a', 'expr_slice'), should we bother? for now on the side of yes
                code._maybe_add_singleton_tuple_comma()

    else:
        if is_ast := isinstance(code, AST):
            if code.__class__ not in ASTS_LEAF_EXPR:  # if not an expr then try coerce if allowed
                if not coerce:
                    raise NodeError(f'expecting {_EXPR_PARSE_FUNC_TO_NAME[parse]}, got {code.__class__.__name__}'
                                    ', coerce disabled', rawable=True)

                code, _ = _coerce_to_expr_ast(code, False, parse_params, _EXPR_PARSE_FUNC_TO_NAME[parse])

            src = unparse(code)
            lines = src.split('\n')

        elif isinstance(code, list):
            src = '\n'.join(lines := code)
        else:  # str
            lines = (src := code).split('\n')

        ast = parse(src, parse_params)

        assert not is_ast or (ast.__class__ is code.__class__)  # sanity check

        code = fst.FST(ast, lines, None, parse_params=parse_params)

    return code._sanitize() if sanitize else code


def _code_as_op(
    code: Code,
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    op_type: type[boolop | operator | unaryop | cmpop],  # only one of these, not subclasses
    sanitize: bool,
) -> fst.FST:
    """Convert `code` to an op `FST` if possible."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(code.a, op_type):
            raise NodeError(f'expecting {op_type.__name__}, got {code.a.__class__.__name__}', rawable=True)

    elif isinstance(code, AST):
        if not isinstance(code, op_type):
            raise NodeError(f'expecting {op_type.__name__}, got {code.__class__.__name__}', rawable=True)

        code_cls = code.__class__

        return fst.FST(code_cls(), [OPCLS2STR[code_cls]], None, parse_params=parse_params)  # don't use same AST as was passed in

    else:
        if isinstance(code, list):
            src = '\n'.join(lines := code)
        else:  # str
            lines = (src := code).split('\n')

        code = fst.FST(parse(src, parse_params), lines, None, parse_params=parse_params)

    return code._sanitize() if sanitize else code


# ----------------------------------------------------------------------------------------------------------------------

def code_as_lines(code: Code | None) -> list[str]:
    """Get list of lines of `code` if is `FST`, unparse `AST`, split `str` or just return `list[str]` if is that.
    `code=None` is returned as `['']`."""

    if isinstance(code, str):
        return code.split('\n')
    elif code is None:
        return ['']
    elif isinstance(code, list):
        return code
    elif isinstance(code, AST):
        return unparse(code).split('\n')
    elif not code.is_root:  # isinstance(code, fst.FST)
        raise ValueError('expecting root node')
    else:
        return code._lines


def code_as_all(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to any parsable `FST` if possible. If `FST` passed then it is returned as itself."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

    else:
        if isinstance(code, AST):
            mode = code.__class__
            code = unparse(code)
            lines = code.split('\n')

        else:
            mode = 'all'

            if isinstance(code, list):
                code = '\n'.join(lines := code)
            else:  # str
                lines = code.split('\n')

        code = fst.FST(parse(code, mode), lines, None, parse_params=parse_params)

    return code._sanitize() if sanitize else code


def code_as_stmts(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to zero or more `stmt`s and return in the `body` of a `Module` `FST` if possible.

    **Note:** `sanitize` does nothing since the return is a `Module` which always includes the whole source.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if codea.__class__ is Expression:  # coerce Expression to expr
            codea = codea.body

            code._unmake_fst_parents(True)

        if codea.__class__ in ASTS_LEAF_EXPR:  # coerce expr to Expr stmt
            codea = Expr(value=codea, lineno=codea.lineno, col_offset=codea.col_offset,
                         end_lineno=codea.end_lineno, end_col_offset=codea.end_col_offset)

        codea_cls = codea.__class__

        if codea_cls in ASTS_LEAF_STMT:
            return fst.FST(Module(body=[codea], type_ignores=[]), code._lines, None, from_=code, lcopy=False)

        if codea_cls is Module:
            return code

        if codea_cls is Interactive:
            code._unmake_fst_parents(True)

            return fst.FST(Module(body=codea.body, type_ignores=[]), code._lines, None, from_=code, lcopy=False)

        raise NodeError(f'expecting zero or more stmts, got {codea_cls.__name__}', rawable=True)

    if isinstance(code, AST):
        if code.__class__ not in ASTS_LEAF_EXPR_STMT_OR_MOD:  # all these can be coerced into stmts
            raise NodeError(f'expecting zero or more stmts, got {code.__class__.__name__}', rawable=True)

        code = _fixing_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return fst.FST(parse_stmts(code, parse_params), lines, None, parse_params=parse_params)


def code_as__ExceptHandlers(
    code: Code,
    parse_params: Mapping[str, Any] = {},
    *,
    sanitize: bool = False,
    coerce: bool = False,
    is_trystar: bool | None = None,
) -> fst.FST:
    """Convert `code` to zero or more `ExceptHandler`s and return in an `_ExceptHandlers` SPECIAL SLICE if possible.

    **Note:** `sanitize` does nothing since the return is an `_ExceptHandlers` which always includes the whole source.

    **Parameters:**
    - `is_trystar`: What kind of except handler to accept:
        - `False`: Plain only, no `except*`.
        - `True`: Star only, no plain.
        - `None`: Accept either as `FST` or source, if `AST` passed then default to plain.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a
        codea_cls = codea.__class__

        if codea_cls is ExceptHandler:
            code = fst.FST(_ExceptHandlers(handlers=[codea], lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                           end_col_offset=ls[-1].lenbytes), ls, None, from_=code, lcopy=False)

        elif codea_cls is not _ExceptHandlers:
            raise NodeError(f'expecting zero or more ExceptHandlers, got {codea_cls.__name__}')#, rawable=True)

        error = NodeError

    else:
        error = ParseError

        if isinstance(code, AST):
            code_cls = code.__class__

            if code_cls is ExceptHandler:
                handlers = [code]
            elif code_cls is _ExceptHandlers:
                handlers = code.handlers
            else:
                raise NodeError(f'expecting zero or more ExceptHandlers, got {code_cls.__name__}')#, rawable=True)

            code = _fixing_unparse((TryStar if is_trystar else Try)(body=[Pass()],
                                                                    handlers=handlers, orelse=[], finalbody=[]))
            code = code[code.index('except'):]
            lines = code.split('\n')
            is_trystar = None  # so that unnecessary check is not done below

        elif isinstance(code, list):
            code = '\n'.join(lines := code)
        else:  # str
            lines = code.split('\n')

        code = fst.FST(parse__ExceptHandlers(code, parse_params), lines, None, parse_params=parse_params)

    if (handlers := code.a.handlers) and is_trystar is not None:
        if is_trystar != handlers[0].f.is_except_star():
            raise error("expecting star 'except*' handler, got plain 'except'" if is_trystar else
                        "expecting plain 'except' handler, got star 'except*'")

    return code


def code_as__match_cases(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to zero or more `match_case`s and return in a `_match_cases` SPECIAL SLICE if possible.

    **Note:** `sanitize` does nothing since the return is a `_match_cases` which always includes the whole source.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a
        codea_cls = codea.__class__

        if codea_cls is match_case:
            return fst.FST(_match_cases(cases=[codea], lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                        end_col_offset=ls[-1].lenbytes), ls, None, from_=code, lcopy=False)

        if codea_cls is not _match_cases:
            raise NodeError(f'expecting zero or more match_cases, got {codea_cls.__name__}', rawable=True)

        return code

    if isinstance(code, AST):
        if code.__class__ not in (match_case, _match_cases):
            raise NodeError(f'expecting zero or more match_cases, got {code.__class__.__name__}', rawable=True)

        code = unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return fst.FST(parse__match_cases(code, parse_params), lines, None, parse_params=parse_params)


def code_as_expr(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `expr` using `parse_expr()`."""

    return _code_as_expr(code, parse_params, parse_expr, False, False, sanitize, coerce)


def code_as_expr_all(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `expr` using `parse_expr_all()`."""

    return _code_as_expr(code, parse_params, parse_expr_all, True, True, sanitize, coerce)


def code_as_expr_arglike(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `expr` in the context of a `Call.args` which has special parse rules for `Starred`."""

    return _code_as_expr(code, parse_params, parse_expr_arglike, False, False, sanitize, coerce)


def code_as_expr_slice(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a any `expr` `FST` that can go into a `Subscript.slice` if possible."""

    return _code_as_expr(code, parse_params, parse_expr_slice, True, True, sanitize, coerce)


def code_as_Tuple_elt(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `expr` which can be an element of a `Tuple` anywhere, including `Slice` and arglike
    expressions like `*not a` on py 3.11+ (both in a `Tuple` in `Subscript.slice`)."""

    return _code_as_expr(code, parse_params, parse_Tuple_elt, True, False, sanitize, coerce)


def code_as_Tuple(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `Tuple` using `parse_Tuple()`. The `Tuple` can contain any other kind of expression,
    including `Slice` and arglike (if py version supports it in `Subscript.slice`)."""

    fst_ = _code_as_expr(code, parse_params, parse_Tuple, False, True, sanitize, coerce)

    if fst_ is code and fst_.a.__class__ is not Tuple:  # fst_ is code only if FST passed in, in which case is passed through and we need to check that was Tuple to begin with
        raise NodeError(f'expecting Tuple, got {fst_.a.__class__.__name__}', rawable=True)

    return fst_


def code_as__Assign_targets(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_Assign_targets` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__Assign_targets, _Assign_targets, sanitize,
                    _coerce_to__Assign_targets if coerce else False)


def code_as__decorator_list(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_decorator_list` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__decorator_list, _decorator_list, sanitize,
                    _coerce_to__decorator_list if coerce else False)


def code_as__arglike(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a single `expr_arglike` or `keyword` if possible."""

    fst_ = _code_as(code, parse_params, parse__arglike, (expr, keyword), sanitize,
                    _coerce_to__arglike if coerce else False,
                    name='expression (arglike)')

    if fst_ is code and fst_.a.__class__ in ASTS_LEAF_FTSTR_FMT_OR_SLICE:  # fst_ is code only if FST passed in, in which case make sure we didn't get an invalid arglike
        raise NodeError(f'expecting expression (arglike), got {fst_.a.__class__.__name__}', rawable=True)

    return fst_


def code_as__arglikes(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_arglikes` of `expr`s and `keyword`s SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__arglikes, _arglikes, sanitize,
                    _coerce_to__arglikes if coerce else False)


def code_as_boolop(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `boolop` `FST` if possible."""

    return _code_as_op(code, parse_params, parse_boolop, boolop, sanitize)


def code_as_operator(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `operator` `FST` if possible."""

    return _code_as_op(code, parse_params, parse_operator, operator, sanitize)


def code_as_unaryop(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `unaryop` `FST` if possible."""

    return _code_as_op(code, parse_params, parse_unaryop, unaryop, sanitize)


def code_as_cmpop(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `cmpop` `FST` if possible."""

    return _code_as_op(code, parse_params, parse_cmpop, cmpop, sanitize)


def code_as_comprehension(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(code, parse_params, parse_comprehension, comprehension, sanitize)


def code_as__comprehensions(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `_comprehensions` of `comprehensions` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__comprehensions, _comprehensions, sanitize,
                    _coerce_to__comprehensions if coerce else False)


def code_as__comprehension_ifs(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `_comprehension_ifs` of `if` prepended `expr`s SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__comprehension_ifs, _comprehension_ifs, sanitize,
                    _coerce_to__comprehension_ifs if coerce else False)


def code_as_arguments(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a arguments `FST` if possible."""

    return _code_as(code, parse_params, parse_arguments, arguments, sanitize,
                    _coerce_to_arguments if coerce else False)


def code_as_arguments_lambda(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a lambda arguments `FST` if possible (no annotations allowed)."""

    fst_ = _code_as(code, parse_params, parse_arguments_lambda, arguments, sanitize,
                    _coerce_to_arguments_lambda if coerce else False,
                    name='lambda arguments')

    if fst_ is code:  # validation if returning same FST that was passed in
        ast = fst_.a

        if (((args := ast.args) and any(a.annotation for a in args))
            or ((args := ast.kwonlyargs) and any(a.annotation for a in args))
            or ((arg := ast.vararg) and arg.annotation)
            or ((arg := ast.kwarg) and arg.annotation)
            or ((args := ast.posonlyargs) and any(a.annotation for a in args))
        ):
            raise NodeError('lambda arguments cannot have annotations')

    return fst_


def code_as_arg(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an arg `FST` if possible."""

    return _code_as(code, parse_params, parse_arg, arg, sanitize,
                    _coerce_to_arg if coerce else False)


def code_as_keyword(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a keyword `FST` if possible."""

    return _code_as(code, parse_params, parse_keyword, keyword, sanitize)


def code_as_alias(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, star or dotted."""

    return _code_as(code, parse_params, parse_alias, alias, sanitize,
                    _coerce_to_alias if coerce else False)


def code_as__aliases(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, star or dotted."""

    return _code_as(code, parse_params, parse__aliases, _aliases, sanitize,
                    _coerce_to__aliases if coerce else False)


def code_as_Import_name(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, dotted as in `alias` for `Import.names`."""

    fst_ = _code_as(code, parse_params, parse_Import_name, alias, sanitize,
                    _coerce_to__Import_name if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if fst_.a.name == '*':
            raise NodeError("'*' star alias not allowed")

    return fst_


def code_as__Import_names(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, dotted as in `alias` for `Import.names`."""

    fst_ = _code_as(code, parse_params, parse__Import_names, _aliases, sanitize,
                    _coerce_to__Import_names if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if any(a.name == '*' for a in fst_.a.names):
            raise NodeError("'*' star alias not allowed")

    return fst_


def code_as_ImportFrom_name(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, possibly star as in `alias` for `FromImport.names`."""

    fst_ = _code_as(code, parse_params, parse_ImportFrom_name, alias, sanitize,
                    _coerce_to__ImportFrom_name if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if '.' in fst_.a.name:
            raise NodeError("'.' dotted alias not allowed")

    return fst_


def code_as__ImportFrom_names(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, possibly star as in `alias` for
    `FromImport.names`."""

    fst_ = _code_as(code, parse_params, parse__ImportFrom_names, _aliases, sanitize,
                    _coerce_to__ImportFrom_names if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        for a in (names := fst_.a.names):
            if '.' in (n := a.name):
                raise NodeError("'.' dotted alias not allowed")

            if n == '*' and a is not names[0]:
                raise NodeError("'*' star can only be a single element")

        if len(names) > 1 and names[0].name == '*':  # someone really wanted to get a star in there...
            raise NodeError("'*' star can only be a single element")

    return fst_


def code_as_withitem(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(code, parse_params, parse_withitem, withitem, sanitize,
                    _coerce_to_withitem if coerce else False)


def code_as__withitems(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `_withitems` of `withitem` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__withitems, _withitems, sanitize,
                    _coerce_to__withitems if coerce else False)


def code_as_pattern(
    code: Code,
    parse_params: Mapping[str, Any] = {},
    *,
    sanitize: bool = False,
    coerce: bool = False,
    allow_invalid_matchor: bool = False,
) -> fst.FST:
    """Convert `code` to a pattern `FST` if possible."""

    fst_ = _code_as(code, parse_params, parse_pattern, pattern, sanitize)

    if fst_ is code:  # validation if returning same FST that was passed in
        if not allow_invalid_matchor and (a := fst_.a).__class__ is MatchOr:  # SPECIAL SLICE
            if not (len_pattern := len(a.patterns)):
                raise NodeError('expecting valid pattern, got zero-length MatchOr')

            if len_pattern == 1:  # a length 1 MatchOr can just return its single element pattern
                fst_._unmake_fst_parents(True)

                return fst.FST(a.patterns[0], fst_._lines, None, from_=fst_, lcopy=False)

    return fst_


def code_as_type_param(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a type_param `FST` if possible."""

    return _code_as(code, parse_params, parse_type_param, type_param, sanitize,
                    _coerce_to_type_param if coerce else False)


def code_as__type_params(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `_type_params` of `type_param` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__type_params, _type_params, sanitize,
                    _coerce_to__type_params if coerce else False)


def code_as_identifier(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> str:
    """Convert `code` to valid identifier string if possible.

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier(code):
        raise ParseError(f'expecting identifier, got {shortstr(code)!r}')

    return code


def code_as_identifier_dotted(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> str:
    """Convert `code` to valid dotted identifier string if possible (for Import module).

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_dotted(code):
        raise ParseError(f'expecting dotted identifier, got {shortstr(code)!r}')

    return code


def code_as_identifier_star(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> str:
    """Convert `code` to valid identifier string or star '*' if possible (for ImportFrom names).

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_star(code):
        raise ParseError(f"expecting identifier or '*', got {shortstr(code)!r}")

    return code


def code_as_identifier_alias(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> str:
    """Convert `code` to valid dotted identifier string or star '*' if possible (for any alias).

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_alias(code):
        raise ParseError(f"expecting dotted identifier or '*', got {shortstr(code)!r}")

    return code


def code_as_constant(
    code: Code | constant, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> constant:
    """Convert `code` to valid constant if possible. If `code` is a `str` then it is treated as the constant value and
    not as the python representation of the constant. The only `FST` or `AST` accepted is a `Constant`, whose `value` is
    returned.

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.a

    if isinstance(code, AST):
        if code.__class__ is not Constant:
            raise NodeError('expecting constant', rawable=True)

        code = code.value

        if isinstance(code, (int, float)):
            if code < 0:
                raise NodeError('constants cannot be negative', rawable=True)

        elif isinstance(code, complex):
            if code.real:
                raise NodeError('imaginary constants cannot have real componenets', rawable=True)
            if code.imag < 0:
                raise NodeError('imaginary constants cannot be negative', rawable=True)

    elif isinstance(code, list):
        code = '\n'.join(code)
    elif not isinstance(code, constant):
        raise NodeError('expecting constant', rawable=True)

    return code


# ......................................................................................................................
# internal stuff, not meant for direct user use

def code_as__expr_arglikes(
    code: Code,
    parse_params: Mapping[str, Any] = {},
    *,
    sanitize: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `Tuple` contianing possibly arglike expressions. Meant for putting slices to `Call.args` and
    `ClassDef.bases`. The `Tuple` will be unparenthesized and the location will be the entire source. We use a `Tuple`
    for this because unfortunately sometimes a `Tuple` is valid with arglikes in it and sometimes not.

    **WARNING!** The `Tuple` that is returned is just being used as a container and may be an invalid python `Tuple` as
    it may be an empty `Tuple` `AST` with source having no parentheses or an unparenthesized `Tuple` with incorrect
    start and stop locations (since its the whole source). Singleton `Tuple` may also not have trailing comma. Meant for
    internal use only!
    """

    if code.__class__ is Tuple:  # strip parentheses
        code = _fixing_unparse(code)[1:-1]

    fst_ = _code_as(code, parse_params, parse__expr_arglikes, Tuple, sanitize,
                    _coerce_to__expr_arglikes if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if any(e.__class__ is Slice for e in fst_.a.elts):
            raise NodeError('expecting non-Slice expressions (arglike), found Slice')

        if fst_._is_delimited_seq():
            fst_._trim_delimiters()

    return fst_
