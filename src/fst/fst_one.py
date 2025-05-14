"""Misc lower level FST methods."""

import re
from ast import *
from types import FunctionType
from typing import Any, Callable, NamedTuple, Optional, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, type_param, TypeVar, ParamSpec, TypeVarTuple, TemplateStr, Interpolation

from .shared import (
    STMTISH, Code, NodeTypeError, astfield, fstloc, srcwpos,
    _prev_src, _next_find, _prev_find, _next_find_re, _fixup_one_index,)

_re_identifier = re.compile(r'[^\d\W]\w*')


def _slice_indices(self: 'FST', idx: int, field: str, body: list[AST], to: Optional['FST']):
    """If a `to` parameter is passed then try to convert it to an index in the same field body list of `self`."""

    idx = _fixup_one_index(len(body), idx)

    if not to:
        return idx, idx + 1

    elif to.parent is self is not None and (pf := to.pfield).name == field:
        if (to_idx := pf.idx) < idx:
            raise ValueError("invalid 'to' node, must follow self in body")

        return idx, to_idx + 1

    raise NodeTypeError(f"invalid 'to' node")


# ----------------------------------------------------------------------------------------------------------------------
# get

def _get_one(self: 'FST', idx: int | None, field: str, cut: bool, **options) -> Optional['FST']:
    """Copy or cut (if possible) a node or non-node from a field of `self`."""

    ast    = self.a
    child  = getattr(ast, field)
    childa = child if idx is None else child[idx]

    if isinstance(childa, STMTISH):
        return self._get_slice_stmtish(*_slice_indices(self, idx, field, child, None), field, cut=cut, one=True,
                                       **options)

    childf = childa.f
    loc    = childf.pars(options.get('pars') is True)

    if not loc:
        raise ValueError('cannot copy node which does not have a location')

    fst = childf._make_fst_and_dedent(childf, copy_ast(childa), loc, docstr=options.get('docstr'))

    if cut:
        options['to'] = None

        self._put_one(None, idx, field, **options)

    if FST.get_option('fix', options):
        fst = fst._fix(inplace=True)

    return fst


# ----------------------------------------------------------------------------------------------------------------------
# put

def _code_as_identifier(code: Code) -> str | None:

    # TODO: handle text identifiers with multiple lines, preceding and following comments, line continuations and maybe semicolons? I am going nuts with this, definitely...

    if isinstance(code, str):
        return code if is_valid_identifier(code) else None
    if isinstance(code, list):
        return code if len(code) == 1 and is_valid_identifier(code := code[0]) else None  # join without newlines to ignore one or two extraneous ones

    if isinstance(code, FST):
        code = code.a

    return code.id if isinstance(code, Name) else None


_normalize_code_str2op = {
    AugAssign: OPSTR2CLS_AUG,
    BoolOp:    OPSTR2CLS_BOOL,
    BinOp:     OPSTR2CLS_BIN,
    UnaryOp:   OPSTR2CLS_UNARY,
    Compare:   OPSTR2CLS_CMP,
    None:      OPSTR2CLSWAUG,
}

_normalize_code_ops = {
    AugAssign: frozenset(OPSTR2CLS_AUG.values()),
    BoolOp:    frozenset(OPSTR2CLS_BOOL.values()),
    BinOp:     frozenset(OPSTR2CLS_BIN.values()),
    UnaryOp:   frozenset(OPSTR2CLS_UNARY.values()),
    Compare:   frozenset(OPSTR2CLS_CMP.values()),
    None:      frozenset(OPSTR2CLS.values()),
}

def _normalize_code_op(code: Code,
                       target: type[AugAssign] | type[BoolOp] | type[BinOp] | type[UnaryOp] | type[Compare] |
                       None = None) -> 'FST':
    """Convert `code` to an operator `FST` of the kind we need if is possible."""

    # TODO: handle text operators with multiple lines, preceding following comments, line continuations and maybe semicolons?

    if isinstance(code, FST):
        if (src := code.get_src(*code.loc)) not in _normalize_code_str2op[target]:
            raise NodeTypeError(f'bad operator {src!r}')

    elif isinstance(code, AST):
        code = FST(code, lines=[(OPCLS2STR_AUG if target is AugAssign else OPCLS2STR).get(code.__class__, '')])

    else:
        if isinstance(code, list):
            code = '\n'.join(lines := code)
        else:
            lines = code.split('\n')

        if not (cls := _normalize_code_str2op[target].get(code)):
            raise NodeTypeError(f'bad operator {code!r}')

        code = FST(cls(), lines=lines)

    if code.a.__class__ not in _normalize_code_ops[target]:
        raise NodeTypeError(f'expecting operator{f" for {target.__name__}" if target else ""}'
                            f', got {code.a.__class__.__name__}')

    return code


def _is_valid_MatchAs_value(ast: AST) -> bool:
    if isinstance(ast, Constant):
        return isinstance(ast.value, (str, int, float, complex))
    if isinstance(ast, Attribute):
        return True
    if isinstance(ast, BinOp):
        return (isinstance(ast.op, Add) and
                isinstance(l := ast.left, Constant) and isinstance(r := ast.right, Constant) and
                isinstance(l.value, (int, float)) and isinstance(r.value, complex))

    return False


class _FieldInfo(NamedTuple):
    loc:     fstloc  # For expr?: This is only used for create new or delete (and is set appropriately), replace is done using existing child location. For identifier? this is the search span.
    prefix:  str                = ' '
    ctx:     type[expr_context] = Load
    can_put: bool               = True
    can_del: bool               = True

