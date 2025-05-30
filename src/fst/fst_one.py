"""Get and put single node."""

import re
from ast import *
from types import FunctionType
from typing import Any, Callable, NamedTuple, Optional, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, type_param, TypeVar, ParamSpec, TypeVarTuple, TemplateStr, Interpolation

from .shared import (
    STMTISH, Code, NodeError, astfield, fstloc,
    _next_src, _prev_src, _next_find, _prev_find, _next_find_re, _prev_pars, _fixup_one_index,
)

from .fst_parse import (
    _code_as_expr, _code_as_slice, _code_as_expr_slice_tuple, _code_as_expr_call_arg,
    _code_as_boolop, _code_as_operator, _code_as_operator_aug, _code_as_unaryop, _code_as_cmpop,
    _code_as_pattern, _code_as_comprehension, _code_as_arguments,
    _code_as_arguments_lambda, _code_as_arg, _code_as_keyword, _code_as_alias_maybe_star, _code_as_alias_dotted,
    _code_as_withitem, _code_as_type_param, _code_as_identifier, _code_as_identifier_dotted, _code_as_identifier_alias,
)

_re_merged_alnum = re.compile(r'\w\w')


def _slice_indices(self: 'FST', idx: int, field: str, body: list[AST], to: Optional['FST']):
    """If a `to` parameter is passed then try to convert it to an index in the same field body list of `self`."""

    idx = _fixup_one_index(len(body), idx)

    if not to:
        return idx, idx + 1

    elif to.parent is self is not None and (pf := to.pfield).name == field:
        if (to_idx := pf.idx) < idx:
            raise ValueError("invalid 'to' node, must follow self in body")

        return idx, to_idx + 1

    raise NodeError(f"invalid 'to' node")


def _Compare_None_index(self: 'FST', idx: int | None) -> tuple[int, str, AST | list[AST]]:
    ast         = self.a
    comparators = ast.comparators
    idx         = _fixup_one_index(len(comparators) + 1, idx)

    return (idx - 1, 'comparators', comparators) if idx else (None, 'left', ast.left)


# ----------------------------------------------------------------------------------------------------------------------
# get

def _get_one(self: 'FST', idx: int | None, field: str, cut: bool, **options) -> Optional['FST'] | constant:
    """Copy or cut (if possible) a node or non-node from a field of `self`."""

    ast = self.a

    if field:
        child = getattr(ast, field)
    elif not isinstance(ast, Compare):
        raise ValueError(f'cannot get single element from combined field of {ast.__class__.__name__}')
    else:
        idx, field, child = _Compare_None_index(self, idx)

    childa = child if idx is None else child[idx]

    if isinstance(childa, STMTISH):
        return self._get_slice_stmtish(*_slice_indices(self, idx, field, child, None), field, cut=cut, one=True,
                                       **options)

    if not isinstance(childa, AST):  # empty None field or identifier or some other constant
        ret = childa

    else:
        childf = childa.f
        loc    = childf.pars(pars=self.get_option('pars', options) is True)

        if not loc:
            raise ValueError('cannot copy node which does not have a location')

        ret = childf._make_fst_and_dedent(childf, copy_ast(childa), loc, docstr=options.get('docstr'))

        ret._maybe_fix(self.get_option('pars', options))

    if cut:
        options['raw'] = False
        options['to']  = None

        self._put_one(None, idx, field, **options)

    return ret


# ----------------------------------------------------------------------------------------------------------------------
# put

class onestatic(NamedTuple):
    getinfo:  Callable[['FST', 'onestatic', int | None, str], 'oneinfo'] | None
    restrict: type[AST] | tuple[type[AST]] | list[type[AST]] | Callable[[AST], bool] | None = None
    code_as:  Callable[[Code, dict], 'FST']                                                 = _code_as_expr
    ctx:      type[expr_context]                                                            = Load


class oneinfo(NamedTuple):
    prefix:      str           = ''    # prefix to add on insert
    loc_insdel:  fstloc | None = None  # only present if insert (put new to nonexistent) or delete is possible and is the location for the specific mutually-exclusive operation
    loc_ident:   fstloc | None = None  # location of identifier
    suffix:      str           = ''    # or ': ' for dict '**'
    delstr:      str           = ''    # or '**'


def _validate_put(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST] | AST | None,
                  options: dict[str, Any], *, can_del: bool = False) -> AST | None:
    """Check that `idx` was passed (or not) as needed and that not deleting if not possible and that `to` raw parameter
    is not present."""

    if isinstance(child, list):
        if idx is None:
            raise IndexError(f'{self.a.__class__.__name__}.{field} needs an index')

        _fixup_one_index(len(child), idx)

        child = child[idx]

    elif idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')

    if not can_del and code is None:
        raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field}{"" if idx is None else f"[{idx}]"}')
    if options.get('to'):
        raise NodeError(f"cannot put with 'to' to {self.a.__class__.__name__}.{field} without 'raw'")

    return child


def _validate_put_ast(self: 'FST', put_ast: AST, idx: int | None, field: str, static: onestatic):
    if restrict := static.restrict:
        if isinstance(restrict, list):  # list means these types not allowed
            if isinstance(put_ast, tuple(restrict)):
                raise NodeError(f'{self.a.__class__.__name__}.{field}{" " if idx is None else f"[{idx}] "}'
                                f'cannot be {put_ast.__class__.__name__}')

        elif isinstance(restrict, FunctionType):
            if not restrict(put_ast):
                raise NodeError(f'invalid value for {self.a.__class__.__name__}.{field}' +
                                ('' if idx is None else f'[{idx}]'))

        elif not isinstance(put_ast, restrict):  # single AST type or tuple means only these allowed
            raise NodeError((f'expecting a {restrict.__name__} for {self.a.__class__.__name__}.{field}'
                              if isinstance(restrict, type) else
                              f'expecting one of ({", ".join(c.__name__ for c in restrict)}) for '
                              f'{self.a.__class__.__name__}.{field}{"" if idx is None else f"[{idx}]"}') +
                             f', got {put_ast.__class__.__name__}')


# ......................................................................................................................
# other

def _put_one_constant(self: 'FST', code: Code | None, idx: int | None, field: str, child: constant, static: onestatic,
                      **options) -> 'FST':
    """Put a single constant value, only Constant and MatchSingleton (and only exists because of the second one)."""

    child   = _validate_put(self, code, idx, field, child, options)
    put_fst = _code_as_expr(code, self.root.parse_params)
    put_ast = put_fst.a

    _validate_put_ast(self, put_ast, idx, field, static)
    self.put_src(put_fst.get_src(*put_fst.loc, True), *self.loc, True)  # we want pure constant, no parens or spaces or comments or anything

    self.a.value = put_ast.value

    return self  # this breaks the rule of returning the child node since it is just a primitive


def _put_one_BoolOp_op(self: 'FST', code: Code | None, idx: int | None, field: str, child: type[boolop], static: None,
                       **options) -> 'FST':
    """Put BoolOp op to potentially multiple places."""

    child  = _validate_put(self, code, idx, field, child, options)
    code   = _code_as_boolop(code, self.root.parse_params)
    childf = child.f
    src    = 'and' if isinstance(codea := code.a, And) else 'or'
    tgt    = 'and' if isinstance(child, And) else 'or'
    ltgt   = len(tgt)
    lines  = self.root._lines

    _, _, end_ln, end_col = self.loc

    for value in self.a.values[:-1]:
        _, _, ln, col = value.f.pars()
        ln, col       = _next_find(lines, ln, col, end_ln, end_col, tgt)  # must be there

        self.put_src(src, ln, col, ln, col + ltgt, False)

    childf._set_ast(codea)

    return childf


def _put_one_op(self: 'FST', code: Code | None, idx: int | None, field: str,
                child: type[boolop] | type[operator] | type[unaryop] | type[cmpop],
                static: None, **options) -> 'FST':
    """Put a single operation, with or without '=' for AugAssign."""

    child  = _validate_put(self, code, idx, field, child, options)
    code   = static.code_as(code, self.root.parse_params)
    childf = child.f

    ln, col, end_ln, end_col = childf.loc

    self.put_src(code._lines, ln, col, end_ln, end_col, False)
    childf._set_ast(code.a)

    return childf


def _put_one_stmtish(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST], static: None,
                     **options) -> Optional['FST']:
    """Put or delete a single statementish node to a list of them (body, orelse, handlers, finalbody or cases)."""

    self._put_slice_stmtish(code, *_slice_indices(self, idx, field, child, options.get('to')), field, True, **options)

    return None if code is None else getattr(self.a, field)[idx].f


