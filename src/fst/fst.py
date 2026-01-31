"""Main FST module. Contains the `FST` class as well as drop-in replacement `parse()` and `unparse()` functions for
their respective `ast` module counterparts."""

from __future__ import annotations

import builtins  # because of the unfortunate choice for the name of an Interpolation field, '.str', we have a '.str' property in FST which messes with the type annotations
import io
import os
import sys
from ast import iter_fields
from ast import dump as ast_dump, unparse as ast_unparse
from io import TextIOBase
from typing import Any, Callable, Generator, Literal, Mapping, TextIO

from . import parsex
from . import code
from . import fst_traverse
from . import fst_options
from . import fst_type_predicates

from .asttypes import (
    ASTS_LEAF_MOD,
    ASTS_LEAF_STMT,
    ASTS_LEAF_EXPR,
    ASTS_LEAF_EXPR_CONTEXT,
    ASTS_LEAF_BOOLOP,
    ASTS_LEAF_OPERATOR,
    ASTS_LEAF_UNARYOP,
    ASTS_LEAF_CMPOP,
    ASTS_LEAF_PATTERN,
    ASTS_LEAF_TYPE_PARAM,
    ASTS_LEAF_STMT_OR_MOD,
    ASTS_LEAF_EXPR_CHAIN,
    ASTS_LEAF_STMTLIKE,
    ASTS_LEAF_STMTLIKE_OR_MOD,
    ASTS_LEAF_BLOCK,
    ASTS_LEAF_BLOCK_OR_MOD,
    ASTS_LEAF_SCOPE,
    ASTS_LEAF_SCOPE_OR_MOD,
    ASTS_LEAF_SCOPE_NAMED,
    ASTS_LEAF_SCOPE_NAMED_OR_MOD,
    ASTS_LEAF_SCOPE_ANON,
    ASTS_LEAF_FUNCDEF,
    ASTS_LEAF_DEF,
    ASTS_LEAF_DEF_OR_MOD,
    ASTS_LEAF_FOR,
    ASTS_LEAF_WITH,
    ASTS_LEAF_TRY,
    ASTS_LEAF_IMPORT,
    ASTS_LEAF_COMP,
    ASTS_LEAF_FTSTR,
    ASTS_LEAF_FTSTR_FMT,
    ASTS_LEAF_DELIMITED,
    ASTS_LEAF_MAYBE_DOCSTR,
    ASTS_LEAF__SLICE,
    AST,
    Add,
    And,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    AugAssign,
    BitAnd,
    BitOr,
    BitXor,
    Call,
    ClassDef,
    Compare,
    Constant,
    Del,
    Dict,
    Div,
    Eq,
    ExceptHandler,
    Expr,
    FloorDiv,
    For,
    FormattedValue,
    FunctionDef,
    Global,
    Gt,
    GtE,
    If,
    Import,
    ImportFrom,
    In,
    Interpolation,
    Invert,
    Is,
    IsNot,
    LShift,
    Load,
    Lt,
    LtE,
    MatMult,
    Match,
    MatchMapping,
    MatchSequence,
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
    Pow,
    RShift,
    Slice,
    Starred,
    Store,
    Sub,
    Tuple,
    TypeIgnore,
    UAdd,
    USub,
    While,
    With,
    arg,
    arguments,
    comprehension,
    match_case,
    stmt,
    withitem,
    _ExceptHandlers,
    _match_cases,
)

from .astutil import (
    constant,
    OPCLS2STR,
    bistr,
    WalkFail,
    repr_str_multiline,
    compare_asts,
    copy_ast,
)

from .common import PYLT13, re_empty_line_start, astfield, fstloc, fstlocn, nspace, next_frag, next_delims, prev_delims
from .parsex import Mode
from .code import Code, _code_as_lines, code_as_all

from .view import (
    fstview,
    fstview_Dict,
    fstview_MatchMapping,
    fstview_Compare,
    fstview_arguments,
    fstview__body,
    fstview_arglikes,
)

from .reconcile import Reconcile
from .fst_misc import DEFAULT_COLOR, IPYTHON_COLOR, DUMP_COLOR, DUMP_NO_COLOR, Trivia, clip_src_loc, fixup_field_body
from .fst_locs import _loc_arguments, _loc_comprehension, _loc_withitem, _loc_match_case, _loc_op
from .fst_options import check_options, filter_options


__all__ = [
    'parse', 'unparse', 'dump', 'castf', 'gastf', 'FST'
]


_DEFAULT_FILENAME = '<FST>'
_DEFAULT_PARSE_PARAMS = dict(filename=_DEFAULT_FILENAME, type_comments=False, feature_version=None)
_DEFAULT_INDENT = '    '

_LOC_FUNCS = {  # quick lookup table for FST.loc
    arguments:     _loc_arguments,
    comprehension: _loc_comprehension,
    withitem:      _loc_withitem,
    match_case:    _loc_match_case,
    And:           _loc_op,
    Or:            _loc_op,
    Add:           _loc_op,
    Sub:           _loc_op,
    Mult:          _loc_op,
    MatMult:       _loc_op,
    Div:           _loc_op,
    Mod:           _loc_op,
    Pow:           _loc_op,
    LShift:        _loc_op,
    RShift:        _loc_op,
    BitOr:         _loc_op,
    BitXor:        _loc_op,
    BitAnd:        _loc_op,
    FloorDiv:      _loc_op,
    Invert:        _loc_op,
    Not:           _loc_op,
    UAdd:          _loc_op,
    USub:          _loc_op,
    Eq:            _loc_op,
    NotEq:         _loc_op,
    Lt:            _loc_op,
    LtE:           _loc_op,
    Gt:            _loc_op,
    GtE:           _loc_op,
    Is:            _loc_op,
    IsNot:         _loc_op,
    In:            _loc_op,
    NotIn:         _loc_op,
}

_ASTS_LEAF_SCOPE_SYMBOLS = ASTS_LEAF_DEF | ASTS_LEAF_TYPE_PARAM | {Name, arg, AugAssign, Import, ImportFrom, Nonlocal,
                                                                   Global}  # used in scope_symbols() to optimize walk a tiny bit

_ASTS_LEAF_EXPR_CHAIN_OP_OR_CTX = (ASTS_LEAF_EXPR_CHAIN | ASTS_LEAF_EXPR_CONTEXT | ASTS_LEAF_BOOLOP | ASTS_LEAF_OPERATOR
                                   | ASTS_LEAF_UNARYOP | ASTS_LEAF_CMPOP)


def _swizzle_getput_params(
    start: str | int | None,  #  | Literal['end']
    stop: str | int | None,  #  | Literal['end']
    field: str | None,
    default_start: int | None,
    default_stop: Literal['end'] | None,
) -> tuple[int | Literal['end'] | None, int | None | Literal[False], str | None]:
    """Allow passing `stop` and `field` for get/put() functions positionally. Will accept `get/put('field')`,
    `get/put(start, 'field')` and `get/put(start, stop, 'field')`."""

    if isinstance(start, str) and start != 'end':
        return default_start, default_stop, start
    if isinstance(stop, str) and stop != 'end':
        return start, default_stop, stop

    return start, stop, field


def _validate_get_put_line_comment_field(self: FST, field: str) -> None:
    if field in ('orelse', 'finalbody'):
        if not getattr(self.a, field):
            raise ValueError(f'field {field!r} is empty')

    elif field not in (None, 'body'):
        raise ValueError(f'invalid field {field!r}')


# ----------------------------------------------------------------------------------------------------------------------

def parse(
    source: builtins.str | bytes | AST,
    filename: str = '<unknown>',
    mode: str = 'exec',
    *,
    type_comments: bool = False,
    feature_version: tuple[int, int] | None = None,
    **kwargs,
) -> AST:
    r"""Executes `ast.parse()` and then adds `FST` nodes to the parsed tree. Drop-in replacement for `ast.parse()`. For
    parameters, see `ast.parse()`. Returned `AST` tree has added `.f` attribute at each node which accesses the parallel
    `FST` tree.

    **Parameters:**
    - `source`: The python source to parse.
    - `filename`: `ast.parse()` parameter.
    - `mode`: Parse mode. Either one of the normal `ast` module parse modes `'exec'`, `'eval'` or `'single'`, or an
        extended `fst` parse mode parameter which allows parsing things the `ast` module cannot, See `fst.parsex.Mode`.
    - `type_comments`: `ast.parse()` parameter.
    - `feature_version`: `ast.parse()` parameter.

    **Returns:**
    - `AST`: Tree with an `FST` `.f` attribute added to each `AST` node.

    **Examples:**

    >>> import ast, fst
    >>> a = fst.parse('if 1:\n  i = 2')

    >>> type(a)
    <class 'ast.Module'>

    >>> a.f  # FST node
    <Module ROOT 0,0..1,7>

    >>> print(fst.dump(a, indent=2))
    Module(
      body=[
        If(
          test=Constant(value=1),
          body=[
            Assign(
              targets=[
                Name(id='i', ctx=Store())],
              value=Constant(value=2))],
          orelse=[])],
      type_ignores=[])

    >>> _ = a.f.dump()
    Module - ROOT 0,0..1,7
      .body[1]
       0] If - 0,0..1,7
         .test Constant 1 - 0,3..0,4
         .body[1]
          0] Assign - 1,2..1,7
            .targets[1]
             0] Name 'i' Store - 1,2..1,3
            .value Constant 2 - 1,6..1,7
    """

    if isinstance(source, AST):
        return FST.fromast(source, None, filename=filename, type_comments=type_comments,
                           feature_version=feature_version, **kwargs).a

    if not isinstance(source, str):
        source = bytes(source).decode()

    return FST.fromsrc(source, mode, filename=filename, type_comments=type_comments,
                       feature_version=feature_version, **kwargs).a


def unparse(ast_obj: AST) -> str:
    """Returns the formatted source that is kept for this tree. Drop-in replacement for `ast.unparse()` If there is no
    `FST` information in the `AST` tree then just executes `ast.unparse()`.

    **Parameters:**
    - `ast_obj`: The `AST` to unparse.

    **Returns:**
    - `str`: The unparsed source code, formatted if it came from `FST`.

    **Examples:**

    >>> import ast, fst
    >>> a = fst.parse('''
    ... if 1: i = 1  # same line
    ... else:
    ...   j=2 # comment
    ... '''.strip())

    >>> print(ast.unparse(a))
    if 1:
        i = 1
    else:
        j = 2

    >>> print(fst.unparse(a))
    if 1: i = 1  # same line
    else:
      j=2 # comment

    >>> a = ast.parse('i = 1')
    >>> ast.unparse(a)
    'i = 1'

    >>> fst.unparse(a)  # also unparses regular AST
    'i = 1'
    """

    if (f := getattr(ast_obj, 'f', None)) and isinstance(f, FST):
        try:
            return f.own_src()
        except Exception:
            pass

    return ast_unparse(ast_obj)


def dump(
    node: AST,
    annotate_fields: bool = True,
    include_attributes: bool = False,
    *,
    indent: int | str | None = None,
    show_empty: bool = True,
) -> str:
    """This function is a convenience function and only exists to make python version 3.13 and above `ast.dump()` output
    compatible on a default call with previous python versions (important for doctests). All arguments correspond to
    their respective `ast.dump()` arguments and `show_empty` is eaten on python versions below 3.13."""

    if PYLT13:
        return ast_dump(node, annotate_fields, include_attributes, indent=indent)
    else:
        return ast_dump(node, annotate_fields, include_attributes, indent=indent, show_empty=show_empty)


def castf(ast: AST) -> FST:
    """Cast AST F, type-safe way to access `ast.f` when you know it exists. Intentionally fail with `AttributeError` if
    `ast` does not have `.f`.

    **Example:**

    >>> a = fst.parse('module')

    >>> print(type(a))
    <class 'ast.Module'>

    >>> print(type(castf(a)))
    <class 'fst.fst.FST'>

    >>> castf(a) is a.f
    True

    >>> del a.f
    >>> print(castf(a))
    Traceback (most recent call last):
    ...
    AttributeError: 'Module' object has no attribute 'f'
    """

    return ast.f  # type: ignore


def gastf(ast: AST) -> FST | None:
    """Get AST F, type-safe way to get `ast.f` when it may or may not exist. Returns `None` if `ast` does not have an
    `.f`.

    **Example:**

    >>> a = fst.parse('module')

    >>> print(type(a))
    <class 'ast.Module'>

    >>> print(type(gastf(a)))
    <class 'fst.fst.FST'>

    >>> gastf(a) is a.f
    True

    >>> del a.f
    >>> print(gastf(a))
    None
    """

    return getattr(ast, 'f', None)


# ----------------------------------------------------------------------------------------------------------------------