def _field_info_FunctionDef_returns(self: 'FST', idx: int | None) -> _FieldInfo:
    ln, col, end_ln, end_col = self._loc_block_header_end(True)
    ret_end_ln               = end_ln
    ret_end_col              = end_col - 1

    if returns := self.a.returns:
        ln, col               = prev.loc[2:] if (prev := (retf := returns.f).prev()) else self.loc[:2]
        end_ln, end_col, _, _ = retf.pars()

    args_end_ln, args_end_col = _prev_find(self.root._lines, ln, col, end_ln, end_col, ')')  # must be there

    return _FieldInfo(fstloc(args_end_ln, args_end_col + 1, ret_end_ln, ret_end_col), ' -> ')

def _field_info_Return_value(self: 'FST', idx: int | None) -> _FieldInfo:
    return _FieldInfo(fstloc((loc := self.loc).ln, loc.col + 6, loc.end_ln, loc.end_col), ' ')

def _field_info_AnnAssign_value(self: 'FST', idx: int | None) -> _FieldInfo:
    return _FieldInfo(fstloc((loc := self.a.annotation.f.pars()).end_ln, loc.end_col, self.end_ln, self.end_col), ' = ')

def _field_info_Raise_exc(self: 'FST', idx: int | None) -> _FieldInfo:
    _, _, end_ln, end_col = a.exc.f.pars() if (a := self.a).cause else self.loc

    return _FieldInfo(fstloc((loc := self.loc).ln, loc.col + 5, end_ln, end_col), ' ', can_del=not self.a.cause)

def _field_info_Raise_cause(self: 'FST', idx: int | None) -> _FieldInfo:
    if exc := self.a.exc:
        _, _, ln, col = exc.f.pars()
    else:
        ln  = self.ln
        col = self.col + 5

    return _FieldInfo(fstloc(ln, col, self.end_ln, self.end_col), ' from ', can_put=bool(exc))

def _field_info_Assert_msg(self: 'FST', idx: int | None) -> _FieldInfo:
    return _FieldInfo(fstloc((loc := self.a.test.f.pars()).end_ln, loc.end_col, self.end_ln, self.end_col), ', ')

def _field_info_ImportFrom_module(self: 'FST', idx: int | None) -> _FieldInfo:
    ln, col, src = _prev_src(self.root.lines, self_ln := self.ln, self_col := self.col, *self.a.names[0].f.loc[:2])  # 'import'

    assert src == 'import'

    ln, col, src = _prev_src(self.root.lines, self_ln, self_col, ln, col)  # must be there, the module name with any/some/all preceding '.' level indicators
    end_col      = col + len(src)
    col          = end_col - len(src.lstrip('.'))

    return _FieldInfo(fstloc(ln, col, ln, end_col), '', can_del=bool(self.a.level))

def _field_info_Yield_value(self: 'FST', idx: int | None) -> _FieldInfo:
    return _FieldInfo(fstloc((loc := self.loc).ln, loc.col + 5, self.end_ln, self.end_col), ' ')

def _field_info_Slice_lower(self: 'FST', idx: int | None) -> _FieldInfo:
    ln, col, end_ln, end_col = self.loc

    if lower := self.a.lower:
        end_ln, end_col = _next_find(self.root._lines, (loc := lower.f.loc).end_ln, loc.end_col, end_ln, end_col, ':')  # must be there
    else:
        end_ln, end_col = _next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # must be there

    return _FieldInfo(fstloc(ln, col, end_ln, end_col), '')

def _field_info_Slice_upper(self: 'FST', idx: int | None) -> _FieldInfo:
    ln                    = (lloc := _field_info_Slice_lower(self, idx).loc).end_ln
    col                   = lloc.end_col + 1
    _, _, end_ln, end_col = self.loc

    if upper := self.a.upper:
        end = _next_find(self.root._lines, (loc := upper.f.loc).end_ln, loc.end_col, end_ln, end_col, ':')  # may or may not be there
    else:
        end = _next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # may or may not be there

    if end:
        end_ln, end_col = end

    return _FieldInfo(fstloc(ln, col, end_ln, end_col), '')

def _field_info_Slice_step(self: 'FST', idx: int | None) -> _FieldInfo:
    ln  = (uloc := _field_info_Slice_upper(self, idx).loc).end_ln
    col = uloc.end_col

    if self.root._lines[ln].startswith(':', col):
        col    += 1
        prefix  = ''
    else:
        prefix = ':'

    return _FieldInfo(fstloc(ln, col, self.end_ln, self.end_col), prefix)

def _field_info_ExceptHandler_type(self: 'FST', idx: int | None) -> _FieldInfo:
    if type_ := self.a.type:
        _, _, end_ln, end_col = type_.f.pars()
    else:
        end_ln, end_col  = self._loc_block_header_end()  # because 'name' can not be there
        end_col         -= 1

    return _FieldInfo(fstloc((loc := self.loc).ln, loc.col + 6, end_ln, end_col), ' ', can_del=not self.a.name)

def _field_info_ExceptHandler_name(self: 'FST', idx: int | None) -> _FieldInfo:
    if type_ := self.a.type:
        _, _, ln, col = type_.f.pars()
    else:
        ln  = self.ln
        col = self.col + 6

    end_ln, end_col  = self._loc_block_header_end()
    end_col         -= 1

    return _FieldInfo(fstloc(ln, col, end_ln, end_col), ' as ', can_put=bool(type_))

def _field_info_arguments_kw_defaults(self: 'FST', idx: int | None) -> _FieldInfo:
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

    return _FieldInfo(fstloc(ln, col, end_ln, end_col), prefix)