# ......................................................................................................................
# exprish (expr, pattern, comprehension, etc...)

def _make_exprish_fst(self: 'FST', code: Code | None, idx: int | None, field: str, static: onestatic,
                      target: Union['FST', fstloc], ctx: type[expr_context], prefix: str  = '', suffix: str = '',
                      **options) -> 'FST':
    """Make an expression `FST` from `Code` for a field/idx containing an existing node creating a new one. Takes care
    of parenthesizing, indenting and offsetting."""

    put_fst = static.code_as(code, self.root.parse_params)
    put_ast = put_fst.a

    _validate_put_ast(self, put_ast, idx, field, static)

    # figure out parentheses

    pars         = FST.get_option('pars', options)
    tgt_is_FST   = target.is_FST
    del_tgt_pars = False

    def need_pars(adding: bool) -> bool:
        if not put_fst.is_atom(pars=False):
             if precedence_require_parens(put_ast, self.a, field, idx):
                 return True

        elif (tgt_is_FST and field == 'value' and isinstance(put_ast, Constant) and isinstance(put_ast.value, int) and  # veeery special case "3.__abs__()" -> "(3).__abs__()"
              (tgt_parent := target.parent) and isinstance(tgt_parent.a, Attribute)):
            return True

        if not self.is_enclosed_in_parents(field) and not put_fst.is_enclosed(pars=adding):
            return True

        return False

    if pars:
        if put_fst.pars(True)[1]:  # src has grouping pars
            del_tgt_pars = True

            if pars == 'auto':
                if not need_pars(False):
                    put_fst._unparenthesize_grouping()

        else:  # src does not have grouping pars
            if ((tgt_has_pars := tgt_is_FST and target.pars(True, shared=False)[1]) and
                put_fst.is_parenthesized_tuple() is False
            ):
                del_tgt_pars = True
                tgt_has_pars = False

            if tgt_has_pars:
                if not need_pars(True):
                    if pars is True or not (field == 'target' and (tgt_parent := target.parent) and  # suuuper minor special case, don't automatically unparenthesize AnnAssign targets
                                            isinstance(tgt_parent.a, AnnAssign)):
                        del_tgt_pars = True

            elif need_pars(True):
                put_fst.parenthesize()  # could be parenthesizing grouping or a tuple

    # figure out put target location

    if not tgt_is_FST:
        ln, col, end_ln, end_col = target

    else:
        loc = target.pars(shared=False, pars=del_tgt_pars)

        if not del_tgt_pars and target.is_solo_call_arg_genexp():  # need to check this otherwise might eat Call args pars
            if (loc2 := target.pars(shared=False)) > loc:
                loc = loc2

        ln, col, end_ln, end_col = loc

    # make sure put doesn't merge alphanumerics

    lines     = self.root._lines
    put_lines = put_fst._lines

    if col and _re_merged_alnum.match(lines[ln][col - 1] + (prefix or put_lines[0][:1])):  # if start would merge then prepend prefix with space
        prefix = ' ' + prefix

    if end_col < len(l := lines[end_ln]) and _re_merged_alnum.match((suffix or put_lines[-1])[-1:] + l[end_col]):  # if end would merge then append space to suffix
        suffix = suffix + ' '

    # do it

    if prefix:
        put_fst.put_src([prefix], 0, 0, 0, 0, True)

    if suffix:
        ls[-1] = bistr((ls := put_fst._lines)[-1] + suffix)  # don't need to offset anything so just tack onto the end

    put_fst.indent_lns(self.get_indent(), docstr=options.get('docstr'))


    dcol_offset    = self.root._lines[ln].c2b(col)
    end_col_offset = lines[end_ln].c2b(end_col)
    params_offset  = self.put_src(put_fst._lines, ln, col, end_ln, end_col, True, False, exclude=self)

    self.offset(*params_offset, exclude=target, self_=False)  # excluding an fstloc instead of FST is harmless, will not exclude anything
    put_fst.offset(0, 0, ln, dcol_offset)
    set_ctx(put_ast, ctx)

    # possibly fix FormattedValue and Interpolation .format_spec location if present above self - because can follow IMMEDIATELY after modified value (which doesn't normally happen in py syntax) and thus would not have their start offset due to head=False in put_src() above

    cur = self

    while parent := cur.parent:
        if isinstance(parenta := parent.a, (FormattedValue, Interpolation)):
            if (cur.pfield.name == 'value' and (fs := parenta.format_spec) and
                fs.col_offset == end_col_offset and fs.lineno == end_ln + 1
            ):
                fs.lineno     = (a := self.a).end_lineno
                fs.col_offset = a.end_col_offset

            break

        cur = parent

    return put_fst


def _put_one_exprish_required(self: 'FST', code: Code | None, idx: int | None, field: str,
                              child: list[AST] | AST | None, static: onestatic, validate: bool = True,
                              target: fstloc | None = None, prefix: str = '', **options) -> 'FST':
    """Put a single required expression. Can be standalone or as part of sequence."""

    if validate:
        child = _validate_put(self, code, idx, field, child, options)

        if not child:
            raise ValueError(f'cannot replace nonexistent {self.a.__class__.__name__}.{field}' +
                             ("" if idx is None else f"[{idx}]"))

    childf  = child.f
    ctx     = ((ctx := getattr(child, 'ctx', None)) and ctx.__class__) or Load
    put_fst = _make_exprish_fst(self, code, idx, field, static, target or childf, ctx, prefix, **options)

    childf._set_ast(put_fst.a)

    return childf


def _put_one_exprish_optional(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                              static: onestatic, **options) -> Optional['FST']:
    """Put new, replace or delete an optional expression."""

    child = _validate_put(self, code, idx, field, child, options, can_del=True)

    if code is None:
        if child is None:  # delete nonexistent node, noop
            return None

    elif child:  # replace existing node
        return _put_one_exprish_required(self, code, idx, field, child, static, False, **options)

    info = static.getinfo(self, static, idx, field)
    loc  = info.loc_insdel

    if code is None:  # delete existing node
        if not loc:
            raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field} in this state')

        self.put_src(info.delstr or None, *loc, True)
        set_field(self.a, None, field, idx)
        child.f._unmake_fst_tree()

        return None

    # put new node

    if not loc:
        raise ValueError(f'cannot create {self.a.__class__.__name__}.{field} in this state')

    put_fst = _make_exprish_fst(self, code, idx, field, static, loc, static.ctx, info.prefix, info.suffix, **options)
    put_fst = FST(put_fst.a, self, astfield(field, idx))

    self._make_fst_tree([put_fst])
    put_fst.pfield.set(self.a, put_fst.a)

    return put_fst


def _put_one_exprish_sliceable(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                               static: onestatic, **options) -> Optional['FST']:
    """If deleting then will do so using slice operation, otherwise just a required expression."""

    if code is None:
        if options.get('to'):
            raise NodeError("delete with 'to' requires 'raw'")

        return lambda: self._put_slice(code, i := _fixup_one_index(len(child), idx), i + 1, field, True, **options)  # this informs _put_one() to delegate operation to this

    return _put_one_exprish_required(self, code, idx, field, child, static, **options)


def _put_one_FunctionDef_arguments(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                                   static: onestatic, **options) -> 'FST':
    """Put FunctionDef.arguments. Does not have location if there are no arguments."""

    return _put_one_exprish_required(self, code or '', idx, field, child, static, True,
                                     None if (args := self.a.args.f).loc else args._loc_arguments_empty(),
                                     **options)


def _put_one_Compare_None(self: 'FST', code: Code | None, idx: int | None, field: str, child: None,
                          static: onestatic, **options) -> 'FST':
    """Put to combined [Compare.left, Compare.comparators] using this total indexing."""

    idx, field, child = _Compare_None_index(self, idx)

    return _put_one_exprish_required(self, code, idx, field, child, static, **options)


def _put_one_Lambda_arguments(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                              static: onestatic, **options) -> 'FST':
    """Put Lambda.arguments. Does not have location if there are no arguments."""

    if code is None:
        code = ''

    child  = _validate_put(self, code, idx, field, child, options)  # we want to do it in same order as all other puts
    code   = static.code_as(code, self.root.parse_params)  # and we coerce here just so we can check if is empty args being put to set the prefix correctly
    prefix = ' ' if code.loc else ''  # if arguments has .loc then it is not empty

    if not (args := self.a.args.f).loc:
        target = args._loc_arguments_empty()

    else:  # need whole arguments location (including preceding space) because may be replacing with empty arguments
        _, _, last_ln, last_col  = args.last_child().loc
        ln, col, end_ln, end_col = self.loc
        end_ln, end_col          = _next_find(self.root._lines, last_ln, last_col, end_ln, end_col, ':')
        target                   = fstloc(ln, col + 6, end_ln, end_col)

    return _put_one_exprish_required(self, code, idx, field, child, static, False, target, prefix, **options)