class FST:
    """Class which maintains structure and formatted source code for an `AST` tree. An instance of this class is added
    to each `AST` node in a tree. It provides format-preserving operations as well as ability to navigate the tree in
    any direction."""

    a:            AST | None       ; """The actual `AST` node. Will be set to `None` for `FST` nodes which were deleted or otherwise invalidated so can be checked for that to see if the `FST` is still alive (while walking and modifying for example)."""
    parent:       FST | None       ; """Parent `FST` node, `None` in root node."""
    pfield:       astfield | None  ; """The `fst.common.astfield` location of this node in the parent, `None` in root node."""
    _cache:       dict

    # ROOT ONLY
    parse_params: Mapping[builtins.str, Any]  ; """The parameters to use for any `ast.parse()` (filename, type_comments, feature_version). Exists mostly for passing filename and future-proofing."""
    indent:       builtins.str                ; """The default single level block indentation string for this tree when not available from context."""
    _lines:       list[bistr]                 ; """The actual full source lines as `bistr`."""

    # class attributes
    is_FST:       bool = True  ; """Allows to quickly differentiate between actual `FST` nodes vs. views or locations."""  # for quick checks vs. `fstloc` or `fstview`

    @property
    def is_alive(self) -> bool:
        """`True` if the node is part of a tree, `False` if has been replaced or removed."""

        return self.a is not None

    @property
    def is_root(self) -> bool:
        """`True` for the root node, `False` otherwise."""

        return self.parent is None

    @property
    def root(self) -> FST:
        """Root node of the tree this node belongs to."""

        while parent := self.parent:
            self = parent

        return self

    @property
    def lines(self) -> list[builtins.str]:
        """Whole lines of this node from the **RAW SOURCE**, without any dedentation, may also contain parts of
        enclosing nodes. Will have indentation as it appears in the top level source if multiple lines. If gotten at
        root then the entire source is returned, which may extend beyond the location of the top-level node (mostly for
        statements which may have leading / trailing comments or empty lines).

        A valid list of strings is always returned, even for nodes which can never have source like `Load`, etc... The
        lines list returned is always a copy so safe to modify.

        **WARNING!** You get just the text that is there so you will get unparsable source if you get for example a
        string `Constant` from the `values` field of a `JoinedStr`, or a `format_spec`.
        """

        if not self.parent:  # is_root
            return self._lines[:]
        elif loc := self.bloc:
            return self.root._lines[loc.ln : loc.end_ln + 1]
        else:
            return [s] if (s := OPCLS2STR.get(self.a.__class__, None)) else ['']  # for boolop or expr_context

    @property
    def src(self) -> builtins.str:
        """Source code of this node from the **RAW SOURCE** clipped out as a single string, without any dedentation.
        Will have indentation as it appears in the top level source if multiple lines. If gotten at root then the entire
        source is returned, regardless of whether the actual top level node location includes it or not.

        A string is always returned, even for nodes which can never have source like `Load`, etc...

        **WARNING!** You get just the text that is there so you will get unparsable source if you get for example a
        string `Constant` from the `values` field of a `JoinedStr`, or a `format_spec`.
        """

        if not self.parent:  # is_root
            return '\n'.join(self._lines)
        elif loc := self.bloc:
            return self._get_src(*loc)
        else:
            return OPCLS2STR.get(self.a.__class__, '')  # for boolop or expr_context

    @property
    def has_own_loc(self) -> bool:
        """`True` when the node has its own location which comes directly from AST `lineno` and other location fields.
        Otherwise `False` if no `loc` or `loc` is calculated."""

        return hasattr(self.a, 'end_col_offset')

    @property
    def whole_loc(self) -> fstloc:
        """Whole source location, from (0, 0) to end of source. Works from any node (not just root)."""

        return fstloc(0, 0, len(ls := self.root._lines) - 1, len(ls[-1]))

    @property
    def loc(self) -> fstloc | None:
        """Zero based character indexed location of node (may not be entire location if node has decorators). Not all
        nodes have locations (like `expr_context`). Other nodes which normally don't have locations like `arguments` or
        most operators have this location calculated from their children or source.

        **Note:** Empty `arguments` do **NOT** have a location even though the `AST` exists, while non-empty `arguments`
        have a calculated location.
        """

        try:
            return self._cache['loc']
        except KeyError:
            pass

        ast = self.a

        try:
            ln = ast.lineno - 1
            col_offset = ast.col_offset
            end_ln = ast.end_lineno - 1
            end_col_offset = ast.end_col_offset

        except AttributeError:
            if loc_func := _LOC_FUNCS.get(ast.__class__):
                loc = loc_func(self)
            elif not self.parent:
                loc = fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))
            else:
                loc = None

        else:
            lines = self.root._lines
            col = lines[ln].b2c(col_offset)
            end_col = lines[end_ln].b2c(end_col_offset)
            loc = fstloc(ln, col, end_ln, end_col)

        self._cache['loc'] = loc

        return loc

    @property
    def bloc(self) -> fstloc | None:
        """Bounding location of node. For non-statements or non-block statements is same as `loc`. For block statements
        will include any leading decorators and a trailing line comment on the last child (or self if no children).

        **Examples:**

        >>> f = FST('''
        ... @decorator
        ... def func():
        ...     pass  # comment
        ... '''.strip())

        >>> f.bloc
        fstloc(0, 0, 2, 19)

        >>> f.loc
        fstloc(1, 0, 2, 8)

        >>> f = FST('stmt  # comment')

        Non-block statement doesn't include line comment.

        >>> f.bloc
        fstloc(0, 0, 0, 4)
        """

        try:
            return self._cache['bloc']
        except KeyError:
            pass

        if (bloc := self.loc) and self.a.__class__ in ASTS_LEAF_BLOCK:  # bloc can only be different for block-type ASTs
            ln, col, end_ln, end_col = bloc
            last_line = self.root._lines[end_ln]

            if last_line.find('#', end_col) != -1:  # if comment present on last line then set end to end of line to include the comment
                end_col = len(last_line)

            if getattr(self.a, 'decorator_list', None):  # if has any decorators then start at first one
                ln, col, _, _ = self._loc_decorator(0, False)

            bloc = fstloc(ln, col, end_ln, end_col)

        self._cache['bloc'] = bloc

        return bloc

    @property
    def ln(self) -> int:
        """Line number of the first line of this node (0 based)."""

        return (l := self.loc) and l[0]

    @property
    def col(self) -> int:  # char index
        """CHARACTER index of the start of this node (0 based)."""

        return (l := self.loc) and l[1]

    @property
    def end_ln(self) -> int:  # 0 based
        """Line number of the LAST LINE of this node (0 based)."""

        return (l := self.loc) and l[2]

    @property
    def end_col(self) -> int:  # char index
        """CHARACTER index one past the end of this node (0 based)."""

        return (l := self.loc) and l[3]

    @property
    def bln(self) -> int:
        """Line number of the first line of this node or the first decorator if present (0 based)."""

        return (l := self.bloc) and l[0]

    @property
    def bcol(self) -> int:
        """CHARACTER column of this node or the first decorator if present (0 based)."""

        return (l := self.bloc) and l[1]

    @property
    def bend_ln(self) -> int:
        """Line number of the last line of this node."""

        return (l := self.bloc) and l[2]

    @property
    def bend_col(self) -> int:
        """CHARACTER column of the end of the last line of this node, past a trailing line comment on last child if
        `self` is a block statement."""

        return (l := self.bloc) and l[3]

    @property
    def lineno(self) -> int:  # 1 based
        """AST-style line number of the first line of this node (1 based), available for all nodes which have `loc`
        (otherwise `None`)."""

        return (loc := self.loc) and loc[0] + 1

    @property
    def col_offset(self) -> int:  # byte index
        """AST-style BYTE index of the start of this node (0 based), available for all nodes which have `loc`
        (otherwise `None`)."""

        return (loc := self.loc) and self.root._lines[loc[0]].c2b(loc[1])

    @property
    def end_lineno(self) -> int:  # 1 based
        """AST-style line number of the LAST LINE of this node (1 based), available for all nodes which have `loc`
        (otherwise `None`)."""

        return (loc := self.loc) and loc[2] + 1

    @property
    def end_col_offset(self) -> int:  # byte index
        """AST-style BYTE index one past the end of this node (0 based), available for all nodes which have `loc`
        (otherwise `None`)."""

        return (loc := self.loc) and self.root._lines[loc[2]].c2b(loc[3])

    @property
    def has_docstr(self) -> bool:
        """Indicates whether this node has a docstring. Can only be `True` for `FunctionDef`, `AsyncFunctionDef`,
        `ClassDef` or `Module`. For quick use as start index."""

        return True if (
            (a := self.a).__class__ in ASTS_LEAF_MAYBE_DOCSTR
            and (b := a.body)
            and (b0 := b[0]).__class__ is Expr
            and (v := b0.value).__class__ is Constant
            and isinstance(v := v.value, str)
        ) else False  # IfExp because of the (b := a.body)

    @property
    def f(self) -> None:
        """Runtime confusion protection.
        @private"""

        raise RuntimeError(f"you probably think you're accessing an AST node '.f', but you're not, "
                           f"you're accessing an FST {self}.f")

    # ------------------------------------------------------------------------------------------------------------------
    # Create / manage

    def __repr__(self) -> builtins.str:
        return f'<{self.a.__class__.__name__}{self._repr_tail()}>'

    def __new__(
        cls,
        src_or_ast_or_fst: FST | AST | builtins.str | list[builtins.str] = '',
        mode: FST | list[builtins.str] | Mode | Literal[False] | None = None,
        pfield: astfield | Literal[False] | None = False,
        /,
        **kwargs,
    ) -> 'FST':
        r"""Create a new individual `FST` node or full tree. The main way to use this constructor is as a shortcut for
        `FST.fromsrc()`, `FST.fromast()` or `FST.as_()`, the usage is:

        **`FST(src_or_ast_or_fst, mode=None)`**

        This will create an `FST` from either an `AST` or source code in the form of a string or list of lines, or it
        will attempt to coerce an existing `FST` to the type you want specified by `mode`.

        **WARNING!** In normal usage, you should always leave `pfield` at its default as anything else will select other
        modes of opertation for this constructor.

        **Parameters:**
        - `src_or_ast_or_fst`: Source code or an `AST` or `FST` node.
        - `mode`: See `fst.parsex.Mode`. Has the following meanings when the `src_or_ast_or_fst` parameter is:
            - `src`: If `mode` is `None` then we will try to guess what the source is and parse it accordingly. If
                specified then will attempt to parse this type and if fails then the exception will propagate. If
                guessing then it may take more than one attempt so it is always better to specify what you expect to get
                if you know it.
            - `AST`: If `mode` is `None` then defaults to the type of the `AST`, which will always succeed in generating
                valid source unless the `AST` itself is in an invalid state (like an empty `Set`). Anything else you
                pass here will be passed on as the `mode` to `fromast()`. In which case if the `AST` is this then the
                `FST` tree is just build for it and otherwise coercion will be attempted to this type.
            - `FST`: `mode` should be specified and will be the type of node you want to coerce the `FST` you pass in
                to. If you leave it at the default `None` then you will just get either the same `FST` or a copy of it,
                depending on the `copy` kwarg.
        - `kwargs`: `options` if coercing from another `FST` or extra parameters, mostly for internal use documented
            below. One extra parameter relevant to this use case is:
            - `copy`: If coercing from another `FST`, this parameter is what will be passed to `as_()`. It defaults to
                `True` here so that `FST(other_FST)` works in the same way as `list(other_list)`, meaning it doesn't
                alter the source object, which is the opposite of what the default for the `as_()` function is.

        **Examples:**

        >>> FST('def f(): call()\ndef g(): pass')
        <Module ROOT 0,0..1,13>

        Minimal node representation is created by default, so `stmt` instead of `mod` if possible and `expr` instead of
        `stmt`.

        >>> FST('def f(): call()')
        <FunctionDef ROOT 0,0..0,15>

        >>> FST('call()')
        <Call ROOT 0,0..0,6>

        You can force a module.

        >>> FST('call()', 'exec')
        <Module ROOT 0,0..0,6>

        Can parse things not normally parsable.

        >>> FST('start:stop:step')
        <Slice ROOT 0,0..0,15>

        `FST` guesses what you want in this case but doesn't always get it right.

        >>> FST('start:stop')
        <AnnAssign ROOT 0,0..0,10>

        So you can tell it. This is also usually faster to parse than if `fst` has to guess and try parsing something
        that it is not before finding out what it is, so if this is important to you then always pass the type you
        expect to get when you can.

        >>> FST('start:stop', 'Slice')
        <Slice ROOT 0,0..0,10>

        You can tell it to only parse things which are top-level parsable by `ast.parse()`.

        >>> try:
        ...     FST('start:stop:step', 'strict')
        ... except Exception as exc:
        ...     print(str(exc))
        invalid syntax (<FST>, line 1)

        You can also pass an `AST` and the source will be generated from it.

        >>> FST(ast.Slice(Constant(1), Constant(2), Constant(3)))
        <Slice ROOT 0,0..0,5>

        >>> print(_.src)
        1:2:3

        Coercion is straightforward.

        >>> f = FST('expr')
        >>> f, f.src
        (<Name ROOT 0,0..0,4>, 'expr')

        >>> g = FST(f, 'stmt')
        >>> g, g.src
        (<Expr ROOT 0,0..0,4>, 'expr')

        >>> g = FST(f, 'Name')
        >>> g, g.src, g is f
        (<Name ROOT 0,0..0,4>, 'expr', False)

        Turn off `copy` to return the same node if it is the type you are requesting.

        >>> g = FST(f, 'Name', copy=False)
        >>> g, g.src, g is f
        (<Name ROOT 0,0..0,4>, 'expr', True)

        But still coerces if is not.

        >>> g = FST(f, 'arg', copy=False)
        >>> g, g.src, g is f
        (<arg ROOT 0,0..0,4>, 'expr', False)

        Same `options` apply as to all other operations.

        >>> FST(FST('[]'), 'Set').src  # will give invalid empty Set node
        '{}'

        >>> FST(FST('[]'), 'Set', norm=True).src
        '{*()}'

        The other forms of this function are meant for internal use, their parameters are below for reference just in
        case:

        **Parameters:**
        - `src_or_ast_or_fst`: `AST` node for `FST` or source code in the form of a `str` or a list of lines. If an `AST` then
            will be processed differently depending on if creating child node, top level node or using this as a
            shortcut for a full `fromsrc()` or `fromast()`. If left as empty default then just creates a new empty
            `Module`.
        - `mode`: Is really `mode_or_lines_or_parent`. Parent node for this child node or lines for a root node creating
            a new tree. If `pfield` is `False` then this is a shortcut to create a full tree from an `AST` node or
            source provided in `src_or_ast_or_fst`.
        - `pfield`: `fst.common.astfield` indication position in parent of this node. If provided then creating a simple
            child node and it is created with the `self.parent` set to `mode` node and `self.pfield` set to this. If
            `None` then it means the creation of a full new `FST` tree and this is the root node with `mode` providing
            the source. If `False` then this is a shortcut for `FST.fromsrc()` or `FST.fromast()`.
        - `kwargs`: Contextual parameters:
            - `from_`: If this is provided then it must be an `FST` node from which this node is being created. This
                allows to copy parse parameters and already determined default indentation. Does not have to be root.
            - `parse_params`: A `dict` with values for `filename`, `type_comments` and `feature_version` which will be
                used for any `AST` reparse done on this tree. Only valid when creating a root node.
            - `indent`: Indentation string to use as default indentation. If not provided and not gotten from `from_`
                then indentation will be inferred from source. Only valid when creating a root node.
            - `filename`, `type_comments` and `feature_version`: If creating from an `AST` or source only then these are
                the parameteres passed to the respective `.fromsrc()` or `.fromast()` functions. Only valid when
                `pfield` is `False`, meaning a shortcut use of `FST()`.
            - `lcopy`: Whether to copy lines of source on root node create or just use what is passed in, which in this
                case must be a list of `fst.astutil.bistr` and this node takes ownership of the list.
            - `tmake`: Whether to do `_make_fst_tree()` on `self` or not. Turning this off can be used to create a root
                node for a specific existing `FST` tree. Useful for optimizing some operations.
        """

        if pfield is False:  # top level shortcut
            if src_or_ast_or_fst.__class__ is FST:
                return src_or_ast_or_fst.as_(mode, kwargs.get('copy', True), **filter_options(kwargs))

            parse_params = {k: v for k in ('filename', 'type_comments', 'feature_version')
                            if (v := kwargs.get(k, k)) is not k}  # k used as sentinel
            indent = None

            if from_ := kwargs.get('from_'): # copy parse_params from source tree
                from_root = from_.root
                parse_params = {**from_root.parse_params, **parse_params}
                indent = from_root.indent

            if isinstance(src_or_ast_or_fst, (str, list)):
                f = FST.fromsrc(src_or_ast_or_fst, mode or 'all', **parse_params)
            else:  # isinstance(src_or_ast_or_fst, AST)
                f = FST.fromast(src_or_ast_or_fst, mode, **parse_params)

            if indent is not None or (indent := kwargs.get('indent')) is not None:
                f.indent = indent

            return f

        # creating actual node

        if not (self := getattr(src_or_ast_or_fst, 'f', None)):  # reuse FST node assigned to AST node (because otherwise it isn't valid anyway)
            self = src_or_ast_or_fst.f = object.__new__(cls)

        elif not self.parent:  # if was previously root then clear out root attributes
            del self.parse_params, self.indent, self._lines

        self.a = src_or_ast_or_fst  # we don't assume `self.a` is `src_or_ast_or_fst` if even if `.f` exists, it should always be but juuuuust in case
        self.pfield = pfield
        self._cache = {}  # this is same a self._touch() if .f already existed in AST

        if pfield:  # if this is not a root node then we are done
            self.parent = mode

            return self

        # ROOT

        self.parent = None
        self._lines = ([bistr(s) for s in mode] if kwargs.get('lcopy', True) else mode)

        if from_ := kwargs.get('from_'):  # copy params from source tree
            from_root = from_.root
            self.parse_params = kwargs.get('parse_params', from_root.parse_params)
            self.indent = kwargs.get('indent', from_root.indent)

        else:
            self.parse_params = kwargs.get('parse_params', _DEFAULT_PARSE_PARAMS)

            if (indent := kwargs.get('indent')) is not None:
                self.indent = indent
            elif (
                (is_modlike := (src_or_ast_or_fst.__class__ in (Module, _ExceptHandlers, _match_cases)))
                or src_or_ast_or_fst.__class__ in ASTS_LEAF_BLOCK
            ):
                self.indent = '?'
            else:
                self.indent = _DEFAULT_INDENT

        if getattr(kwargs, 'tmake', True):
            self._make_fst_tree()

        if self.indent == '?':  # infer indentation from source, just use first indentation found for performance, don't try to find most common or anything like that, note that self.indent = '?' is used for checking
            if is_modlike:
                asts = (getattr(src_or_ast_or_fst, 'body', None) or
                        getattr(src_or_ast_or_fst, 'handlers', None) or
                        getattr(src_or_ast_or_fst, 'cases', None) or ())
            else:
                asts = (src_or_ast_or_fst,)

            for a in asts:
                a_cls = a.__class__

                if a_cls in (FunctionDef, AsyncFunctionDef, ClassDef, With, AsyncWith, ExceptHandler, match_case):  # we check ExceptHandler and match_case because they may be supported as standalone parsed elements eventually
                    indent = a.body[0].f._get_block_indent()

                elif a_cls in (For, AsyncFor, While, If):
                    if (indent := a.body[0].f._get_block_indent()) == '?' and (orelse := a.orelse):
                        if not (indent := orelse[0].f._get_block_indent()):  # because can be 'elif'
                            indent = '?'

                elif a_cls in ASTS_LEAF_TRY:
                    if (indent := a.body[0].f._get_block_indent()) == '?':
                        if not (orelse := a.orelse) or (indent := orelse[0].f._get_block_indent()) == '?':
                            if not (finalbody := a.finalbody) or (indent := finalbody[0].f._get_block_indent()) == '?':
                                for handler in a.handlers:
                                    if (indent := handler.body[0].f._get_block_indent()) != '?':
                                        break

                elif a_cls is Match:
                    indent = a.cases[0].f._get_block_indent()
                else:
                    continue

                if indent != '?':
                    self.indent = indent

                    break

            else:
                self.indent = _DEFAULT_INDENT

        return self

    @staticmethod
    def fromsrc(
        src: builtins.str | list[builtins.str],
        mode: Mode = 'exec',
        *,
        filename: builtins.str = _DEFAULT_FILENAME,
        type_comments: bool = False,
        feature_version: tuple[int, int] | None = None,
    ) -> FST:
        """Parse and create a new `FST` tree from source, preserving the original source and locations.

        **WARNING!** The `type_comments` parameter is `False` by default and no guarantees are made if you turn it on.
        It is provided just in case but really shouldn't be used as `fst` takes care of comments anyway, this just turns
        on storing the comments in the `AST` nodes which may cause all sorts of madness like duplication on unparse or
        nodes failing to reparse to themselves on operations.

        **Parameters:**
        - `src`: The source to parse as a single `str` or list of individual line strings (without newlines).
        - `mode`: Parse mode, extended `ast.parse()` parameter, see `fst.parsex.Mode`. If you know what kind of node you
            are expecting then it is always better to pass in this parameter because otherwise several different parse
            attempts may be made to try to find the type.
        - `filename`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter. Don't use this, see warning above.
        - `feature_version`: `ast.parse()` parameter. Don't use this either, here just in case.

        **Returns:**
        - `FST`: The parsed tree with `.f` attributes added to each `AST` node for `FST` access.

        **Examples:**

        >>> _ = FST.fromsrc('var').dump()
        Module - ROOT 0,0..0,3
          .body[1]
           0] Expr - 0,0..0,3
             .value Name 'var' Load - 0,0..0,3

        >>> _ = FST.fromsrc('var', mode='stmt').dump()
        Expr - ROOT 0,0..0,3
          .value Name 'var' Load - 0,0..0,3

        >>> _ = FST.fromsrc('var', mode='expr').dump()
        Name 'var' Load - ROOT 0,0..0,3

        >>> _ = FST.fromsrc('except Exception: pass', 'ExceptHandler').dump()
        ExceptHandler - ROOT 0,0..0,22
          .type Name 'Exception' Load - 0,7..0,16
          .body[1]
           0] Pass - 0,18..0,22

        >>> _ = FST.fromsrc('case f(a=1): pass', 'match_case').dump()
        match_case - ROOT 0,0..0,17
          .pattern MatchClass - 0,5..0,11
            .cls Name 'f' Load - 0,5..0,6
            .kwd_attrs[1]
             0] 'a'
            .kwd_patterns[1]
             0] MatchValue - 0,9..0,10
               .value Constant 1 - 0,9..0,10
          .body[1]
           0] Pass - 0,13..0,17

        >>> import ast
        >>> _ = FST.fromsrc('a:b', ast.Slice).dump()
        Slice - ROOT 0,0..0,3
          .lower Name 'a' Load - 0,0..0,1
          .upper Name 'b' Load - 0,2..0,3
        """

        if isinstance(src, str):
            lines = src.split('\n')
        else:
            lines = src
            src = '\n'.join(lines)

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)
        ast = parsex.parse(src, mode, parse_params)

        return FST(ast, lines, None, parse_params=parse_params)

    @staticmethod
    def fromast(
        ast: AST,
        mode: Mode | None = None,
        *,
        coerce: bool = True,
        filename: builtins.str = _DEFAULT_FILENAME,
        type_comments: bool = False,
        feature_version: tuple[int, int] | None = None,
    ) -> FST:
        r"""Convert an `AST` tree to a full `FST` tree. This can take the existing node and just create the `FST` nodes
        for it (unparsing to get source code). Or if `mode` is specified, will try to coerce the `AST` node to this type
        and create the `FST` tree for that.

        The passed `ast` node is not actually consumed. It is unparsed and reparsed to a new `AST` since we need to make
        sure the locations are all correct.

        **WARNING!** The `type_comments` parameter is `False` by default and no guarantees are made if you turn it on.
        It is provided just in case but really shouldn't be used as `fst` takes care of comments anyway, this just turns
        on storing the comments in the `AST` nodes which may cause all sorts of madness like duplication on unparse or
        nodes failing to reparse to themselves on operations.

        **Parameters:**
        - `ast`: The root `AST` node. This is **NOT** consumed and will **NOT** become the actual `AST` node of the
            `FST` tree.
        - `mode`: Parse mode to enable coercion, see `fst.parsex.Mode`. If `None` then will just use the given `ast`
            type and make an `FST` using that type.
        - `coerce`: This exists to allow you to turn **OFF** coercion for some reason as by default coerce is attempted.
        - `filename`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter. Don't use this, see warning above.
        - `feature_version`: `ast.parse()` parameter. Don't use this either, here just in case.

        **Returns:**
        - `FST`: The augmented tree with `.f` attributes added to each `AST` node for `FST` access.

        **Examples:**

        >>> import ast
        >>> from ast import Assign, Constant, List, Name, Slice

        >>> _ = FST.fromast(Assign(targets=[Name(id='var')],
        ...                        value=Constant(value=123))).dump('stmt')
        0: var = 123
        Assign - ROOT 0,0..0,9
          .targets[1]
           0] Name 'var' Store - 0,0..0,3
          .value Constant 123 - 0,6..0,9

        >>> _ = FST.fromast(Slice(lower=Constant(value=1),
        ...                       step=Name(id='step'))).dump('node')
        0: 1::step
        Slice - ROOT 0,0..0,7
        0: 1
          .lower Constant 1 - 0,0..0,1
        0:    step
          .step Name 'step' Load - 0,3..0,7

        >>> _ = FST.fromast(List(elts=[Name(id='var')]),
        ...                 'pattern', coerce=True).dump('stmt')
        0: [var]
        MatchSequence - ROOT 0,0..0,5
          .patterns[1]
           0] MatchAs - 0,1..0,4
             .name 'var'

        >>> _ = FST.fromast(List(elts=[Name(id='var')]),
        ...                 'pattern', coerce=False).dump('stmt')
        Traceback (most recent call last):
        ...
        fst.NodeError: expecting pattern, got List, coerce disabled

        >>> _ = FST.fromast(ast.parse('if 1:\n    j = 5')).dump('stmt')
        Module - ROOT 0,0..1,9
          .body[1]
        0: if 1:
           0] If - 0,0..1,9
             .test Constant 1 - 0,3..0,4
             .body[1]
        1:     j = 5
              0] Assign - 1,4..1,9
                .targets[1]
                 0] Name 'j' Store - 1,4..1,5
                .value Constant 5 - 1,8..1,9
        """

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)

        return code.code_as(ast, mode or ast.__class__, parse_params=parse_params, coerce=coerce)

    get_options = fst_options.get_options  # we do assign instead of import so that pdoc gets the right order
    get_option = fst_options.get_option
    set_options = fst_options.set_options
    options = fst_options.options

    def as_(self, mode: Mode | None = None, copy: bool = False, **options) -> FST:
        """Attempt to coerce `self` to the type of node given by `mode`. If `self` is already the requested type of node
        at root level then will do nothing and return `self`. If is not at root level then will copy the node first and
        then attempt to coerce.

        If `self` is not the type requested then will attempt to coerce, which is a destructive operation to the
        original node (`self`) even if it fails, rendering `self` unusable. For this reason the `copy` parameter allows
        you to specify that `self` must be copied first before coerce is attempted, leaving the original node intact.
        Note that a copy is always made regardless if `self` is not a root node so the original node will be unharmed in
        that case.

        **Note:** If `self` is a subclass of the type you request then it counts as a match and `self` is returned
        unchanged, e.g. `Assign` and you request a `stmt`.

        **Parameters:**
        - `mode`: The type of node you want, `None` means no coerce and just return `self`, see `fst.parsex.Mode`.
        - `copy`: This only matters if you are calling this function on a root node, in which case a copy is made before
            coerce is attempted in order to make sure the node you are calling remains valid.
        - `options`: See `options()`. These same options will be used for both a possible copy and for coercion.

        **Returns:**
        - `FST`: Coerced node.

        **Examples:**

        >>> f = FST('expr')
        >>> f
        <Name ROOT 0,0..0,4>

        >>> (f := f.as_('stmt'))
        <Expr ROOT 0,0..0,4>

        >>> f.as_('exec')
        <Module ROOT 0,0..0,4>

        >>> _ = FST('if a if b', '_comprehension_ifs').as_(expr).dump()
        Tuple - ROOT 0,0..0,4
          .elts[2]
           0] Name 'a' Load - 0,0..0,1
           1] Name 'b' Load - 0,3..0,4
          .ctx Load

        >>> _ = FST('case [a, cls(b)]: pass').pattern.as_(expr).dump()
        List - ROOT 0,0..0,11
          .elts[2]
           0] Name 'a' Load - 0,1..0,2
           1] Call - 0,4..0,10
             .func Name 'cls' Load - 0,4..0,7
             .args[1]
              0] Name 'b' Load - 0,8..0,9
          .ctx Load
        """

        check_options(options)

        if copy or self.parent:
            self = self.copy(**options)

        return code.code_as(self, mode or 'all', options, self.parse_params, coerce=True)

    def reparse(self) -> FST:  # -> self
        """Force a reparse of this node to synchronize the `AST` tree with the source in case the source was changed
        with non-native or non-synchronous operations such as `put_src()` with only offset. Can use on any node, not
        just root.

        **Returns:**
        - `self`: New `self` after reparse, if possible, otherwise `None` if could not be found. May also be another
            neighbor node if the source of `self` was structurally changed too much. If used on root node then `self`
            will not change.

        **Examples:**

        >>> f = FST('f"{expr}"')

        >>> _ = f.dump('stmt', loc=False)  # loc=False because of py < 3.12
        0: f"{expr}"
        JoinedStr - ROOT
          .values[1]
           0] FormattedValue
             .value Name 'expr' Load
             .conversion -1

        >>> f.put_src('=', 0, 7, 0, 7, 'offset')
        (0, 8)

        >>> _ = f.dump('stmt', loc=False)
        0: f"{expr=}"
        JoinedStr - ROOT
          .values[1]
           0] FormattedValue
             .value Name 'expr' Load
             .conversion -1

        >>> bool(f.verify(raise_=False))
        False

        >>> f = f.reparse()

        >>> bool(f.verify(raise_=False))
        True

        >>> _ = f.dump('stmt', loc=False)
        0: f"{expr=}"
        JoinedStr - ROOT
          .values[2]
           0] Constant 'expr='
           1] FormattedValue
             .value Name 'expr' Load
             .conversion 114
        """

        if not (loc := self.loc):
            raise ValueError('cannot reparse node without a location')

        ln, col, end_ln, end_col = loc

        self.put_src(self._get_src(ln, col, end_ln, end_col), ln, col, end_ln, end_col)

        if new := self.repath():
            return new

        return self.find_loc(ln, col, end_ln, end_col, True)

    def verify(
        self,
        mode: Mode | None = None,
        reparse: bool = True,
        *,
        locs: bool = True,
        ctx: bool = True,
        raise_: bool = True,
    ) -> FST | None:
        """Sanity check. Walk the tree and make sure all `AST`s have corresponding `FST` nodes with valid parent / child
        links, then (optionally) reparse source and make sure parsed tree matches currently stored tree (locations and
        everything). The reparse can only be carried out on root nodes but the link validation can be done on any level.

        SPECIAL SLICEs like `_decorator_list` will verify ok with reparse but invalid nodes like an empty `Set` or
        block statements with empty bodies will not.

        **Parameters:**
        - `mode`: Parse mode to use, otherwise if `None` then use the top level `AST` node type for the mode. Depending
            on how this is set will determine whether the verification is checking if is parsable by python (`'exec'` or
            `'strict'` for example), or if the node itself is just in a valid state (`None` specifies this). See
            `fst.parsex.Mode`.
        - `reparse`: Whether to reparse the source and compare `AST`s (including location). Otherwise the check is
            limited to a structure check that all children have `FST` nodes which are all liked correctly to their
            parents. `reparse=True` only allowed on root node.
        - `locs`: Whether to compare locations after reparse or not.
        - `ctx`: Whether to compare `ctx` nodes after reparse or not.
        - `raise_`: Whether to raise an exception on verify failed or return `None`.

        **Returns:**
        - `None` on failure to verify (if not `raise_`), otherwise `self`.

        **Examples:**

        >>> FST('var = 123').verify()
        <Assign ROOT 0,0..0,9>

        >>> FST('a:b:c').verify()
        <Slice ROOT 0,0..0,5>

        >>> bool(FST('a:b:c').verify('exec', raise_=False))
        False

        >>> FST('if a if b').verify()
        <_comprehension_ifs ROOT 0,0..0,9>

        >>> bool(FST('if a if b').verify('strict', raise_=False))
        False

        >>> (f := FST('a + b')).put_src('-', 0, 2, 0, 3, action=None)
        (0, 3)

        >>> f.verify()
        Traceback (most recent call last):
        ...
        fst.astutil.WalkFail: child classes differ in BinOp.op, Sub vs. Add, locs ('?', '?', '?', '?') / ('?', '?', '?', '?')
        """

        # validate tree links

        ast = self.a
        stack = [(ast, self.parent, self.pfield)]  # [(AST, parent FST, pfield), ...]

        while stack:
            a, parent, pfield = stack.pop()

            if not (f := getattr(a, 'f', None)) or f.parent is not parent or f.pfield != pfield or f.a is not a:
                if not raise_:
                    return None

                path = self.child_path(parent) + [pfield] if a is not ast else []
                path = '.'.join(af.name if (i := af.idx) is None else f'{af.name}[{i}]' for af in path)
                reason = ', no AST.f node' if not f else ', bad parent' if f.parent is not parent else ', bad pfield'

                raise WalkFail(f'invalid child {a.__class__.__name__} at {path if path else "self"}{reason}')

            for field, child in iter_fields(a):
                if isinstance(child, AST):
                    stack.append((child, f, astfield(field)))
                elif isinstance(child, list):
                    stack.extend((c, f, astfield(field, i)) for i, c in enumerate(child) if isinstance(c, AST))

        if not reparse:
            return self

        # reparse

        if not self.is_root:
            raise ValueError('verify with reparse can only be called on root node')

        parse_params = self.parse_params

        try:
            astp = parsex.parse(self.src, mode or self._get_parse_mode(), parse_params=parse_params)

        except SyntaxError:
            if raise_:
                raise

            return None

        if not compare_asts(astp, ast, locs=locs, ctx=ctx, type_comments=parse_params.get('type_comments', False),
                            raise_=raise_):
            return None

        return self

    def dump(
        self,
        src: Literal['stmt', 'all'] | str | None = None,  # noqa: PYI051
        full: bool = False,
        *,
        expand: bool = False,
        indent: int = 2,
        list_indent: int | bool = 1,
        loc: bool = True,
        color: bool | None = None,
        out: Literal['print', 'str', 'lines'] | Callable[[str], None] | TextIO = 'print',
        eol: builtins.str | None = None,
    ) -> FST | builtins.str | list[builtins.str]:  # -> self if not returning str or lines
        r"""Dump a representation of the tree to stdout or other `TextIO` or return as a `str` or `list[str]` of lines,
        or call a provided function once with each line of the output.

        **Parameters:**
        - `src`: Either what level of source to show along with the nodes or a shorthand string which can specify almost
            all the formatting parameters as a string of characters.
            - `'stmt'` or `'stmt+'` means output statement source lines (including `ExceptHandler` and `match_case`)
                or top level source if level is below statement. The `+` means put all lines of source including
                non-coding ones so that whole source is shown.
            - `'node'` or `'node+'` means output source for each individual node. The `+` means the same as for
                `'stmt+'`.
            - `None` does not output any source.
            - `str`: Can be a string for shortcut specification of source and flags by first letter, `'s+feL'` would be
                equivalent to `.dump(src='stmt+', full=True, expand=True, loc=False)`.
                - `'s'` or `'s+'` means `src='stmt'` or `src='stmt+'`
                - `'S'` same as `'s+'`
                - `'n'` or `'n+'` means `src='node'` or `src='node+'`
                - `'N'` same as `'N+'`
                - `'f'` means `full=True`
                - `'e'` means `expand=True`
                - `'i'` means `list_indent=indent`
                - `'I'` means `list_indent=False`
                - `'L'` means `loc=False`
                - `'c'` means `color=True`
                - `'C'` means `color=False`
        - `full`: If `True` then will list all fields in nodes including empty ones, otherwise will exclude most empty
            fields.
        - `expand`: If `False` then the output is a nice compact representation. If `True` then it is ugly and wasteful.
        - `indent`: Indentation per level as an integer (number of spaces) or a string.
        - `list_indent`: Extra indentation for elements of lists as an integer or string (added to indent). If `True`
            then will be same as `indent`.
        - `loc`: Whether to dump locations of nodes or not.
        - `color`: `True` or `False` means whether to use ANSI color codes or not. If `None` then will autodetect, which
            can be overridden with environment variables `FORCE_COLOR` and `NO_COLOR`.
        - `out`: `'print'` means print to stdout, `'lines'` returns a list of lines and `'str'` returns a whole string.
            A `TextIO` object here will use the `write` method for each line of output. Otherwise a
            `Callable[[str], None]` which is called for each line of output individually. If `'str'` or `'lines'` then
            that is returned, otherwise `self` is returned for chaining.
        - `eol`: What to put at the end of each text line, `None` means newline for a `TextIO` out and nothing for other
            types of `out`.

        **Returns:**
        - `str`: If was requested with `out='str'`, string of entire dump, lines ended with `eol`.
        - `list[str]`: If was requested with `out='lines'`, list of lines ended wiith `eol`.
        - `self`: If `out` is anything else, for convenience.

        **Examples:**

        >>> f = FST('''
        ... if 1:
        ...     call(a=b, **c)
        ... '''.strip())

        >>> _ = f.dump()
        If - ROOT 0,0..1,18
          .test Constant 1 - 0,3..0,4
          .body[1]
           0] Expr - 1,4..1,18
             .value Call - 1,4..1,18
               .func Name 'call' Load - 1,4..1,8
               .keywords[2]
                0] keyword - 1,9..1,12
                  .arg 'a'
                  .value Name 'b' Load - 1,11..1,12
                1] keyword - 1,14..1,17
                  .value Name 'c' Load - 1,16..1,17

        >>> _ = f.dump(src='node', indent=3, list_indent=True)
        0: if 1:
        If - ROOT 0,0..1,18
        0:    1
           .test Constant 1 - 0,3..0,4
           .body[1]
        1:     call(a=b, **c)
              0] Expr - 1,4..1,18
                 .value Call - 1,4..1,18
        1:     call
                    .func Name 'call' Load - 1,4..1,8
                    .keywords[2]
        1:          a=b
                       0] keyword - 1,9..1,12
                          .arg 'a'
        1:            b
                          .value Name 'b' Load - 1,11..1,12
        1:               **c
                       1] keyword - 1,14..1,17
        1:                 c
                          .value Name 'c' Load - 1,16..1,17

        >>> f.dump(out='str')[:64]
        'If - ROOT 0,0..1,18\n  .test Constant 1 - 0,3..0,4\n  .body[1]\n   '

        >>> from pprint import pp
        >>> pp(f.dump('stmt', loc=False, out='lines'))
        ['0: if 1:',
         'If - ROOT',
         '  .test Constant 1',
         '  .body[1]',
         '1:     call(a=b, **c)',
         '   0] Expr',
         '     .value Call',
         "       .func Name 'call' Load",
         '       .keywords[2]',
         '        0] keyword',
         "          .arg 'a'",
         "          .value Name 'b' Load",
         '        1] keyword',
         "          .value Name 'c' Load"]
        """

        src_plus = False

        if isinstance(src, str):
            if src in ('stmt+', 'node+'):
                src = src[:-1]
                src_plus = True

            elif src not in ('stmt', 'node'):  # shorthand
                full = True if 'f' in src else False if 'F' in src else full
                expand = True if 'e' in src else False if 'E' in src else expand
                loc = True if 'l' in src else False if 'L' in src else loc
                color =True if 'c' in src else False if 'C' in src else color
                list_indent = indent if 'i' in src else 0 if 'I' in src else list_indent

                if 'S' in src:
                    src_plus = True
                    src = 'stmt'
                elif 'N' in src:
                    src_plus = True
                    src = 'node'
                else:
                    src_plus = '+' in src
                    src = 'stmt' if 's' in src else 'node' if 'n' in src else None

        if out == 'print':
            out = print

            if color is None and (color := DEFAULT_COLOR) is None:
                if not hasattr(sys.stdout, 'fileno'):
                    color = False  # pragma: no cover
                else:
                    try:
                        color = os.isatty(sys.stdout.fileno()) or IPYTHON_COLOR
                    except io.UnsupportedOperation:
                        color = hasattr(sys.stdout, 'isatty') and (sys.stdout.isatty() or IPYTHON_COLOR)

        if isinstance(out, TextIOBase):
            out = out.write

            if eol is None:
                eol = '\n'

        elif eol is None:
            eol = ''

        sind = indent if isinstance(indent, str) else ' ' * indent
        lind = sind + (sind if list_indent is True else
                       list_indent if isinstance(list_indent, str) else
                       ' ' * list_indent)
        color = DUMP_COLOR if color else DUMP_NO_COLOR
        st = nspace(src=src, src_plus=src_plus, full=full, expand=expand, loc=loc, color=color,
                    eol=eol, sind=sind, lind=lind)

        if (is_lines := out == 'lines') or out == 'str':
            lines = []
            st.linefunc = lines.append

            self._dump(st, src_plus)

            return lines if is_lines else '\n'.join(lines)

        st.linefunc = out

        self._dump(st, src_plus)

        return self

    # ------------------------------------------------------------------------------------------------------------------
    # Reconcile

    def mark(self) -> FST:  # -> self
        """Create a checkpoint with data needed for a later `reconcile()`. After this function is used, no more
        FST-native modifications should be made to the tree until after the `reconcile()`. Any changes for the
        `reconcile()` to work must be exclusively in the `AST` tree. If any modifications are made using `FST` functions
        then the checkpoint will be invalidated and will need to be recreated if `reconcile()` is wanted after the
        modifications.

        **Returns:**
        - `self`
        """

        if not self.is_root:
            raise ValueError('can only mark root nodes')

        self._cache['mark'] = self.copy()

        return self

    def reconcile(
        self,
        trivia_ast_put: Trivia | None = None,
        trivia_fst_put: Trivia | None = None,
        trivia_fst_get: Trivia | None = None,
        *,
        cleanup: bool = True,
        **options
    ) -> FST:
        r"""Reconcile `self` with a previously marked version and return a new valid `FST` tree. This is meant for
        allowing non-FST modifications to an `FST` tree and later converting it to a valid `FST` tree to preserve as
        much formatting as possible and maybe continue operating in `FST` land. Only `AST` nodes from the original tree
        carry formatting information, so the more of those are replaced the more formatting is lost.

        **Note:** When replacing the `AST` nodes, make sure you are replacing the nodes in the actual `AST` node fields,
        not the `.a` attribute in `FST` nodes, that won't do anything.

        **Disclaimer:** This functionality is still experimental and unfinished so not all comments which should be may
        be preserved and others may be duplicated.

        **Parameters:**
        - `trivia_ast_put`: The `trivia` option to use when putting an `AST` node. Since `AST` nodes have no trivia in
            practice this means how much of the existing trivia at the target node is deleted. `None` means use default.
        - `trivia_fst_put`: The `trivia` option to use when putting an `FST` node, which may or may not have attached
            trivia depending on the `trivia_fst_get` option. This option only specifies what happens to the target
            trivia so depending on if the node being put has any it means delete or replace. `None` means use default.
        - `trivia_fst_get`: The `trivia` option to use when getting `FST` nodes for put. This can happen due to nodes
            completely translated to a place they were not anywhere near or due to movement because of deletions or
            insertions into the body where the nodes live. `None` means use default.
        - `cleanup`: By default after a successful reconcile `self` is cleanued up and no more reconcile can be
            attempted on it. It can be left in place to continue working on it and `reconcile()` again by passing
            `cleanup=False` but this is not guaranteed to survive further reconcile development.
        - `options`: Only a few options are allowed for reconcile as others are managed during the process. The most
            useful ones are `elif_` and `pep8space`. See `options()`.

        **Returns:**
        - `FST`: A new valid reconciled `FST` if possible.

        **Examples:**

        >>> f = FST('''
        ... @decorator  # something
        ... def function(a: int, b=2)->int:  # blah
        ...     return a+b  # return this
        ...
        ... def other_function(a, b):
        ...     return a - b  # return that
        ... '''.strip())

        >>> f.mark()
        <Module ROOT 0,0..5,31>

        >>> f.a.body[0].returns = Name('float')  # pure AST
        >>> f.a.body[0].args.args[0].annotation = Name('float')
        >>> f.a.body[0].decorator_list[0] = FST('call_decorator(1, 2, 3)').a
        >>> f.a.body[1].name = 'last_function'  # can change non-AST
        >>> f.a.body[1].body[0] = f.a.body[0].body[0]  # AST from same FST tree
        >>> other = FST('def first_function(a, b): return a * b  # yay!')
        >>> f.a.body.insert(0, other.a)  # AST from other FST tree

        >>> f = f.reconcile(pep8space=1)

        >>> print('\n'.join(l or '.' for l in f.lines))  # print this way for doctest
        def first_function(a, b): return a * b  # yay!
        .
        @call_decorator(1, 2, 3)  # something
        def function(a: float, b=2)->float:  # blah
            return a+b  # return this
        .
        def last_function(a, b):
            return a+b  # return this

        >>> f.mark()
        <Module ROOT 0,0..7,29>

        >>> body = f.a.body[1].body
        >>> f.a.body[1] = FST('def f(): pass').a
        >>> f.a.body[1].body = body

        >>> f = f.reconcile(pep8space=1)

        >>> print('\n'.join(l or '.' for l in f.lines))
        def first_function(a, b): return a * b  # yay!
        .
        def f():
            return a+b  # return this
        .
        def last_function(a, b):
            return a+b  # return this
        """

        check_options(options)

        if any((bad := o) in (
            'raw',
            'trivia',
            'coerce',
            'docstr',
            'pars',
            'pars_walrus',
            'pars_arglike',
            'norm',
            'norm_self',
            'norm_get',
        ) for o in options):
            raise ValueError(f'option {bad!r} not allowed in reconcile()')

        if not self.is_root:
            raise ValueError('can only reconcile root nodes')

        if not (mark := self._cache.get('mark')):
            raise RuntimeError('not marked or modification detected after mark, irreconcilable')

        reconcile = Reconcile(
            self,
            mark,
            options,
            trivia_ast_put=trivia_ast_put,
            trivia_fst_put=trivia_fst_put,
            trivia_fst_get=trivia_fst_get,
        )

        with FST.options(
            raw = False,
            trivia = False,
            coerce = False,
            docstr = True,
            pars = 'auto',
            pars_walrus = True,
            pars_arglike = True,
            norm = False,
            norm_self = False,
            norm_get = False,
        ):
            reconcile.recurse_node(self.a)

        if cleanup:
            self._touch()  # delete marked copy
            self._unmake_fst_tree()  # clean up as best we can

        return reconcile.out

    # ------------------------------------------------------------------------------------------------------------------
    # Edit

    def __getitem__(self, idx: int | builtins.slice) -> fstview | FST | builtins.str | None:
        r"""Get a single item or a slice view from the default field of `self`. This is just an access, not a cut or a
        copy, so if you want a copy you must explicitly do `.copy()` on the returned value.

        Same as `self.default_field[idx]`.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when dealing with
        return values which may be `None` or may not be `FST` nodes.

        **Parameters:**
        - `idx`: The index or `builtins.slice` where to get the element(s) from.

        **Returns:**
        - `fstview | FST | str | None`: Either a single `FST` node if accessing a single item or a new `fstview` view
            according to the slice passed. `builtins.str` can also be returned from a view of `Global.names` or `None`
            from a `Dict.keys`.

        **Examples:**

        >>> FST('[0, 1, 2, 3]')[1].src
        '1'

        >>> FST('[0, 1, 2, 3]')[:3]
        <<List ROOT 0,0..0,12>.elts[:3] [<Constant 0,1..0,2>, <Constant 0,4..0,5>, <Constant 0,7..0,8>]>

        >>> FST('[0, 1, 2, 3]')[:3].copy().src
        '[0, 1, 2]'

        >>> FST('[0, 1, 2, 3]')[-3:]
        <<List ROOT 0,0..0,12>.elts[1:4] [<Constant 0,4..0,5>, <Constant 0,7..0,8>, <Constant 0,10..0,11>]>

        >>> FST('def fun(): pass\nclass cls: pass\nvar = val').body[1]
        <ClassDef 1,0..1,15>

        >>> FST('global a, b, c').names
        <<Global ROOT 0,0..0,14>.names ['a', 'b', 'c']>

        >>> FST('global a, b, c')[1]
        'b'

        @public
        """

        field, _ = fixup_field_body(self.a, None, True)

        return getattr(self, field)[idx]

    def __setitem__(self, idx: int | builtins.slice, code: Code | None) -> None:
        """Set a single item or a slice view in the default field of `self`.

        Same as `self.default_field[idx] = code`.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when assigning
        values.

        **Parameters:**
        - `idx`: The index or `builtins.slice` where to put the element(s).

        **Examples:**

        >>> from fst import FST

        >>> (f := FST('[0, 1, 2, 3]'))[1] = '4'; f.src
        '[0, 4, 2, 3]'

        >>> (f := FST('[0, 1, 2, 3]'))[:3] = '5'; f.src
        '[5, 3]'

        >>> (f := FST('[0, 1, 2, 3]'))[:3] = '[5]'; f.src
        '[[5], 3]'

        >>> (f := FST('[0, 1, 2, 3]'))[:3] = '5,'; f.src
        '[5, 3]'

        >>> (f := FST('[0, 1, 2, 3]'))[-3:] = '6'; f.src
        '[0, 6]'

        >>> (f := FST('[0, 1, 2, 3]'))[-3:] = '[6]'; f.src
        '[0, [6]]'

        >>> (f := FST('[0, 1, 2, 3]'))[:] = '7, 8'; f.src
        '[7, 8]'

        >>> (f := FST('[0, 1, 2, 3]'))[:] = '[7, 8]'; f.src
        '[[7, 8]]'

        >>> f = FST('[0, 1, 2, 3]')
        >>> f[2:2] = f[1:3].copy()
        >>> f.src
        '[0, 1, 1, 2, 2, 3]'

        @public
        """

        field, _ = fixup_field_body(self.a, None, True)

        getattr(self, field)[idx] = code

    def __delitem__(self, idx: int | builtins.slice) -> None:
        """Delete a single item or a slice from default field of `self`.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when assigning
        values.

        **Parameters:**
        - `idx`: The index or `builtins.slice` to delete.

        **Examples:**

        >>> from fst import FST

        >>> del (f := FST('[0, 1, 2, 3]'))[1]; f.src
        '[0, 2, 3]'

        >>> del (f := FST('[0, 1, 2, 3]'))[:3]; f.src
        '[3]'

        >>> del (f := FST('[0, 1, 2, 3]'))[-3:]; f.src
        '[0]'

        >>> del (f := FST('[0, 1, 2, 3]'))[:]; f.src
        '[]'

        @public
        """

        field, _ = fixup_field_body(self.a, None, True)

        del getattr(self, field)[idx]

    def own_lines(
        self, whole: bool = True, *, docstr: bool | Literal['strict'] | None = None
    ) -> list[builtins.str]:
        r"""Lines of this node copied out of the tree and dedented as if the node were copied out. Unlike the `.lines`
        property these will not contain parts of other nodes.

        This function is a faster way to get this if you just want the source over `self.copy().lines`. The intermediate
        parameters for getting this are also cached (not the lines themselves), so it is not so expensive to call this
        repeatedly.

        A valid list of strings is always returned, even for nodes which can never have source like `Load`, etc... The
        lines list returned is always a copy so safe to modify.

        **Caveat:** There is an actual qualitative difference between this and `self.copy().lines`, though it is usually
        inconsequential. The copy operation may carry out some reformatting to make sure the node is presentable at root
        level (mostly adding parentheses), this function does not do that. It will however convert an `elif` to an `if`.
        The copy also does trivia, we do not here (yet).

        **WARNING!** With the exception of the `elif` fix, you get just the text that is there so you will get
        unparsable source if you get for example a string `Constant` from the `values` field of a `JoinedStr`, or a
        `format_spec`.

        **Parameters:**
        - `whole`: If at root this determines whether to return the whole source or just the location of the node
            (which may not be the whole source).
        - `docstr`: How to treat multiline string docstring lines.
            - `False`: Don't dedent any.
            - `True`: Dedent all `Expr` multiline strings (as they serve no coding purpose).
            - `'strict'`: Only dedent `Expr` multiline strings in standard docstring locations.
            - `None`: Use the global default for the `docstr` option.

        **Returns:**
        - `list[str]`: List of lines belonging to this node dedented or list with one empty string if node does not have
            location to get source from (unless at root and `whole=True`, in which case the whole source is returned).

        **Examples:**

        >>> f = FST('''
        ... def func():
        ...     return ('not_self', [
        ...         'self1',
        ...         'self2',
        ...     ], 'other_not_self',
        ...     'outside_lines')
        ... '''.strip())

        Notice the indentation comes with it as well as parts of other nodes.

        >>> for l in f.body[0].value.elts[1].lines:  # the list node in the return value
        ...     print(repr(l))
        "    return ('not_self', ["
        "        'self1',"
        "        'self2',"
        "    ], 'other_not_self',"

        And here it is all cleaned up.

        >>> for l in f.body[0].value.elts[1].own_lines():
        ...     print(repr(l))
        '['
        "    'self1',"
        "    'self2',"
        ']'
        """

        if (is_root := not self.parent) and whole:
            return self._lines[:]

        if not (loc := self.loc):
            return [s] if (s := OPCLS2STR.get(self.a.__class__, None)) else ['']  # for boolop or expr_context

        if is_root:
            return self._get_src(loc.ln, loc.col, loc.end_ln, loc.end_col, True)  # note, elif cannot exist at root so we don't check for it

        if docstr is None:
            docstr = FST.get_option('docstr')

        key = 'ownlS' if docstr == 'strict' else 'ownlT' if docstr else 'ownlF'

        if cached := self._cache.get(key):  # cached indent and indentable lines
            dedent, lns = cached

        else:
            dedent = self._get_block_indent()
            lns = tuple(self._get_indentable_lns(1, docstr=docstr))

            self._cache[key] = (dedent, lns)

        # params set up, now do it

        bound_ln, bound_col, bound_end_ln, bound_end_col = self.bloc

        lines = self._get_src(bound_ln, bound_col, bound_end_ln, bound_end_col, True)

        if dedent and lns:
            ldedent = len(dedent)
            bound_end_ln -= bound_ln

            for ln in lns:
                ln -= bound_ln

                if (0 <= ln <= bound_end_ln) and (l := lines[ln]):
                    if (l.startswith(dedent)
                        or (lempty_start := re_empty_line_start.match(l, 0, 0x7fffffffffffffff).end()) >= ldedent
                    ):  # only full dedent non-empty lines which have dedent length leading space
                        lines[ln] = l[ldedent:]
                    else:  # inconsistent dedentation
                        lines[ln] = l[lempty_start:]

        if self.is_elif():
            assert lines[0].startswith('elif')

            lines[0] = lines[0][2:]  # it will always be right at the beginning

        return lines

    def own_src(
        self, whole: bool = True, *, docstr: bool | Literal['strict'] | None = None
    ) -> builtins.str:
        """Source of this node as a string copied out of the tree and dedented as if the node were copied out.

        This function is a faster way to get this if you just want the source over `self.copy().src`. The intermediate
        parameters for getting this are also cached (not the source itself), so it is not so expensive to call this
        repeatedly.

        Here is a rough performance comparison for scale when using the three methods of getting source of the
        `FST.mark()` function from this class (py 3.14).
        - `.src`: 532 nanoseconds
        - `.copy().src`: 140 microseconds
        - `.own_src()`: 7.96 microseconds  - intermediate parameters not in cache
        - `.own_src()`: 2.43 microseconds  - intermediate parameters in cache (second+ time)

        A string is always returned, even for nodes which can never have source like `Load`, etc...

        **Note:** The first line is always completely dedented.

        **Caveat:** There is an actual qualitative difference between this and `self.copy().src`, though it is usually
        inconsequential. The copy operation may carry out some reformatting to make sure the node is presentable at root
        level (mostly adding parentheses), this function does not do that. It will however convert an `elif` to an `if`.
        The copy also does trivia, we do not here (yet).

        **WARNING!** With the exception of the `elif` fix, you get just the text that is there so you will get
        unparsable source if you get for example a string `Constant` from the `values` field of a `JoinedStr`, or a
        `format_spec`.

        **Parameters:**
        - `whole`: If at root this determines whether to return the whole source or just the location of the node
            (which may not be the whole source).
        - `docstr`: How to treat multiline string docstring lines.
            - `False`: Don't dedent any.
            - `True`: Dedent all `Expr` multiline strings (as they serve no coding purpose).
            - `'strict'`: Only dedent `Expr` multiline strings in standard docstring locations.
            - `None`: Use the global default for the `docstr` option.

        **Returns:**
        - `str`: The source of this node dedented as a string or empty string if node does not have location to get
        source from (unless at root and `whole=True`, in which case the whole source is returned).

        **Examples:**

        >>> f = FST('''
        ... def func():
        ...     return ('not_self', [
        ...         'self1',
        ...         'self2',
        ...     ], 'other_not_self',
        ...     'outside_lines')
        ... '''.strip())

        Notice the indentation comes with it, but not parts of other nodes like for `.lines`. The first line for `.src`
        is also completely dedented just like `.own_src()`.

        >>> print(f.body[0].value.elts[1].src)  # the list node in the return value
        [
                'self1',
                'self2',
            ]

        And here it is all cleaned up.

        >>> print(f.body[0].value.elts[1].own_src())
        [
            'self1',
            'self2',
        ]
        """

        return '\n'.join(self.own_lines(whole, docstr=docstr))

    def ast_src(self) -> str:
        """Unparse the `AST` tree of self discarding all formatting. The unparse will correctly handle our own SPECIAL
        SLICE nodes and does a few other minor tweaks like removing parentheses from top-level `Tuple` which contains
        `Slice` nodes.

        **Returns:**
        - `str`: Unparsed source with all formatting lost.

        **Examples:**
        >>> f = FST('if a: b=c  # comment')

        >>> print(f.src)
        if a: b=c  # comment

        >>> print(f.ast_src())
        if a:
            b = c

        >>> f = FST('array[start : stop : step, other_start : other_stop]')

        >>> print(ast.unparse(f.slice.a))  # invalid in any universe
        (start:stop:step, other_start:other_stop)

        >>> print(f.slice.ast_src())
        start:stop:step, other_start:other_stop
        """

        return parsex.unparse(self.a)

    def copy_ast(self) -> AST:
        """Copy the `AST` node tree of this `FST` node, not including any `FST` stuff. Use when you just want a copy of
        the `AST` tree from this point down.

        Needless to say since this just returns an `AST` all formatting is lost, except that the `AST` nodes will have
        the same `lineno`, `col_offset`, `end_lineno` and `end_col_offset` values as they had in the `FST` tree.

        **Returns:**
        - `AST`: Copied `AST` tree from this point down.

        **Examples:**

        >>> a = FST('[0, 1, 2, 3]').copy_ast()

        >>> print(type(a))
        <class 'ast.List'>

        >>> print(dump(a))
        List(elts=[Constant(value=0), Constant(value=1), Constant(value=2), Constant(value=3)], ctx=Load())
        """

        return copy_ast(self.a)

    def copy(self, whole: bool = True, **options) -> FST:
        r"""Copy this node to a new top-level tree, dedenting and fixing as necessary. If copying root node then an
        identical copy is made and no fixes / modifications are applied unless `whole=False`.

        **Parameters:**
        - `whole`: This only has meaning when copying a root node, otherwise all `options` rules apply.
            - `True`: Copies the entire tree and source without any modifications (including leading and trailing source
                which is not part of the node), no `options` are honored.
            - `False`: For statementlike nodes will honor the `trivia` option and only copy allowed trivia source along
                with the node. For expressions and patterns the various `pars` options will be honored and any
                parentesization which may happen on a normal copy will be carried out as well. For all other node types
                that have a location will trim away any source that falls outside of the node and only copy the node and
                its own source.
        - `options`: See `options()`.

        **Returns:**
        - `FST`: Copied node.

        **Examples:**

        >>> FST('[a(), b(), c(), d()]').elts[1].copy().src
        'b()'

        Copies at root are special, default copies everything.

        >>> f = FST('''
        ... # pre
        ... call()  # tail
        ... # post
        ... '''.strip(), 'expr')

        >>> print('\n'.join(repr(l) for l in f.copy().lines))
        '# pre'
        'call()  # tail'
        '# post'

        >>> print('\n'.join(repr(l) for l in f.copy(whole=False).lines))
        'call()'

        A module is always copied whole.

        >>> f = FST('''
        ... # pre
        ... call()  # tail
        ... # post
        ... '''.strip(), 'Module')

        >>> print('\n'.join(repr(l) for l in f.copy(whole=False).lines))
        '# pre'
        'call()  # tail'
        '# post'
        """

        check_options(options)

        if parent := self.parent:
            return parent._get_one((pf := self.pfield).idx, pf.name, False, options)

        lines = self._lines
        ast = self.a

        if whole or not (loc := (self.pars() if FST.get_option('pars', options) is True else self.bloc)):
            return FST(copy_ast(ast), lines[:], None, from_=self, lcopy=False)

        if ast.__class__ not in ASTS_LEAF_STMTLIKE:
            ret, _ = self._make_fst_and_dedent('', copy_ast(self.a), loc, docstr=False)

            ret._fix_copy(options)

            return ret

        # we do all this so that we can apply trivia rules at root, otherwise we could have just done the above for everything

        tmpf = FST(Module(body=[], type_ignores=[]), lines, None, from_=self, lcopy=False)

        tmpf._set_field([ast], 'body', True, False)  # yeah, hacky

        try:
            ret = tmpf._get_one(0, 'body', False, options)

            tmpf._unmake_fst_parents(True)  # unmake the tmpf, can still use as `from_` below since the unmake just breaks .f/.a links

        finally:  # in case of error try to remake self anyway to leave in valid state
            FST(ast, lines, None, from_=tmpf, lcopy=False, tmake=False)  # recreate self as root node

        return ret

    def cut(self, **options) -> FST:
        """Cut out this node to a new top-level tree (if possible), dedenting and fixing as necessary. Cannot cut root
        node.

        **Parameters:**
        - `options`: See `options()`.

        **Returns:**
        - `FST`: Cut node.

        **Examples:**

        >>> (f := FST('[0, 1, 2, 3]')).elts[1].cut().src
        '1'

        >>> f.src
        '[0, 2, 3]'
        """

        check_options(options)

        if parent := self.parent:
            return parent._get_one((pf := self.pfield).idx, pf.name, True, options)

        raise ValueError('cannot cut root node')

    def replace(self, code: Code | None, one: bool | None = True, **options) -> FST | None:  # -> replaced self or None if deleted
        """Replace or delete (if `code=None`, if possible) this node. Returns the new node for `self`, not the old
        replaced node, or `None` if was deleted or raw replaced and the old node disappeared. Cannot delete root node.
        **CAN** replace root node, in which case `self` remains the same but the top-level `AST` and source change.

        **Note:** If replacing root node, the `trivia` option is not honored.

        **WARNING!** If passing an `FST` then this is not guaranteed to become the new node (on purpose). If you wish to
        continue using the `FST` node you just replaced then make sure to use the one returned from this function. The
        `AST` node will also not be identical if coercion happened.

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to put at this location. `None` to delete this node.
        - `one`: Default `True` means replace with a single element. If `False` and field allows it then can replace
            single element with a slice.
        - `options`: See `options()`.
            - `to`: Special option which only applies replacing in `raw` mode (either through `True` or `'auto'`).
                Instead of replacing just this node, will replace the entire span from this node to the node specified
                in `to` with the `code` passed.

        **Returns:**
        - `FST` or `None`: Returns the new node if successfully replaced or `None` if deleted or raw replace and
            corresponding new node could not be found.

        **Examples:**

        >>> FST('[0, 1, 2, 3]').elts[1].replace('4').root.src
        '[0, 4, 2, 3]'

        >>> f = FST('def f(a, /, b, *c, **d) -> int: pass')

        >>> f.args.posonlyargs[0].replace(')', to=f.returns, raw=True)  # raw reparse
        <arguments 0,6..0,6>

        >>> f.src
        'def f(): pass'
        """

        check_options(options)

        if parent := self.parent:
            field, idx = pfield = self.pfield

            if one:
                return parent._put_one(code, idx, field, options)

            if idx is None:
                raise ValueError(f"cannot replace {parent.a.__class__.__name__}.{field} with slice")

            parent = parent._put_slice(code, idx, idx + 1, field, None if one is None else False, options)

            if code is None or not parent:
                return None

            if a := pfield.get_default(parent.a, None):  # may not be there due to removal of last element or raw reparsing of weird *(^$
                return a.f

            return None

        if code is None:
            raise ValueError('cannot delete root node')
        if options.get('to'):
            raise ValueError("cannot replace root node with 'to' option")

        with self._modifying():
            code = code_as_all(code, options, self.parse_params)
            self._lines = code._lines

            self._set_ast(code.a, True)

        return self

    def remove(self, **options) -> None:
        """Delete this node if possible, equivalent to `replace(None, ...)`. Cannot delete root node.

        **Parameters:**
        - `options`: See `options()`.

        **Examples:**

        >>> (f := FST('[0, 1, 2, 3]')).elts[1].remove()
        >>> f.src
        '[0, 2, 3]'
        """

        check_options(options)

        if not (parent := self.parent):
            raise ValueError('cannot delete root node')

        parent._put_one(None, (pf := self.pfield).idx, pf.name, options)

    def insert(
        self,
        code: Code,
        idx: int | Literal['end'] = 0,
        field: builtins.str | None = None,
        *,
        one: bool | None = True,
        **options
    ) -> FST:  # -> self or None if deleted due to raw reparse
        """Insert into `field` of `self` at a specific index. Default field if `field=None`. This is a convenience
        function for `self.put_slice()`.

        Same as `self.field.insert()`.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to insert.
        - `idx`: Index to insert before. Can be `'end'` to indicate add at end of slice.
        - `field`: Field to operate on or the default field if is `None`. Must be a list field.
        - `one`: If `True` then will insert `code` as a single item. Otherwise `False` will attempt a slice insertion
            (type must be compatible).
        - `options`: See `fst.fst.FST.options()`.

        **Note:** The `field` value can optionally be passed positionally in the `idx` parameter. If passed in `idx`
        `idx` is assumed to be 0.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').insert('4, 5', 1).src
        '[0, (4, 5), 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').insert('(4, 5)', 1).src
        '[0, (4, 5), 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').insert('4, 5', 'end', one=False).src
        '[0, 1, 2, 3, 4, 5]'

        >>> FST('[0, 1, 2, 3]').insert('(4, 5)', 'end', one=False).src
        '[0, 1, 2, 3, (4, 5)]'

        >>> # same as 'end' but 'end' is always 'end'
        >>> FST('[0, 1, 2, 3]').insert('4, 5', 4, one=False).src
        '[0, 1, 2, 3, 4, 5]'

        >>> FST('[0, 1, 2, 3]').insert('(4, 5)', 4, one=False).src
        '[0, 1, 2, 3, (4, 5)]'

        >>> FST('[0, 1, 2, 3]')[1:3].insert('*star').base.src
        '[0, *star, 1, 2, 3]'
        """

        check_options(options)

        idx, _, field = _swizzle_getput_params(idx, field, field, 0, None)
        field, _ = fixup_field_body(self.a, field, True)

        return self._put_slice(code, idx, idx, field, one, options)

    def append(self, code: Code, field: builtins.str | None = None, **options) -> FST:  # -> self or None if deleted due to raw reparse
        """Append `code` as a single element to `field` of `self`. Default field if `field=None`. This is a convenience
        function for `self.put_slice()`.

        Same as `self.field.append()`.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to append.
        - `field`: Field to operate on or the default field if is `None`. Must be a list field.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').append('(4, 5)').src
        '[0, 1, 2, 3, (4, 5)]'

        >>> FST('[0, 1, 2, 3]')[1:3].append('*star').base.src
        '[0, 1, 2, *star, 3]'
        """

        check_options(options)

        field, _ = fixup_field_body(self.a, field, True)

        return self._put_slice(code, 'end', 'end', field, True, options)

    def extend(
        self, code: Code, field: builtins.str | None = None, one: Literal[False] | None = False, **options
    ) -> FST:  # -> self or None if deleted due to raw reparse
        """Extend `field` of `self` with the slice in `code` (type must be compatible). Default field if `field=None`.
        This is a convenience function for `self.put_slice()`.

        Same as `self.field.extend()`.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` slice to extend.
        - `field`: Field to operate on or the default field if is `None`. Must be a list field.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').extend('4, 5').src
        '[0, 1, 2, 3, 4, 5]'

        >>> FST('[0, 1, 2, 3]').extend('(4, 5)').src
        '[0, 1, 2, 3, (4, 5)]'

        >>> FST('[0, 1, 2, 3]')[1:3].extend('4, 5').base.src
        '[0, 1, 2, 4, 5, 3]'

        >>> FST('[0, 1, 2, 3]')[1:3].extend('(4, 5)').base.src
        '[0, 1, 2, (4, 5), 3]'
        """

        check_options(options)

        field, _ = fixup_field_body(self.a, field, True)

        return self._put_slice(code, 'end', 'end', field, None if one is None else False, options)

    def prepend(self, code: Code, field: builtins.str | None = None, **options) -> FST:  # -> self or None if deleted due to raw reparse
        """prepend `code` as a single element to the beginning of `field` of `self`. Default field if `field=None`. This
        is a convenience function for `self.put_slice()`.

        Same as `self.field.prepend()`.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to preappend.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').prepend('(4, 5)').src
        '[(4, 5), 0, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]')[1:3].prepend('*star').base.src
        '[0, *star, 1, 2, 3]'
        """

        check_options(options)

        field, _ = fixup_field_body(self.a, field, True)

        return self._put_slice(code, 0, 0, field, True, options)

    def prextend(
        self, code: Code, field: builtins.str | None = None, one: Literal[False] | None = False, **options
    ) -> fstview:  # -> self or None if deleted due to raw reparse
        """Extend the beginning of the `field` of `self` with the slice in `code` (type must be compatible). Default
        field if `field=None`. This is a convenience function for `self.put_slice()`.

        Same as `self.field.prextend()`.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to extend at the start.
        - `field`: Field to operate on or the default field if is `None`. Must be a list field.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').prextend('4, 5').src
        '[4, 5, 0, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').prextend('(4, 5)').src
        '[(4, 5), 0, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]')[1:3].prextend('4, 5').base.src
        '[0, 4, 5, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]')[1:3].prextend('(4, 5)').base.src
        '[0, (4, 5), 1, 2, 3]'
        """

        check_options(options)

        field, _ = fixup_field_body(self.a, field, True)

        return self._put_slice(code, 0, 0, field, None if one is None else False, options)

    def get(
        self,
        idx: int | Literal['end'] | None = None,
        stop: int | Literal['end'] | None = None,
        field: builtins.str | None = None,
        cut: bool = False,
        **options,
    ) -> FST | None | builtins.str | constant:
        r"""Copy or cut an individual child node or a slice of child nodes from `self` if possible. This function can do
        everything that `get_slice()` can do.

        **Parameters:**
        - `idx`: The index of the child node to get if the field being gotten from contains multiple elements or the
            start of the slice to get if getting a slice (by specifying `stop`). If the field being gotten from is
            an individual element then this must be `None`.
        - `stop`: The end index (exclusive) of the child node to get if getting a slice from a field that contains
            multiple elements. This should be one past the last element to get (like python list indexing). If the field
            being gotten from is an individual element then this must be `None`.
        - `field`: The name of the field to get the element(s) from, which can be an individual element like a `value`
            or a list like `body`. If this is `None` then the default field for the node type is used. Most node types
            have a common-sense default field, e.g. `body` for all block statements, `value` for things like `Return`
            and `Yield`. `Dict`, `MatchMapping` and `Compare` nodes have special handling for a `None` field (which
            defaults to the `_all` virtual field for them).
        - `cut`: Whether to cut out the child node (if possible) or not (just copy).
        - `options`: See `options()`.

        **Note:** The `field` value can optionally be passed positionally in either the `idx` or `stop` parameter. If
        passed in `idx` a value of `None` is used for `idx`, which will select either just the element from a single
        element field or the entire slice from a list field. If passed in `stop` then the `idx` value is present and
        `stop` is assumed to be `None`.

        **Returns:**
        - `FST`: When getting an actual node (most situations).
        - `str`: When getting an identifier, like from `Name.id`.
        - `constant`: When getting a constant (`fst.astutil.constant`), like from `Constant.value` or
            `MatchSingleton.value`.

        **Examples:**

        >>> FST('[0, 1, 2, 3]').get(1).src
        '1'

        >>> (f := FST('[0, 1, 2, 3]')).get(1, 3).src
        '[1, 2]'
        >>> f.src
        '[0, 1, 2, 3]'

        >>> (f := FST('[0, 1, 2, 3]')).get(1, 3, cut=True).src
        '[1, 2]'
        >>> f.src
        '[0, 3]'

        >>> FST('[0, 1, 2, 3]').get(0, 3).src
        '[0, 1, 2]'

        >>> FST('[0, 1, 2, 3]').get(-3, 'end').src
        '[1, 2, 3]'

        >>> FST('if 1: i = 1\nelse: j = 2').get(0).src
        'i = 1'

        >>> FST('if 1: i = 1\nelse: j = 2').get('orelse').src
        'j = 2'

        >>> FST('if 1: i = 1\nelse: j = 2; k = 3').get(1, 'orelse').src
        'k = 3'

        >>> FST('if 1: i = 1\nelse: j = 2; k = 3; l = 4; m = 5').get(1, 3, 'orelse').src
        'k = 3; l = 4'

        >>> FST('return 1').get().src  # default field is 'value'
        '1'

        >>> FST('[0, 1, 2, 3]').get().src  # 'elts' slice copy is made
        '[0, 1, 2, 3]'
        """

        check_options(options)

        ast = self.a
        idx, stop, field = _swizzle_getput_params(idx, stop, field, None, None)
        field, body = fixup_field_body(ast, field, False)

        if isinstance(body, list):
            if stop is not None:
                return self._get_slice(idx or 0, stop, field, cut, options)
            if idx is None:
                return self._get_slice(0, 'end', field, cut, options)
            if idx == 'end':
                return self._get_slice('end', 'end', field, cut, options)

        elif stop is not None or idx is not None:
            raise IndexError(f'{ast.__class__.__name__}.{field} does not take an index')

        return self._get_one(idx, field, cut, options)

    def put(
        self,
        code: Code | builtins.str | constant | None,
        idx: int | Literal['end'] | None = None,
        stop: int | Literal['end'] | None = None,
        field: builtins.str | None = None,
        one: bool | None = True,
        **options,
    ) -> FST | None:  # -> self or None if deleted due to raw reparse
        r"""Put an individual node or a slice of nodes to `self` if possible. The node is passed as an existing
        top-level `FST`, `AST`, string or list of string lines. If passed as an `FST` then it should be considered
        "consumed" after this function returns and should not be accessed again, even on failure. If passed as an `AST`
        then it is copied and can be reused after this function returns. This is the most general form of node put
        function and can do everything that the other node put functions can.

        **WARNING!** The original `self` node may be invalidated during the operation if using raw mode (either
        `raw=True` or if it happened as a fallback from `raw='auto'`). If there is a possibility of this happening then
        make sure to use the new `self` returned from this function, otherwise if no raw happens then `self` remains
        unchanged and usable.

        **Parameters:**
        - `code`: The node to put as an `FST` (must be root node), `AST`, a string or list of line strings. If putting
            to an identifier field then this should be a string and it will be taken literally (no parsing). If putting
            to a constant like `MatchSingleton.value` or `Constant.value` then this should be an appropriate primitive
            constant value.
        - `idx`: The index of the field node to put to if the field being put to contains multiple elements or the start
            of the slice to put if putting a slice (by specifying `stop`). If the field being put to is an individual
            element then this must be `None`.
        - `stop`: The end index (exclusive) of the field node to put to if putting a slice to a field that contains
            multiple elements. This should be one past the last element to put (like python list indexing). If the field
            being put to is an individual element then this must be `None`.
        - `field`: The name of the field to put the element(s) to, which can be an individual element like a `value` or
            a list like `body`. If this is `None` then the default field for the node type is used. Most node types have
            a common-sense default field, e.g. `body` for all block statements, `value` for things like `Return` and
            `Yield`. `Dict`, `MatchMapping` and `Compare` nodes have special handling for a `None` field (which defaults
            to the `_all` virtual field for them).
        - `one`: Only has meaning if putting a slice and in this case `True` specifies that the source should be put as
            a single element to the range specified even if it is a valid slice. `False` indicates that a slice value
            should be put as slice and not an individual element, which must in this case be a compatible slice type.
        - `options`: See `options()`.
            - `to`: Special option which only applies when putting a single element in `raw` mode (either through `True`
                or `'auto'`). Instead of replacing just the target node, will replace the entire span from the target
                node to the node specified in `to` with the `code` passed.

        **Note:** The `field` value can optionally be passed positionally in either the `idx` or `stop` parameter. If
        passed in `idx` a value of `None` is used for `idx`, which will select either just the element from a single
        element field or the entire slice from a list field. If passed in `stop` then the `idx` value is present and
        `stop` is assumed to be `None`.

        **Returns:**
        - `self` or `None` if a raw put was done and corresponding new node could not be found.

        **Examples:**

        >>> FST('[0, 1, 2, 3]').put('x', 1).src
        '[0, x, 2, 3]'

        >>> FST('[0, 1, 2, 3]').put('x, y', 1, 3).src
        '[0, (x, y), 3]'

        >>> FST('[0, 1, 2, 3]').put('x, y', 1, 3, one=False).src
        '[0, x, y, 3]'

        >>> FST('[0, 1, 2, 3]').put('x, y', 0, 3).src
        '[(x, y), 3]'

        >>> FST('[0, 1, 2, 3]').put('x, y', -3, 'end', one=False).src
        '[0, x, y]'

        >>> FST('[0, 1]').put('x, y', 'end').src
        '[0, 1, (x, y)]'

        >>> FST('[0, 1]').put('x, y', 'end', one=False).src
        '[0, 1, x, y]'

        >>> print(FST('if 1: i = 1\nelse: j = 2').put('z = -1', 0).src)
        if 1:
            z = -1
        else: j = 2

        >>> print(FST('if 1: i = 1\nelse: j = 2').put('z = -1', 0, 'orelse').src)
        if 1: i = 1
        else:
            z = -1

        >>> print(FST('if 1: i = 1\nelse: j = 2')
        ...       .put('z = -1\ny = -2\nx = -3', 'orelse', one=False).src)
        if 1: i = 1
        else:
            z = -1
            y = -2
            x = -3

        >>> f = FST('if 1: i = 1\nelse: j = 2')
        >>> print(f.put('z = -1', 0, raw=True, to=f.orelse[-1]).root.src)
        if 1: z = -1
        """

        check_options(options)

        ast = self.a
        idx, stop, field = _swizzle_getput_params(idx, stop, field, None, None)
        field, body = fixup_field_body(ast, field, False)

        if isinstance(body, list):
            if stop is not None:
                return self._put_slice(code, idx or 0, stop, field, one, options)
            if idx is None:
                return self._put_slice(code, 0, 'end', field, one, options)
            if idx == 'end':
                return self._put_slice(code, 'end', 'end', field, one, options)

        elif stop is not None or idx is not None:
            raise IndexError(f'{ast.__class__.__name__}.{field} does not take an index')

        if not one:
            raise ValueError("cannot use 'one=False' in non-slice put()")

        return self._put_one(code, idx, field, options, False)

    def get_slice(
        self,
        start: int | Literal['end'] = 0,
        stop: int | Literal['end'] = 'end',
        field: builtins.str | None = None,
        cut: bool = False,
        **options,
    ) -> FST:
        r"""Copy or cut a slice of child nodes from `self` if possible.

        **Parameters:**
        - `start`: The start index of the slice to get. You can use `'end'` here but you will just wind up getting an
            empty slice.
        - `stop`: The end index (exclusive) of the slice to get. This should be one past the last element to get (like
            python list indexing). If this is `'end'` then it indicates a slice operation to the end of the list (like
            python `a[start:]`).
        - `field`: The name of the field to get the elements from, which can be an individual element like a `value` or
            a list like `body`. If this is `None` then the default field for the node type is used. Most node types
            have a common-sense default field, e.g. `body` for all block statements, `elts` for things like `List` and
            `Tuple`. `Dict`, `MatchMapping` and `Compare` nodes have special handling for a `None` field (which defaults
            to the `_all` virtual field for them).
        - `cut`: Whether to cut out the slice or not (just copy).
        - `options`: See `options()`.

        **Note:** The `field` value can optionally be passed positionally in either the `start` or `stop` parameter. If
        passed in `start` then the range is assumed to be the entire field. If passed in `stop` then the `start` value
        is present and `stop` is assumed to be `'end'`.

        **Returns:**
        - `FST`: Slice node of nodes gotten.

        **Examples:**

        >>> FST('[0, 1, 2, 3]').get_slice(1).src
        '[1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').get_slice(0, -1).src
        '[0, 1, 2]'

        >>> (f := FST('[0, 1, 2, 3]')).get_slice(1, 3, cut=True).src
        '[1, 2]'
        >>> f.src
        '[0, 3]'

        >>> f = FST('if 1: i = 1\nelse: j = 2; k = 3; l = 4; m = 5')
        >>> print(f.src)
        if 1: i = 1
        else: j = 2; k = 3; l = 4; m = 5

        >>> print(f.get_slice(1, 3, 'orelse', cut=True).src)
        k = 3; l = 4

        >>> print(f.src)
        if 1: i = 1
        else: j = 2; m = 5
        """

        check_options(options)

        start, stop, field = _swizzle_getput_params(start, stop, field, 0, 'end')
        field, _ = fixup_field_body(self.a, field, True)

        return self._get_slice(start, stop, field, cut, options)

    def put_slice(
        self,
        code: Code | None,
        start: int | Literal['end'] = 0,
        stop: int | Literal['end'] = 'end',
        field: builtins.str | None = None,
        one: bool | None = False,
        **options,
    ) -> FST | None:  # -> self or None if deleted due to raw reparse
        r"""Put a slice of nodes to `self` if possible.  The node is passed as an existing top-level `FST`, `AST`, string
        or list of string lines. If passed as an `FST` then it should be considered "consumed" after this function
        returns and is no longer valid, even on failure. `AST` is copied.

        **WARNING!** The original `self` node may be invalidated during the operation if using raw mode (either
        `raw=True` or if it happened as a fallback from `raw='auto'`). If there is a possibility of this happening then
        make sure to use the new `self` returned from this function, otherwise if no raw happens then `self` remains
        unchanged and usable.

        **Parameters:**
        - `code`: The slice to put as an `FST` (must be root node), `AST`, a string or list of line strings.
        - `start`: The start index of the slice to put. `'end'` here allows extending at the end of the field.
        - `stop`: The end index (exclusive) of the slice. This should be one past the last element to put (like python
            list indexing). If this is `'end'` then it indicates a slice operation to the end of the list (like python
            `a[start:]`).
        - `field`: The name of the field to put the elements to. If this is `None` then the default field for the node
            type is used. Most node types have a common-sense default field, e.g. `body` for all block statements,
            `elts` for things like `List` and `Tuple`. `Dict`, `MatchMapping` and `Compare` nodes have special handling
            for a `None` field (which defaults to the `_all` virtual field for them).
        - `one`: `True` specifies that the source should be put as a single element to the range specified even if it
            is a valid slice. `False` indicates a true slice operation replacing the range with the slice passed, which
            must in this case be a compatible slice type.
        - `options`: See `options()`.

        **Note:** The `field` value can optionally be passed positionally in either the `start` or `stop` parameter. If
        passed in `start` then the range is assumed to be the entire field. If passed in `stop` then the `start` value
        is present and `stop` is assumed to be `'end'`.

        **Returns:**
        - `self` or `None` if a raw put was done and corresponding new node could not be found.

        **Examples:**

        >>> FST('[0, 1, 2, 3]').put_slice('x', 1).src
        '[0, x]'

        >>> FST('[0, 1, 2, 3]').put_slice('x, y', 1, 3).src
        '[0, x, y, 3]'

        >>> FST('[0, 1, 2, 3]').put_slice('x, y', 1, 3, one=True).src
        '[0, (x, y), 3]'

        >>> FST('[0, 1, 2, 3]').put_slice('x, y', 0, 3).src
        '[x, y, 3]'

        >>> FST('[0, 1, 2, 3]').put_slice('x, y', -3, 'end', one=True).src
        '[0, (x, y)]'

        >>> print(FST('if 1: i = 1\nelse: j = 2').put_slice('z = -1', 0).src)
        if 1:
            z = -1
        else: j = 2

        >>> print(FST('if 1: i = 1\nelse: j = 2').put_slice('z = -1', 0, 'orelse').src)
        if 1: i = 1
        else:
            z = -1

        >>> print(FST('if 1: i = 1\nelse: j = 2')
        ...       .put_slice('z = -1\ny = -2\nx = -3', 'orelse').src)
        if 1: i = 1
        else:
            z = -1
            y = -2
            x = -3
        """

        check_options(options)

        start, stop, field = _swizzle_getput_params(start, stop, field, 0, 'end')
        field, _ = fixup_field_body(self.a, field, True)

        return self._put_slice(code, start, stop, field, one, options)

    def get_src(
        self,
        ln: int | Literal['end'],
        col: int | Literal['end'],
        end_ln: int | Literal['end'],
        end_col: int | Literal['end'],
        as_lines: bool = False
    ) -> builtins.str | list[builtins.str]:
        r"""Get source at location, without dedenting or any other modification, returned as a string or list of
        individual lines.

        Can call on any node in tree to access source for the whole tree.

        The coordinates passed in are clipped to the whole valid source area. Negative indexing is supported and the
        `'end'` special value means either the last line if used for `ln` or `end_ln` or one past the last column on
        their respective line if used for `col` or `end_col`.

        **Parameters:**
        - `ln`: Start line of span to get (0 based).
        - `col`: Start column (character) on start line.
        - `end_ln`: End line of span to get (0 based, inclusive).
        - `end_col`: End column (character, exclusive) on end line.
        - `as_lines`: If `False` then source is returned as a single string with embedded newlines. If `True` then
            source is returned as a list of line strings (without newlines).

        **Returns:**
        - `str | list[str]`: A single string or a list of lines if `as_lines=True`. If lines then there are no trailing
            newlines in the individual line strings.

        **Examples:**

        >>> FST('if 1:\n  i = 2').get_src(0, 3, 1, 5)
        '1:\n  i ='

        >>> FST('if 1:\n  i = 2').get_src(0, 3, 1, 5, as_lines=True)
        ['1:', '  i =']

        >>> (f := FST('if 1:\n  i = 2')).get_src(*f.body[0].bloc)
        'i = 2'

        >>> FST('if 1:\n  i = 2').get_src('end', -3, 'end', 'end')
        '= 2'
        """

        ln, col, end_ln, end_col = clip_src_loc(self, ln, col, end_ln, end_col)

        return self._get_src(ln, col, end_ln, end_col, as_lines)

    def put_src(
        self,
        code: Code | None,
        ln: int | Literal['end'],
        col: int | Literal['end'],
        end_ln: int | Literal['end'],
        end_col: int | Literal['end'],
        action: Literal['reparse', 'offset'] | None = 'reparse',
    ) -> tuple[int, int]:
        r"""Put source and maybe adjust `AST` tree for source modified. The adjustment may be a reparse of the area
        changed, an offset of nodes (assuming put source was just trivia and wouldn't affect the tree) or nothing at
        all. The `action` options are:

        * `'reparse'`: Put source and reparse. There are no rules on what is put, it is simply put and parse is
          attempted.

          The reparse that is triggered is of at least a statement level node or a statement block header, and can be
          multiple statements if the location spans those or even statements outside of the location if the reparse
          affects things like `elif`. `FST` nodes in the region of the put or even outside of it can become invalid. The
          only `FST` node guaranteed not to change is the root node (identity, the `AST` it holds can change).

          When putting source raw by location like this there are no automatic modifications made to the source or
          destination. No parenthesization, prefixes or suffixes or indentation, the source is just put and parsed so you
          are responsible for the correct indentation and precedence.

          After put and successful reparse a new node can be found using `find_loc()` functions from the original start
          `ln` and `col` and newly returned `end_ln` and `end_col`. It is possible that `None` is returned from these
          functions if no good candidate is found (since this can be used to delete or merge nodes).

          `self` doesn't matter in this case, can call on any node in tree, even one which is not touched by the source
          change and the appropriate nodes will be found and reparsed.

        * `'offset'`: Put source and offset nodes around it according to what node the `put_src()` was called on. In
          this case `self` matters and should be the last node down within which the location is contained. Any child
          nodes of this node are offset differently from this `self` node and its parents.

          The `self` node and its parents will not have their start locations offset if the put is an insert at the
          start (as the location is considered to be **INSIDE** these nodes), whereas child nodes will be moved.

          The `self` node and its parents will have their end locations offset if the put ends at this location whereas
          child nodes will not.

        * `None`: Nothing is reparsed or offset, the source is just put. There are few cases where this will result in
          a valid tree but can include removal of comments and trailing whitespace on a line or changing lines between
          empty and comment. Some caches are cleared on put determined by the node this is called on so best to call on
          the node that "ows" the source being put. For comment, block statement it is in or general statement it is on
          the line of. For other misc, best just node that it is "in".

        If the `code` is passed as an `AST` then it is unparsed to a string and that string is put into the location. If
        `code` is an `FST` then the exact source of the `FST` is put. If passed as a string or lines then that is put
        directly.

        The coordinates passed in are clipped to the whole valid source area. Negative indexing is supported and the
        `'end'` special value means either the last line if used for `ln` or `end_ln` or one past the last column on
        their respective line if used for `col` or `end_col`.

        **Parameters:**
        - `code`: The code to put as an `FST` (must be root node), `AST`, a string or list of line strings.
        - `ln`: Start line of span to put (0 based).
        - `col`: Start column (character) on start line.
        - `end_ln`: End line of span to put (0 based, inclusive).
        - `end_col`: End column (character, exclusive) on end line.
        - `action`: What action to take on the `AST` tree, the options are `'reparse'`, `'offset'` or `None`.

        **Returns:**
        - `(end_ln, end_col)`: New end location of source put (all source after this was not modified).

        **Examples:**

        >>> f = FST('i = 1')
        >>> f.put_src('2', 0, 4, 0, 5)
        (0, 5)
        >>> f.src
        'i = 2'

        >>> f = FST('i = 1')
        >>> f.put_src('+= 3', 0, 2, 0, 5)
        (0, 6)
        >>> f.src
        'i += 3'

        >>> f = FST('{a: b, c: d, e: f}')
        >>> f.put_src('**', 0, 7, 0, 10)
        (0, 9)
        >>> f.src
        '{a: b, **d, e: f}'

        >>> f = FST('''
        ... if a:
        ...   i = 2
        ... elif b:
        ...   j = 3
        ... '''.strip())

        >>> print(f.src)
        if a:
          i = 2
        elif b:
          j = 3

        >>> f.put_src('''
        ... else:
        ...   if b:
        ...     k = 4
        ... '''.strip(), *f.orelse[0].loc[:2], *f.loc[2:])
        (4, 9)

        >>> print(f.src)
        if a:
          i = 2
        else:
          if b:
            k = 4

        >>> (f := FST('a, b')).put_src(' ', 0, 4, 0, 4, 'offset')
        (0, 5)

        >>> f.src, f.loc, f.elts[1].loc
        ('a, b ', fstloc(0, 0, 0, 5), fstloc(0, 3, 0, 4))
        """

        root = self.root
        ln, col, end_ln, end_col = clip_src_loc(self, ln, col, end_ln, end_col)

        if action == 'reparse':
            allow_exact = self.a.__class__ in ASTS_LEAF_STMTLIKE
            parent = root.find_contains_loc(ln, col, end_ln, end_col, allow_exact) or root  # we will get either the exact statementlike node if the location matches otherwise a parent, always a parent if the node is not statementlike

            with parent._modifying(False, True):
                return parent._reparse_raw(code, ln, col, end_ln, end_col)

        put_lines = _code_as_lines(code)

        if action == 'offset':  # self matters in this mode!
            # TODO: there may be issues with certain zero-length trees but I can't think of any that might occur in normal usage, not arguments because at zero-length it has no loc

            if not (loc := self.loc):
                raise ValueError("cannot be called with 'offset' on a node which has no location")

            self_ln, self_col, self_end_ln, self_end_col = loc

            if (ln < self_ln
                or (ln == self_ln and col < self_col)
                or end_ln > self_end_ln
                or (end_ln == self_end_ln and end_col > self_end_col)
            ):
                raise ValueError("location with 'offset' must be at or inside location of node")

            field = 'value' if self.a.__class__ in ASTS_LEAF_FTSTR_FMT else False  # the 'value' is so that modifying spacing inside a debug string updates its preceding string Constant, don't need to do this for 'reparse'

            with self._modifying(field, None):  # we use raw=None to signal that the modification should be allowed on py < 3.12 as it only offsets
                params_offset = self._put_src(put_lines, ln, col, end_ln, end_col, True, False, self)

                self._offset(*params_offset, False, True, self_=False)

        elif action is None:
            self._put_src(put_lines, ln, col, end_ln, end_col)
            self._touchall(True, True, False)  # touch parents to clear bloc caches because comment on last child statement is included in parent bloc, include self_ just to be sure

        else:
            raise ValueError(f"action must be 'reparse', 'offset' or None, got {action!r}")

        if len(put_lines) == 1:
            return ln, col + len(put_lines[0])
        else:
            return ln + len(put_lines) - 1, len(put_lines[-1])

    def get_docstr(self) -> builtins.str | None:
        r"""Get the unformatted docstring value of this node if it is a `FunctionDef`, `AsyncFunctionDef`, `ClassDef` or
        `Module`. The docstring is dedented and returned as a normal string, not a node. Keep in mind an empty docstring
        may exist but will be a falsey value so make sure to explicitly check for `None` return. If you want the actual
        docstring node then just check for presence with `.has_docstr` and get `.body[0]`.

        **Returns:**
        - `str | None`: Actual dedented docstring value, not the node or syntactic string representation with quotes.
            `None` if there is no docstring or the node cannot have a docstring.

        **Examples:**

        >>> f = FST('''
        ... def func():
        ...     \'\'\'docstring indented
        ...     in source with codes\\x3f\\x3f\\x3f\'\'\'
        ... '''.strip())

        >>> print(f.src)
        def func():
            '''docstring indented
            in source with codes\x3f\x3f\x3f'''

        >>> f.get_docstr()
        'docstring indented\nin source with codes???'
        """

        if not self.has_docstr:
            return None

        b0 = self.a.body[0]
        dedent = b0.f._get_block_indent()
        ldedent = len(dedent)
        lines = b0.value.value.split('\n')

        for i, l in enumerate(lines):
            if l.startswith(dedent) or (lempty_start := re_empty_line_start.match(l).end()) >= ldedent:
                lines[i] = l[ldedent:]
            else:
                lines[i] = l[lempty_start:]

        return '\n'.join(lines)

    def put_docstr(self, text: builtins.str | None, reput: bool = False, **options) -> FST:  # -> self
        r'''Set or delete the docstring of this node if it is a `FunctionDef`, `AsyncFunctionDef`, `ClassDef` or
        `Module`. Will replace, insert or delete the node as required. If setting, the `text` string that is passed will
        be formatted with triple quotes and indented as needed.

        **Parameters:**
        - `text`: The string to set as a docstring or `None` to delete.
        - `reput`: If `True` then remove old docstring `Expr` first (if present) before reinserting new one. This is to
            allow repositioning the docstring before any comments.
        - `options`: The options to use for a put if a put is done, see `options()`.

        **Returns:**
        - `self`

        **Examples:**

        >>> f = FST('def func(): pass')

        >>> print(f.put_docstr('docstring indented\nin source with codes\x3f\x3f\x3f').src)
        def func():
            """docstring indented
            in source with codes???"""
            pass
        '''

        # TODO: differentiate better header comments of Module and put after shebang and encoding but before others using specific line number once that functionality is concretized

        check_options(options)

        if (a := self.a).__class__ not in ASTS_LEAF_MAYBE_DOCSTR:
            return self

        has_docstr = 1 if (
            (b := a.body)
            and (b0 := b[0]).__class__ is Expr
            and (v := b0.value).__class__ is Constant
            and isinstance(v := v.value, str)
        ) else 0

        if text is not None:
            text = repr_str_multiline(text)
        elif not has_docstr:
            return self

        if 'trivia' not in options:
            options['trivia'] = (False, False)

        if reput and has_docstr:  # if user wants to re-put then delete old one first
            self._put_slice(None, 0, 1, 'body', False, options)

            has_docstr = False

        self._put_slice(text, 0, has_docstr, 'body', False, options)

        return self

    def get_line_comment(
        self, field: Literal['body', 'orelse', 'finalbody'] | None = None, full: bool = False
    ) -> builtins.str | None:
        r"""Get current line comment for this node.

        The line comment is the single comment at the end of the last line of the location of this node, with the
        exception of statement block nodes where the line comment lives on the last line of the header of the node
        (after the `:`, since the comment on the last line of the location belongs to the last child).

        **Note:** Currently this functionality is limited to statement nodes.

        **Parameters:**
        - `field`: If `self` is a block statement then this can specify which field to operate on, only `'body'`,
            `'orelse'` and `'finalbody'` make sense to use and an error will be raised if the field is not present or
            there is nothing in it. `None` means use default `'body'` if block statement.
        - `full`:
            - `False`: The gotten comment text is returned stripped of the `'#'` and any leading and trailing
                whitespace.
            - `True`: The entire gotten comment from the end of the node to the end of the line is returned with no
                whitespace stripped, e.g. `'  # comment  '`.

        **Returns:**
        - `str`: The current comment, with or without the leading whitespace and `'#'` as per the `full` paramenter.
        - `None`: There is no comment present.

        **Examples:**

        >>> FST('statement  # comment  ', 'stmt').get_line_comment()
        'comment'

        >>> FST('statement  # comment  ', 'stmt').get_line_comment(full=True)
        '  # comment  '

        >>> FST('if a:  # ifc\n  pass  # bodyc').body[0].get_line_comment()
        'bodyc'

        >>> FST('if a:  # ifc\n  pass  # bodyc').get_line_comment()
        'ifc'

        >>> FST('if a: pass\nelse:  # elsec\n  pass').get_line_comment('orelse')
        'elsec'
        """

        _validate_get_put_line_comment_field(self, field)

        return self._getput_line_comment(False, field, full)

    def put_line_comment(
        self,
        comment: builtins.str | None = None,
        field: Literal['body', 'orelse', 'finalbody'] | None = None,
        full: bool = False
    ) -> builtins.str | None:
        r"""Put line comment for this node returning whatever comment was there before.

        The line comment is the single comment at the end of the last line of the location of this node, with the
        exception of statement block nodes where the line comment lives on the last line of the header of the node
        (after the `:`, since the comment on the last line of the location belongs to the last child).

        **Note:** Currently this functionality is limited to statement nodes.

        **Parameters:**
        - `comment`: The comment operation to perform after getting the current comment.
            - `str`: Put new comment which may or may not need to have the initial `'#'` according to the `full`
                parameter.
            - `None`: Delete current comment (if present).
        - `field`: If `self` is a block statement then this can specify which field to operate on, only `'body'`,
            `'orelse'` and `'finalbody'` make sense to use and an error will be raised if the field is not present or
            there is nothing in it. `None` means use default `'body'` if block statement.
        - `full`:
            - `False`: The gotten comment text is returned stripped of the `'#'` and any leading and trailing
                whitespace. The put `comment` text is put to existing comment if is present and otherwise is prepended
                with `'  #'` and a single leading whitespace after that if needed and put after the node.
            - `True`: The entire gotten comment from the end of the node to the end of the line is returned with no
                whitespace stripped, e.g. `'  # comment  '`. The put `comment` **MUST** start with a `'#'` and possible
                leading whitespace before that and is put verbatim with no stripping, replacing any existing comment
                from the end of the node to the end of the line.

        **Returns:**
        - `str`: The current comment, before replacement, with or without the leading whitespace and `'#'` as per the
            `full` paramenter.
        - `None`: There was no comment present.

        **Examples:**

        >>> f = FST('statement  # comment  ', 'stmt')
        >>> f.put_line_comment('new comment')
        'comment'
        >>> print(f.src)
        statement  # new comment

        >>> f = FST('if a:  # ifc\n  pass  # bodyc')
        >>> f.body[0].put_line_comment('new body comment')
        'bodyc'
        >>> print(f.src)
        if a:  # ifc
          pass  # new body comment

        >>> f = FST('if a:  # ifc\n  pass  # bodyc')
        >>> f.put_line_comment('new if comment')
        'ifc'
        >>> print(f.src)
        if a:  # new if comment
          pass  # bodyc

        >>> f = FST('if a: pass\nelse:  # elsec\n  pass')
        >>> f.put_line_comment('new else comment', 'orelse')
        'elsec'
        >>> print(f.src)
        if a: pass
        else:  # new else comment
          pass
        """

        _validate_get_put_line_comment_field(self, field)

        return self._getput_line_comment(comment, field, full)

    # TODO: get/put_leading/trailing_comments()

    def pars(self, *, shared: bool | None = True) -> fstloc | None:
        """Return the location of enclosing **GROUPING** parentheses if present. Will balance parentheses if `self` is
        an element of a tuple and not return the parentheses of the tuple. Likwise will not normally return the
        parentheses of an enclosing `arguments` parent or class bases list (unless `shared=None`, but that is mostly for
        internal use).

        Only normally works on (and makes sense for) `expr` or `pattern` nodes, otherwise returns `self.bloc` and count
        of 0. Also handles special case of a single generator expression argument to a function sharing parameters with
        the call arguments, in which case a count of -1 and the location of the `GeneratorExp` without its enclosing
        parentheses may be returned, if this is enabled with `shared=False`.

        This function is cached so feel free to call as often as is needed.

        **Note:** For a `Starred` this will always return the location of the whole `Starred` since that cannot be
        parenthesized itself but rather its child. If you want he parenteses of the child then do
        `starred.value.pars()`.

        **Parameters:**
        - `shared`: If `True` then will include parentheses of a single call argument generator expression if they are
            shared with the call arguments enclosing parentheses with a count of 0. If `False` then does not return
            these and returns a count of -1, and thus the location is not a full valid `GeneratorExp` location. If
            `None` then returns **ANY** directly enclosing parentheses, whether they belong to this node or not.

        **Returns:**
        - `fstloc | None`: Location of enclosing parentheses if present else `self.bloc` (which can be `None`). Negative
            parentheses count (from shared pars solo call arg generator expression) can also be checked in the case of
            `shared=False` via `fst.pars() > fst.bloc`. If only loc is returned, it will be an `fstloc` which will
            still have the count of parentheses in an attribute `.n`.

        **Examples:**

        >>> FST('i').pars()
        fstlocn(0, 0, 0, 1, n=0)

        >>> FST('(i)').pars()
        fstlocn(0, 0, 0, 3, n=1)

        >>> FST('((i))').pars()
        fstlocn(0, 0, 0, 5, n=2)

        >>> FST('(1, 2)').pars()  # tuple pars are not considered grouping pars
        fstlocn(0, 0, 0, 6, n=0)

        >>> FST('((1, 2))').pars()
        fstlocn(0, 0, 0, 8, n=1)

        >>> FST('call(a)').args[0].pars()  # any node, not just root
        fstlocn(0, 5, 0, 6, n=0)

        >>> FST('call((a))').args[0].pars()
        fstlocn(0, 5, 0, 8, n=1)

        >>> FST('call(i for i in j)').args[0].pars()
        fstlocn(0, 4, 0, 18, n=0)

        >>> FST('call(i for i in j)').args[0].pars(shared=False)  # exclude shared pars
        fstlocn(0, 5, 0, 17, n=-1)

        >>> FST('call((i for i in j))').args[0].pars(shared=False)
        fstlocn(0, 5, 0, 19, n=0)
        """

        key = 'parsT' if shared else 'parsF' if shared is False else 'parsN'

        try:
            return self._cache[key]
        except KeyError:
            pass

        if not self.is_parenthesizable() and shared is not None:
            if (l := self.bloc) is None:
                locn = None
            else:
                locn = fstlocn(l[0], l[1], l[2], l[3], n=0)

        else:
            lines = self.root._lines
            ln, col, end_ln, end_col = self.bloc

            rpars = next_delims(lines, end_ln, end_col, *self._next_bound())

            if (lrpars := len(rpars)) == 1:  # no pars on right
                if not shared and self._is_solo_call_arg_genexp():
                    locn = fstlocn(ln, col + 1, end_ln, end_col - 1, n=-1)
                else:
                    locn = fstlocn(ln, col, end_ln, end_col, n=0)

            else:
                lpars = prev_delims(lines, *self._prev_bound(), ln, col)

                if (llpars := len(lpars)) == 1:  # no pars on left
                    locn = fstlocn(ln, col, end_ln, end_col, n=0)

                else:
                    if (llpars <= lrpars
                        and shared is not None
                        and (self._is_solo_call_arg() or self._is_solo_class_base() or self._is_solo_matchcls_pat())
                    ):
                        llpars -= 1

                    if llpars != lrpars:  # unbalanced pars so we know we can safely use the lower count
                        locn = fstlocn(*lpars[n := min(llpars, lrpars) - 1], *rpars[n], n=n)
                    else:
                        locn = fstlocn(*lpars[n := llpars - 1], *rpars[n], n=n)

        self._cache[key] = locn

        return locn

    def par(self, force: bool | Literal['invalid'] = False, *, whole: bool = True) -> FST:  # -> self
        """Parenthesize node if it **MAY** need it. Will not parenthesize atoms which are always enclosed like `List`,
        or nodes which are not `is_parenthesizable()`, unless `force=True`. Will add intrinsic node-owned parentheses to
        unparenthesized `Tuple` and brackets to unbracketed `MatchSequence`, adjusting the node location. If dealing with
        a `Starred` then the parentheses are applied to the child.

        **WARNING!** If you invalid-force-parenthesize something that shouldn't be parenthesized, and you wind up poking
        an eye out, that's on you.

        **Parameters:**
        - `force`:
            - `False`: Only parenthesize if not currently parenthesized and if the node type is not an atom or is an
                atom which can be split over multiple lines (in which case it would need parentheses for parsability).
            - `True`: Add a layer of perentheses regardless if any already present or if node type is an atom, but only
                if allowed by syntax, e.g. this won't parenthesize an `arg`, `withitem` any kind of `statement` or
                anything which would cause a syntax error with the parentheses there, so no `Slice`s or f-string
                `Constant`s either.
            - `'invalid'`: Add a layer of parentheses regardless if any already present or even syntactically allowed.
        - `whole`: If at root then parenthesize whole source instead of just node, if `False` then only node.

        **Returns:**
        - `self`

        **Examples:**

        >>> FST('a + b').par().src
        '(a + b)'

        >>> FST('(a + b)').par().src  # already parenthesized, so nothing done
        '(a + b)'

        >>> FST('(a + b)').par(force=True).src  # force it
        '((a + b))'

        >>> FST('1, 2').par().src  # parenthesize tuple
        '(1, 2)'

        >>> FST('i').par().src  # an atom doesn't need parentheses
        'i'

        >>> FST('i').par(force=True).src  # so must be forced
        '(i)'

        >>> FST('a:b:c', 'Slice').par(force=True).src  # syntactically wrong
        'a:b:c'

        >>> FST('a:b:c', 'Slice').par(force='invalid').src  # can still force
        '(a:b:c)'

        >>> # parethesize MatchSequence puts brackets like ast.unparse()
        >>> FST('1, 2', 'pattern').par().src
        '[1, 2]'

        >>> FST('*a or b').par().src  # par() a Starred parenthesizes its child
        '*(a or b)'

        >>> FST('call(i = 1 + 2)').keywords[0].value.par().root.src  # not just root node
        'call(i = (1 + 2))'
        """

        ast_cls = self.a.__class__

        if not force:
            if (not self.is_parenthesizable()
                or (is_atom := self._is_atom()) in (True, 'pars')
                or (
                    (is_atom or (ast_cls is Starred and self.a.value.f._is_atom() in (True, 'pars')))
                    and self._is_enclosed_or_line()  # _is_enclosed_or_line() can return 'unenclosable'
            )):
                return self

        elif force is True:
            if not self.is_parenthesizable():
                return self

        elif force != 'invalid':
            raise ValueError(f"invalid force parameter {force!r}, can only be True, False or 'invalid'")

        with self._modifying():
            if ast_cls is Tuple:
                if not (force and self.is_parenthesized_tuple()):
                    self._delimit_node(whole)

                    return self

            elif ast_cls is MatchSequence:
                if not (force and self.is_delimited_matchseq()):
                    self._delimit_node(whole, '[]')

                    return self

            self._parenthesize_grouping(whole)

        return self

    def unpar(self, node: bool | Literal['invalid'] = False, *, shared: bool | None = True) -> FST:  # -> self
        """Remove all parentheses if present. Normally removes just grouping parentheses but can also remove intrinsic
        `Tuple` node parentheses and `MatchSequence` parentheses or brackets if `node=True`. If dealing with a `Starred`
        then the parentheses are checked in and removed from the child.

        If `shared=None` then will also remove parentheses which do not belong to this node but enclose it directly,
        this is meant for internal use.

        **WARNING!** This function doesn't do any higher level parsability validation. So if you unparenthesize
        something that shouldn't be unparenthesized, and you wind up poking an eye out, that's on you.

        **Parameters:**
        - `node`: What to remove.
            - `False`: Only grouping parentheses.
            - `True`: Grouping parentheses and also remove intrinsic parentheses from a parenthesized `Tuple` and
                parentheses / brackets from parenthesized / bracketed `MatchSequence`. Also from a parentesized
                `Starred` arglike-only expression which can cause it to become unparsable, e.g. `*(a or b)`.
            - `'invalid'`: Remove intrinsic delimiters also from `List`, `Set`, `Dict`, `MatchMapping`, `ListComp`,
                `SetComp`, `DictComp` and `GeneratorExp`.
        - `shared`: Whether to allow merge of parentheses of single call argument generator expression with `Call`
            parentheses or not. If `None` then will attempt to unparenthesize **ANY** enclosing parentheses, whether
            they belong to this node or not (meant for internal use).

        **Returns:**
        - `self`

        **Examples:**

        >>> FST('a + b').unpar().src  # nothing done if no pars
        'a + b'

        >>> FST('(a + b)').unpar().src
        'a + b'

        >>> FST('((a + b))').unpar().src  # removes all
        'a + b'

        >>> FST('(1, 2)').unpar().src  # but not from tuple
        '(1, 2)'

        >>> FST('(1, 2)').unpar(node=True).src  # unless explicitly specified
        '1, 2'

        >>> FST('(((1, 2)))').unpar().src
        '(1, 2)'

        >>> FST('(((1, 2)))').unpar(node=True).src
        '1, 2'

        >>> FST('[1, 2]', 'pattern').unpar().src
        '[1, 2]'

        >>> FST('[1, 2]', 'pattern').unpar(node=True).src
        '1, 2'

        >>> FST('*(a)').unpar().src  # Starred unparenthesizes its child
        '*a'

        >>> # unless it is arglike since that is syntax error, the pars belong to the node
        >>> FST('*(a or b)').unpar().src
        '*(a or b)'

        >>> FST('*(a or b)').unpar(node=True).src  # so can force with node=True
        '*a or b'

        Not just root node.

        >>> FST('call(i = (1 + 2))').keywords[0].value.unpar().root.src
        'call(i = 1 + 2)'

        By default allows sharing.

        >>> FST('call(((i for i in j)))').args[0].unpar().root.src
        'call(i for i in j)'

        Unless told not to.

        >>> FST('call(((i for i in j)))').args[0].unpar(shared=False).root.src
        'call((i for i in j))'

        Invalid stuff.

        >>> FST('{1: a, **rest}', pattern).unpar(node='invalid').root.src
        '1: a, **rest'

        >>> FST('[i for i in j if i]').unpar(node='invalid').root.src
        'i for i in j if i'
        """

        ast = self.a
        ast_cls = self.a.__class__

        if ((node is not True and node != 'invalid') if node else (node is not False)):
            raise ValueError(f"invalid node parameter {node!r}, can only be True, False or 'invalid'")

        if ast_cls is Starred:
            is_expr_arglike = self._is_expr_arglike_only()
            value = ast.value.f

            if (value.pars().n if is_expr_arglike is None else node and not is_expr_arglike):
                with self._modifying():
                    value._unparenthesize_grouping(shared)

            return self

        modifying = None

        try:
            shared_test = None if shared is None or (shared and self._is_solo_call_arg_genexp()) else True

            if self.pars(shared=shared_test).n > 0:
                modifying = self._modifying().enter()

                self._unparenthesize_grouping(shared)

            if node:
                if ast_cls in (Tuple, MatchSequence) or (node == 'invalid' and ast_cls in ASTS_LEAF_DELIMITED):
                    modifying = modifying or self._modifying().enter()

                    self._undelimit_node()

        except:
            if modifying:
                modifying.fail()

            raise

        else:
            if modifying:
                modifying.success()

        return self  # ret

    # ------------------------------------------------------------------------------------------------------------------
    # Traverse

    def scope_symbols(
        self,
        full: bool = False,
        *,
        local: bool = True,
        free: bool = True,
        import_star: bool = False,
    ) -> dict[builtins.str, list[FST]] | dict[builtins.str, dict[builtins.str, list[FST]]]:
        """Get the symbols accessed in the scope of `self` (from `self` on down, will not search up if `self` is only
        part of a scope and doesn't define its own). Normally should be called on something that has a scope like a
        module or function definition or lambda or comprehension, but can be called on anything. Returns either a simple
        dictionary of all the symbol names (with the respective `FST` nodes where they are accessed) or a categorized
        dictionary of these if `full=True`.

        **Note:** The order of the nodes in the various dictionaries are the order in which they appear
        **SYNTACTICALLY**, not the order they will be processed in semantically by the interpreter.

        **Note:** For `AugAssign` nodes the same node will appear in both the `load` and `store` dictionaries in a
        `full=True` return but only once in the single dictionary returned when `full=False`.

        **Parameters:**
        - `full`: Whether to return a single dictionary with all names or a catgorized dictionary of dictionaries. If
            `True` then the categories are:
            - `'load'`: Dictionary of symbol names to list of nodes where these names are read.
            - `'store'`: Dictionary of symbol names to list of nodes where these names are written.
            - `'del'`: Dictionary of symbol names to list of nodes where these names are deleted.
            - `'global'`: Dictionary of symbol names to list of `Global` nodes where these names are declared. The nodes
                aren't where the symbols are used, those are still in the `'load'` / `'store'` / `'del'` lists, just
                where they are **DECLARED** as global. Multiple symbol names will probably have the same node since a
                single `global` declaration can declare multiple names and the names themselves don't have their own
                individual nodes, they are just strings in the `Global` node.
            - `'nonlocal'`: Similar to `global` but for `nonlocal` declarations. This is just the declarations, these
                are not necessarily all the truly nonlocal symbols as there can be "free" variables which are nonlocal
                but not explicitly declared as such.
            - `'local'`: This is a dictionary of symbols determined to be local to the scope. These are all `'store'`
                symbols which do not appear in either `'global'` or `'nonlocal'` explicit declarations. There are no
                `'load'` or `'del'` nodes in these lists even if they are local both because "local" symbols are defined
                as such by a store operation and also because it is faster. If you need any respective `'load'` or
                `'del'` nodes then look them up in their respective category dictionary.
            - `'free'`: This is a dictionary of symbols determined to be implicitly nonlocal to the scope. Basically all
                nodes which are read but never written or deleted and are not explicitly `global` or `nonlocal`. Note
                that this is slightly different from the python definition of a "free" variable as those can include
                explicitly `nonlocal` variables. For our purposes here it is only the **IMPLICIT** nonlocal symbols.
        - `local`: Whether to compute the `'local'` category of symbols or not, set to `False` if you don't need this.
        - `free`: Whether to compute the `'free'` category symbols or not, set to `False` if you don't need this.
        - `import_star`: Normally a `from mod import *` does not generate any symbols. If you pass this parameter as
            `True` then the `*` (invalid) name with its `alias` node is added to the `'store'` category.

        **Examples:**

        >>> print(FST('def f(v=b): v = a').scope_symbols())  # notice no 'b' or 'f'
        {'v': [<arg 0,6..0,7>, <Name 0,12..0,13>], 'a': [<Name 0,16..0,17>]}

        >>> from pprint import pp
        >>> pp(FST('''
        ... def func(arg: int = default) -> object:
        ...     global mod0, declared_global  # this will make the import global
        ...     nonlocal aug
        ...     loc = arg
        ...     del delete
        ...     aug += implicit_nonlocal
        ...     import mod0
        ...     import mod1.submod
        ...     import mod2 as asname1
        ...     from mod3 import mod_name1
        ...     from mod4 import mod_name2 as asname2
        ...     from mod5 import *
        ...     return str(arg)
        ... '''.strip()).scope_symbols(full=True, import_star=True))
        {'load': {'arg': [<Name 3,10..3,13>, <Name 12,15..12,18>],
                  'aug': [<Name 5,4..5,7>],
                  'implicit_nonlocal': [<Name 5,11..5,28>],
                  'str': [<Name 12,11..12,14>]},
         'store': {'arg': [<arg 0,9..0,17>],
                   'loc': [<Name 3,4..3,7>],
                   'aug': [<Name 5,4..5,7>],
                   'mod0': [<alias 6,11..6,15>],
                   'mod1': [<alias 7,11..7,22>],
                   'asname1': [<alias 8,11..8,26>],
                   'mod_name1': [<alias 9,21..9,30>],
                   'asname2': [<alias 10,21..10,41>],
                   '*': [<alias 11,21..11,22>]},
         'del': {'delete': [<Name 4,8..4,14>]},
         'global': {'mod0': [<Global 1,4..1,32>],
                    'declared_global': [<Global 1,4..1,32>]},
         'nonlocal': {'aug': [<Nonlocal 2,4..2,16>]},
         'local': {'arg': [<arg 0,9..0,17>],
                   'loc': [<Name 3,4..3,7>],
                   'mod1': [<alias 7,11..7,22>],
                   'asname1': [<alias 8,11..8,26>],
                   'mod_name1': [<alias 9,21..9,30>],
                   'asname2': [<alias 10,21..10,41>],
                   '*': [<alias 11,21..11,22>]},
         'free': {'implicit_nonlocal': [<Name 5,11..5,28>],
                  'str': [<Name 12,11..12,14>]}}
        """

        ast = self.a
        full_and_comp = full and ast.__class__ in ASTS_LEAF_COMP

        if not full:
            syms_load = syms_store = syms_del = syms_global = syms_nonlocal = {}

        else:
            syms_load = {}  # every varname loaded in this scope  - {'name': [FST, ...]}
            syms_store = {}  # explicitly or implicitly stored
            syms_del = {}  # explicitly 'del'eted
            syms_global = {}  # explicitly 'global'
            syms_nonlocal = {}  # explicitly 'nonlocal'
            syms_walrus = set()  # this will only get NamedExpr.target if self is a Comprehension, only used for the symbol names

        for f in self.walk(all=_ASTS_LEAF_SCOPE_SYMBOLS, scope=True):
            a = f.a
            a_cls = a.__class__

            if a_cls is Name:
                name = a.id
                ctx_cls = a.ctx.__class__

                if ctx_cls is Load:
                    syms = syms_load
                elif ctx_cls is Del:
                    syms = syms_del

                else:  # ctx_cls is Store
                    syms = syms_store

                    if (full_and_comp  # we check for full because otherwise we would put the node twice to the single list which doesn't distinguish "free" symbols anyway
                        and f.pfield.name == 'target'
                        and f.parent.a.__class__ is NamedExpr  # if is_comp and pfield.name == 'target' then there is a parent for sure
                    ):  # Comprehensions NamedExpr.target is a "free" variable in some outer scope
                        syms_walrus.add(name)  # we need the names of these to build 'local' and 'load' correctly

                        if name_fsts := syms_load.get(name):  # we also add to load because that is what will be used to generate sorted "free" symbols with their nodes, will be filtered out for the actual "load" symbol dict
                            name_fsts.append(f)
                        else:
                            syms_load[name] = [f]

                syms = syms_load if ctx_cls is Load else syms_store if ctx_cls is Store else syms_del

            elif a_cls is arg:  # these will only be returned for top-level node so their arg is part of our scope
                name = a.arg
                syms = syms_store

            elif a_cls in ASTS_LEAF_DEF:
                if a is ast:  # self, its name belongs to outer scope
                    continue

                name = a.name
                syms = syms_store

            elif a_cls is AugAssign:  # if this has a Name target then it is marked for Store, we also want to mark it as Load
                if full and (target := a.target).__class__ is Name:  # we check for full because otherwise we would put the node twice to the single list
                    name = target.id

                    if name_fsts := syms_load.get(name):
                        name_fsts.append(target.f)
                    else:
                        syms_load[name] = [target.f]

                continue

            elif a_cls is Import:
                for alias_ in a.names:
                    if not (name := alias_.asname):
                        name = alias_.name.split('.', 1)[0]

                    if name_fsts := syms_store.get(name):
                        name_fsts.append(alias_.f)
                    else:
                        syms_store[name] = [alias_.f]

                continue

            elif a_cls is ImportFrom:
                names = a.names

                if import_star or not (len(names) == 1 and names[0].name == '*'):  # what do we do with 'from mod import *'
                    for alias_ in a.names:
                        name = alias_.asname or alias_.name

                        if name_fsts := syms_store.get(name):
                            name_fsts.append(alias_.f)
                        else:
                            syms_store[name] = [alias_.f]

                continue

            elif a_cls in ASTS_LEAF_TYPE_PARAM:  # these will only be returned for top-level node so their arg is part of our scope
                name = a.name
                syms = syms_store

            else:
                if a_cls is Nonlocal:
                    syms = syms_nonlocal

                else:  # a_cls is Global:
                    assert a_cls is Global

                    syms = syms_global

                for name in a.names:
                    if name_fsts := syms.get(name):
                        name_fsts.append(f)
                    else:
                        syms[name] = [f]

                continue

            if name_fsts := syms.get(name):
                name_fsts.append(f)
            else:
                syms[name] = [f]

        if not full:
            return syms_load  # they're all the same

        ret = {
            'load': syms_load,
            'store': syms_store,
            'del': syms_del,
            'global': syms_global,
            'nonlocal': syms_nonlocal,
        }

        if local:
            non_local_names = set(syms_global)

            non_local_names.update(syms_nonlocal)
            non_local_names.update(syms_walrus)  # these only come from NamedExpr.target when top-level node is a Comprehension

            ret['local'] = {n: fs for n, fs in syms_store.items() if n not in non_local_names}

        if free:
            non_load_names = set(syms_store)

            if full_and_comp:  # top-level Comprehension, we may have syms_walrus from walruses, there are no syms_del/nonlocal/global
                non_load_names.difference_update(syms_walrus)

                ret['free'] = {n: fs for n, fs in syms_load.items() if n not in non_load_names}
                ret['load'] = {n: ffs for n, fs in syms_load.items()
                               if (ffs := [f for f in fs if f.a.ctx.__class__ is Load])}  # filter out store nodes which came from walruses

            else:
                non_load_names.update(syms_del)
                non_load_names.update(syms_nonlocal)
                non_load_names.update(syms_global)

                ret['free'] = {n: fs for n, fs in syms_load.items() if n not in non_load_names}

        return ret

    walk = fst_traverse.walk  # we do assign instead of import so that pdoc gets the right order
    next = fst_traverse.next
    prev = fst_traverse.prev
    first_child = fst_traverse.first_child
    last_child = fst_traverse.last_child
    last_header_child = fst_traverse.last_header_child
    next_child = fst_traverse.next_child
    prev_child = fst_traverse.prev_child
    step_fwd = fst_traverse.step_fwd
    step_back = fst_traverse.step_back

    def parents(self, self_: bool = False) -> Generator[FST, None, None]:
        """Generator which yields parents all the way up to root. If `self_` is `True` then will yield `self` first.

        **Parameters:**
        - `self_`: Whether to yield `self` first.

        **Returns:**
        - `Generator`: Will walk up the parent chain.

        **Examples:**

        >>> list(FST('i = (f(), g())', 'exec').body[0].value.elts[0].parents())
        [<Tuple 0,4..0,14>, <Assign 0,0..0,14>, <Module ROOT 0,0..0,14>]

        >>> list(FST('i = (f(), g())', 'exec').body[0].value.elts[0].parents(self_=True))
        [<Call 0,5..0,8>, <Tuple 0,4..0,14>, <Assign 0,0..0,14>, <Module ROOT 0,0..0,14>]
        """

        if self_:
            yield self

        while self := self.parent:
            yield self

    def parent_stmt(self, self_: bool = False, mod: bool = True) -> FST | None:
        """The first parent which is a `stmt` or optionally `mod` node (if any). If `self_` is `True` then will check
        `self` first (possibly returning `self`), otherwise only checks parents.

        **Parameters:**
        - `self_`: Whether to include `self` in the search, if so and `self` matches criteria then it is returned.
        - `mod`: Whether to return `mod` nodes if found.

        **Returns:**
        - `FST | None`: First `stmt` or optionally `mod` parent if present, else `None`.

        **Examples:**

        >>> FST('if 1: i = 1', 'exec').body[0].body[0].value.parent_stmt()
        <Assign 0,6..0,11>

        >>> FST('if 1: i = 1', 'exec').body[0].body[0].parent_stmt()
        <If 0,0..0,11>

        >>> FST('if 1: i = 1', 'exec').body[0].parent_stmt()
        <Module ROOT 0,0..0,11>

        >>> print(FST('if 1: i = 1', 'exec').body[0].parent_stmt(mod=False))
        None

        >>> FST('if 1: i = 1', 'exec').body[0].parent_stmt(self_=True)
        <If 0,0..0,11>
        """

        types = ASTS_LEAF_STMT_OR_MOD if mod else ASTS_LEAF_STMT

        if self_ and self.a.__class__ in types:
            return self

        while (self := self.parent) and self.a.__class__ not in types:
            pass

        return self

    def parent_stmtlike(self, self_: bool = False, mod: bool = True) -> FST | None:
        r"""The first parent which is a `stmt`, `ExceptHandler`, `match_case` or optionally `mod` node (if any). If
        `self_` is `True` then will check `self` first, otherwise only checks parents.

        **Returns:**
        - `FST | None`: First `stmtlike` or optionally `mod` parent if present, else `None`.

        **Examples:**

        >>> (FST('try: pass\nexcept: pass', 'exec')
        ...  .body[0].handlers[0].body[0].parent_stmtlike())
        <ExceptHandler 1,0..1,12>

        >>> FST('try: pass\nexcept: pass', 'exec').body[0].handlers[0].parent_stmtlike()
        <Try 0,0..1,12>

        >>> FST('try: pass\nexcept: pass', 'exec').body[0].parent_stmtlike()
        <Module ROOT 0,0..1,12>

        >>> FST('match a:\n  case 1: pass').cases[0].body[0].parent_stmtlike()
        <match_case 1,2..1,14>

        >>> FST('match a:\n  case 1: pass').cases[0].pattern.parent_stmtlike()
        <match_case 1,2..1,14>
        """

        types = ASTS_LEAF_STMTLIKE_OR_MOD if mod else ASTS_LEAF_STMTLIKE

        if self_ and self.a.__class__ in types:
            return self

        while (self := self.parent) and self.a.__class__ not in types:
            pass

        return self

    def parent_block(self, self_: bool = False, mod: bool = True) -> FST | None:
        """The first parent which opens a block that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `For`, `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`,
        `TryStar`, `ExceptHandler`, `match_case` or optionally `mod` node (if any). If `self_` is `True` then will check
        `self` first, otherwise only checks parents.

        **Returns:**
        - `FST | None`: First block `stmt` or optionally `mod` parent if present, else `None`.

        **Examples:**

        >>> FST('if 1: i = 1', 'exec').body[0].body[0].value.parent_block()
        <If 0,0..0,11>

        >>> FST('if 1: i = 1', 'exec').body[0].parent_block()
        <Module ROOT 0,0..0,11>
        """

        types = ASTS_LEAF_BLOCK_OR_MOD if mod else ASTS_LEAF_BLOCK

        if self_ and self.a.__class__ in types:
            return self

        while (self := self.parent) and self.a.__class__ not in types:
            pass

        return self

    def parent_scope(self, self_: bool = False, mod: bool = True) -> FST | None:
        r"""The first parent which opens a scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `Lambda`, `ListComp`, `SetComp`, `DictComp`, `GeneratorExp` or optionally `mod`
        node (if any). If `self_` is `True` then will check `self` first, otherwise only checks parents.

        **Returns:**
        - `FST | None`: First scope `stmt` or optionally `mod` parent if present, else `None`.

        **Examples:**

        >>> FST('if 1: i = 1', 'exec').body[0].body[0].value.parent_scope()
        <Module ROOT 0,0..0,11>

        >>> (FST('def f():\n  if 1: i = 1', 'exec')
        ...  .body[0].body[0].body[0].value.parent_scope())
        <FunctionDef 0,0..1,13>

        >>> FST('lambda: None', 'exec').body[0].value.body.parent_scope()
        <Lambda 0,0..0,12>

        >>> FST('[i for i in j]', 'exec').body[0].value.elt.parent_scope()
        <ListComp 0,0..0,14>
        """

        types = ASTS_LEAF_SCOPE_OR_MOD if mod else ASTS_LEAF_SCOPE

        if self_ and self.a.__class__ in types:
            return self

        while (self := self.parent) and self.a.__class__ not in types:
            pass

        return self

    def parent_named_scope(self, self_: bool = False, mod: bool = True) -> FST | None:
        r"""The first parent which opens a named scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef` or optionally `mod` node (if any). If `self_` is `True` then will check `self`
        first, otherwise only checks parents.

        **Returns:**
        - `FST | None`: First named scope `stmt` or optionally `mod` parent if present, else `None`.

        **Examples:**

        >>> FST('if 1: i = 1', 'exec').body[0].body[0].value.parent_named_scope()
        <Module ROOT 0,0..0,11>

        >>> (FST('def f():\n  if 1: i = 1', 'exec')
        ...  .body[0].body[0].body[0].value.parent_named_scope())
        <FunctionDef 0,0..1,13>

        >>> (FST('def f(): lambda: None', 'exec')
        ...  .body[0].body[0].value.body.parent_named_scope())
        <FunctionDef 0,0..0,21>

        >>> (FST('class cls: [i for i in j]', 'exec')
        ...  .body[0].body[0].value.elt.parent_named_scope())
        <ClassDef 0,0..0,25>
        """

        types = ASTS_LEAF_SCOPE_NAMED_OR_MOD if mod else ASTS_LEAF_SCOPE_NAMED

        if self_ and self.a.__class__ in types:
            return self

        while (self := self.parent) and self.a.__class__ not in types:
            pass

        return self

    def parent_non_expr(self, self_: bool = False, strict: bool = False) -> FST | None:
        r"""The first parent which is not an `expr`. If `self_` is `True` then will check `self` first (possibly
        returning `self`), otherwise only checks parents.

        **Parameters:**
        - `self_`: Whether to include `self` in the search, if so and `self` matches criteria then it is returned.
        - `strict`: `False` means consider `comprehension`, `arguments`, `arg` and `keyword` nodes as `expr` for the
            sake of the walk up since these nodes can have other `expr` parents (meaning they will be skipped). `True`
            means only `expr` nodes, which means you could get an `arg` or `comprehension` node for example which still
            has `expr` parents. Also `expr_context`, `boolop`, `operator`, `unaruop` and `cmpop` are included if
            `strict=False` but this only makes sense if `self_=True` and you are calling this function on one of those.

        **Returns:**
        - `FST | None`: First non-`expr` parent if present, possibly skipping mentioned nodes according to `strict`,
            else `None`.

        **Examples:**

        >>> FST('if 1: i = 1 + a[b]').body[0].value.right.value.parent_non_expr()
        <Assign 0,6..0,18>

        >>> (FST('match a:\n case {a.b.c: 1}: pass')
        ...  .cases[0].pattern.keys[0].value.value.parent_non_expr())
        <MatchMapping 1,6..1,16>

        >>> FST('var = call(a, b=1)').value.keywords[0].value.parent_non_expr()
        <Assign ROOT 0,0..0,18>

        >>> (FST('var = call(a, b=1)')
        ...  .value.keywords[0].value.parent_non_expr(strict=True))
        <keyword 0,14..0,17>
        """

        types = ASTS_LEAF_EXPR if strict else _ASTS_LEAF_EXPR_CHAIN_OP_OR_CTX  # ops and ctx because of maybe self_

        if self_ and self.a.__class__ not in types:
            return self

        while (self := self.parent) and self.a.__class__ in types:
            pass

        return self

    def parent_pattern(self, self_: bool = False) -> FST | None:
        r"""The first parent which is a `pattern`. If `self_` is `True` then will check `self` first (possibly returning
        `self`), otherwise only checks parents.

        **Parameters:**
        - `self_`: Whether to include `self` in the search, if so and `self` matches criteria then it is returned.

        **Returns:**
        - `FST | None`: First `pattern` parent if present, else `None`.

        **Examples:**

        >>> FST('case 1+1j: pass').pattern.value.left.parent_pattern().src
        '1+1j'

        >>> (FST('case 1 | {a.b: c}: pass')
        ...  .pattern.patterns[1].patterns[0].parent_pattern(self_=True))
        <MatchAs 0,15..0,16>

        >>> (FST('case 1 | {a.b: c}: pass')
        ...  .pattern.patterns[1].patterns[0].parent_pattern())
        <MatchMapping 0,9..0,17>

        >>> (FST('case 1 | {a.b: c}: pass')
        ...  .pattern.patterns[1].patterns[0].parent_pattern().parent_pattern())
        <MatchOr 0,5..0,17>
        """

        if self_ and self.a.__class__ in ASTS_LEAF_PATTERN:
            return self

        while (self := self.parent) and (a := self.a).__class__ not in ASTS_LEAF_PATTERN:
            if isinstance(a, (match_case, stmt)):
                return None

        return self

    def parent_ftstr(self, self_: bool = False) -> FST | None:
        r"""The first parent which is an f or t-string. If `self_` is `True` then will check `self` first (possibly
        returning `self`), otherwise only checks parents. This can be used to determine if an expression (or anything
        else like lambda arguments) are ultimately inside one of these.

        **Returns:**
        - `FST | None`: First `JoinedStr` or `TemplateStr` parent if present, else `None`.

        **Parameters:**
        - `self_`: Whether to include `self` in the search, if so and `self` matches criteria then it is returned.

        **Examples:**

        >>> bool(FST('f"{a}"').values[0].value.parent_ftstr())
        True

        >>> bool(FST('f"{a}"').parent_ftstr())
        False

        >>> bool(FST('f"{a}"').parent_ftstr(self_=True))
        True

        >>> bool(FST('f"{a:{b}}"').values[0].format_spec.parent_ftstr(self_=True))
        True
        """

        types = ASTS_LEAF_FTSTR

        if self_ and self.a.__class__ in types:
            return self

        while (self := self.parent) and self.a.__class__ not in types:
            pass

        return self

    def child_path(self, child: FST, as_str: bool = False) -> list[astfield] | builtins.str:
        """Get path to `child` node from `self` which can later be used on a copy of this tree to get to the  same
        relative child node.

        **Note:** This function is intentionally made to work for nodes which have been removed from a tree (because
        their parent links are not severed). This is useful for finding a node if it has been replaced by a raw reparse.

        **Parameters:**
        - `child`: Child node to get path to, can be `self` in which case an empty path is returned.
        - `as_str`: If `True` will return the path as a python-ish string suitable for attribute access, else a list of
            `astfield`s which can be used more directly.

        **Returns:**
        - `list[astfield] | str`: Path to child if exists, otherwise raises.

        **Examples:**

        >>> (f := FST('[i for i in j]', 'exec')).child_path(f.body[0].value.elt)
        [astfield('body', 0), astfield('value'), astfield('elt')]

        >>> ((f := FST('[i for i in j]', 'exec'))
        ...  .child_path(f.body[0].value.elt, as_str=True))
        'body[0].value.elt'

        >>> (f := FST('i')).child_path(f)
        []

        >>> (f := FST('i')).child_path(f, as_str=True)
        ''
        """

        if child.root is not self.root:
            raise ValueError('child is not part of same tree')

        path = []

        while child is not self:
            path.append(child.pfield)

            if not (child := child.parent):
                raise ValueError('invalid child')

        path.reverse()

        return path if not as_str else '.'.join(af.name if (i := af.idx) is None else f'{af.name}[{i}]' for af in path)

    def child_from_path(self, path: list[astfield] | builtins.str, last_valid: bool = False) -> FST | Literal[False]:
        """Get child node specified by `path` if it exists. If succeeds then it doesn't mean that the child node is
        guaranteed to be the same or even same type as was originally used to get the path, just that the path is valid.
        For example after deleting an element from a list the item at the former element's location will be the previous
        next element.

        **Parameters:**
        - `path`: Path to child as a list of `astfield`s or string.
        - `last_valid`: If `True` then return the last valid node along the path, will not fail, can return `self`.

        **Returns:**
        - `FST`: Child node if path is valid, otherwise `False` if path invalid. `False` and not `None` because `None`
            can be in a field that can hold an `AST` but `False` can not.

        **Examples:**

        >>> f = FST('[i for i in j]', 'exec')

        >>> f.child_from_path(f.child_path(f.body[0].value.elt)).src
        'i'

        >>> f.child_from_path(f.child_path(f.body[0].value.elt, True)).src
        'i'

        >>> FST('[0, 1, 2, 3]', 'exec').child_from_path('body[0].value.elts[4]')
        False

        >>> (FST('[0, 1, 2, 3]', 'exec')
        ...  .child_from_path('body[0].value.elts[4]', last_valid=True).src)
        '[0, 1, 2, 3]'

        >>> (f := FST('i')).child_from_path([]) is f
        True

        >>> (f := FST('i')).child_from_path('') is f
        True
        """

        if isinstance(path, str):
            path = [astfield(p[:i], int(p[i + 1 : -1])) if (i := p.find('[')) != -1 else astfield(p)
                    for p in path.split('.')] if path else []

        for p in path:
            if (next := p.get_default(self.a)) is False:
                return self if last_valid else False

            self = next.f

        return self

    def repath(self) -> FST:
        """Recalculate `self` from path from root. Useful if `self` has been replaced by another node by some operation.
        When nodes are deleted the corresponding `FST.a` and `AST.f` attributes are set to `None`. The `parent` and
        `pfield` attributes are left so that things like this can work. Useful when a node has been deleted but you want
        to know where it was and what may be there now.

        **Returns:**
        - `FST`: Possibly `self` or the node which took our place at our relative position from `root`.

        **Examples:**

        >>> f = FST('[0, 1, 2, 3]')
        >>> g = f.elts[1]

        >>> print(type(g.a), g.root)
        <class 'ast.Constant'> <List ROOT 0,0..0,12>

        >>> f.put('x', 1, raw=True)  # raw forces reparse at List
        <List ROOT 0,0..0,12>

        >>> print(g.is_alive, g.a, g.root)
        False None <List ROOT 0,0..0,12>

        >>> g = g.repath()
        >>> print(g.is_alive, type(g.a), g.root)
        True <class 'ast.Name'> <List ROOT 0,0..0,12>
        """

        root = self.root

        return root.child_from_path(root.child_path(self))

    def find_contains_loc(
        self, ln: int, col: int, end_ln: int, end_col: int, allow_exact: bool | Literal['top'] = True
    ) -> FST | None:
        r"""Find the lowest level node which entirely contains location (starting search at `self`). The search will
        only find nodes at self or below, no parents.

        **Parameters:**
        - `ln`: Start line of location to search for (0 based).
        - `col`: Start column (character) on start line.
        - `end_ln`: End line of location to search for (0 based, inclusive).
        - `end_col`: End column (character, inclusive with `FST.end_col`, exclusive with `FST.col`) on end line.
        - `allow_exact`: Whether to allow return of exact location match with node or not. `True` means allow return of
            node which matches location exactly. `False` means location must be inside the node but cannot be touching
            **BOTH** ends of the node. This basically determines whether you can get the exact node of the location or
            its parent. A value of `'top'` specifies an exact match is allowed and return the highest level node with
            the match, otherwise the lowest level exact match is returned. This only applies to nodes like `Expr` which
            will have the same location as the contained `expr` or a `Module` which only contains a single statement
            without any other junk like comments or empty lines surrounding it.

        **Returns:**
        - `FST | None`: Node which entirely contains location, either exactly or not, or `None` if no such node.

        **Examples:**

        >>> FST('i = val', 'exec').find_contains_loc(0, 6, 0, 7)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_contains_loc(0, 4, 0, 7)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_contains_loc(0, 4, 0, 7, allow_exact=False)
        <Assign 0,0..0,7>

        >>> FST('i = val', 'exec').find_contains_loc(0, 5, 0, 7, allow_exact=False)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_contains_loc(0, 4, 0, 6, allow_exact=False)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_contains_loc(0, 3, 0, 7)
        <Assign 0,0..0,7>

        >>> FST('i = val', 'exec').find_contains_loc(0, 3, 0, 7, allow_exact=False)
        <Assign 0,0..0,7>

        >>> print(FST('i = val', 'exec').find_contains_loc(0, 0, 0, 7, allow_exact=False))
        None

        >>> FST('i = val\n', 'exec').find_contains_loc(0, 0, 0, 7, allow_exact=False)
        <Module ROOT 0,0..1,0>

        >>> FST('i = val', 'exec').find_contains_loc(0, 0, 0, 7)
        <Assign 0,0..0,7>

        >>> FST('i = val', 'exec').find_contains_loc(0, 0, 0, 7, allow_exact='top')
        <Module ROOT 0,0..0,7>
        """

        fln, fcol, fend_ln, fend_col = self.loc

        if ((((same_ln := fln == ln) and fcol <= col) or fln < ln)
            and (((same_end_ln := fend_ln == end_ln) and fend_col >= end_col) or fend_ln > end_ln)
        ):
            if same_ln and same_end_ln and fcol == col and fend_col == end_col:
                if not allow_exact:
                    return None

                if allow_exact == 'top':
                    return self

        else:
            return None

        while True:
            for f in self.walk('loc', self_=False):
                fln, fcol, fend_ln, fend_col = f.loc

                if fend_ln < ln or (fend_ln == ln and fend_col <= col):
                    continue

                if (fln > ln
                    or ((same_ln := fln == ln) and fcol > col)
                    or fend_ln < end_ln
                    or ((same_end_ln := fend_ln == end_ln) and fend_col < end_col)
                ):
                    return self

                if not allow_exact and same_ln and same_end_ln and fcol == col and fend_col == end_col:
                    return self

                self = f

                break

            else:
                return self

    def find_in_loc(self, ln: int, col: int, end_ln: int, end_col: int) -> FST | None:
        """Find the first highest level node which is contained entirely in location (inclusive, starting search at
        `self`). The search will only find nodes at self or below, no parents.

        **Parameters:**
        - `ln`: Start line of location to search (0 based).
        - `col`: Start column (character) on start line.
        - `end_ln`: End line of location to search (0 based, inclusive).
        - `end_col`: End column (character, inclusive with `FST.end_col`, exclusive with `FST.col`) on end line.

        **Returns:**
        - `FST | None`: First node in syntactic order which is entirely contained in the location or `None` if no such
            node.

        **Examples:**

        >>> FST('i = val', 'exec').find_in_loc(0, 0, 0, 7)
        <Module ROOT 0,0..0,7>

        >>> FST('i = val', 'exec').find_in_loc(0, 1, 0, 7)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_in_loc(0, 4, 0, 7)
        <Name 0,4..0,7>

        >>> print(FST('i = val', 'exec').find_in_loc(0, 5, 0, 7))
        None
        """

        fln, fcol, fend_ln, fend_col = self.loc

        if ((fln > ln or (fln == ln and fcol >= col))
            and (fend_ln < end_ln or (fend_ln == end_ln and fend_col <= end_col))
        ):
            return self

        while True:
            for f in self.walk('loc', self_=False):
                fln, fcol, fend_ln, fend_col = f.loc

                if fln < ln or (fln == ln and fcol < col):
                    continue

                if fend_ln < end_ln or (fend_ln == end_ln and fend_col <= end_col):
                    return f

                self = f

                break

            else:
                return None

    def find_loc(self, ln: int, col: int, end_ln: int, end_col: int, exact_top: bool = False) -> FST | None:
        r"""Find node which best fits location. If an exact location match is found then that is returned with the `top`
        parameter specifying which of multiple nodes at same location is returned if that is the case. Otherwise
        `find_in_loc()` is preferred if there is a match and if not then `find_contains_loc()`. The search is done
        efficiently so that the same nodes are not walked multiple times.

        **Parameters:**
        - `ln`: Start line of location to search for (0 based).
        - `col`: Start column (character) on start line.
        - `end_ln`: End line of location to search for (0 based, inclusive).
        - `end_col`: End column (character, inclusive with `FST.end_col`, exclusive with `FST.col`) on end line.
        - `exact_top`: If an exact location match is found and multiple nodes share this location (`Expr` and `expr`)
            then this decides whether the highest level node is returned or the lowest (`True` means highest).

        **Returns:**
        - `FST | None`: Node found if any.

        **Examples:**

        >>> FST('var', 'exec').find_loc(0, 0, 0, 3)
        <Name 0,0..0,3>

        >>> FST('var', 'exec').find_loc(0, 0, 0, 3, exact_top=True)
        <Module ROOT 0,0..0,3>

        >>> FST('var', 'exec').find_loc(0, 1, 0, 2)
        <Name 0,0..0,3>

        >>> FST('var', 'exec').find_loc(0, 1, 0, 2, exact_top=True)
        <Name 0,0..0,3>

        >>> FST('var', 'exec').find_loc(0, 0, 1, 4)
        <Module ROOT 0,0..0,3>

        >>> repr(FST('var', 'exec').find_loc(0, 2, 1, 4))
        'None'
        """

        f = self.find_contains_loc(ln, col, end_ln, end_col, 'top' if exact_top else True)

        if not f:
            return self.find_in_loc(ln, col, end_ln, end_col)

        fln, fcol, fend_ln, fend_col = f.loc

        if fcol == col and fend_col == end_col and fln == ln and fend_ln == end_ln:
            return f

        return f.find_in_loc(ln, col, end_ln, end_col) or f

    # TODO: more types of search

    # ------------------------------------------------------------------------------------------------------------------
    # Predicates

    def is_parenthesizable(self, *, star: bool = True) -> bool:
        """Whether `self` is parenthesizable with grouping parentheses or not. `True` for all `pattern`s and almost all
        `expr`s (those which which are not `Slice`, `FormattedValue` or `Interpolation` and are not themselves inside
        `pattern`s).

        **Note:** `Starred` may return `True` even though the `Starred` itself is not parenthesizable but rather its
        child is.

        **Parameters:**
        - `star`: Whether to return top-level `Starred` as parenthesizable or not. It is convenient to consider it
            parenthesizable like a normal expression since its children are parenthesizable and that is what gets
            parenthesized if you try to `par()` a `Starred`.

        **Returns:**
        - `bool`: Whether is syntactically legal to add grouping parentheses or not. Can always be forced.

        **Examples:**

        >>> FST('i + j').is_parenthesizable()  # expr
        True

        >>> FST('{a.b: c, **d}', 'pattern').is_parenthesizable()
        True

        >>> FST('a:b:c').is_parenthesizable()  # Slice
        False

        >>> FST('for i in j').is_parenthesizable()  # comprehension
        False

        >>> FST('a: int, b=2', 'arguments').is_parenthesizable()  # arguments
        False

        >>> FST('a: int', 'arg').is_parenthesizable()
        False

        >>> FST('key="word"', 'keyword').is_parenthesizable()
        False

        >>> FST('a as b', 'alias').is_parenthesizable()
        False

        >>> f = FST('with a: pass')
        >>> f.items[0].is_parenthesizable()  # withitem is not parenthesizable
        False
        >>> f.items[0].context_expr.is_parenthesizable()  # the expr in it is
        True

        >>> f = FST('case 1: pass')
        >>> f.pattern.is_parenthesizable()  # pattern is parenthesizable
        True
        >>> f.pattern.value.is_parenthesizable()  # expr in pattern is not
        False
        """

        ast_cls = self.a.__class__

        if ast_cls not in ASTS_LEAF_EXPR:
            return ast_cls in ASTS_LEAF_PATTERN

        if ast_cls in (
            (Slice, FormattedValue, Interpolation)
            if star else
            (Starred, Slice, FormattedValue, Interpolation)
        ):
            return False

        if parent := self.parent:
            if ast_cls is Constant and parent.a.__class__ in ASTS_LEAF_FTSTR:
                return False

            while True:
                ast_cls = parent.a.__class__

                if ast_cls not in ASTS_LEAF_EXPR:
                    if ast_cls in ASTS_LEAF_PATTERN:
                        return False

                    break

                if not (parent := parent.parent):
                    break

        return True

    def is_parenthesized_tuple(self) -> bool | None:
        """Whether `self` is a parenthesized `Tuple` or not, or not a `Tuple` at all.

        **Returns:**
        - `True`: Is a parenthesized `Tuple` node.
        - `False`: Is an unparenthesized `Tuple` node.
        - `None`: Is not a `Tuple` node.

        **Examples:**

        >>> FST('1, 2').is_parenthesized_tuple()
        False

        >>> FST('(1, 2)').is_parenthesized_tuple()
        True

        >>> print(FST('1').is_parenthesized_tuple())
        None
        """

        return self._is_delimited_seq() if self.a.__class__ is Tuple else None

    def is_delimited_matchseq(self) -> Literal['', '[]', '()'] | None:
        r"""Whether `self` is a delimited `MatchSequence` or not (parenthesized or bracketed), or not a `MatchSequence`
        at all.

        **Returns:**
        - `'()'` or `'[]'`: Is a `MatchSequence` delimited with these delimiters.
        - `''`: Is an undelimited `MatchSequence`.
        - `None`: Is not a `MatchSequence`.

        **Examples:**

        >>> FST('case 1, 2: pass').pattern.is_delimited_matchseq()
        ''

        >>> FST('case [1, 2]: pass').pattern.is_delimited_matchseq()
        '[]'

        >>> FST('case (1, 2): pass').pattern.is_delimited_matchseq()
        '()'

        >>> print(FST('case 1: pass').pattern.is_delimited_matchseq())
        None
        """

        if self.a.__class__ is not MatchSequence:
            return None

        ln, col, _, _ = self.loc
        lpar = self.root._lines[ln][col : col + 1]  # could be end of line

        if lpar == '(':
            return '()' if self._is_delimited_seq('patterns', '()') else ''
        if lpar == '[':
            return '[]' if self._is_delimited_seq('patterns', '[]') else ''

        return ''

    def is_empty_arguments(self) -> bool | None:
        """Is this an empty `arguments` node or not an `arguments` node at all?

        **Returns:**
        - `True`: Is an empty `arguments` node.
        - `False`: Is an `arguments` node but not empty.
        - `None`: Is not an `arguments` node.

        **Examples:**

        >>> print(FST('def f(): pass').args.is_empty_arguments())
        True

        >>> print(FST('def f(a, b): pass').args.is_empty_arguments())
        False

        >>> print(FST('def f(): pass').body[0].is_empty_arguments())
        None
        """

        if self.a.__class__ is not arguments:
            return None

        return not ((a := self.a).posonlyargs or a.args or a.vararg or a.kwonlyargs or a.kwarg)

    def is_except_star(self) -> bool | None:
        """Whether `self` is an `except*` `ExceptHandler` or a normal `ExceptHandler`, or not and `ExceptHandler` at
        all.

        **Note:** This function checks the source, not the parent `Try` or `TryStar` node so it will give the correct
        answer even for top-level `ExceptHandler` nodes cut out of their blocks.

        **Returns:**
        - `True`: Is an `except*` `ExceptHandler`.
        - `False`: Is a normal `ExceptHandler`.
        - `None`: Is not an `ExceptHandler`.

        **Examples:**

        >>> import sys

        >>> if sys.version_info[:2] >= (3, 11):
        ...     f = FST('try: pass\\nexcept* Exception: pass')
        ...     print(f.handlers[0].is_except_star())
        ... else:
        ...     print(True)
        True

        >>> if sys.version_info[:2] >= (3, 11):
        ...     f = FST('try: pass\\nexcept Exception: pass')
        ...     print(f.handlers[0].is_except_star())
        ... else:
        ...     print(False)
        False

        >>> print(FST('i = 1').is_except_star())
        None
        """

        if self.a.__class__ is not ExceptHandler:
            return None

        ln, col, end_ln, end_col = self.loc

        return next_frag(self.root._lines, ln, col + 6, end_ln, end_col).src.startswith('*')  # something must be there

    def is_elif(self) -> bool | None:
        r"""Whether `self` is an `elif` or not, or not an `If` at all.

        **Returns:**
        - `True`: Is an `elif` `If`.
        - `False`: Is a normal `If`.
        - `None`: Is not an `If`.

        **Examples:**

        >>> FST('if 1: pass\nelif 2: pass').orelse[0].is_elif()
        True

        >>> FST('if 1: pass\nelse:\n  if 2: pass').orelse[0].is_elif()
        False

        >>> print(FST('if 1: pass\nelse:\n  i = 2').orelse[0].is_elif())
        None
        """

        if self.a.__class__ is not If:
            return None

        ln, col, _, _ = self.loc

        return self.root._lines[ln].startswith('elif', col)

    @property
    def is_mod(self) -> bool:
        """Is a `mod` node."""

        return self.a.__class__ in ASTS_LEAF_MOD

    @property
    def is_stmt(self) -> bool:
        """Is a `stmt` node."""

        return self.a.__class__ in ASTS_LEAF_STMT

    @property
    def is_expr(self) -> bool:
        """Is an `expr` node."""

        return self.a.__class__ in ASTS_LEAF_EXPR

    @property
    def is_expr_context(self) -> bool:
        """Is an `expr_context` node."""

        return self.a.__class__ in ASTS_LEAF_EXPR_CONTEXT

    @property
    def is_boolop(self) -> bool:
        """Is a `boolop` node."""

        return self.a.__class__ in ASTS_LEAF_BOOLOP

    @property
    def is_operator(self) -> bool:
        """Is an `operator` node."""

        return self.a.__class__ in ASTS_LEAF_OPERATOR

    @property
    def is_unaryop(self) -> bool:
        """Is a `unaryop` node."""

        return self.a.__class__ in ASTS_LEAF_UNARYOP

    @property
    def is_cmpop(self) -> bool:
        """Is a `cmpop` node."""

        return self.a.__class__ in ASTS_LEAF_CMPOP

    @property
    def is_excepthandler(self) -> bool:
        """Is a `excepthandler` node."""

        return self.a.__class__ is ExceptHandler  # here for completeness

    @property
    def is_pattern(self) -> bool:
        """Is a `pattern` node."""

        return self.a.__class__ in ASTS_LEAF_PATTERN

    @property
    def is_type_ignore(self) -> bool:
        """Is a `type_ignore` node."""

        return self.a.__class__ is TypeIgnore  # here for completeness

    @property
    def is_type_param(self) -> bool:
        """Is a `type_param` node."""

        return self.a.__class__ in ASTS_LEAF_TYPE_PARAM

    @property
    def is_stmt_or_mod(self) -> bool:
        """Is a `stmt` or `mod` node."""

        return self.a.__class__ in ASTS_LEAF_STMT_OR_MOD

    @property
    def is_stmtlike(self) -> bool:
        """Is a `stmt`, `ExceptHandler` or `match_case` node."""

        return self.a.__class__ in ASTS_LEAF_STMTLIKE

    @property
    def is_stmtlike_or_mod(self) -> bool:
        """Is a `stmt`, `ExceptHandler`, `match_case` or `mod` node."""

        return self.a.__class__ in ASTS_LEAF_STMTLIKE_OR_MOD

    @property
    def is_block(self) -> bool:
        """Is a node which opens a block. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `For`,
        `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`, `TryStar`, `ExceptHandler` or `match_case`."""

        return self.a.__class__ in ASTS_LEAF_BLOCK

    @property
    def is_block_or_mod(self) -> bool:
        """Is a node which opens a block. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `For`,
        `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`, `TryStar`, `ExceptHandler`, `match_case` or
        `mod`."""

        return self.a.__class__ in ASTS_LEAF_BLOCK_OR_MOD

    @property
    def is_scope(self) -> bool:
        """Is a node which opens a scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Lambda`,
        `ListComp`, `SetComp`, `DictComp` or `GeneratorExp`."""

        return self.a.__class__ in ASTS_LEAF_SCOPE

    @property
    def is_scope_or_mod(self) -> bool:
        """Is a node which opens a scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Lambda`,
        `ListComp`, `SetComp`, `DictComp`, `GeneratorExp` or `mod`."""

        return self.a.__class__ in ASTS_LEAF_SCOPE_OR_MOD

    @property
    def is_named_scope(self) -> bool:
        """Is a node which opens a named scope. Types include `FunctionDef`, `AsyncFunctionDef` or `ClassDef`."""

        return self.a.__class__ in ASTS_LEAF_SCOPE_NAMED

    @property
    def is_named_scope_or_mod(self) -> bool:
        """Is a node which opens a named scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef` or `mod`."""

        return self.a.__class__ in ASTS_LEAF_SCOPE_NAMED_OR_MOD

    @property
    def is_anon_scope(self) -> bool:
        """Is a node which opens an anonymous scope. Types include `Lambda`, `ListComp`, `SetComp`, `DictComp` or
        `GeneratorExp`."""

        return self.a.__class__ in ASTS_LEAF_SCOPE_ANON

    @property
    def is_funcdef(self) -> bool:
        """Is a sync or async function definition node, `FunctionDef` or `AsyncFunctionDef`."""

        return self.a.__class__ in ASTS_LEAF_FUNCDEF

    @property
    def is_def(self) -> bool:
        """Is a sync or async function or class definition node, `FunctionDef`, `AsyncFunctionDef` or `ClassDef`."""

        return self.a.__class__ in ASTS_LEAF_DEF

    @property
    def is_def_or_mod(self) -> bool:
        """Is a sync or async function or class definition node, `FunctionDef`, `AsyncFunctionDef`, `ClassDef` or
        `mod`."""

        return self.a.__class__ in ASTS_LEAF_DEF_OR_MOD

    @property
    def is_for(self) -> bool:
        """Is a sync or async `for` node, `For` or `AsyncFor`, different from `is_For` or `is_AsyncFor`."""

        return self.a.__class__ in ASTS_LEAF_FOR

    @property
    def is_with(self) -> bool:
        """Is a sync or async `with` node, `With` or `AsyncWith`, different from `is_For` or `is_AsyncFor`."""

        return self.a.__class__ in ASTS_LEAF_WITH

    @property
    def is_try(self) -> bool:
        """Is a `Try` or `TryStar` node, different from `is_Try` or `is_TryStar`."""

        return self.a.__class__ in ASTS_LEAF_TRY

    @property
    def is_import(self) -> bool:
        """Is an `Import` or `ImportFrom` node, different from `is_Import` or `is_ImportFrom`."""

        return self.a.__class__ in ASTS_LEAF_IMPORT

    @property
    def is_ftstr(self) -> bool:
        """Is an f-string `JoinedStr` or t-string `TemplateStr` node."""

        return self.a.__class__ in ASTS_LEAF_FTSTR

    @property
    def is_ftstr_fmt(self) -> bool:
        """Is an f-string `FormattedValue` or t-string `Interpolation` node."""

        return self.a.__class__ in ASTS_LEAF_FTSTR_FMT

    @property
    def is__slice(self) -> bool:
        """Is one of our own custom SPECIAL SLICE nodes."""

        return self.a.__class__ in ASTS_LEAF__SLICE

    is_Module = fst_type_predicates.is_Module  # we do assign instead of import so that pdoc gets the right order
    is_Interactive = fst_type_predicates.is_Interactive
    is_Expression = fst_type_predicates.is_Expression
    is_FunctionType = fst_type_predicates.is_FunctionType
    is_FunctionDef = fst_type_predicates.is_FunctionDef
    is_AsyncFunctionDef = fst_type_predicates.is_AsyncFunctionDef
    is_ClassDef = fst_type_predicates.is_ClassDef
    is_Return = fst_type_predicates.is_Return
    is_Delete = fst_type_predicates.is_Delete
    is_Assign = fst_type_predicates.is_Assign
    is_TypeAlias = fst_type_predicates.is_TypeAlias
    is_AugAssign = fst_type_predicates.is_AugAssign
    is_AnnAssign = fst_type_predicates.is_AnnAssign
    is_For = fst_type_predicates.is_For
    is_AsyncFor = fst_type_predicates.is_AsyncFor
    is_While = fst_type_predicates.is_While
    is_If = fst_type_predicates.is_If
    is_With = fst_type_predicates.is_With
    is_AsyncWith = fst_type_predicates.is_AsyncWith
    is_Match = fst_type_predicates.is_Match
    is_Raise = fst_type_predicates.is_Raise
    is_Try = fst_type_predicates.is_Try
    is_TryStar = fst_type_predicates.is_TryStar
    is_Assert = fst_type_predicates.is_Assert
    is_Import = fst_type_predicates.is_Import
    is_ImportFrom = fst_type_predicates.is_ImportFrom
    is_Global = fst_type_predicates.is_Global
    is_Nonlocal = fst_type_predicates.is_Nonlocal
    is_Expr = fst_type_predicates.is_Expr
    is_Pass = fst_type_predicates.is_Pass
    is_Break = fst_type_predicates.is_Break
    is_Continue = fst_type_predicates.is_Continue
    is_BoolOp = fst_type_predicates.is_BoolOp
    is_NamedExpr = fst_type_predicates.is_NamedExpr
    is_BinOp = fst_type_predicates.is_BinOp
    is_UnaryOp = fst_type_predicates.is_UnaryOp
    is_Lambda = fst_type_predicates.is_Lambda
    is_IfExp = fst_type_predicates.is_IfExp
    is_Dict = fst_type_predicates.is_Dict
    is_Set = fst_type_predicates.is_Set
    is_ListComp = fst_type_predicates.is_ListComp
    is_SetComp = fst_type_predicates.is_SetComp
    is_DictComp = fst_type_predicates.is_DictComp
    is_GeneratorExp = fst_type_predicates.is_GeneratorExp
    is_Await = fst_type_predicates.is_Await
    is_Yield = fst_type_predicates.is_Yield
    is_YieldFrom = fst_type_predicates.is_YieldFrom
    is_Compare = fst_type_predicates.is_Compare
    is_Call = fst_type_predicates.is_Call
    is_FormattedValue = fst_type_predicates.is_FormattedValue
    is_Interpolation = fst_type_predicates.is_Interpolation
    is_JoinedStr = fst_type_predicates.is_JoinedStr
    is_TemplateStr = fst_type_predicates.is_TemplateStr
    is_Constant = fst_type_predicates.is_Constant
    is_Attribute = fst_type_predicates.is_Attribute
    is_Subscript = fst_type_predicates.is_Subscript
    is_Starred = fst_type_predicates.is_Starred
    is_Name = fst_type_predicates.is_Name
    is_List = fst_type_predicates.is_List
    is_Tuple = fst_type_predicates.is_Tuple
    is_Slice = fst_type_predicates.is_Slice
    is_Load = fst_type_predicates.is_Load
    is_Store = fst_type_predicates.is_Store
    is_Del = fst_type_predicates.is_Del
    is_And = fst_type_predicates.is_And
    is_Or = fst_type_predicates.is_Or
    is_Add = fst_type_predicates.is_Add
    is_Sub = fst_type_predicates.is_Sub
    is_Mult = fst_type_predicates.is_Mult
    is_MatMult = fst_type_predicates.is_MatMult
    is_Div = fst_type_predicates.is_Div
    is_Mod = fst_type_predicates.is_Mod
    is_Pow = fst_type_predicates.is_Pow
    is_LShift = fst_type_predicates.is_LShift
    is_RShift = fst_type_predicates.is_RShift
    is_BitOr = fst_type_predicates.is_BitOr
    is_BitXor = fst_type_predicates.is_BitXor
    is_BitAnd = fst_type_predicates.is_BitAnd
    is_FloorDiv = fst_type_predicates.is_FloorDiv
    is_Invert = fst_type_predicates.is_Invert
    is_Not = fst_type_predicates.is_Not
    is_UAdd = fst_type_predicates.is_UAdd
    is_USub = fst_type_predicates.is_USub
    is_Eq = fst_type_predicates.is_Eq
    is_NotEq = fst_type_predicates.is_NotEq
    is_Lt = fst_type_predicates.is_Lt
    is_LtE = fst_type_predicates.is_LtE
    is_Gt = fst_type_predicates.is_Gt
    is_GtE = fst_type_predicates.is_GtE
    is_Is = fst_type_predicates.is_Is
    is_IsNot = fst_type_predicates.is_IsNot
    is_In = fst_type_predicates.is_In
    is_NotIn = fst_type_predicates.is_NotIn
    is_comprehension = fst_type_predicates.is_comprehension
    is_ExceptHandler = fst_type_predicates.is_ExceptHandler
    is_arguments = fst_type_predicates.is_arguments
    is_arg = fst_type_predicates.is_arg
    is_keyword = fst_type_predicates.is_keyword
    is_alias = fst_type_predicates.is_alias
    is_withitem = fst_type_predicates.is_withitem
    is_match_case = fst_type_predicates.is_match_case
    is_MatchValue = fst_type_predicates.is_MatchValue
    is_MatchSingleton = fst_type_predicates.is_MatchSingleton
    is_MatchSequence = fst_type_predicates.is_MatchSequence
    is_MatchMapping = fst_type_predicates.is_MatchMapping
    is_MatchClass = fst_type_predicates.is_MatchClass
    is_MatchStar = fst_type_predicates.is_MatchStar
    is_MatchAs = fst_type_predicates.is_MatchAs
    is_MatchOr = fst_type_predicates.is_MatchOr
    is_TypeIgnore = fst_type_predicates.is_TypeIgnore
    is_TypeVar = fst_type_predicates.is_TypeVar
    is_ParamSpec = fst_type_predicates.is_ParamSpec
    is_TypeVarTuple = fst_type_predicates.is_TypeVarTuple
    is__ExceptHandlers = fst_type_predicates.is__ExceptHandlers
    is__match_cases = fst_type_predicates.is__match_cases
    is__Assign_targets = fst_type_predicates.is__Assign_targets
    is__decorator_list = fst_type_predicates.is__decorator_list
    is__arglikes = fst_type_predicates.is__arglikes
    is__comprehensions = fst_type_predicates.is__comprehensions
    is__comprehension_ifs = fst_type_predicates.is__comprehension_ifs
    is__aliases = fst_type_predicates.is__aliases
    is__withitems = fst_type_predicates.is__withitems
    is__type_params = fst_type_predicates.is__type_params

    # ------------------------------------------------------------------------------------------------------------------
    # Private

    from .fst_core import (
        _make_fst_tree,
        _unmake_fst_tree,
        _unmake_fst_parents,
        _set_ast,
        _set_field,
        _set_ctx,
        _set_start_pos,
        _set_end_pos,

        _is_atom,
        _is_enclosed_or_line,
        _is_enclosed_in_parents,
        _get_parse_mode,
        _get_block_indent,
        _get_indentable_lns,

        _modifying,
        _touch,
        _touchall,
        _offset,
        _offset_lns,
        _indent_lns,
        _dedent_lns,
        _redent_lns,

        _get_src,
        _put_src,
        _sanitize,
        _make_fst_and_dedent,
    )

    from .fst_misc import (
        _repr_tail,
        _dump,
        _cached_allargs,
        _cached_arglikes,

        _is_expr_arglike_only,
        _is_solo_class_base,
        _is_solo_call_arg,
        _is_solo_call_arg_genexp,
        _is_solo_matchcls_pat,
        _is_any_parent_format_spec_start_pos,
        _is_delimited_seq,
        _has_Slice,
        _has_Starred,

        _trail_sep,
        _maybe_ins_sep,
        _maybe_add_singleton_comma,
        _maybe_add_line_continuations,
        _fix_joined_alnums,
        _fix_undelimited_seq,
        _fix_Tuple,
        _fix_Set,
        _fix_arglikes,
        _fix_elif,
        _fix_copy,

        _parenthesize_grouping,
        _unparenthesize_grouping,
        _delimit_node,
        _undelimit_node,
        _trim_delimiters,
        _normalize_block,

        _getput_line_comment,
    )

    from .fst_traverse import (
        _next_bound,
        _prev_bound,
        _next_bound_step,
        _prev_bound_step,
    )

    from .fst_locs import (
        _loc_maybe_key,
        _loc_arguments,
        _loc_comprehension,
        _loc_withitem,
        _loc_match_case,
        _loc_op,
        _loc_block_header_end,
        _loc_comprehension_if,
        _loc_argument,
        _loc_decorator,
        _loc_Lambda_args_entire,
        _loc_ClassDef_bases_pars,
        _loc_ImportFrom_names_pars,
        _loc_With_items_pars,
        _loc_BoolOp_op,
        _loc_Call_pars,
        _loc_Subscript_brackets,
        _loc_MatchMapping_rest,
        _loc_MatchClass_pars,
        _loc_FunctionDef_type_params_brackets,
        _loc_ClassDef_type_params_brackets,
        _loc_TypeAlias_type_params_brackets,
        _loc_Global_Nonlocal_names,
    )

    from .fst_options import (
        _get_opt_eff_pars_arglike,
        _get_opt_eff_norm_self,
        _get_opt_eff_norm_get,
        _get_opt_eff_set_norm_self,
        _get_opt_eff_set_norm_get,
    )

    from .fst_raw import _reparse_raw
    from .fst_get_slice import _get_slice
    from .fst_put_slice import _put_slice
    from .fst_get_one import _get_one
    from .fst_put_one import _put_one

    # ------------------------------------------------------------------------------------------------------------------
    # AST field accessors

    from .fst_accessors import (
        body,
        type_ignores,
        argtypes,
        returns,
        decorator_list,
        name,
        type_params,
        args,
        type_comment,
        bases,
        keywords,
        value,
        targets,
        target,
        op,
        annotation,
        simple,
        iter,
        orelse,
        test,
        items,
        subject,
        cases,
        exc,
        cause,
        handlers,
        finalbody,
        msg,
        names,
        module,
        level,
        values,
        left,
        right,
        operand,
        keys,
        elts,
        elt,
        generators,
        key,
        ops,
        comparators,
        func,
        conversion,
        format_spec,
        str,
        kind,
        attr,
        ctx,
        slice,
        id,
        lower,
        upper,
        step,
        ifs,
        is_async,
        type,
        posonlyargs,
        defaults,
        vararg,
        kwonlyargs,
        kw_defaults,
        kwarg,
        arg,
        asname,
        context_expr,
        optional_vars,
        pattern,
        guard,
        patterns,
        rest,
        cls,
        kwd_attrs,
        kwd_patterns,
        tag,
        bound,
        default_value,
        arglikes,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Virtual field accessors

    @property
    def _all(self: FST) -> fstview:
        """Virtual `_all` field view for `Dict`, `MatchMapping`, `Compare` and `arguments`.

        **Examples:**

        >>> FST('{a: b, c: d, e: f}')._all[1:2].copy().src
        '{c: d}'

        >>> FST('{1: a, 2: b, **rest}', 'MatchMapping')._all[1:].copy().src
        '{2: b, **rest}'

        >>> FST('a < b == c > d')._all[1:3].copy().src
        'b == c'

        >>> FST('def f(a=1, *b, c: int = 3, **d): pass').args._all[-2:].copy().src
        '*, c: int = 3, **d'

        @public
        """

        if view_cls := _VIRTUAL_FIELD_VIEW__ALL.get(self.a.__class__):
            return view_cls(self, '_all')

        raise AttributeError(f"{self.a.__class__.__name__} does not have virtual field '_all'")

    @_all.setter
    def _all(self: FST, code: Code | None) -> None:
        self._put_slice(code, 0, 'end', '_all')

    @_all.deleter
    def _all(self: FST) -> None:
        self._put_slice(None, 0, 'end', '_all')

    @property
    def _body(self: FST) -> fstview:
        r"""Virtual `_body` field for statements. Special field view for statements which excludes a docstring if
        present from the list and indexing.

        **Examples:**

        >>> f = FST('''
        ... def func():
        ...     \'\'\'docstring\'\'\'
        ...     first_stmt()
        ...     second_stmt()
        ... '''.strip())

        >>> f._body[0].src
        'first_stmt()'

        >>> list(f.src for f in reversed(f._body))
        ['second_stmt()', 'first_stmt()']

        >>> f._body[0] = 'replacement_stmt'
        >>> print(f.src)
        def func():
            '''docstring'''
            replacement_stmt
            second_stmt()

        @public
        """

        ast_cls = self.a.__class__

        if ast_cls in ASTS_LEAF_MAYBE_DOCSTR:
            return fstview__body(self, '_body')

        if ast_cls in ASTS_LEAF_BLOCK:
            return fstview(self, 'body')

        raise AttributeError(f"{ast_cls.__name__} does not have virtual field '_body'")

    @_body.setter
    def _body(self: FST, code: Code | None) -> None:
        self._put_slice(code, 0, 'end', '_body')

    @_body.deleter
    def _body(self: FST) -> None:
        self._put_slice(None, 0, 'end', '_body')

    @property
    def _args(self: FST) -> fstview:
        """Virtual `_args` field view for merged `Call.args+keywords`.

        **Examples:**

        >>> list(f.src for f in FST('call(a, *not b, c=d, *e, **h, f=g)')._args)
        ['a', '*not b', 'c=d', '*e', '**h', 'f=g']

        >>> FST('call(a, *not b, c=d, *e, **h, f=g)')._args[1:-1].copy().src
        '*not b, c=d, *e, **h'

        >>> FST('call(a, b, c, d)').put_slice('k=w, *s', 1, 'end').src
        'call(a, k=w, *s)'

        >>> FST('call(a, b)').put('k=w', 0)
        Traceback (most recent call last):
        ...
        fst.NodeError: keyword arglike cannot precede positional arglike

        @public
        """

        if self.a.__class__ is Call:
            return fstview_arglikes(self, '_args')

        raise AttributeError(f"{self.a.__class__.__name__} does not have virtual field '_args'")

    @_args.setter
    def _args(self: FST, code: Code | None) -> None:
        self._put_slice(code, 0, 'end', '_args')

    @_args.deleter
    def _args(self: FST) -> None:
        self._put_slice(None, 0, 'end', '_args')

    @property
    def _bases(self: FST) -> fstview:
        """Virtual `_bases` field view for merged `ClassDef.bases+keywords`.

        **Examples:**

        >>> list(f.src for f in FST('class cls(a, *not b, c=d, *e, **h): pass')._bases)
        ['a', '*not b', 'c=d', '*e', '**h']

        >>> FST('class cls(base, meta=cls, *other_bases): pass')._bases[-2:].copy().src
        'meta=cls, *other_bases'

        >>> f = FST('class cls(base, meta=cls): pass')

        >>> del f._bases

        >>> print(f.src)
        class cls: pass

        @public
        """

        if self.a.__class__ is ClassDef:
            return fstview_arglikes(self, '_bases')

        raise AttributeError(f"{self.a.__class__.__name__} does not have virtual field '_bases'")

    @_bases.setter
    def _bases(self: FST, code: Code | None) -> None:
        self._put_slice(code, 0, 'end', '_bases')

    @_bases.deleter
    def _bases(self: FST) -> None:
        self._put_slice(None, 0, 'end', '_bases')


_VIRTUAL_FIELD_VIEW__ALL = {
    Dict:         fstview_Dict,
    MatchMapping: fstview_MatchMapping,
    Compare:      fstview_Compare,
    arguments:    fstview_arguments,
}