def _field_info_arg_annotation(self: 'FST', idx: int | None) -> _FieldInfo:
    return _FieldInfo(fstloc((loc := self.loc).ln, loc.col + len(self.a.arg), self.end_ln, self.end_col), ': ')

def _field_info_alias_asname(self: 'FST', idx: int | None) -> _FieldInfo:
    return _FieldInfo(fstloc(self.ln, self.col + len(self.a.name), self.end_ln, self.end_col), ' as ')

def _field_info_withitem_optional_vars(self: 'FST', idx: int | None) -> _FieldInfo:
    _, _, ln, col = self.a.context_expr.f.pars()

    if optional_vars := self.a.optional_vars:
        _, _, end_ln, end_col = optional_vars.f.pars()
    else:
        end_ln  = ln
        end_col = col

    return _FieldInfo(fstloc(ln, col, end_ln, end_col), ' as ', Store)

def _field_info_match_case_guard(self: 'FST', idx: int | None) -> _FieldInfo:
    _, _, ln, col          = self.a.pattern.f.pars()
    _, _, end_ln, end_col  = self._loc_block_header_end(True)
    end_col               -= 1

    return _FieldInfo(fstloc(ln, col, end_ln, end_col), ' if ')

def _field_info_TypeVar_bound(self: 'FST', idx: int | None) -> _FieldInfo:
    ln  = self.ln
    col = self.col + len(self.a.name)

    if bound := self.a.bound:
        _, _, end_ln, end_col = bound.f.pars()
    else:
        end_ln  = ln
        end_col = col

    return _FieldInfo(fstloc(ln, col, end_ln, end_col), ': ')

def _field_info_TypeVar_default_value(self: 'FST', idx: int | None) -> _FieldInfo:
    if bound := self.a.bound:
        _, _, ln, col = bound.f.pars()
    else:
        ln  = self.ln
        col = self.col + len(self.a.name)

    return _FieldInfo(fstloc(ln, col, self.end_ln, self.end_col), ' = ')

def _field_info_ParamSpec_default_value(self: 'FST', idx: int | None) -> _FieldInfo:
    ln, col, end_ln, end_col = self.loc
    ln, col, src             = _next_find_re(self.root._lines, ln, col + 2, end_ln, end_col, _re_identifier)  # + '**', identifier must be there

    return _FieldInfo(fstloc(ln, col + len(src), self.end_ln, self.end_col), ' = ')

def _field_info_TypeVarTuple_default_value(self: 'FST', idx: int | None) -> _FieldInfo:
    ln, col, end_ln, end_col = self.loc
    ln, col, src             = _next_find_re(self.root._lines, ln, col + 1, end_ln, end_col, _re_identifier)  # + '*', identifier must be there

    return _FieldInfo(fstloc(ln, col + len(src), self.end_ln, self.end_col), ' = ')


def _validate_put(self: 'FST', code: Code | None, idx: int | None, field: str,  child: list[AST] | AST | None,
                  options: dict[str: Any], *, can_del: bool = False) -> AST | None:
    """Check that `idx` was passed (or not) as needed and that not deleting if not possible and that `to` raw parameter
    is not present."""

    if isinstance(child, list):
        if idx is None:
            raise IndexError(f'{self.a.__class__.__name__}.{field} needs an index')

        child = child[idx]

    elif idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')

    if not can_del and code is None:
        raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field}{"" if idx is None else f"[{idx}]"}')
    if options.get('to'):
        raise NodeTypeError(f"cannot put with 'to' to {self.a.__class__.__name__}.{field}")

    return child


def _make_expr_fst(self: 'FST', code: Code | None, idx: int | None, field: str,
                   types: tuple[type[AST]] | list[type[AST]] | type[AST] | None,  # single or tuple means allow only these, list means do not allow these
                   target: Union['FST', fstloc], ctx: type[expr_context], prefix: str  = '',
                   **options) -> 'FST':
    """Make an expression `FST` from `Code` for a field/idx containing an existing node creating a new one. Takes care
    of parenthesizing, indenting and offsetting."""

    put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)
    put_ast = put_fst.a

    if types:
        if isinstance(types, list):  # list means these types not allowed
            if isinstance(put_ast, tuple(types)):
                raise NodeTypeError(f'{self.a.__class__.__name__}.{field}{" " if idx is None else f"[{idx}] "}'
                                    f'cannot be {put_ast.__class__.__name__}')

        elif isinstance(types, FunctionType):
            if not types(put_ast):
                raise NodeTypeError(f'invalid value for {self.a.__class__.__name__}.{field}' +
                                    ('' if idx is None else f'[{idx}]'))

        elif not isinstance(put_ast, types):  # single AST type or tuple means only these allowed
            raise NodeTypeError((f'expecting a {types.__name__} for {self.a.__class__.__name__}.{field}'
                                 if isinstance(types, type) else
                                 f'expecting one of ({", ".join(c.__name__ for c in types)}) for '
                                 f'{self.a.__class__.__name__}.{field}{"" if idx is None else f"[{idx}]"}') +
                                f', got {put_ast.__class__.__name__}')

    pars    = bool(FST.get_option('pars', options))
    delpars = pars or put_fst.is_parenthesized_tuple() is False  # need tuple check because otherwise Tuple location would be wrong after (wouldn't include possible enclosing parens)
    is_FST  = target.is_FST

    if precedence_require_parens(put_ast, self.a, field, idx):
        if not put_fst.is_atom() and (delpars or not is_FST or not target.pars(ret_npars=True)[1]):
            put_fst.parenthesize()

    elif pars:  # remove parens only if allowed to
        put_fst.unparenthesize()

    if prefix:
        put_fst.put_src([prefix], 0, 0, 0, 0, True)

    put_fst.indent_lns(self.get_indent(), docstr=options.get('docstr'))

    ln, col, end_ln, end_col = target.pars(delpars) if target.is_FST else target

    dcol_offset   = self.root._lines[ln].c2b(col)
    params_offset = self.put_src(put_fst._lines, ln, col, end_ln, end_col, True, False, exclude=self)

    put_fst.offset(0, 0, ln, dcol_offset)
    self.offset(*params_offset, exclude=target, self_=False)
    set_ctx(put_ast, ctx)

    return put_fst