def _put_one_Dict_keys(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                       static: onestatic, **options) -> 'FST':
    """Put optional dict key and if deleted parenthesize the value if needed."""

    ret = _put_one_exprish_optional(self, code, idx, field, child, static, **options)

    if (code is None and not (value := (a := self.a).values[idx].f).is_atom() and
        precedence_require_parens(value.a, a, 'values',  idx)
    ):
        value._parenthesize_grouping()

    return ret


def _put_one_withitem_optional_vars(self: 'FST', code: Code | None, idx: int | None, field: str, child: str,
                         static: onestatic, **options) -> str:
    """If delete leaves a single parenthesized context_expr `Tuple` then need to parenthesize that, otherwise it can be
    reparsed as multiple `withitems` instead of a single `Tuple`."""

    ret = _put_one_exprish_optional(self, code, idx, field, child, static, **options)

    if (code is None and (parent := self.parent) and isinstance(parenta := parent.a, (With, AsyncWith)) and
        len(parenta.items) == 1 and (f := self.a.context_expr.f).is_parenthesized_tuple() and
        len(_prev_pars(self.root.lines, parent.ln, parent.col, f.ln, f.col)) == 1  # no pars between start of `with` and start of parenthesized tuple?
    ):
        f._parenthesize_grouping()

    return ret


def _put_one_MatchValue_value(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                              static: onestatic, **options) -> 'FST':
    """Put MatchValue.value. Need to do this because a standalone MatchValue does not encompass parenthesized value
    parentheses."""

    ret              = _put_one_exprish_required(self, code, idx, field, child, static, **options)
    a                = self.a
    v                = a.value
    a.lineno         = v.lineno
    a.col_offset     = v.col_offset
    a.end_lineno     = v.end_lineno
    a.end_col_offset = v.end_col_offset

    return ret


# ......................................................................................................................
# identifier

def _put_one_identifier_required(self: 'FST', code: Code | None, idx: int | None, field: str, child: str,
                                 static: onestatic, **options) -> str:
    """Put a single required identifier."""

    _validate_put(self, code, idx, field, child, options)

    code = static.code_as(code, self.root.parse_params)
    info = static.getinfo(self, static, idx, field)

    self.put_src(code, *info.loc_ident, True)
    set_field(self.a, code, field, idx)

    return code


def _put_one_identifier_optional(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                                 static: onestatic, **options) -> str | None:
    """Put new, replace or delete an optional identifier."""

    child = _validate_put(self, code, idx, field, child, options, can_del=True)

    if code is None and child is None:  # delete nonexistent identifier, noop
        return None

    info = static.getinfo(self, static, idx, field)
    loc  = info.loc_insdel

    if code is None:  # delete existing identifier
        if not loc:
            raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field} in this state')

        self.put_src(info.delstr or None, *loc, True)
        set_field(self.a, None, field, idx)

        return None

    code = static.code_as(code, self.root.parse_params)

    if child is not None:  # replace existing identifier
        self.put_src(code, *info.loc_ident, True)
        set_field(self.a, code, field, idx)

    else: # put new identifier
        if not loc:
            raise ValueError(f'cannot create {self.a.__class__.__name__}.{field} in this state')

        params_offset = self.put_src(info.prefix + code + info.suffix, *loc, True, exclude=self)

        self.offset(*params_offset, self_=False)
        set_field(self.a, code, field, idx)

    return code


def _put_one_identifier_sliceable(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                                  static: onestatic, **options) -> Optional['FST']:
    """If deleting then will do so using slice operation, otherwise just a required identifier."""

    if code is None:
        if options.get('to'):
            raise NodeError("delete with 'to' requires 'raw'")

        return lambda: self._put_slice(code, i := _fixup_one_index(len(child), idx), i + 1, field, True, **options)  # this informs _put_one() to delegate operation to this

    return _put_one_identifier_required(self, code, idx, field, child, static, **options)


def _put_one_ExceptHandler_name(self: 'FST', code: Code | None, idx: int | None, field: str, child: str,
                                static: onestatic, **options) -> str:
    """If adding a name to an ExceptHandler with tuple of exceptions then make sure it is parenthesized."""

    ret = _put_one_identifier_optional(self, code, idx, field, child, static, **options)

    if ret and (typef := self.a.type.f).is_parenthesized_tuple() is False:
        typef._parenthesize_tuple()

    return ret


def _put_one_keyword_arg(self: 'FST', code: Code | None, idx: int | None, field: str, child: str,
                         static: onestatic, **options) -> str:
    """Don't allow delete keyword.arg if non-keywords follow."""

    if code is None and (parent := self.parent):
        if isinstance(parenta := parent.a, Call):
            if (args := parenta.args) and args[-1].f.loc > self.loc:
                raise ValueError(f'cannot delete Call.keywords[{self.pfield.idx}].arg in this state (non-keywords follow)')

        elif isinstance(parenta, ClassDef):
            if (bases := parenta.bases) and bases[-1].f.loc > self.loc:
                raise ValueError(f'cannot delete ClassDef.keywords[{self.pfield.idx}].arg in this state (non-keywords follow)')

    return _put_one_identifier_optional(self, code, idx, field, child, static, **options)


def _put_one_MatchStar_name(self: 'FST', code: Code | None, idx: int | None, field: str, child: str, static: onestatic,
                            **options) -> str:
    """Slightly annoying MatchStar.name. '_' really means delete."""

    if code is None:
        code = '_'

    ret = _put_one_identifier_required(self, code, idx, field, child, static, **options)

    if self.a.name == '_':
        self.a.name = None

    return ret


def _put_one_MatchAs_name(self: 'FST', code: Code | None, idx: int | None, field: str, child: str, static: onestatic,
                          **options) -> str:
    """Very annoying MatchAs.name. '_' really means delete, which can't be done if there is a pattern, and can't be
    assigned to a pattern."""

    if code is None:
        code = '_'
    else:
        code = _code_as_identifier(code, self.root.parse_params)

    if self.a.pattern and code == '_':
        raise ValueError("cannot change MatchAs with pattern into wildcard '_'")

    ret = _put_one_identifier_required(self, code, idx, field, child, static, **options)

    if self.a.name == '_':
        self.a.name = None

    return ret


# ......................................................................................................................

def _put_one(self: 'FST', code: Code | None, idx: int | None, field: str, **options) -> Optional['FST']:
    """Put new, replace or delete a node (or limited non-node) to a field of `self`.

    **Parameters:**
    - `code`: The code to put in the form of an `FST`, an `AST`, a string of source or a list of lines of source. If
        is `None` then will attempt to remove optional field or delete node from a mutable body list of nodes using
        slice operations.
    - `idx`: The index in the body list of the field to put, or `None` if is a standalone node.
    - `field`: The `AST` field to modify.
    - `options`: See `FST.set_option`.
    """

    ast             = self.a
    child           = getattr(self.a, field) if field else None
    raw             = FST.get_option('raw', options)
    handlers        = _PUT_ONE_HANDLERS.get((ast.__class__, field))
    modified        = self._modifying(field)
    ret_or_delegate = None

    if raw is not True:
        try:
            if handlers:
                handler, _, static = handlers
                ret_or_delegate    = handler(self, code, idx, field, child, static, modified=modified, **options)

                if not isinstance(ret_or_delegate, FunctionType):
                    modified()

                    return ret_or_delegate

        except (SyntaxError, NodeError):
            if not raw:
                raise

        else:
            if ret_or_delegate is not None:  # delegate operation to slice?
                return ret_or_delegate()

            if not raw:
                raise ValueError(f'cannot {"delete" if code is None else "replace"} {ast.__class__.__name__}.{field}')


    # TODO: redo raw starting below


    if isinstance(child, list):
        child = child[idx]

    # special raw cases, TODO: move into dedicated _put_raw or do via _PUT_ONE_RAW_HANDLERS

    is_dict = isinstance(ast, Dict)

    if not field:  # maybe putting to special case field?
        if is_dict or isinstance(ast, MatchMapping):
            key = key.f if (key := ast.keys[idx]) else self._dict_key_or_mock_loc(key, ast.values[idx].f)
            end = (ast.values if is_dict else ast.patterns)[idx].f

            self._reparse_raw_loc(code, key.ln, key.col, end.end_ln, end.end_col)

            return self.repath()

        if isinstance(ast, Compare):
            idx   = _fixup_one_index(len(ast.comparators) + 1, idx)  # need to do this because of compound body including 'left'
            child = ast.comparators[idx - 1] if idx else ast.left

    if is_dict and field == 'keys' and (keys := ast.keys)[idx] is None:  # '{**d}' with key=None
        start_loc = self._dict_key_or_mock_loc(keys[idx], ast.values[idx].f)

        ln, col, end_ln, end_col = start_loc.loc

        self.put_src([': '], ln, col, end_ln, end_col)
        self._reparse_raw_loc(code, ln, col, ln, col)

        return self.repath()

    ret = child.f._reparse_raw_node(code, **options)

    return None if code is None else ret


# ......................................................................................................................
# field info

_restrict_default     = [FormattedValue, Interpolation, Slice]
_restrict_fstr_values = [FormattedValue, Interpolation]
_oneinfo_default      = oneinfo()

def _one_info_constant(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:  # only Constant and MatchSingleton
    return oneinfo('', None, self.loc)

def _one_info_exprish_required(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _oneinfo_default

_onestatic_expr_required             = onestatic(_one_info_exprish_required, _restrict_default)
_onestatic_comprehension_required    = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_comprehension)
_onestatic_arguments_required        = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_arguments)
_onestatic_arguments_lambda_required = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_arguments_lambda)
_onestatic_arg_required              = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_arg)
_onestatic_keyword_required          = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_keyword)
_onestatic_withitem_required         = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_withitem)
_onestatic_pattern_required          = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_pattern)
_onestatic_type_param_required       = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_type_param)
_onestatic_target_Name               = onestatic(_one_info_exprish_required, Name, ctx=Store)
_onestatic_target_single             = onestatic(_one_info_exprish_required, (Name, Attribute, Subscript), ctx=Store)
_onestatic_target                    = onestatic(_one_info_exprish_required, (Name, Attribute, Subscript, Tuple, List), ctx=Store)

def _one_info_identifier_required(self: 'FST', static: onestatic, idx: int | None, field: str, prefix: str | None = None,
                                 ) -> oneinfo:  # required, cannot delete or put new
    ln, col, end_ln, end_col = self.loc
    lines                    = self.root._lines

    if not prefix:
        end_col = re_identifier.match(lines[ln], col, end_col).end()  # must be there

    else:
        ln, col      = _next_find(lines, ln, col, end_ln, end_col, prefix, lcont=None)  # must be there, have to search because could be preceded by something (like 'async')
        ln, col, src =  _next_find_re(lines, ln, col + len(prefix), end_ln, end_col, re_identifier, lcont=None)  # must be there
        end_col      = col + len(src)

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

_onestatic_identifier_required = onestatic(_one_info_identifier_required, _restrict_default, code_as=_code_as_identifier)