def _put_one_expr_required(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST] | AST | None,
                           extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                           validate: bool = True, **options) -> 'FST':
    """Put a single required expression. Can be standalone or as part of sequence."""

    if validate:
        child = _validate_put(self, code, idx, field, child, options)

        if not child:
            raise ValueError(f'cannot replace nonexistent {self.a.__class__.__name__}.{field}' +
                             ("" if idx is None else f"[{idx}]"))

    childf  = child.f
    ctx     = ((ctx := getattr(child, 'ctx', None)) and ctx.__class__) or Load
    put_fst = _make_expr_fst(self, code, idx, field, extra, childf, ctx, **options)

    childf._set_ast(put_fst.a)

    return childf


def _put_one_expr_optional(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                           extra: tuple[
                               Callable[['FST'], _FieldInfo],
                               tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                           ], **options) -> Optional['FST']:
    """Put new, replace or delete an optional expression."""

    child = _validate_put(self, code, idx, field, child, options, can_del=True)

    field_info, required_extra = extra

    if code is None:
        if child is None:  # delete nonexistent node, noop
            return None

    elif child:  # replace existing node
        return _put_one_expr_required(self, code, idx, field, child, required_extra, False, **options)

    loc, prefix, ctx, can_put, can_del = field_info(self, idx)

    if code is None:  # delete existing node
        if not can_del:
            raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field} in this state')

        self.put_src(None, *loc, True)
        set_field(self.a, None, field, idx)
        child.f._unmake_fst_tree()

        return None

    # put new node

    if not can_put:
        raise ValueError(f'cannot create {self.a.__class__.__name__}.{field} in this state')

    put_fst = _make_expr_fst(self, code, idx, field, required_extra, loc, ctx, prefix, **options)
    put_fst = FST(put_fst.a, self, astfield(field, idx))

    self._make_fst_tree([put_fst])
    put_fst.pfield.set(self.a, put_fst.a)

    return put_fst


def _put_one_Dict_key(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST],
                      extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                      **options) -> Optional['FST']:
    """Allow for deleting or adding a `Dict` key value to change between `a: b` and `**b`."""

    return _put_one_expr_required(self, code, idx, field, child, extra, **options)


    # TODO: this



def _put_one_Compare_None(self: 'FST', code: Code | None, idx: int | None, field: str, child: None,
                          extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                          **options) -> 'FST':

    """Put to combined [Compare.left, Compare.comparators] using this total indexing."""

    ast         = self.a
    comparators = ast.comparators
    idx         = _fixup_one_index(len(comparators) + 1, idx)

    if idx:
        field = 'comparators'
        idx   = idx - 1
        child = comparators

    else:
        field = 'left'
        idx   = None
        child = ast.left

    return _put_one_expr_required(self, code, idx, field, child, extra, **options)


def _put_one_Interpolation_value(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                                 extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                                 **options) -> 'FST':
    """Put Interpolation.value. Do normal expr put and if successful copy source to `.str` attribute."""

    ret        = _put_one_expr_required(self, code, idx, field, child, extra, **options)
    self.a.str = self.get_src(*ret.loc)

    return ret


def _validate_code_as_identifier(self: 'FST', code: Code | None, field: str) -> str:
    if not (code := _code_as_identifier(code)):
        raise NodeTypeError(f"expecting identifier for {self.a.__class__.__name__}.{field}")

    return code


def _put_one_MatchValue_value(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST, extra: None,
                              **options) -> 'FST':
    """Put MatchValue.value. Need to do this because a standalone MatchValue encompassing a parenthesized constant ends
    before the closing parenthesis and so doesn't get offset correctly."""

    ret              = _put_one_expr_required(self, code, idx, field, child, _is_valid_MatchAs_value, **options)
    a                = self.a
    v                = a.value
    a.lineno         = v.lineno
    a.col_offset     = v.col_offset
    a.end_lineno     = v.end_lineno
    a.end_col_offset = v.end_col_offset

    return ret


def _put_one_identifier_required(self: 'FST', code: Code | None, idx: int | None, field: str, child: str,
                                 extra: str | None, loc: fstloc | None = None, validate: bool = True, **options) -> str:
    """Put a single required identifier."""

    if validate:
        _validate_put(self, code, idx, field, child, options)

    code                     = _validate_code_as_identifier(self, code, field)
    ln, col, end_ln, end_col = loc or self.loc
    lines                    = self.root._lines

    if not extra:
        m            = _re_identifier.match(lines[ln], col, end_col)  # must be there
        col, end_col = m.span()

    else:
        ln, col      = _next_find(lines, ln, col, end_ln, end_col, extra, lcont=None)  # must be there
        ln, col, src =  _next_find_re(lines, ln, col + len(extra), end_ln, end_col, _re_identifier, lcont=None)  # must be there
        end_ln       = ln
        end_col      = col + len(src)

    self.put_src(code, ln, col, end_ln, end_col, True)
    setattr(self.a, field, code)

    return code