def _one_info_identifier_alias(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:  # required, cannot delete or put new
    ln, col, _, end_col = self.loc
    end_col             = re_identifier_alias.match(self.root._lines[ln], col, end_col).end()  # must be there

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

def _one_info_FunctionDef_name(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, 'def')

_onestatic_FunctionDef_name = onestatic(_one_info_FunctionDef_name, _restrict_default, code_as=_code_as_identifier)

def _one_info_FunctionDef_returns(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self._loc_block_header_end(True)
    ret_end_ln               = end_ln
    ret_end_col              = end_col - 1

    if returns := self.a.returns:
        ln, col               = prev.loc[2:] if (prev := (retf := returns.f).prev()) else self.loc[:2]
        end_ln, end_col, _, _ = retf.pars()

    args_end_ln, args_end_col = _prev_find(self.root._lines, ln, col, end_ln, end_col, ')')  # must be there

    return oneinfo(' -> ', fstloc(args_end_ln, args_end_col + 1, ret_end_ln, ret_end_col))

_onestatic_FunctionDef_returns = onestatic(_one_info_FunctionDef_returns, _restrict_default)

def _one_info_ClassDef_name(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, 'class')

def _one_info_Return_value(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' ', fstloc((loc := self.loc).ln, loc.col + 6, loc.end_ln, loc.end_col))

def _one_info_AnnAssign_value(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' = ',
                   fstloc((loc := self.a.annotation.f.pars()).end_ln, loc.end_col, self.end_ln, self.end_col))

def _one_info_Raise_exc(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if self.a.cause:
        return _oneinfo_default  # can not del (and exists, so can't put new)

    ln, col, end_ln, end_col = self.loc

    return oneinfo(' ', fstloc(ln, col + 5, end_ln, end_col))

def _one_info_Raise_cause(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if not (exc := self.a.exc):
        return _oneinfo_default  # can not put (or del because cause doesn't exist)

    _, _, ln, col = exc.f.pars()

    return oneinfo(' from ', fstloc(ln, col, self.end_ln, self.end_col))

def _one_info_Assert_msg(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(', ', fstloc((loc := self.a.test.f.pars()).end_ln, loc.end_col, self.end_ln, self.end_col))

def _one_info_ImportFrom_module(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    lines                    = self.root._lines

    if not self.a.level:  # cannot insert or delete
        ln, col, src =  _next_find_re(lines, ln, col + 4, end_ln, end_col, re_identifier_dotted, lcont=None)  # must be there, col+4 is for 'from'
        end_col      = col + len(src)

        return oneinfo('', None, fstloc(ln, col, ln, end_col))

    self_ln, self_col, _, _ = self.loc
    ln, col                 = _prev_find(self.root._lines, self_ln, self_col, *self.a.names[0].f.loc[:2], 'import')
    ln, col, src            = _prev_src(self.root._lines, self_ln, self_col, ln, col)  # must be there, the module name with any/some/all preceding '.' level indicators
    end_col                 = col + len(src)
    col                     = end_col - len(src.lstrip('.'))

    return oneinfo('', loc := fstloc(ln, col, ln, end_col), loc)

def _one_info_Global_Nonlocal_names(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc

    col   += 6 if isinstance(self.a, Global) else 8
    lines  = self.root._lines
    idx    = idx % len(names := self.names)

    while idx:  # skip the commas
        ln, col  = _next_find(lines, ln, col, end_ln, end_col, ',')  # must be there (idx assumed to be validated)
        col     += 1
        idx     -= 1

    ln, col, src = _next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there

    return oneinfo('', None, fstloc(ln, col, ln, col + len(src)))

_onestatic_Global_Nonlocal_names = onestatic(_one_info_Global_Nonlocal_names, _restrict_default, code_as=_code_as_identifier)

def _one_info_Dict_key(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    key                   = (a := self.a).keys[idx]
    value                 = a.values[idx].f
    end_ln, end_col, _, _ = value.pars()
    ln, col, _, _         = self._dict_key_or_mock_loc(key, value) if key is None else key.f.pars()

    return oneinfo('', fstloc(ln, col, end_ln, end_col), None, ': ', '**')

def _one_info_Yield_value(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' ', fstloc((loc := self.loc).ln, loc.col + 5, loc.end_ln, loc.end_col))

def _one_info_Attribute_attr(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col         = self.a.value.f.loc
    _, _, end_ln, end_col = self.loc
    lines                 = self.root._lines
    ln, col               = _next_find(lines, ln, col, end_ln, end_col, '.')  # must be there
    ln, col, src          = _next_src(lines, ln, col + 1, end_ln, end_col)  # must be there

    return oneinfo('', None, fstloc(ln, col, ln, col + len(src)))

def _one_info_Slice_lower(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc

    if lower := self.a.lower:
        end_ln, end_col = _next_find(self.root._lines, (loc := lower.f.loc).end_ln, loc.end_col, end_ln, end_col, ':')  # must be there
    else:
        end_ln, end_col = _next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # must be there

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

_onestatic_Slice_lower = onestatic(_one_info_Slice_lower, _restrict_default)

def _one_info_Slice_upper(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln                    = (lloc := _one_info_Slice_lower(self, _onestatic_Slice_lower, idx, field).loc_insdel).end_ln
    col                   = lloc.end_col + 1
    _, _, end_ln, end_col = self.loc

    if upper := self.a.upper:
        end = _next_find(self.root._lines, (loc := upper.f.loc).end_ln, loc.end_col, end_ln, end_col, ':')  # may or may not be there
    else:
        end = _next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # may or may not be there

    if end:
        end_ln, end_col = end

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

_onestatic_Slice_upper = onestatic(_one_info_Slice_upper, _restrict_default)

def _one_info_Slice_step(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln  = (uloc := _one_info_Slice_upper(self, _onestatic_Slice_upper, idx, field).loc_insdel).end_ln
    col = uloc.end_col

    if self.root._lines[ln].startswith(':', col):
        col    += 1
        prefix  = ''
    else:
        prefix = ':'

    return oneinfo(prefix, fstloc(ln, col, self.end_ln, self.end_col))

_onestatic_Slice_step = onestatic(_one_info_Slice_step, _restrict_default)

def _one_info_ExceptHandler_type(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if (a := self.a).name:
        return _oneinfo_default  # can not del (and exists, so can't put new)

    if type_ := a.type:
        _, _, end_ln, end_col = type_.f.pars()
    else:
        end_ln, end_col  = self._loc_block_header_end()  # because 'name' can not be there
        end_col         -= 1

    ln, col, _, _ = self.loc
    col           = col + 6  # 'except'

    if star := _next_src(self.root.lines, ln, col, end_ln, end_col):  # 'except*'?
        if star.src.startswith('*'):
            return _oneinfo_default  # can not del type from except* and can not insert because can never not exist

    return oneinfo(' ', fstloc(ln, col, end_ln, end_col))

def _one_info_ExceptHandler_name(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if not (type_ := (a := self.a).type):
        return _oneinfo_default  # can not put new and does not exist

    _, _, ln, col   = type_.f.pars()
    end_ln, end_col = self._loc_block_header_end()
    loc_insdel      = fstloc(ln, col, end_ln, end_col - 1)

    if (name := a.name) is None:
        loc_ident = None

    else:
        lines     = self.root._lines
        ln, col   = _next_find(lines, ln, col, end_ln, end_col, 'as')  # skip the 'as'
        ln, col   = _next_find(lines, ln, col + 2, end_ln, end_col, name)  # must be there
        loc_ident = fstloc(ln, col, ln, col + len(name))

    return oneinfo(' as ', loc_insdel, loc_ident)

def _one_info_arguments_vararg(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if vararg := (a := self.a).vararg:  # delete location
        if next := (varargf := vararg.f).next():
            _, _, end_ln, end_col = varargf.pars()
        else:
            _, _, end_ln, end_col = self.loc  # there may be a trailing comma

        if prev := varargf.prev():
            delstr = ', *' if a.kwonlyargs else ''

            if not (a.posonlyargs and ((field := prev.pfield.name) == 'posonlyargs' or
                (field == 'defaults' and prev.prev().pfield.name == 'posonlyargs'))
            ):
                _, _, ln, col = prev.pars()

                return oneinfo('', fstloc(ln, col, end_ln, end_col), delstr=delstr)

            ln, col = _next_find(self.root._lines, prev.end_ln, prev.end_col, end_ln, end_col, '/')  # must be there

            return oneinfo('', fstloc(ln, col + 1, end_ln, end_col), delstr=delstr)

        if next:
            if a.kwonlyargs and next.pfield.name == 'kwonlyargs':
                next_ln, next_col, _, _ = next.pars()

                return oneinfo('', fstloc(self.ln, self.col, next_ln, next_col), delstr='*, ')

            end_ln, end_col = _next_find(self.root._lines, end_ln, end_col, next.ln, next.col, '**')  # must be there

            return oneinfo('', fstloc(self.ln, self.col, end_ln, end_col))

        if not (parent := self.parent) or not isinstance(parent.a, Lambda):
            return oneinfo('', self.loc)

        ln, col, _, _ = parent.loc

        return oneinfo('', fstloc(ln, col + 6, end_ln, end_col))

    # insert location

    if kwonlyargs := a.kwonlyargs:
        end_ln, end_col, _, _ = (kwonlyarg := kwonlyargs[0].f).loc

        if prev := kwonlyarg.prev():
            _, _, ln, col = prev.loc
        else:
            ln, col, _, _ = self.loc

        ln, col = _next_find(self.root._lines, ln, col, end_ln, end_col, '*')  # must be there

        return oneinfo('', fstloc(ln, (col := col + 1), ln, col))

    if kwarg := a.kwarg:
        end_ln, end_col, _, _ = (kwargf := kwarg.f).loc

        if prev := kwargf.prev():
            _, _, ln, col = prev.loc
        else:
            ln, col, _, _ = self.loc

        ln, col = _next_find(self.root._lines, ln, col, end_ln, end_col, '**')  # must be there

        return oneinfo('*', fstloc(ln, col, ln, col), None, ', ')

    if a.args:
        _, _, ln, col = self.last_child().pars()

        return oneinfo(', *', fstloc(ln, col, ln, col))

    if a.posonlyargs:
        _, _, ln, col = self.last_child().loc

        ln, col = _next_find(self.root._lines, ln, col, self.end_ln, self.end_col, '/')  # must be there

        return oneinfo(', *', fstloc(ln, (col := col + 1), ln, col))

    loc    = self._loc_arguments_empty()
    prefix = ' *' if (parent := self.parent) and isinstance(parent.a, Lambda) else '*'

    return oneinfo(prefix, loc)

def _one_info_arguments_kw_defaults(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if ann := (arg := self.a.kwonlyargs[idx]).annotation:
        _, _, ln, col = ann.f.pars()
        prefix        = ' = '

    else:
        ln     = (loc := arg.f.loc).ln
        col    = loc.col + len(arg.arg)
        prefix = '='

    if default := self.a.kw_defaults[idx]:
        _, _, end_ln, end_col = default.f.pars()

    else:
        end_ln  = ln
        end_col = col

    return oneinfo(prefix, fstloc(ln, col, end_ln, end_col))

def _one_info_arguments_kwarg(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if kwarg := (a := self.a).kwarg:  # delete location
        if not (prev := (kwargf := kwarg.f).prev()):
            if not (parent := self.parent) or not isinstance(parent.a, Lambda):
                return oneinfo('', self.loc)

            ln, col, _, _ = parent.loc

            return oneinfo('', fstloc(ln, col + 6, self.end_ln, self.end_col))

        if not (a.posonlyargs and ((field := prev.pfield.name) == 'posonlyargs' or
            (field == 'defaults' and prev.prev().pfield.name == 'posonlyargs'))
        ):
            _, _, ln, col = prev.pars()

        else:
            ln, col  = _next_find(self.root._lines, prev.end_ln, prev.end_col, kwargf.ln, kwargf.col, '/')  # must be there
            col     += 1

        return oneinfo('', fstloc(ln, col, self.end_ln, self.end_col))

    # insert location

    if not (loc := self.loc):
        loc    = self._loc_arguments_empty()
        prefix = ' **' if (parent := self.parent) and isinstance(parent.a, Lambda) else '**'

        return oneinfo(prefix, loc)

    _, _, end_ln, end_col = loc

    last = self.last_child()

    if not (a.posonlyargs and ((field := last.pfield.name) == 'posonlyargs' or
        (field == 'defaults' and last.prev().pfield.name == 'posonlyargs'))
    ):
        _, _, ln, col = last.pars()

    else:
        ln, col  = _next_find(self.root._lines, last.end_ln, last.end_col, end_ln, end_col, '/')  # must be there
        col     += 1

    return oneinfo(', **', fstloc(ln, col, end_ln, end_col))

def _one_info_arg_annotation(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(': ', fstloc((loc := self.loc).ln, loc.col + len(self.a.arg), self.end_ln, self.end_col))

def _one_info_keyword_arg(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    end_ln, end_col, _, _ = (a := self.a).value.f.pars()
    ln, col, _, _         = self.loc
    arg_end_col           = col + 2 if a.arg is None else re_identifier.match(self.root._lines[ln], col).end() # must be there

    return oneinfo('', fstloc(ln, col, end_ln, end_col), fstloc(ln, col, ln, arg_end_col), '=', '**')

def _one_info_alias_asname(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col  = self.loc
    loc_insdel                = fstloc(ln, col + len((a := self.a).name), end_ln, end_col)

    if (asname := a.asname) is None:
        loc_ident = None

    else:
        lines     = self.root._lines
        ln, col   = _next_find(lines, ln, col, end_ln, end_col, 'as')  # skip the 'as'
        ln, col   = _next_find(lines, ln, col + 2, end_ln, end_col, asname)  # must be there
        loc_ident = fstloc(ln, col, ln, col + len(asname))

    return oneinfo(' as ', loc_insdel, loc_ident)

def _one_info_withitem_optional_vars(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col = self.a.context_expr.f.pars()

    if optional_vars := self.a.optional_vars:
        _, _, end_ln, end_col = optional_vars.f.pars()
    else:
        end_ln  = ln
        end_col = col

    return oneinfo(' as ', fstloc(ln, col, end_ln, end_col))

def _one_info_match_case_guard(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col          = self.a.pattern.f.pars()
    _, _, end_ln, end_col  = self._loc_block_header_end(True)
    end_col               -= 1

    return oneinfo(' if ', fstloc(ln, col, end_ln, end_col))

def _one_info_MatchMapping_rest(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col  = self.loc
    end_col                  -= 1

    if patterns := (a := self.a).patterns:
        _, _, ln, col = patterns[-1].f.pars()
        prefix        = ', **'

    else:
        col    += 1
        prefix  = '**'

    if (rest := a.rest) is None:
        loc_ident = None
    else:
        rest_ln, rest_col = _next_find(self.root._lines, ln, col, end_ln, end_col, rest)
        loc_ident         = fstloc(rest_ln, rest_col, rest_ln, rest_col + len(rest))

    return oneinfo(prefix, fstloc(ln, col, end_ln, end_col), loc_ident)

def _one_info_MatchClass_kwd_attrs(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast          = self.a
    lines        = self.root._lines
    kwd_patterns = ast.kwd_patterns

    if idx % len(kwd_patterns):  # could be negative
        _, _, ln, col = kwd_patterns[idx - 1].f.loc
    elif patterns := ast.patterns:
        _, _, ln, col = patterns[-1].f.loc
    else:
        _, _, ln, col = ast.cls.f.loc

    end_ln, end_col = _prev_find(lines, ln, col, *kwd_patterns[idx].f.loc[:2], '=')  # must be there
    ln, col, src    = _prev_src(lines, ln, col, end_ln, end_col)  # must be there
    end_col         = col + len(src)
    col             = end_col - len(src.lstrip('(,'))

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

def _one_info_MatchStar_name(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '*')

def _one_info_MatchAs_pattern(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if (name := (a := self.a).name) is None:
        return _oneinfo_default  # cannot insert or delete because is wildcard '_'

    ln, col, end_ln, end_col = self.loc

    if (pattern := a.pattern) is None:
        return oneinfo('', fstloc(ln, col, ln, col), None, ' as ')

    lines           = self.root._lines
    as_ln, as_col   = _next_find(lines, *pattern.f.pars()[2:], end_ln, end_col, 'as')  # skip the 'as'
    end_ln, end_col = _next_find(lines, as_ln, as_col + 2, end_ln, end_col, name)

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

def _one_info_MatchAs_name(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc

    if (pattern := (a := self.a).pattern) is None:
        prefix  = ''

    else:
        prefix  = 'as'
        lines   = self.root._lines
        ln, col = _next_find(lines, *pattern.f.pars()[2:], end_ln, end_col, 'as')  # skip the 'as'
        ln, col = _next_find(lines, ln, col + 2, end_ln, end_col, a.name or '_')

    return oneinfo(prefix, None, fstloc(ln, col, ln, end_col))

def _one_info_TypeVar_bound(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln  = self.ln
    col = self.col + len(self.a.name)

    if bound := self.a.bound:
        _, _, end_ln, end_col = bound.f.pars()
    else:
        end_ln  = ln
        end_col = col

    return oneinfo(': ', fstloc(ln, col, end_ln, end_col))

def _one_info_TypeVar_default_value(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    if bound := self.a.bound:
        _, _, ln, col = bound.f.pars()
    else:
        ln  = self.ln
        col = self.col + len(self.a.name)

    return oneinfo(' = ', fstloc(ln, col, self.end_ln, self.end_col))

def _one_info_ParamSpec_name(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '**')

def _one_info_ParamSpec_default_value(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    ln, col, src             = _next_find_re(self.root._lines, ln, col + 2, end_ln, end_col, re_identifier)  # + '**', identifier must be there

    return oneinfo(' = ', fstloc(ln, col + len(src), self.end_ln, self.end_col))

def _one_info_TypeVarTuple_default_value(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    ln, col, src             = _next_find_re(self.root._lines, ln, col + 1, end_ln, end_col, re_identifier)  # + '*', identifier must be there

    return oneinfo(' = ', fstloc(ln, col + len(src), self.end_ln, self.end_col))

def _one_info_TypeVarTuple_name(self: 'FST', static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '*')


# TODO: finish these

_PUT_ONE_HANDLERS = {
    (Module, 'body'):                     (_put_one_stmtish, None, None), # stmt*
    (Interactive, 'body'):                (_put_one_stmtish, None, None), # stmt*
    (Expression, 'body'):                 (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (FunctionDef, 'decorator_list'):      (_put_one_exprish_sliceable, None, _onestatic_expr_required), # expr*
    (FunctionDef, 'name'):                (_put_one_identifier_required, None, _onestatic_FunctionDef_name), # identifier
    (FunctionDef, 'type_params'):         (_put_one_exprish_sliceable, None, _onestatic_type_param_required), # type_param*
    (FunctionDef, 'args'):                (_put_one_FunctionDef_arguments, None, _onestatic_arguments_required), # arguments
    (FunctionDef, 'returns'):             (_put_one_exprish_optional, None, _onestatic_FunctionDef_returns), # expr?
    (FunctionDef, 'body'):                (_put_one_stmtish, None, None), # stmt*
    (AsyncFunctionDef, 'decorator_list'): (_put_one_exprish_sliceable, None, _onestatic_expr_required), # expr*
    (AsyncFunctionDef, 'name'):           (_put_one_identifier_required, None, _onestatic_FunctionDef_name), # identifier
    (AsyncFunctionDef, 'type_params'):    (_put_one_exprish_sliceable, None, _onestatic_type_param_required), # type_param*
    (AsyncFunctionDef, 'args'):           (_put_one_FunctionDef_arguments, None, _onestatic_arguments_required), # arguments
    (AsyncFunctionDef, 'returns'):        (_put_one_exprish_optional, None, _onestatic_FunctionDef_returns), # expr?
    (AsyncFunctionDef, 'body'):           (_put_one_stmtish, None, None), # stmt*
    (ClassDef, 'decorator_list'):         (_put_one_exprish_sliceable, None, _onestatic_expr_required), # expr*
    (ClassDef, 'name'):                   (_put_one_identifier_required, None, onestatic(_one_info_ClassDef_name, _restrict_default, code_as=_code_as_identifier)), # identifier
    (ClassDef, 'type_params'):            (_put_one_exprish_sliceable, None, _onestatic_type_param_required), # type_param*
    (ClassDef, 'bases'):                  (_put_one_exprish_sliceable, None, _onestatic_expr_required), # expr*
    (ClassDef, 'keywords'):               (_put_one_exprish_sliceable, None, _onestatic_keyword_required), # keyword*
    (ClassDef, 'body'):                   (_put_one_stmtish, None, None), # stmt*
    (Return, 'value'):                    (_put_one_exprish_optional, None, onestatic(_one_info_Return_value, _restrict_default)), # expr?
    (Delete, 'targets'):                  (_put_one_exprish_sliceable, None, _onestatic_target), # expr*
    (Assign, 'targets'):                  (_put_one_exprish_sliceable, None, _onestatic_target), # expr*
    (Assign, 'value'):                    (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (TypeAlias, 'name'):                  (_put_one_exprish_required, None, _onestatic_target_Name), # expr
    (TypeAlias, 'type_params'):           (_put_one_exprish_sliceable, None, _onestatic_type_param_required), # type_param*
    (TypeAlias, 'value'):                 (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (AugAssign, 'target'):                (_put_one_exprish_required, None, _onestatic_target_single), # expr
    (AugAssign, 'op'):                    (_put_one_op, None, onestatic(None, code_as=_code_as_operator_aug)), # operator
    (AugAssign, 'value'):                 (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (AnnAssign, 'target'):                (_put_one_exprish_required, None, _onestatic_target_single), # expr
    (AnnAssign, 'annotation'):            (_put_one_exprish_required, None, onestatic(_one_info_exprish_required, _restrict_default)), # expr  - exclude [Lambda, Yield, YieldFrom, Await, NamedExpr]?
    (AnnAssign, 'value'):                 (_put_one_exprish_optional, None, onestatic(_one_info_AnnAssign_value, _restrict_default)), # expr?
    (For, 'target'):                      (_put_one_exprish_required, None, _onestatic_target), # expr
    (For, 'iter'):                        (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (For, 'body'):                        (_put_one_stmtish, None, None), # stmt*
    (For, 'orelse'):                      (_put_one_stmtish, None, None), # stmt*
    (AsyncFor, 'target'):                 (_put_one_exprish_required, None, _onestatic_target), # expr
    (AsyncFor, 'iter'):                   (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (AsyncFor, 'body'):                   (_put_one_stmtish, None, None), # stmt*
    (AsyncFor, 'orelse'):                 (_put_one_stmtish, None, None), # stmt*
    (While, 'test'):                      (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (While, 'body'):                      (_put_one_stmtish, None, None), # stmt*
    (While, 'orelse'):                    (_put_one_stmtish, None, None), # stmt*
    (If, 'test'):                         (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (If, 'body'):                         (_put_one_stmtish, None, None), # stmt*
    (If, 'orelse'):                       (_put_one_stmtish, None, None), # stmt*
    (With, 'items'):                      (_put_one_exprish_sliceable, None, _onestatic_withitem_required), # withitem*
    (With, 'body'):                       (_put_one_stmtish, None, None), # stmt*
    (AsyncWith, 'items'):                 (_put_one_exprish_sliceable, None, _onestatic_withitem_required), # withitem*
    (AsyncWith, 'body'):                  (_put_one_stmtish, None, None), # stmt*
    (Match, 'subject'):                   (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Match, 'cases'):                     (_put_one_stmtish, None, None), # match_case*
    (Raise, 'exc'):                       (_put_one_exprish_optional, None, onestatic(_one_info_Raise_exc, _restrict_default)), # expr?
    (Raise, 'cause'):                     (_put_one_exprish_optional, None, onestatic(_one_info_Raise_cause, _restrict_default)), # expr?
    (Try, 'body'):                        (_put_one_stmtish, None, None), # stmt*
    (Try, 'handlers'):                    (_put_one_stmtish, None, None), # excepthandler*
    (Try, 'orelse'):                      (_put_one_stmtish, None, None), # stmt*
    (Try, 'finalbody'):                   (_put_one_stmtish, None, None), # stmt*
    (TryStar, 'body'):                    (_put_one_stmtish, None, None), # stmt*
    (TryStar, 'handlers'):                (_put_one_stmtish, None, None), # excepthandler*
    (TryStar, 'orelse'):                  (_put_one_stmtish, None, None), # stmt*
    (TryStar, 'finalbody'):               (_put_one_stmtish, None, None), # stmt*
    (Assert, 'test'):                     (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Assert, 'msg'):                      (_put_one_exprish_optional, None, onestatic(_one_info_Assert_msg, _restrict_default)), # expr?
    (Import, 'names'):                    (_put_one_exprish_sliceable, None, onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_alias_dotted)), # alias*
    (ImportFrom, 'module'):               (_put_one_identifier_optional, None, onestatic(_one_info_ImportFrom_module, _restrict_default, code_as=_code_as_identifier_dotted)), # identifier? (dotted)
    (ImportFrom, 'names'):                (_put_one_exprish_sliceable, None, onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_alias_maybe_star)), # alias*
    (Global, 'names'):                    (_put_one_identifier_sliceable, None, _onestatic_Global_Nonlocal_names), # identifier*
    (Nonlocal, 'names'):                  (_put_one_identifier_sliceable, None, _onestatic_Global_Nonlocal_names), # identifier*
    (Expr, 'value'):                      (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (BoolOp, 'op'):                       (_put_one_BoolOp_op, None, _onestatic_identifier_required), # boolop
    (BoolOp, 'values'):                   (_put_one_exprish_sliceable, None, _onestatic_expr_required), # expr*
    (NamedExpr, 'target'):                (_put_one_exprish_required, None, _onestatic_target_Name), # expr
    (NamedExpr, 'value'):                 (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (BinOp, 'left'):                      (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (BinOp, 'op'):                        (_put_one_op, None, onestatic(None, code_as=_code_as_operator)), # operator
    (BinOp, 'right'):                     (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (UnaryOp, 'op'):                      (_put_one_op, None, onestatic(None, code_as=_code_as_unaryop)), # unaryop
    (UnaryOp, 'operand'):                 (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Lambda, 'args'):                     (_put_one_Lambda_arguments, None, _onestatic_arguments_lambda_required), # arguments
    (Lambda, 'body'):                     (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (IfExp, 'body'):                      (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (IfExp, 'test'):                      (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (IfExp, 'orelse'):                    (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Dict, 'keys'):                       (_put_one_Dict_keys, None, onestatic(_one_info_Dict_key, _restrict_default)), # expr*
    (Dict, 'values'):                     (_put_one_exprish_required, None, _onestatic_expr_required), # expr*
    (Set, 'elts'):                        (_put_one_exprish_sliceable, None, _onestatic_expr_required), # expr*
    (ListComp, 'elt'):                    (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (ListComp, 'generators'):             (_put_one_exprish_sliceable, None, _onestatic_comprehension_required), # comprehension*
    (SetComp, 'elt'):                     (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (SetComp, 'generators'):              (_put_one_exprish_sliceable, None, _onestatic_comprehension_required), # comprehension*
    (DictComp, 'key'):                    (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (DictComp, 'value'):                  (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (DictComp, 'generators'):             (_put_one_exprish_sliceable, None, _onestatic_comprehension_required), # comprehension*
    (GeneratorExp, 'elt'):                (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (GeneratorExp, 'generators'):         (_put_one_exprish_sliceable, None, _onestatic_comprehension_required), # comprehension*
    (Await, 'value'):                     (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Yield, 'value'):                     (_put_one_exprish_optional, None, onestatic(_one_info_Yield_value, _restrict_default)), # expr?
    (YieldFrom, 'value'):                 (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Compare, 'left'):                    (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Compare, 'ops'):                     (_put_one_op, None, onestatic(None, code_as=_code_as_cmpop)), # cmpop*
    (Compare, 'comparators'):             (_put_one_exprish_required, None, _onestatic_expr_required), # expr*
    (Compare, ''):                        (_put_one_Compare_None, None, _onestatic_expr_required), # expr*
    (Call, 'func'):                       (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Call, 'args'):                       (_put_one_exprish_sliceable, None, onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_expr_call_arg)), # expr*
    (Call, 'keywords'):                   (_put_one_exprish_sliceable, None, _onestatic_keyword_required), # keyword*
    (FormattedValue, 'value'):            (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    # (FormattedValue, 'format_spec'):      (_put_one_default, None, None), # expr?
    (Interpolation, 'value'):             (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    # (Interpolation, 'format_spec'):       (_put_one_default, None, None), # expr?
    # (JoinedStr, 'values'):                (_put_one_default, None, None), # expr*  - ??? no location on py < 3.12
    # (TemplateStr, 'values'):              (_put_one_default, None, None), # expr*  - ??? no location on py < 3.12
    (Constant, 'value'):                  (_put_one_constant, None, onestatic(_one_info_constant, Constant)), # constant
    (Attribute, 'value'):                 (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Attribute, 'attr'):                  (_put_one_identifier_required, None, onestatic(_one_info_Attribute_attr, _restrict_default, code_as=_code_as_identifier)), # identifier
    (Subscript, 'value'):                 (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Subscript, 'slice'):                 (_put_one_exprish_required, None, onestatic(_one_info_exprish_required, _restrict_fstr_values, code_as=_code_as_slice)), # expr
    (Starred, 'value'):                   (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (Name, 'id'):                         (_put_one_identifier_required, None, _onestatic_identifier_required), # identifier
    (List, 'elts'):                       (_put_one_exprish_sliceable, None, _onestatic_expr_required), # expr*
    (Tuple, 'elts'):                      (_put_one_exprish_sliceable, None, onestatic(_one_info_exprish_required, _restrict_fstr_values, code_as=_code_as_expr_slice_tuple)), # expr*  - special handling because Tuples can contain Slices in a .slice field
    (Slice, 'lower'):                     (_put_one_exprish_optional, None, _onestatic_Slice_lower), # expr?
    (Slice, 'upper'):                     (_put_one_exprish_optional, None, _onestatic_Slice_upper), # expr?
    (Slice, 'step'):                      (_put_one_exprish_optional, None, _onestatic_Slice_step), # expr?
    (comprehension, 'target'):            (_put_one_exprish_required, None, _onestatic_target), # expr
    (comprehension, 'iter'):              (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (comprehension, 'ifs'):               (_put_one_exprish_sliceable, None, _onestatic_expr_required), # expr*
    (ExceptHandler, 'type'):              (_put_one_exprish_optional, None, onestatic(_one_info_ExceptHandler_type, _restrict_default)), # expr?
    (ExceptHandler, 'name'):              (_put_one_ExceptHandler_name, None, onestatic(_one_info_ExceptHandler_name, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (ExceptHandler, 'body'):              (_put_one_stmtish, None, None), # stmt*
    (arguments, 'posonlyargs'):           (_put_one_exprish_sliceable, None, _onestatic_arg_required), # arg*
    (arguments, 'args'):                  (_put_one_exprish_sliceable, None, _onestatic_arg_required), # arg*
    (arguments, 'defaults'):              (_put_one_exprish_required, None, _onestatic_expr_required), # expr*
    (arguments, 'vararg'):                (_put_one_exprish_optional, None, onestatic(_one_info_arguments_vararg, _restrict_default, code_as=_code_as_arg)), # arg?
    (arguments, 'kwonlyargs'):            (_put_one_exprish_sliceable, None, _onestatic_arg_required), # arg*
    (arguments, 'kw_defaults'):           (_put_one_exprish_optional, None, onestatic(_one_info_arguments_kw_defaults, _restrict_default)), # expr*
    (arguments, 'kwarg'):                 (_put_one_exprish_optional, None, onestatic(_one_info_arguments_kwarg, _restrict_default, code_as=_code_as_arg)), # arg?
    (arg, 'arg'):                         (_put_one_identifier_required, None, _onestatic_identifier_required), # identifier
    (arg, 'annotation'):                  (_put_one_exprish_optional, None, onestatic(_one_info_arg_annotation, _restrict_default)), # expr?  - exclude [Lambda, Yield, YieldFrom, Await, NamedExpr]?
    (keyword, 'arg'):                     (_put_one_keyword_arg, None, onestatic(_one_info_keyword_arg, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (keyword, 'value'):                   (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (alias, 'name'):                      (_put_one_identifier_required, None, onestatic(_one_info_identifier_alias, _restrict_default, code_as=_code_as_identifier_alias)), # identifier  - alias star or dotted not valid for all uses but being general here (and lazy, don't feel like checking parent)
    (alias, 'asname'):                    (_put_one_identifier_optional, None, onestatic(_one_info_alias_asname, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (withitem, 'context_expr'):           (_put_one_exprish_required, None, _onestatic_expr_required), # expr
    (withitem, 'optional_vars'):          (_put_one_withitem_optional_vars, None, onestatic(_one_info_withitem_optional_vars, (Name, Tuple, List, Attribute, Subscript), ctx=Store)), # expr?
    (match_case, 'pattern'):              (_put_one_exprish_required, None, _onestatic_pattern_required), # pattern
    (match_case, 'guard'):                (_put_one_exprish_optional, None, onestatic(_one_info_match_case_guard, _restrict_default)), # expr?
    (match_case, 'body'):                 (_put_one_stmtish, None, None), # stmt*
    (MatchValue, 'value'):                (_put_one_MatchValue_value, None, onestatic(_one_info_exprish_required, is_valid_MatchValue_value)), # expr
    (MatchSingleton, 'value'):            (_put_one_constant, None, onestatic(_one_info_constant, is_valid_MatchSingleton_value)), # constant
    (MatchSequence, 'patterns'):          (_put_one_exprish_sliceable, None, _onestatic_pattern_required), # pattern*
    (MatchMapping, 'keys'):               (_put_one_exprish_required, None, onestatic(_one_info_exprish_required, is_valid_MatchMapping_key)), # expr*  Ops for `-1` or `2+3j`, TODO: XXX are there any others allowed?
    (MatchMapping, 'patterns'):           (_put_one_exprish_sliceable, None, _onestatic_pattern_required), # pattern*
    (MatchMapping, 'rest'):               (_put_one_identifier_optional, None, onestatic(_one_info_MatchMapping_rest, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (MatchClass, 'cls'):                  (_put_one_exprish_required, None, onestatic(_one_info_exprish_required, (Name, Attribute))), # expr
    (MatchClass, 'patterns'):             (_put_one_exprish_sliceable, None, _onestatic_pattern_required), # pattern*
    (MatchClass, 'kwd_attrs'):            (_put_one_identifier_required, None, onestatic(_one_info_MatchClass_kwd_attrs, _restrict_default, code_as=_code_as_identifier)), # identifier*
    (MatchClass, 'kwd_patterns'):         (_put_one_exprish_required, None, _onestatic_pattern_required), # pattern*
    (MatchStar, 'name'):                  (_put_one_MatchStar_name, None, onestatic(_one_info_MatchStar_name, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (MatchAs, 'pattern'):                 (_put_one_exprish_optional, None, onestatic(_one_info_MatchAs_pattern, _restrict_default, code_as=_code_as_pattern)), # pattern?
    (MatchAs, 'name'):                    (_put_one_MatchAs_name, None, onestatic(_one_info_MatchAs_name, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (MatchOr, 'patterns'):                (_put_one_exprish_sliceable, None, _onestatic_pattern_required), # pattern*
    (TypeVar, 'name'):                    (_put_one_identifier_required, None, _onestatic_identifier_required), # identifier
    (TypeVar, 'bound'):                   (_put_one_exprish_optional, None, onestatic(_one_info_TypeVar_bound, _restrict_default)), # expr?
    (TypeVar, 'default_value'):           (_put_one_exprish_optional, None, onestatic(_one_info_TypeVar_default_value, _restrict_default)), # expr?
    (ParamSpec, 'name'):                  (_put_one_identifier_required, None, onestatic(_one_info_ParamSpec_name, _restrict_default, code_as=_code_as_identifier)), # identifier
    (ParamSpec, 'default_value'):         (_put_one_exprish_optional, None, onestatic(_one_info_ParamSpec_default_value, _restrict_default)), # expr?
    (TypeVarTuple, 'name'):               (_put_one_identifier_required, None, onestatic(_one_info_TypeVarTuple_name, _restrict_default, code_as=_code_as_identifier)), # identifier
    (TypeVarTuple, 'default_value'):      (_put_one_exprish_optional, None, onestatic(_one_info_TypeVarTuple_default_value, _restrict_default)), # expr?


    # NOT DONE:
    # =========

    # (Module, 'type_ignores'):             (_put_one_default, None), # type_ignore*

    # (FunctionType, 'argtypes'):           (_put_one_default, None), # expr*
    # (FunctionType, 'returns'):            (_put_one_default, None), # expr

    # (FunctionDef, 'type_comment'):        (_put_one_default, None), # string?
    # (AsyncFunctionDef, 'type_comment'):   (_put_one_default, None), # string?
    # (Assign, 'type_comment'):             (_put_one_default, None), # string?
    # (For, 'type_comment'):                (_put_one_default, None), # string?
    # (AsyncFor, 'type_comment'):           (_put_one_default, None), # string?
    # (With, 'type_comment'):               (_put_one_default, None), # string?
    # (AsyncWith, 'type_comment'):          (_put_one_default, None), # string?
    # (arg, 'type_comment'):                (_put_one_default, None), # string?

    # (Attribute, 'ctx'):                   (_put_one_default, None), # expr_context
    # (Subscript, 'ctx'):                   (_put_one_default, None), # expr_context
    # (Starred, 'ctx'):                     (_put_one_default, None), # expr_context
    # (Name, 'ctx'):                        (_put_one_default, None), # expr_context
    # (List, 'ctx'):                        (_put_one_default, None), # expr_context
    # (Tuple, 'ctx'):                       (_put_one_default, None), # expr_context

    # (AnnAssign, 'simple'):                (_put_one_default, None), # int
    # (ImportFrom, 'level'):                (_put_one_default, None), # int?
    # (FormattedValue, 'conversion'):       (_put_one_default, None), # int
    # (Interpolation, 'constant'):          (_put_one_default, None), # str
    # (Interpolation, 'conversion'):        (_put_one_default, None), # int
    # (Constant, 'kind'):                   (_put_one_default, None), # string?
    # (comprehension, 'is_async'):          (_put_one_default, None), # int
    # (TypeIgnore, 'lineno'):               (_put_one_default, None), # int
    # (TypeIgnore, 'tag'):                  (_put_one_default, None), # string
}

# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = ['_get_one', '_put_one']

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