def _put_one_identifier_optional(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                                 field_info: Callable[['FST'], _FieldInfo], **options) -> Optional['FST']:
    """Put new, replace or delete an optional identifier."""

    child = _validate_put(self, code, idx, field, child, options, can_del=True)

    if code is None and child is None:  # delete nonexistent identifier, noop
        return None

    loc, prefix, _, can_put, can_del = field_info(self, idx)

    if code is None:  # delete existing identifier
        if not can_del:
            raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field} in this state')

        self.put_src(None, *loc, True)
        set_field(self.a, None, field, idx)

        return None

    elif child is not None:  # replace existing identifier
        return _put_one_identifier_required(self, code, idx, field, child, prefix.strip(), loc, False, **options)

    # put new identifier

    if not can_put:
        raise ValueError(f'cannot create {self.a.__class__.__name__}.{field} in this state')

    code          = _validate_code_as_identifier(self, code, field)
    params_offset = self.put_src(prefix + code, *loc, True, exclude=self)

    self.offset(*params_offset, self_=False)
    setattr(self.a, field, code)

    return code


def _put_one_Attribute_attr(self: 'FST', code: Code | None, idx: int | None, field: str, child: str, extra: str | None,
                            **options) -> str:
    return _put_one_identifier_required(self, code, idx, field, child, '.',
                                        fstloc(*self.a.value.f.loc[2:], *self.loc[2:]), **options)


def _put_one_ExceptHandler_name(self: 'FST', code: Code | None, idx: int | None, field: str, child: str, extra: None,
                                **options) -> str:
    ret = _put_one_identifier_optional(self, code, idx, field, child, _field_info_ExceptHandler_name, **options)

    if ret and (typef := self.a.type.f).is_parenthesized_tuple() is False:
        typef.parenthesize()

    return ret


def _put_one_MatchStar_name(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST, extra: None,
                            **options) -> 'FST':
    """Slightly annoying MatchStar.name. '_' really means delete."""

    if code is None:
        code = '_'

    ln, col, end_ln, end_col = self.loc

    ret = _put_one_identifier_required(self, code, idx, field, child, None, fstloc(ln, col + 1, end_ln, end_col),
                                       **options)

    if self.a.name == '_':
        self.a.name = None

    return ret


def _put_one_MatchAs_name(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST, extra: None,
                          **options) -> 'FST':
    """Very annoying MatchAs.name. '_' really means delete, which can't be done if there is a pattern, and can't be
    assigned to a pattern."""

    if code is None:
        code = '_'
    else:
        code = _validate_code_as_identifier(self, code, field)

    loc = self.loc

    if pattern := self.a.pattern:
        if code == '_':
            raise ValueError("cannot change MatchAs with pattern into wildcard '_'")

        ln, col = pattern.f.pars()[2:]
        prefix  = 'as'

    else:
        ln, col = loc[:2]
        prefix  = None

    ret = _put_one_identifier_required(self, code, idx, field, child, prefix, fstloc(ln, col, *loc[2:]), **options)

    if self.a.name == '_':
        self.a.name = None

    return ret


def _put_one_op(self: 'FST', code: Code | None, idx: int | None, field: str, child: str,
                extra: tuple[type[AST], str], **options) -> 'FST':
    """Put a single opertation, with or without '=' for AugAssign."""

    child  = _validate_put(self, code, idx, field, child, options)
    code   = _normalize_code_op(code, self.a.__class__)
    childf = child.f

    ln, col, end_ln, end_col = childf.loc

    self.put_src(code._lines, ln, col, end_ln, end_col, False)
    child.f._set_ast(code.a)

    return childf


def _put_one_stmtish(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST], extra: None,
                     **options) -> Optional['FST']:
    """Put or delete a single statementish node to a list of them (body, orelse, handlers, finalbody or cases)."""

    self._put_slice_stmtish(code, *_slice_indices(self, idx, field, child, options.get('to')), field, True, **options)

    return None if code is None else getattr(self.a, field)[idx].f


def _put_one_tuple_list_or_set(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST],
                               extra: None, **options) -> Optional['FST']:
    """Put or delete a single expression to a Tuple, List or Set elts."""

    self._put_slice_tuple_list_or_set(code, *_slice_indices(self, idx, field, child, options.get('to')), field, True,
                                      **options)

    return None if code is None else getattr(self.a, field)[idx].f


def _put_one(self: 'FST', code: Code | None, idx: int | None, field: str | None, **options) -> Optional['FST']:
    """Put new, replace or delete a node (or limited non-node) to a field of `self`."""

    ast   = self.a
    child = getattr(self.a, field) if field else None
    raw   = FST.get_option('raw', options)

    if raw is not True:
        if raw and raw != 'auto':
            raise ValueError(f"invalid value for raw parameter '{raw}'")

        try:
            if handler_and_extra := _PUT_ONE_HANDLERS.get((ast.__class__, field)):
                handler, extra = handler_and_extra

                return handler(self, code, idx, field, child, extra, **options)

        except (SyntaxError, NodeTypeError):
            if not raw:
                raise

        else:
            if not raw:
                raise ValueError(f'cannot {"delete" if code is None else "replace"} {ast.__class__.__name__}.{field}')

    if isinstance(child, list):
        child = child[idx]

    # special raw cases, TODO: move into dedicated _put_raw or do via _PUT_ONE_RAW_HANDLERS

    is_dict = isinstance(ast, Dict)

    if field is None:  # maybe putting to special case field?
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


# TODO: finish these

_PUT_ONE_HANDLERS = {
    (Module, 'body'):                     (_put_one_stmtish, None), # stmt*
    (Interactive, 'body'):                (_put_one_stmtish, None), # stmt*
    (Expression, 'body'):                 (_put_one_expr_required, None), # expr
    # (FunctionDef, 'decorator_list'):      (_put_one_default, None), # expr*                                           - slice
    (FunctionDef, 'name'):                (_put_one_identifier_required, 'def'), # identifier
    # (FunctionDef, 'type_params'):         (_put_one_default, None), # type_param*                                     - slice
    # (FunctionDef, 'args'):                (_put_one_default, None), # arguments                                       - special parse
    (FunctionDef, 'returns'):             (_put_one_expr_optional, (_field_info_FunctionDef_returns, None)), # expr?    - SPECIAL LOCATION OPTIONAL TAIL: '->'                                           - SPECIAL LOCATION CASE!
    (FunctionDef, 'body'):                (_put_one_stmtish, None), # stmt*
    # (AsyncFunctionDef, 'decorator_list'): (_put_one_default, None), # expr*                                           - slice
    (AsyncFunctionDef, 'name'):           (_put_one_identifier_required, 'def'), # identifier
    # (AsyncFunctionDef, 'type_params'):    (_put_one_default, None), # type_param*                                     - slice
    # (AsyncFunctionDef, 'args'):           (_put_one_default, None), # arguments                                       - special parse
    (AsyncFunctionDef, 'returns'):        (_put_one_expr_optional, (_field_info_FunctionDef_returns, None)), # expr?    - SPECIAL LOCATION OPTIONAL TAIL: '->'
    (AsyncFunctionDef, 'body'):           (_put_one_stmtish, None), # stmt*
    # (ClassDef, 'decorator_list'):         (_put_one_default, None), # expr*                                           - slice
    (ClassDef, 'name'):                   (_put_one_identifier_required, 'class'), # identifier
    # (ClassDef, 'type_params'):            (_put_one_default, None), # type_param*                                     - slice
    # (ClassDef, 'bases'):                  (_put_one_default, None), # expr*                                           - slice
    # (ClassDef, 'keywords'):               (_put_one_default, None), # keyword*                                        - slice
    (ClassDef, 'body'):                   (_put_one_stmtish, None), # stmt*
    (Return, 'value'):                    (_put_one_expr_optional, (_field_info_Return_value, None)), # expr?           - OPTIONAL TAIL: ''
    # (Delete, 'targets'):                  (_put_one_default, None), # expr*                                           - slice
    # (Assign, 'targets'):                  (_put_one_default, None), # expr*                                           - slice
    (Assign, 'value'):                    (_put_one_expr_required, None), # expr
    (TypeAlias, 'name'):                  (_put_one_expr_required, Name), # expr
    # (TypeAlias, 'type_params'):           (_put_one_default, None), # type_param*                                     - slice
    (TypeAlias, 'value'):                 (_put_one_expr_required, None), # expr
    (AugAssign, 'target'):                (_put_one_expr_required, (Name, Attribute, Subscript)), # expr
    (AugAssign, 'op'):                    (_put_one_op, None), # operator
    (AugAssign, 'value'):                 (_put_one_expr_required, None), # expr
    (AnnAssign, 'target'):                (_put_one_expr_required, (Name, Attribute, Subscript)), # expr
    (AnnAssign, 'annotation'):            (_put_one_expr_required, [Lambda, Yield, YieldFrom, Await, NamedExpr]), # expr
    (AnnAssign, 'value'):                 (_put_one_expr_optional, (_field_info_AnnAssign_value, None)), # expr?        - OPTIONAL TAIL: '='
    (For, 'target'):                      (_put_one_expr_required, (Name, Tuple, List)), # expr
    (For, 'iter'):                        (_put_one_expr_required, None), # expr
    (For, 'body'):                        (_put_one_stmtish, None), # stmt*
    (For, 'orelse'):                      (_put_one_stmtish, None), # stmt*
    (AsyncFor, 'target'):                 (_put_one_expr_required, (Name, Tuple, List)), # expr
    (AsyncFor, 'iter'):                   (_put_one_expr_required, None), # expr
    (AsyncFor, 'body'):                   (_put_one_stmtish, None), # stmt*
    (AsyncFor, 'orelse'):                 (_put_one_stmtish, None), # stmt*
    (While, 'test'):                      (_put_one_expr_required, None), # expr
    (While, 'body'):                      (_put_one_stmtish, None), # stmt*
    (While, 'orelse'):                    (_put_one_stmtish, None), # stmt*
    (If, 'test'):                         (_put_one_expr_required, None), # expr
    (If, 'body'):                         (_put_one_stmtish, None), # stmt*
    (If, 'orelse'):                       (_put_one_stmtish, None), # stmt*
    # (With, 'items'):                      (_put_one_default, None), # withitem*                                       - slice
    (With, 'body'):                       (_put_one_stmtish, None), # stmt*
    # (AsyncWith, 'items'):                 (_put_one_default, None), # withitem*                                       - slice
    (AsyncWith, 'body'):                  (_put_one_stmtish, None), # stmt*
    (Match, 'subject'):                   (_put_one_expr_required, None), # expr
    (Match, 'cases'):                     (_put_one_stmtish, None), # match_case*
    (Raise, 'exc'):                       (_put_one_expr_optional, (_field_info_Raise_exc, None)), # expr?              - OPTIONAL MIDDLE: ''
    (Raise, 'cause'):                     (_put_one_expr_optional, (_field_info_Raise_cause, None)), # expr?            - CONTINGENT OPTIONAL TAIL: 'from'
    (Try, 'body'):                        (_put_one_stmtish, None), # stmt*
    (Try, 'handlers'):                    (_put_one_stmtish, None), # excepthandler*
    (Try, 'orelse'):                      (_put_one_stmtish, None), # stmt*
    (Try, 'finalbody'):                   (_put_one_stmtish, None), # stmt*
    (TryStar, 'body'):                    (_put_one_stmtish, None), # stmt*
    (TryStar, 'handlers'):                (_put_one_stmtish, None), # excepthandler*
    (TryStar, 'orelse'):                  (_put_one_stmtish, None), # stmt*
    (TryStar, 'finalbody'):               (_put_one_stmtish, None), # stmt*
    (Assert, 'test'):                     (_put_one_expr_required, None), # expr
    (Assert, 'msg'):                      (_put_one_expr_optional, (_field_info_Assert_msg, None)), # expr?             - OPTIONAL TAIL: ','
    # (Import, 'names'):                    (_put_one_default, None), # alias*                                          - slice (special)
    (ImportFrom, 'module'):               (_put_one_identifier_optional, _field_info_ImportFrom_module), # identifier?
    # (ImportFrom, 'names'):                (_put_one_default, None), # alias*                                          - slice (special)
    # (Global, 'names'):                    (_put_one_default, None), # identifier*                                     - slice (special)
    # (Nonlocal, 'names'):                  (_put_one_default, None), # identifier*                                     - slice (special)
    (Expr, 'value'):                      (_put_one_expr_required, None), # expr
    # (BoolOp, 'op'):                       (_put_one_default, None), # boolop
    # (BoolOp, 'values'):                   (_put_one_default, None), # expr*                                           - slice
    (NamedExpr, 'target'):                (_put_one_expr_required, Name), # expr
    (NamedExpr, 'value'):                 (_put_one_expr_required, None), # expr
    (BinOp, 'left'):                      (_put_one_expr_required, None), # expr
    (BinOp, 'op'):                        (_put_one_op, None), # operator
    (BinOp, 'right'):                     (_put_one_expr_required, None), # expr
    (UnaryOp, 'op'):                      (_put_one_op, None), # unaryop
    (UnaryOp, 'operand'):                 (_put_one_expr_required, None), # expr
    # (Lambda, 'args'):                     (_put_one_default, None), # arguments                                       - special parse
    (Lambda, 'body'):                     (_put_one_expr_required, None), # expr
    (IfExp, 'body'):                      (_put_one_expr_required, None), # expr
    (IfExp, 'test'):                      (_put_one_expr_required, None), # expr
    (IfExp, 'orelse'):                    (_put_one_expr_required, None), # expr
    (Dict, 'keys'):                       (_put_one_Dict_key, None), # expr*                                            TODO: handle special key=None
    (Dict, 'values'):                     (_put_one_expr_required, None), # expr*
    (Set, 'elts'):                        (_put_one_tuple_list_or_set, None), # expr*
    (ListComp, 'elt'):                    (_put_one_expr_required, None), # expr
    # (ListComp, 'generators'):             (_put_one_default, None), # comprehension*                                  - slice
    (SetComp, 'elt'):                     (_put_one_expr_required, None), # expr
    # (SetComp, 'generators'):              (_put_one_default, None), # comprehension*                                  - slice
    (DictComp, 'key'):                    (_put_one_expr_required, None), # expr
    (DictComp, 'value'):                  (_put_one_expr_required, None), # expr
    # (DictComp, 'generators'):             (_put_one_default, None), # comprehension*                                  - slice
    (GeneratorExp, 'elt'):                (_put_one_expr_required, None), # expr
    # (GeneratorExp, 'generators'):         (_put_one_default, None), # comprehension*                                  - slice
    (Await, 'value'):                     (_put_one_expr_required, None), # expr
    (Yield, 'value'):                     (_put_one_expr_optional, (_field_info_Yield_value, None)), # expr?            - OPTIONAL TAIL: ''
    (YieldFrom, 'value'):                 (_put_one_expr_required, None), # expr
    (Compare, 'left'):                    (_put_one_expr_required, None), # expr
    (Compare, 'ops'):                     (_put_one_op, None), # cmpop*
    (Compare, 'comparators'):             (_put_one_expr_required, None), # expr*
    (Compare, None):                      (_put_one_Compare_None, None), # expr*
    (Call, 'func'):                       (_put_one_expr_required, None), # expr
    # (Call, 'args'):                       (_put_one_default, None), # expr*                                           - slice
    # (Call, 'keywords'):                   (_put_one_default, None), # keyword*                                        - slice
    (FormattedValue, 'value'):            (_put_one_expr_required, None), # expr
    # (FormattedValue, 'format_spec'):      (_put_one_default, None), # expr?
    (Interpolation, 'value'):             (_put_one_Interpolation_value, None), # expr
    # (Interpolation, 'format_spec'):       (_put_one_default, None), # expr?
    # (JoinedStr, 'values'):                (_put_one_default, None), # expr*                                           - ??? no location on py < 3.12
    # (TemplateStr, 'values'):              (_put_one_default, None), # expr*                                           - ??? no location on py < 3.12
    # (Constant, 'value'):                  (_put_one_default, None), # constant                                        - can do via restricted expr Constant
    (Attribute, 'value'):                 (_put_one_expr_required, None), # expr
    (Attribute, 'attr'):                  (_put_one_Attribute_attr, None), # identifier                                 - after the "value."
    (Subscript, 'value'):                 (_put_one_expr_required, None), # expr
    # (Subscript, 'slice'):                 (_put_one_default, None), # expr                                            - need special parse 'slice'
    (Starred, 'value'):                   (_put_one_expr_required, None), # expr
    (Name, 'id'):                         (_put_one_identifier_required, None), # identifier
    (List, 'elts'):                       (_put_one_tuple_list_or_set, None), # expr*
    (Tuple, 'elts'):                      (_put_one_tuple_list_or_set, None), # expr*
    (Slice, 'lower'):                     (_put_one_expr_optional, (_field_info_Slice_lower, None)), # expr?
    (Slice, 'upper'):                     (_put_one_expr_optional, (_field_info_Slice_upper, None)), # expr?
    (Slice, 'step'):                      (_put_one_expr_optional, (_field_info_Slice_step, None)), # expr?
    (comprehension, 'target'):            (_put_one_expr_required, (Name, Tuple, List)), # expr
    (comprehension, 'iter'):              (_put_one_expr_required, None), # expr
    # (comprehension, 'ifs'):               (_put_one_default, None), # expr*                                           - slice
    (ExceptHandler, 'type'):              (_put_one_expr_optional, (_field_info_ExceptHandler_type, None)), # expr?
    (ExceptHandler, 'name'):              (_put_one_ExceptHandler_name, None), # identifier?
    (ExceptHandler, 'body'):              (_put_one_stmtish, None), # stmt*
    # (arguments, 'posonlyargs'):           (_put_one_default, None), # arg*                                            - need special parse 'arg'
    # (arguments, 'args'):                  (_put_one_default, None), # arg*                                            - need special parse 'arg'
    (arguments, 'defaults'):              (_put_one_expr_required, None), # expr*
    # (arguments, 'vararg'):                (_put_one_default, None), # arg?
    # (arguments, 'kwonlyargs'):            (_put_one_default, None), # arg*                                            - need special parse 'arg'
    (arguments, 'kw_defaults'):           (_put_one_expr_optional, (_field_info_arguments_kw_defaults, None)), # expr*  - can have None with special rules
    # (arguments, 'kwarg'):                 (_put_one_default, None), # arg?
    (arg, 'arg'):                         (_put_one_identifier_required, None), # identifier
    (arg, 'annotation'):                  (_put_one_expr_optional, (_field_info_arg_annotation, [Lambda, Yield, YieldFrom, Await, NamedExpr])), # expr?  - OPTIONAL TAIL: ':' - [Lambda, Yield, YieldFrom, Await, NamedExpr]
    # (keyword, 'arg'):                     (_put_one_default, None), # identifier?
    (keyword, 'value'):                   (_put_one_expr_required, None), # expr
    (alias, 'name'):                      (_put_one_identifier_required, None), # identifier
    (alias, 'asname'):                    (_put_one_identifier_optional, _field_info_alias_asname), # identifier?
    (withitem, 'context_expr'):           (_put_one_expr_required, None), # expr
    (withitem, 'optional_vars'):          (_put_one_expr_optional, (_field_info_withitem_optional_vars, (Name, Tuple, List))), # expr?  - OPTIONAL TAIL: 'as' - Name
    # (match_case, 'pattern'):              (_put_one_default, None), # pattern
    (match_case, 'guard'):                (_put_one_expr_optional, (_field_info_match_case_guard, None)), # expr?       - OPTIONAL TAIL: 'if'
    (match_case, 'body'):                 (_put_one_stmtish, None), # stmt*
    (MatchValue, 'value'):                (_put_one_MatchValue_value, None), # expr                                     - limited values, Constant? Name becomes MatchAs
    # (MatchSingleton, 'value'):            (_put_one_default, None), # constant
    # (MatchSequence, 'patterns'):          (_put_one_default, None), # pattern*
    (MatchMapping, 'keys'):               (_put_one_expr_required, (Constant, Attribute)), # expr*                      TODO: XXX are there any others allowed?
    # (MatchMapping, 'patterns'):           (_put_one_default, None), # pattern*
    # (MatchMapping, 'rest'):               (_put_one_default, None), # identifier?
    (MatchClass, 'cls'):                  (_put_one_expr_required, (Name, Attribute)), # expr
    # (MatchClass, 'patterns'):             (_put_one_default, None), # pattern*                                        - slice
    # (MatchClass, 'kwd_attrs'):            (_put_one_default, None), # identifier*
    # (MatchClass, 'kwd_patterns'):         (_put_one_default, None), # pattern*
    (MatchStar, 'name'):                  (_put_one_MatchStar_name, None), # identifier?
    # (MatchAs, 'pattern'):                 (_put_one_default, None), # pattern?                                        - special parse
    (MatchAs, 'name'):                    (_put_one_MatchAs_name, None), # identifier?
    # (MatchOr, 'patterns'):                (_put_one_default, None), # pattern*                                        - slice
    (TypeVar, 'name'):                    (_put_one_identifier_required, None), # identifier
    (TypeVar, 'bound'):                   (_put_one_expr_optional, (_field_info_TypeVar_bound, None)), # expr?          - OPTIONAL MIDDLE: ':'
    (TypeVar, 'default_value'):           (_put_one_expr_optional, (_field_info_TypeVar_default_value, None)), # expr?  - OPTIONAL TAIL: '='
    (ParamSpec, 'name'):                  (_put_one_identifier_required, '**'), # identifier
    (ParamSpec, 'default_value'):         (_put_one_expr_optional, (_field_info_ParamSpec_default_value, None)), # expr?  - OPTIONAL TAIL: '='
    (TypeVarTuple, 'name'):               (_put_one_identifier_required, '*'), # identifier
    (TypeVarTuple, 'default_value'):      (_put_one_expr_optional, (_field_info_TypeVarTuple_default_value, None)), # expr?  - OPTIONAL TAIL: '='


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


from .fst import FST
