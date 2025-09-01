"""Main FST module. Contains the `FST` class as well as drop-in replacement `parse()` and `unparse()` functions for
their respective `ast` module counterparts."""

from __future__ import annotations

import builtins  # because of the unfortunate choice for the name of an Interpolation field, '.str', we have a '.str' property in FST which messes with the type annotations
from ast import iter_fields
from ast import dump as ast_dump, unparse as ast_unparse, mod as ast_mod
from contextlib import contextmanager
from io import TextIOBase
from typing import Any, Callable, Generator, Iterator, Literal, Mapping, TextIO, Union

from .asttypes import (
    AST,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    Attribute,
    Call,
    ClassDef,
    Constant,
    Dict,
    DictComp,
    ExceptHandler,
    Expression,
    For,
    FormattedValue,
    FunctionDef,
    GeneratorExp,
    If,
    ImportFrom,
    Interactive,
    IsNot,
    JoinedStr,
    Lambda,
    List,
    ListComp,
    Load,
    Match,
    MatchClass,
    MatchMapping,
    MatchSequence,
    MatchSingleton,
    MatchStar,
    MatchValue,
    Module,
    Name,
    NamedExpr,
    NotIn,
    Pass,
    Set,
    SetComp,
    Slice,
    Starred,
    Subscript,
    Try,
    Tuple,
    TypeIgnore,
    While,
    With,
    alias,
    arg,
    arguments,
    boolop,
    cmpop,
    comprehension,
    expr,
    expr_context,
    keyword,
    match_case,
    mod,
    operator,
    pattern,
    stmt,
    unaryop,
    withitem,
    TryStar,
    TypeAlias,
    type_param,
    TemplateStr,
    Interpolation,
)

from .astutil import (
    bistr, constant, FIELDS, AST_FIELDS, OPCLS2STR, OPSTR2CLS_AUG, WalkFail,
    has_type_comments, compare_asts, copy_ast, last_block_header_child, syntax_ordered_children,
)

from .misc import (
    PYLT13,
    EXPRISH_ALL, STMTISH, STMTISH_OR_MOD, BLOCK, BLOCK_OR_MOD, SCOPE, SCOPE_OR_MOD, NAMED_SCOPE,
    NAMED_SCOPE_OR_MOD, ANONYMOUS_SCOPE,
    astfield, fstloc, fstlocns, nspace,
    re_empty_line, re_line_continuation, re_line_end_cont_or_comment,
    Self,
    next_frag, next_find, next_delims, prev_delims,
    swizzle_getput_params, fixup_field_body,
    multiline_str_continuation_lns, multiline_fstr_continuation_lns, continuation_to_uncontinued_lns,
)

from .traverse import AST_FIELDS_NEXT, AST_FIELDS_PREV, check_with_loc
from .reconcile import Reconcile
from .extparse import Mode, get_special_parse_mode
from .code import Code, code_as_all
from .view import fstview
from . import extparse

__all__ = [
    'parse', 'unparse', 'dump', 'FST',
]

_DEFAULT_PARSE_PARAMS = dict(filename='<unknown>', type_comments=False, feature_version=None)
_DEFAULT_INDENT       = '    '

_OPTIONS = {
    'pars':             'auto', # True | False | 'auto'
    'raw':              False,  # True | False | 'auto'
    'trivia':           True,   # True | False | 'all' | 'block' | (True | False | 'all' | 'block', True | False | 'all' | 'block' | 'line'), True means ('block', 'line')
    'elif_':            True,   # True | False
    'docstr':           True,   # True | False | 'strict'
    'pars_walrus':      False,  # True | False
    'fix_set_get':      True,   # True | False | 'star' | 'call' | 'tuple'
    'fix_set_put':      True,   # True | False | 'star' | 'call' | 'both'
    'fix_set_self':     True,   # True | False | 'star' | 'call'
    'fix_del_self':     True,   # True | False
    'fix_assign_self':  True,   # True | False
    'fix_matchor_get':  True,   # True | False | 'strict'
    'fix_matchor_put':  True,   # True | False | 'strict'
    'fix_matchor_self': True,   # True | False | 'strict'
    'pep8space':        True,   # True | False | 1
    'precomms':         True,   # True | False | 'all'
    'postcomms':        True,   # True | False | 'all' | 'block'
    'prespace':         False,  # True | False | int
    'postspace':        False,  # True | False | int
}

# ----------------------------------------------------------------------------------------------------------------------

def parse(source: builtins.str, filename: str = '<unknown>', mode: str = 'exec', *, type_comments: bool = False,
          feature_version: tuple[int, int] | None = None, **kwargs) -> AST:
    r"""Executes `ast.parse()` and then adds `FST` nodes to the parsed tree. Drop-in replacement for `ast.parse()`. For
    parameters, see `ast.parse()`. Returned `AST` tree has added `.f` attribute at each node which accesses the parallel
    `FST` tree.

    **Parameters:**
    - `source`: The python source to parse.
    - `filename`: `ast.parse()` parameter.
    - `mode`: Parse mode, extended `ast.parse()` parameter, See `fst.extparse.Mode`.
    - `type_comments`: `ast.parse()` parameter.
    - `feature_version`: `ast.parse()` parameter.

    **Returns:**
    - `AST`: Tree with an `FST` `.f` attribute added to each `AST` node.

    **Examples:**
    ```py
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

    >>> a.f.dump()
    Module - ROOT 0,0..1,7
      .body[1]
      0] If - 0,0..1,7
        .test Constant 1 - 0,3..0,4
        .body[1]
        0] Assign - 1,2..1,7
          .targets[1]
          0] Name 'i' Store - 1,2..1,3
          .value Constant 2 - 1,6..1,7
    ```
    """

    return FST.fromsrc(source, mode, filename=filename, type_comments=type_comments, feature_version=feature_version,
                       **kwargs).a


def unparse(ast_obj: AST) -> str:
    """Returns the formatted source that is kept for this tree. Drop-in replacement for `ast.unparse()` If there is no
    `FST` information in the `AST` tree then just executes `ast.unparse()`.

    **Parameters:**
    - `ast_obj`: The `AST` to unparse.

    **Returns:**
    - `str`: The unparsed source code, formatted if it came from `FST`.

    **Examples:**
    ```py
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
    ```
    """

    if (f := getattr(ast_obj, 'f', None)) and isinstance(f, FST):
        if f.is_root:
            return f.src

        try:
            return f.copy().src
        except Exception:
            pass

    return ast_unparse(ast_obj)


def dump(node: AST, annotate_fields: bool = True, include_attributes: bool = False, *,
         indent: int | str | None = None, show_empty: bool = True) -> str:
    """This function is a convenience function and only exists to make python version 3.13 and above `ast.dump()` output
    compatible on a default call with previous python versions (important for doctests). All arguments correspond to
    their respective `ast.dump()` arguments and `show_empty` is eaten on python versions below 3.13."""

    if PYLT13:
        return ast_dump(node, annotate_fields, include_attributes, indent=indent)
    else:
        return ast_dump(node, annotate_fields, include_attributes, indent=indent, show_empty=show_empty)


class FST:
    """Class which maintains structure and formatted source code for an `AST` tree. An instance of this class is added
    to each `AST` node in a tree. It provides format-preserving operations as well as ability to navigate the tree in
    any direction."""

    a:            AST              ; """The actual `AST` node."""
    parent:       FST | None       ; """Parent `FST` node, `None` in root node."""
    pfield:       astfield | None  ; """The `astfield` location of this node in the parent, `None` in root node."""
    root:         FST              ; """The root node of this tree, `self` in root node."""
    _cache:       dict

    # ROOT ONLY
    parse_params: Mapping[builtins.str, Any]  ; """The parameters to use for any `ast.parse()` that needs to be done (filename, type_comments, feature_version), root node only."""
    indent:       builtins.str                ; """The default single level of block indentation string for this tree when not available from context, root node only."""
    _lines:       list[bistr]
    _serial:      int

    # class attributes
    is_FST:       bool = True      ; """@private"""  # for quick checks vs. `fstloc` or `fstview`

    @property
    def lines(self) -> list[builtins.str] | None:
        """Whole lines which contain this node, may also contain parts of enclosing nodes. If gotten at root then the
        entire source is returned, which may extend beyond the location of the top level node (mostly for statements
        which may have leading / trailing comments or empty lines)."""

        if self.is_root:
            return self._lines
        elif loc := self.bloc:
            return self.root._lines[loc.ln : loc.end_ln + 1]
        elif isinstance(a := self.a, arguments):  # arguments with no loc are empty arguments
            return ['']
        else:
            return [s] if (s := OPCLS2STR.get(a.__class__, None)) else None  # for boolop only really, otherwise None

    @property
    def src(self) -> builtins.str | None:
        """Source code of this node clipped out of as a single string, without any dedentation. Will have indentation as
        it appears in the top level source if multiple lines. If gotten at root then the entire source is returned,
        regardless of whether the actual top level node location includes it or not."""

        if self.is_root:
            return '\n'.join(self._lines)
        elif loc := self.bloc:
            return self.get_src(*loc)
        elif isinstance(a := self.a, arguments):  # arguments with no loc are empty arguments
            return ''
        else:
            return OPCLS2STR.get(a.__class__, None)  # for boolop only really, otherwise None

    @property
    def is_root(self) -> bool:
        """`True` for the root node, `False` otherwise."""

        return self.parent is None

    @property
    def has_own_loc(self) -> bool:
        """`True` when the node has its own location which comes directly from AST `lineno` and other location fields.
        Otherwise `False` if no `loc` or `loc` is calculated."""

        return hasattr(self.a, 'end_col_offset')

    @property
    def whole_loc(self) -> fstloc:
        """Whole source location, from 0,0 to end of source. Works from any node (not just root)."""

        return fstloc(0, 0, len(ls := self.root._lines) - 1, len(ls[-1]))

    @property
    def loc(self) -> fstloc | None:
        """Zero based character indexed location of node (may not be entire location if node has decorators). Not all
        nodes have locations (like `expr_context`). Other nodes which normally don't have locations like `arguments` or
        most operators have this location calculated from their children or source. NOTE: Empty arguments do NOT have
        a location even though the `AST` exists."""

        try:
            return self._cache['loc']
        except KeyError:
            pass

        ast = self.a

        try:
            ln             = ast.lineno - 1
            col_offset     = ast.col_offset
            end_ln         = ast.end_lineno - 1
            end_col_offset = ast.end_col_offset

        except AttributeError:
            if isinstance(ast, arguments):
                loc = self._loc_arguments()
            elif isinstance(ast, comprehension):
                loc = self._loc_comprehension()
            elif isinstance(ast, withitem):
                loc = self._loc_withitem()
            elif isinstance(ast, match_case):
                loc = self._loc_match_case()
            elif isinstance(ast, (boolop, operator, unaryop, cmpop)):
                loc = self._loc_operator()
            elif not self.parent:
                loc = fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))
            else:
                loc = None

        else:
            col     = self.root._lines[ln].b2c(col_offset)
            end_col = self.root._lines[end_ln].b2c(end_col_offset)
            loc     = fstloc(ln, col, end_ln, end_col)

        self._cache['loc'] = loc

        return loc

    @property
    def bloc(self) -> fstloc | None:
        """Bounding location of node, including any preceding decorators. Not all nodes have locations but any node
        which has a `loc` will have a `bloc`. Will be same as `loc` for all nodes except those that have decorators, in
        which case it will start at the first decorator.

        **Note:** This may be changed in the future to include trailing comments belonging to last elements of block
        statements.
        """

        try:
            return self._cache['bloc']
        except KeyError:
            pass

        if (bloc := self.loc) and (decos := getattr(self.a, 'decorator_list', None)):
            bloc = fstloc(decos[0].f.ln, bloc[1], bloc[2], bloc[3])  # column of deco '@' will be same as our column

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
    def bln(self) -> int:  # bounding location including @decorators
        """Line number of the first line of this node or the first decorator if present (0 based). The corresponding
        `bcol`, `bend_ln` and `bend_col` are just aliases for the normal values."""

        return (l := self.bloc) and l[0]

    bcol     = col  # for symmetry
    bend_ln  = end_ln
    bend_col = end_col

    @property
    def lineno(self) -> int:  # 1 based
        """AST-style Line number of the first line of this node (1 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and loc[0] + 1

    @property
    def col_offset(self) -> int:  # byte index
        """AST-style BYTE index of the start of this node (0 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and self.root._lines[loc[0]].c2b(loc[1])

    @property
    def end_lineno(self) -> int:  # 1 based
        """AST-style Line number of the LAST LINE of this node (1 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and loc[2] + 1

    @property
    def end_col_offset(self) -> int:  # byte index
        """AST-style BYTE index one past the end of this node (0 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and self.root._lines[loc[2]].c2b(loc[3])

    @property
    def is_mod(self) -> bool:
        """Is a `mod`."""

        return isinstance(self.a, mod)

    @property
    def is_stmtish(self) -> bool:
        """Is a `stmt`, `ExceptHandler` or `match_case`."""

        return isinstance(self.a, STMTISH)

    @property
    def is_stmt(self) -> bool:
        """Is a `stmt`."""

        return isinstance(self.a, stmt)

    @property
    def is_block(self) -> bool:
        """Is a node which opens a block. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `For`,
        `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`, `TryStar`, `ExceptHandler`, `match_case` or
        `mod`."""

        return isinstance(self.a, BLOCK_OR_MOD)

    @property
    def is_scope(self) -> bool:
        """Is a node which opens a scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Lambda`,
        `ListComp`, `SetComp`, `DictComp`, `GeneratorExp` or `mod`."""

        return isinstance(self.a, SCOPE_OR_MOD)

    @property
    def is_named_scope(self) -> bool:
        """Is a node which opens a named scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef` or `mod`."""

        return isinstance(self.a, NAMED_SCOPE_OR_MOD)

    @property
    def is_anon_scope(self) -> bool:
        """Is a node which opens an anonymous scope. Types include `Lambda`, `ListComp`, `SetComp`, `DictComp` or
        `GeneratorExp`."""

        return isinstance(self.a, ANONYMOUS_SCOPE)

    @property
    def f(self) -> None:
        """@private"""

        raise RuntimeError(f"you probably think you're accessing an AST node '.f', but you're not, "
                           f"you're accessing an FST {self}.f")

    # ------------------------------------------------------------------------------------------------------------------
    # Management

    def __repr__(self) -> builtins.str:
        return f'<{self.a.__class__.__name__}{self._repr_tail()}>'

    def __new__(cls,
                ast_or_src: AST | builtins.str | list[builtins.str] | None,
                mode_or_lines_or_parent: FST | list[builtins.str] | Mode | None = None,
                pfield: astfield | None = None,
                /, **kwargs):
        """Create a new individual `FST` node or full tree. The main way to use this constructor is as a shortcut for
        `FST.fromsrc()` or `FST.fromast()`, the usage is:

        **`FST(ast_or_src, mode=None)`**

        This will create an `FST` from either an `AST` or source code in the form of a string or list of lines. The
        first parameter can be `None` instead of an `AST` or source to indicate a blank new module of one of the three
        types `'exec'`, `'eval'` or `'single'`. Otherwise if there is `source` or an `AST` then `mode` specifies how it
        will be parsed / reparsed and it can take any of the values from `fst.extparse.Mode`.

        **Parameters:**
        - `ast_or_src`: Source code, an `AST` node or `None`.
        - `mode`: See `fst.extparse.Mode`. If this is `None` then if `ast_or_src` is an `AST` the mode defaults to the
            type of the `AST`. Otherwise if the `ast_or_src` is actual source code then `mode` used is `'all'` to allow
            parsing anything. And if `ast_or_src` is `None` then `mode` must be provided and be one of `'exec'`,
            `'eval'` or `'single'`.

        The other forms of this function are meant for internal use and their parameters are below:

        **Parameters:**
        - `ast_or_src`: `AST` node for `FST` or source code in the form of a `str` or a list of lines. If an `AST` then
            will be processed differently depending on if creating child node, top level node or using this as a
            shortcut for a full `fromsrc()` or `fromast()`.
        - `mode_or_lines_or_parent`: Parent node for this child node or lines for a root node creating a new tree. If
            `pfield` is `None` and this is a shortcut to create a full tree from an `AST` node or source provided in
            `ast_or_src`.
        - `pfield`: `astfield` indication position in parent of this node. If provided then creating a simple child node
            and it is created with the `self.parent` set to `mode_or_lines_or_parent` node and `self.pfield` set to
            this. If `None` then it means the creation of a full new `FST` tree and this is the root node with
            `mode_or_lines_or_parent` providing the source.
        - `kwargs`: Contextual parameters:
            - `from_`: If this is provided then it must be an `FST` node from which this node is being created. This
                allows to copy parse parameters and already determined default indentation.
            - `parse_params`: A `dict` with values for `filename`, `type_comments` and `feature_version` which will be
                used for any `AST` reparse done on this tree. Only valid when creating a root node.
            - `indent`: Indentation string to use as default indentation. If not provided and not gotten from `from_`
                then indentation will be inferred from source. Only valid when creating a root node.
            - `filename`, `type_comments` and `feature_version`: If creating from an `AST` or source only then these are
                the parameteres passed to the respective `.new()`, `.fromsrc()` or `.fromast()` functions. Only valid
                when `mode_or_lines_or_parent` and `pfield` are `None`.
        """

        if pfield is None and not isinstance(mode_or_lines_or_parent, list):  # top level shortcut
            params = {k: v for k in ('filename', 'type_comments', 'feature_version')
                      if (v := kwargs.get(k, k)) is not k}  # k used as sentinel
            indent = None

            if from_ := kwargs.get('from_'): # copy parse params from source tree
                params = {**from_.root.parse_params, **params}
                indent = from_.indent

            if ast_or_src is None:
                f = FST.new('exec' if mode_or_lines_or_parent is None else mode_or_lines_or_parent, **params)
            elif isinstance(ast_or_src, AST):
                f = FST.fromast(ast_or_src, mode_or_lines_or_parent, **params)
            else:
                f = FST.fromsrc(ast_or_src, 'all' if mode_or_lines_or_parent is None else mode_or_lines_or_parent,
                                **params)

            if indent is not None or (indent := kwargs.get('indent')) is not None:
                f.indent = indent

            return f

        # creating actual node

        if self := getattr(ast_or_src, 'f', None):  # reuse FST node assigned to AST node (because otherwise it isn't valid anyway)
            self._touch()
        else:
            self = ast_or_src.f = object.__new__(cls)

        self.a       = ast_or_src  # we don't assume `self.a` is `ast_or_src` if `.f` exists
        self.pfield  = pfield
        self._cache  = {}
        self._serial = 0

        if pfield is not None:
            self.parent = mode_or_lines_or_parent
            self.root   = mode_or_lines_or_parent.root

            return self

        # ROOT

        self.parent = None
        self.root   = self
        self._lines = ([bistr(s) for s in mode_or_lines_or_parent] if kwargs.get('lcopy', True) else
                       mode_or_lines_or_parent)

        if from_ := kwargs.get('from_'):  # copy params from source tree
            from_root         = from_.root
            self.parse_params = kwargs.get('parse_params', from_root.parse_params)
            self.indent       = kwargs.get('indent', from_root.indent)

        else:
            self.parse_params = kwargs.get('parse_params', _DEFAULT_PARSE_PARAMS)
            self.indent       = (('?'
                                  if isinstance(ast_or_src, Module) else
                                  _DEFAULT_INDENT)
                                 if (indent := kwargs.get('indent')) is None else
                                 indent)

        self._make_fst_tree()

        if self.indent == '?':  # infer indentation from source, just use first indentation found for performance, don't try to find most common or anything like that
            for a in ast_or_src.body:
                if isinstance(a, (FunctionDef, AsyncFunctionDef, ClassDef, With, AsyncWith, ExceptHandler,
                                  match_case)):  # we check ExceptHandler and match_case because they may be supported as standalone parsed elements eventually
                    indent = a.body[0].f.get_indent()

                elif isinstance(a, (For, AsyncFor, While, If)):
                    if (indent := a.body[0].f.get_indent()) == '?' and (orelse := a.orelse):
                        if not (indent := orelse[0].f.get_indent()):  # because can be 'elif'
                            indent = '?'

                elif isinstance(a, (Try, TryStar)):
                    if (indent := a.body[0].f.get_indent()) == '?':
                        if not (orelse := a.orelse) or (indent := orelse[0].f.get_indent()) == '?':
                            if not (finalbody := a.finalbody) or (indent := finalbody[0].f.get_indent()) == '?':
                                for handler in a.handlers:
                                    if (indent := handler.body[0].f.get_indent()) != '?':
                                        break

                elif isinstance(a, Match):
                    indent = a.cases[0].f.get_indent()

                else:
                    continue

                if indent != '?':
                    self.indent = indent

                    break

            else:
                self.indent = _DEFAULT_INDENT

        return self

    @staticmethod
    def new(mode: Literal['exec', 'eval', 'single'] = 'exec', *, filename: builtins.str = '<unknown>',
            type_comments: bool = False, feature_version: tuple[int, int] | None = None) -> FST:
        """Create a new empty `FST` tree with the top level node dictated by the `mode` parameter.

        **Parameters:**
        - `mode`: `ast.parse()` parameter, can only be `'exec'`, `'eval'` or `'single'` here.
        - `filename`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.

        **Returns:**
        - `FST`: The new empty top level `FST` node.

        **Examples:**
        ```py
        >>> FST.new()
        <Module ROOT 0,0..0,0>

        >>> FST.new(mode='single')
        <Interactive ROOT 0,0..0,0>

        >>> FST.new(mode='eval')
        <Expression ROOT 0,0..0,4>

        >>> _.dump()
        Expression - ROOT 0,0..0,4
          .body Constant None - 0,0..0,4

        >>> _.src
        'None'
        ```
        """

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)

        if mode == 'exec':
            ast = Module(body=[], type_ignores=[])
            src = ''

        elif mode == 'eval':
            ast = Expression(body=Constant(value=None, lineno=1, col_offset=0, end_lineno=1, end_col_offset=4))
            src = 'None'

        elif mode == 'single':
            ast = Interactive(body=[])
            src = ''

        else:
            raise ValueError(f"invalid mode '{mode}' for blank FST")

        return FST(ast, [bistr(src)], parse_params=parse_params, lcopy=False)

    @staticmethod
    def fromsrc(src: builtins.str | list[builtins.str], mode: Mode = 'exec', *, filename: builtins.str = '<unknown>',
                type_comments: bool = False, feature_version: tuple[int, int] | None = None) -> FST:
        """Parse and create a new `FST` tree from source, preserving the original source and locations.

        **Parameters:**
        - `src`: The source to parse as a single `str` or list of individual line strings (without newlines).
        - `mode`: Parse mode, extended `ast.parse()` parameter, See `fst.extparse.Mode`.
        - `filename`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.

        **Returns:**
        - `FST`: The parsed tree with `.f` attributes added to each `AST` node for `FST` access.

        **Examples:**
        ```py
        >>> FST.fromsrc('var').dump()
        Module - ROOT 0,0..0,3
          .body[1]
          0] Expr - 0,0..0,3
            .value Name 'var' Load - 0,0..0,3

        >>> FST.fromsrc('var', mode='stmt').dump()
        Expr - ROOT 0,0..0,3
          .value Name 'var' Load - 0,0..0,3

        >>> FST.fromsrc('var', mode='expr').dump()
        Name 'var' Load - ROOT 0,0..0,3

        >>> FST.fromsrc('except Exception: pass', 'ExceptHandler').dump()
        ExceptHandler - ROOT 0,0..0,22
          .type Name 'Exception' Load - 0,7..0,16
          .body[1]
          0] Pass - 0,18..0,22

        >>> FST.fromsrc('case f(a=1): pass', 'match_case').dump()
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

        >>> FST.fromsrc('a:b', Slice).dump()
        Slice - ROOT 0,0..0,3
          .lower Name 'a' Load - 0,0..0,1
          .upper Name 'b' Load - 0,2..0,3
        ```
        """

        if isinstance(src, str):
            lines = src.split('\n')
        else:
            lines = src
            src   = '\n'.join(lines)

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)
        ast          = extparse.parse(src, mode, parse_params)

        return FST(ast, lines, parse_params=parse_params)

    @staticmethod
    def fromast(ast: AST, mode: Mode | Literal[False] | None = None, *, filename: builtins.str = '<unknown>',
                type_comments: bool | None = False, feature_version: tuple[int, int] | None = None, ctx: bool = False,
                ) -> FST:
        r"""Unparse and reparse an `AST` for new `FST` (the reparse is necessary to make sure locations are correct).

        **Parameters:**
        - `ast`: The root `AST` node.
        - `mode`: Parse mode, extended `ast.parse()` parameter, see `fst.extparse.Mode`. Two special values are added:
            - `None`: This will attempt to reparse to the same node type as was passed in. This is the default and all
                other values should be considered overrides for special cases.
            - `False`: This will skip the reparse and just `ast.unparse()` the `AST` to generate source for the `FST`.
                Use this only if you are absolutely certain that the `AST` unparsed source will correspond with the
                locations already present in the `AST`. This is almost never the case unless the `AST` was
                `ast.parse()`d from an explicitly `ast.unparse()`d `AST`.
        - `filename`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.
        - `ctx`: Whether to make sure that the `ctx` field of the reparsed `AST` matches or not. `False` for
            convenience, `True` if you're feeling pedantic.

        **Returns:**
        - `FST`: The augmented tree with `.f` attributes added to each `AST` node for `FST` access.

        **Examples:**
        ```py
        >>> import ast
        >>> from ast import Assign, Slice, Constant
        >>> FST.fromast(Assign(targets=[Name(id='var')],
        ...                    value=Constant(value=123))).dump('stmt')
        0: var = 123
        Assign - ROOT 0,0..0,9
          .targets[1]
          0] Name 'var' Store - 0,0..0,3
          .value Constant 123 - 0,6..0,9

        >>> FST.fromast(ast.parse('if 1:\n    j = 5')).dump('stmt')
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

        >>> FST.fromast(Slice(lower=Constant(value=1), step=Name(id='step'))).dump('all')
        0: 1::step
        Slice - ROOT 0,0..0,7
        0: 1
          .lower Constant 1 - 0,0..0,1
        0:    step
          .step Name 'step' Load - 0,3..0,7
        ```
        """

        if type_comments is None:
            type_comments = has_type_comments(ast)

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)
        src          = extparse.unparse(ast)
        lines        = src.split('\n')

        if mode is not False:
            org = ast
            ast = extparse.parse(src, ast.__class__ if mode is None else mode, parse_params)

            try:
                compare_asts(ast, org, type_comments=type_comments, ctx=ctx, raise_=True)
            except WalkFail as exc:
                raise ValueError('could not reparse ast identically') from exc

        return FST(ast, lines, parse_params=parse_params, indent='    ')

    @staticmethod
    def get_options() -> dict[builtins.str, Any]:
        """Get a dictionary of ALL options. These are the same `options` that can be passed to operations and this
        function returns their global defaults which are used when those options are not passed to operations or if they
        are passed with a value of `None`.

        When these options are missing or `None` in a call to an operation, then the default option as specified here is
        used.

        **Parameters:**
        - `options`: Names / values of options to set temporarily, see `options()`.

        **Returns:**
        - `{option: value, ...}`: Dictionary of all global default options.

        **Examples:**
        ```py
        >>> from pprint import pp

        >>> pp(FST.get_options())
        {'pars': 'auto',
         'raw': False,
         'trivia': True,
         'elif_': True,
         'docstr': True,
         'pars_walrus': False,
         'fix_set_get': True,
         'fix_set_put': True,
         'fix_set_self': True,
         'fix_del_self': True,
         'fix_assign_self': True,
         'fix_matchor_get': True,
         'fix_matchor_put': True,
         'fix_matchor_self': True,
         'pep8space': True,
         'precomms': True,
         'postcomms': True,
         'prespace': False,
         'postspace': False}
        ```
        """

        return _OPTIONS.copy()

    @staticmethod
    def get_option(option: builtins.str, options: Mapping[builtins.str, Any] = {}) -> object:
        """Get a single option from `options` dict or global default if option not in dict or is `None` there. For a
        list of options used see `options()`.

        **Parameters:**
        - `option`: Name of option to get, see `options()`.
        - `options`: Dictionary which may or may not contain the requested option.

        **Returns:**
        - `Any`: The `option` value from the passed `options` dict, if passed and not `None` there, else the global
            default value for `option`.

        **Examples:**
        ```py
        >>> FST.get_option('pars')
        'auto'

        >>> FST.get_option('pars', {'pars': True})
        True

        >>> FST.get_option('pars', {'pars': None})
        'auto'
        ```
        """

        return _OPTIONS.get(option) if (o := options.get(option)) is None else o

    @staticmethod
    def set_options(**options) -> dict[builtins.str, Any]:
        """Set global defaults for `options` parameters.

        **Parameters:**
        - `options`: Names / values of parameters to set. These can also be passed to various methods to override the
            defaults set here for those individual operations, see `options()`.

        **Returns:**
        - `options`: `dict` of previous values of changed parameters, reset with `set_options(**options)`.

        **Examples:**
        ```py
        >>> FST.get_option('pars')
        'auto'

        >>> FST.set_options(pars=False)
        {'pars': 'auto'}

        >>> FST.get_option('pars')
        False

        >>> FST.set_options(**{'pars': 'auto'})
        {'pars': False}

        >>> FST.get_option('pars')
        'auto'

        >>> FST.set_options(pars=True, raw=True, docstr=False)
        {'pars': 'auto', 'raw': False, 'docstr': True}
        ```
        """

        ret = {o: _OPTIONS[o] for o in options}

        _OPTIONS.update(options)

        return ret

    @staticmethod
    @contextmanager
    def options(**options) -> Iterator[dict[str, Any]]:
        """Context manager to temporarily set global options defaults for a group of operations.

        **WARNING!** Only the options specified in the call to this function will be returned to their original values
        when the context manager exits.

        **Options:**
        - `pars`: How parentheses are handled, can be `False`, `True` or `'auto'`. This is for individual element
            operations, slice operations ignore this as parentheses usually cannot be removed or may need to be added to
            keep the slices usable. Raw puts generally do not have parentheses added or removed automatically, except
            maybe removed according to this from the destination node if putting to a node instead of a pure location.
            - `False`: Parentheses are not MODIFIED, doesn't mean remove all parentheses. Not copied with nodes or
                removed on put from source or destination. Using incorrectly can result in invalid trees.
            - `True`: Parentheses are copied with nodes, added to copies if needed and not present, removed from
                destination on put if not needed there (but not source).
            - `'auto'`: Same as `True` except they are not returned with a copy and possibly removed from source
                on put if not needed (removed from destination first if needed and present on both).
        - `raw`: When to do raw source operations. This may result in more nodes changed than just the targeted one(s).
            - `False`: Do not do raw source operations.
            - `True`: Only do raw source operations.
            - `'auto'`: Only do raw source operations if the normal operation fails in a way that raw might not.
        - `trivia`: What comments and empty lines to copy / delete when doing operations on elements which may have
            leading or trailing lines of stuff.
            - `False`: Don't copy / delete any trivia.
            - `True`: Same as `('block', 'line')`.
            - `'all'`: Same as `('all', 'all')`.
            - `'block'`: Same as `('block', 'block')`.
            - `(leading, trailing)`: Tuple specifying individual behavior for leading and trailing trivia. The text
                options can also have a suffix of the form `'+/-[#]'`, meaning plus or minus an optional integer which
                adds behavior for leading or trailing empty lines, explained below. The values for each element of the
                tuple can be:
                - `False`: Don't copy / delete any trivia.
                - `True`: For leading means `'block'`, for trailing means `'line'`.
                - `'all[+/-[#]]'`: Get all leading or trailing comments regardless of if they are contiguous or not.
                - `'block[+/-[#]]'`: Get a single contiguous leading or trailing block of comments, an empty line ends
                    the block.
                - `'line[+/-[#]]'`: Valid for trailing trivia only, means just the comment on the last line of the
                    element.
                - `int`: A specific line number specifying the first or last line that can be returned as a comment or
                    empty line. If not interrupted by other code, will always return up to this line.
        - `elif_`: How to handle lone `If` statements as the only statements in an `If` statement `orelse` field.
            - `False`: Always put as a standalone `If` statement.
            - `True`: If putting a single `If` statement to an `orelse` field of a parent `If` statement then
                put it as an `elif`.
        - `docstr`: Which docstrings are indentable / dedentable.
            - `False`: None.
            - `True`: All `Expr` multiline strings (as they serve no coding purpose).
            - `'strict'`: Only multiline strings in expected docstring positions (functions and classes).
        - `pars_walrus`: Whether to parenthesize copied `NamedExpr` nodes or not (only if `pars` is also not `False`).
            - `False`: Do not parenthesize cut / copied `NamedExpr` walrus expressions.
            - `True`: Parenthesize cut / copied `NamedExpr` walrus expressions.
        - `fix_set_get`: Empty set to return when getting an empty slice from a set.
            - `False`: Return an invalid `Set` with zero elements and curlies as delimiters (would parse to a `Dict`).
            - `True`: Same as `'star'`.
            - `'star'`: Starred sequence `{*()}`.
            - `'call'`: `set()` call.
            - `'tuple'`: Empty tuple `()`.
        - `fix_set_put`: What to consider an empty set that is being put (not the target of the put). This applies to
            puts to any types which take a sequence as a source and not just puts to a `Set`, so puts to `Tuple` and
            `List` as well.
            - `False`: Nothing is considered an empty set, `set()` is not considered a sequence and a `{*()}` set is put
                verbatim.
            - `True`: Same a `'both'`.
            - `'star'`: Only starred sequences `{*()}`, `{*[]}` and `{*{}}` are considered empty.
            - `'call'`: Only `set()` call is considered empty.
            - `'both'`: `set()` call and `{*()}`, `{*[]}` and `{*{}}` starred sequences are considered empty.
        - `fix_set_self`: What to leave for an empty set if a `Set` gets everything cut or deleted from it. This is also
            what gets put if you put an invalid empty set with `one=True`.
            - `False`: Leave an invalid `Set` with zero elements and curlies as delimiters (would parse to a `Dict`).
            - `True`: Same as `'star'`.
            - `'star'`: Starred sequence `{*()}`.
            - `'call'`: `set()` call.
        - `fix_del_self`: How to handle operations which would leave a `Delete` with zero `targets`.
            - `False`: Allow, this will leave an invalid `Delete` which should have the `targets` replaced as soon as
                possible.
            - `True`: Don't allow, error.
        - `fix_assign_self`: How to handle operations which would leave a `Assign` with zero `targets`.
            - `False`: Allow, this will leave an invalid `Assign` which should have the `targets` replaced as soon as
                possible.
            - `True`: Don't allow, error.
        - `fix_matchor_get`: How to handle zero or length 1 slice gets from a `MatchOr`. Zero-length `MatchOr`s, or any
            zero-length source spans really can be problematic, try not to hang on to them for too long.
            - `False`: Return invalid one and zero-length `MatchOr`.
            - `True`: Error on zero-length get, return single pattern element (not `MatchOr`) for length 1.
            - `'strict'`: Only allow get length 2+ `MatchOr`, error otherwise.
        - `fix_matchor_put`: How to handle slice puts to `MatchOr`
            - `False`: Accept one or zero-length `MatchOr`, do not accept single element pattern as length 1.
            - `True`: Accept one or zero-length `MatchOr` as well as single element pattern as length 1.
        - `fix_matchor_self`: How to handle zero or length 1 `MatchOr` objects when a cut or del reduces them to this
            length.
            - `False`: Leave one or zero-length `MatchOr`.
            - `True`: Error on zero-length, convert to single element if length 1.
            - `'strict'`: Only allow length 2+ `MatchOr`, error otherwise.
        - `pep8space`: Preceding and trailing empty lines for function and class definitions.
            - `False`: No empty lines.
            - `True`: Two empty lines at module scope and one empty line in other scopes.
            - `1`: One empty line in all scopes.
        - `precomms`: Preceding comments.  - DEPRECATED, STILL USED FOR STMTS, WILL BE REPLACED WITH `trivia`!
            - `False`: No preceding comments.
            - `True`: Single contiguous comment block immediately preceding position.
            - `'all'`: Comment blocks (possibly separated by empty lines) preceding position.
        - `postcomms`: Trailing comments.  - DEPRECATED, STILL USED FOR STMTS, WILL BE REPLACED WITH `trivia`!
            - `False`: No trailing comments.
            - `True`: Only comment trailing on line of position, nothing past that on its own lines.
            - `'block'`: Single contiguous comment block following position.
            - `'all'`: Comment blocks (possibly separated by empty lines) following position.
        - `prespace`: Preceding empty lines (max of this and `pep8space` used).  - DEPRECATED, STILL USED FOR STMTS,
            WILL BE REPLACED WITH `trivia`!
            - `False`: No empty lines.
            - `True`: All empty lines.
            - `int`: A maximum number of empty lines.
        - `postspace`: Same as `prespace` except for trailing empty lines.  - DEPRECATED, STILL USED FOR STMTS, WILL BE
            REPLACED WITH `trivia`!

        **Note:** `pars` behavior:
        ```
                                                                  False      True    'auto'
        Copy pars from source on copy / cut:                         no       yes        no
        Add pars needed for parsability to copy:                     no       yes       yes
        Remove unneeded pars from destination on put:                no       yes       yes
        Remove unneeded pars from source on put:                     no        no       yes
        Add pars needed for parse / precedence to source on put:     no       yes       yes
        ```

        **Note:** `trivia` text suffix behavior:
        - `'+[#]'` Copy and delete an extra number of lines after any comments specified by the `#`. If no number is
            specified and just a `'+'` then all empty lines will be copied / deleted.
        - `'-[#]'` Delete, but not copy, an extra number of lines after any comments specified by the `#`. If  no number
            is specified and just a `'-'` then all empty lines will be deleted.

        **Examples:**
        ```py
        >>> print(FST.get_option('pars'), FST.get_option('elif_'))
        auto True

        >>> with FST.options(pars=False, elif_=False):
        ...     print(FST.get_option('pars'), FST.get_option('elif_'))
        False False

        >>> print(FST.get_option('pars'), FST.get_option('elif_'))
        auto True
        ```
        """

        old_options = FST.set_options(**options)

        try:
            yield old_options
        finally:
            FST.set_options(**old_options)

    def dump(self, src: Literal['stmt', 'all'] | None = None, full: bool = False, expand: bool = False, *,
             indent: int = 2, out: Callable | TextIO = print, eol: builtins.str | None = None,
             ) -> builtins.str | list[builtins.str] | None:
        r"""Dump a representation of the tree to stdout or other `TextIO` or return as a `str` or `list` of lines, or
        call a provided function once with each line of the output.

        **Parameters:**
        - `src`: `'stmt'` means output statement source lines (including `ExceptHandler` and `match_case`), `'all'`
            means output source for each individual and node and `None` does not output any source. Can also be a string
            for shortcut specification of source and flags by first letter: `'s'` means `src='stmt'`, `'a'` means
            `src='all'`, `'f'` means `full=True` and `'e'` means `expand=True`, so `'sfe'` would be a full expanded dump
            showing statement source lines.
        - `full`: If `True` then will list all fields in nodes including empty ones, otherwise will exclude most empty
            fields.
        - `expand`: If `True` then the output is a nice compact representation. If `False` then it is ugly and wasteful.
        - `indent`: The average airspeed of an unladen swallow (European).
        - `out`: `print` means print to stdout, `list` returns a list of lines and `str` returns a whole string.
            `TextIO` will cann the `write` method for each line of output. Otherwise a `Callable[[str], None]` which is
            called for each line of output individually.
        - `eol`: What to put at the end of each text line, `None` means newline for `TextIO` out and nothing for other.

        **Returns:**
        - `str | list[str]`: If those were requested with `out=str` or `out=list` else `None` and the output is send one
            line at a time to `linefunc`, which by default is `print`.
        - `None`: Otherwise.

        **Examples:**
        ```py
        >>> f = FST('''
        ... if 1:
        ...     call(a[i], **b)
        ... '''.strip())

        >>> f.dump()
        If - ROOT 0,0..1,19
          .test Constant 1 - 0,3..0,4
          .body[1]
          0] Expr - 1,4..1,19
            .value Call - 1,4..1,19
              .func Name 'call' Load - 1,4..1,8
              .args[1]
              0] Subscript - 1,9..1,13
                .value Name 'a' Load - 1,9..1,10
                .slice Name 'i' Load - 1,11..1,12
                .ctx Load
              .keywords[1]
              0] keyword - 1,15..1,18
                .value Name 'b' Load - 1,17..1,18

        >>> f.dump(src='all', indent=4)
        0: if 1:
        If - ROOT 0,0..1,19
        0:    1
            .test Constant 1 - 0,3..0,4
            .body[1]
        1:     call(a[i], **b)
            0] Expr - 1,4..1,19
                .value Call - 1,4..1,19
        1:     call
                    .func Name 'call' Load - 1,4..1,8
                    .args[1]
        1:          a[i]
                    0] Subscript - 1,9..1,13
        1:          a
                        .value Name 'a' Load - 1,9..1,10
        1:            i
                        .slice Name 'i' Load - 1,11..1,12
                        .ctx Load
                    .keywords[1]
        1:                **b
                    0] keyword - 1,15..1,18
        1:                  b
                        .value Name 'b' Load - 1,17..1,18

        >>> f.dump(out=str)[:64]
        'If - ROOT 0,0..1,19\n  .test Constant 1 - 0,3..0,4\n  .body[1]\n  0'

        >>> for l in f.dump('stmt', out=list):
        ...     print(repr(l))
        '0: if 1:'
        'If - ROOT 0,0..1,19'
        '  .test Constant 1 - 0,3..0,4'
        '  .body[1]'
        '1:     call(a[i], **b)'
        '  0] Expr - 1,4..1,19'
        '    .value Call - 1,4..1,19'
        "      .func Name 'call' Load - 1,4..1,8"
        '      .args[1]'
        '      0] Subscript - 1,9..1,13'
        "        .value Name 'a' Load - 1,9..1,10"
        "        .slice Name 'i' Load - 1,11..1,12"
        '        .ctx Load'
        '      .keywords[1]'
        '      0] keyword - 1,15..1,18'
        "        .value Name 'b' Load - 1,17..1,18"
        ```
        """

        if isinstance(src, str):
            if (src := src.lower()) not in ('stmt', 'all'):
                if src.replace('f', '').replace('e', '').replace('a', '').replace('s', ''):
                    raise ValueError("invalid character(s) in 'src' string")

                full   = 'f' in src
                expand = 'e' in src
                src    = 'all' if 'a' in src else 'stmt' if 's' in src else None

        if isinstance(out, TextIOBase):
            out = out.write

            if eol is None:
                eol = '\n'

        elif eol is None:
            eol = ''

        st = nspace(src=src, full=full, expand=expand, indent=indent, eol=eol)

        if out in (str, list):
            lines       = []
            st.linefunc = lines.append

            self._dump(st)

            return lines if out is list else '\n'.join(lines)

        st.linefunc = out

        return self._dump(st)

    def verify(self, mode: Mode | None = None, reparse: bool = True, *, locs: bool = True, ctx: bool = True,
               raise_: bool = True) -> Union[Self, None]:
        """Sanity check. Walk the tree and make sure all `AST`s have corresponding `FST` nodes with valid parent / child
        links, then (optionally) reparse source and make sure parsed tree matches currently stored tree (locations and
        everything). The reparse can only be carried out on root nodes but the link validation can be done on any level.

        **Parameters:**
        - `mode`: Parse mode to use, otherwise if `None` then use the top level AST node type for the mode. Depending on
            how this is set will determine whether the verification is checking if is parsable by python (`'exec'` or
            `'strict'` for example), or if the node itself is just in a valid state (where `None` is good). See
            `fst.extparse.Mode`.
        - `reparse`: Whether to reparse the source and compare ASTs (including location). Otherwise the check is limited
            to a structure check that all children have `FST` nodes which are all liked correctly to their parents.
            `reparse=True` only allowed on root node.
        - `locs`: Whether to compare locations after reparse or not.
        - `ctx`: Whether to compare `ctx` nodes after reparse or not.
        - `raise_`: Whether to raise an exception on verify failed or return `None`.

        **Returns:**
        - `None` on failure to verify (if not `raise_`), otherwise `self`.

        **Examples:**
        ```py
        >>> FST('var = 123').verify()
        <Assign ROOT 0,0..0,9>

        >>> FST('a:b:c').verify()
        <Slice ROOT 0,0..0,5>

        >>> bool(FST('a:b:c').verify('exec', raise_=False))
        False
        ```
        """

        # validate tree links

        ast   = self.a
        stack = [(ast, self.parent, self.pfield)]  # [(AST, parent FST, pfield), ...]

        while stack:
            a, parent, pfield = stack.pop()

            if not (f := getattr(a, 'f', None)) or f.parent is not parent or f.pfield != pfield or f.a is not a:
                if not raise_:
                    return None

                path   = self.child_path(parent) + [pfield] if a is not ast else []
                path   = '.'.join(af.name if (i := af.idx) is None else f'{af.name}[{i}]' for af in path)
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
            astp = extparse.parse(self.src, mode or self.get_parse_mode(), parse_params=parse_params)

        except SyntaxError:
            if raise_:
                raise

            return None

        if not compare_asts(astp, ast, locs=locs, ctx=ctx, type_comments=parse_params.get('type_comments', False),
                            raise_=raise_):
            return None

        return self

    # ------------------------------------------------------------------------------------------------------------------
    # Reconcile

    def mark(self) -> FST:
        """Return an object marking the current state of this `FST` tree. Used to `reconcile()` later for non-FST operation
        changes made (changing `AST` nodes directly). Currently is just a copy of the original tree but may change in the
        future.

        **Returns:**
        - `FST`: A marked copy of `self` with any necessary information added for a later `reconcile()`.
        """

        if not self.is_root:
            raise ValueError('can only mark root nodes')

        mark         = self.copy()
        mark._serial = self._serial

        return mark

    def reconcile(self, mark: FST, **options) -> FST:
        r"""Reconcile `self` with a previously marked version and return a new valid `FST` tree. This is meant for allowing
        non-FST modifications to an `FST` tree and later converting it to a valid `FST` tree to preserve as much formatting
        as possible and maybe continue operating in `FST` land. Only `AST` nodes from the original tree carry formatting
        information, so the more of those are replaced the more formatting is lost.

        **Note:** When replacing the `AST` nodes, make sure you are replacing the nodes in the parent `AST` fields, not the
        `.a` attribute in `FST` nodes, that won't do anything.

        **WARNING!** Just like an `ast.unparse()`, the fact that this function completes successfully does NOT mean the
        output is syntactically correct if you put weird nodes where they don't belong, maybe accidentally. In order to make
        sure the result is valid (syntactically) you should run `verify()` on the output. This still won't guarantee you
        have actual valid code, `def f(x, x): pass` parses ok but will cause an error if you try to compile it.

        **Parameters:**
        - `mark`: A previously marked snapshot of `self`. This object is not consumed on use, success or failure.
        - `options`: See `options()`.

        **Returns:**
        - `FST`: A new valid reconciled `FST` if possible.

        **Examples:**
        ```py
        >>> f = FST('''
        ... @decorator  # something
        ... def function(a: int, b=2)->int:  # blah
        ...     return a+b  # return this
        ...
        ... def other_function(a, b):
        ...     return a - b  # return that
        ... '''.strip())

        >>> m = f.mark()

        >>> f.a.body[0].returns = Name('float')  # pure AST
        >>> f.a.body[0].args.args[0].annotation = Name('float')
        >>> f.a.body[0].decorator_list[0] = FST('call_decorator(1, 2, 3)').a
        >>> f.a.body[1].name = 'last_function'  # can change non-AST
        >>> f.a.body[1].body[0] = f.a.body[0].body[0]  # AST from same FST tree
        >>> other = FST('def first_function(a, b): return a * b  # yay!')
        >>> f.a.body.insert(0, other.a)  # AST from other FST tree

        >>> f = f.reconcile(m, pep8space=1)

        >>> print('\n'.join(l or '.' for l in f.lines))  # print this way for doctest
        def first_function(a, b): return a * b  # yay!
        .
        @call_decorator(1, 2, 3)  # something
        def function(a: float, b=2)->float:  # blah
            return a+b  # return this
        .
        def last_function(a, b):
            return a+b  # return this
        .

        >>> m = f.mark()

        >>> body = f.a.body[1].body
        >>> f.a.body[1] = FST('def f(): pass').a
        >>> f.a.body[1].body = body

        >>> f = f.reconcile(m, pep8space=1)

        >>> print('\n'.join(l or '.' for l in f.lines))
        def first_function(a, b): return a * b  # yay!
        .
        def f():
            return a+b  # return this
        .
        def last_function(a, b):
            return a+b  # return this
        .
        ```
        """

        # TODO: allow multiple marked trees to participate?

        if not self.is_root:
            raise ValueError('can only reconcile root nodes')

        if self._serial != mark._serial:
            raise RuntimeError('modification detected after mark(), irreconcilable')

        rec = Reconcile(self, mark, options)

        rec.recurse_node(self.a)

        return rec.out

    # ------------------------------------------------------------------------------------------------------------------
    # High level

    def copy(self, **options) -> FST:
        """Copy this node to a new top-level tree, dedenting and fixing as necessary.

        **Parameters:**
        - `options`: See `options()`.

        **Returns:**
        - `FST`: Copied node.

        **Examples:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts[1].copy().src
        '1'
        ```
        """

        if parent := self.parent:
            return parent._get_one((pf := self.pfield).idx, pf.name, False, options)

        return FST(copy_ast(self.a), self._lines[:], from_=self, lcopy=False)

    def cut(self, **options) -> FST:
        """Cut out this node to a new top-level tree (if possible), dedenting and fixing as necessary. Cannot cut root
        node.

        **Parameters:**
        - `options`: See `options()`.

        **Returns:**
        - `FST`: Cut node.

        **Examples:**
        ```py
        >>> (f := FST('[0, 1, 2, 3]')).elts[1].cut().src
        '1'

        >>> f.src
        '[0, 2, 3]'
        ```
        """

        if parent := self.parent:
            return parent._get_one((pf := self.pfield).idx, pf.name, True, options)

        raise ValueError('cannot cut root node')

    def replace(self, code: Code | None, **options) -> FST | None:  # -> replaced Self or None if deleted
        """Replace or delete (if `code=None`, if possible) this node. Returns the new node for `self`, not the old
        replaced node, or `None` if was deleted or raw replaced and the old node disappeared. Cannot delete root node.
        CAN replace root node, in which case the accessing `FST` node remains the same but the top-level `AST` and
        source change.

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to put at this location. `None` to delete this node.
        - `options`: See `options()`.
            - `to`: Special option which only applies replacing in `raw` mode (either through `True` or `'auto'`).
                Instead of replacing just this node, will replace the entire span from this node to the node specified
                in `to` with the `code` passed.

        **Returns:**
        - `FST | None`: Returns the new node if successfully replaced or `None` if deleted.

        **Examples:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts[1].replace('4').root.src
        '[0, 4, 2, 3]'

        >>> f = FST('def f(a, /, b, *c, **d) -> int: pass')
        >>> f.args.posonlyargs[0].replace(')', to=f.returns, raw=True)  # raw reparse
        >>> f.src
        'def f(): pass'
        ```
        """

        if parent := self.parent:
            return parent._put_one(code, (pf := self.pfield).idx, pf.name, options)

        if code is None:
            raise ValueError('cannot delete root node')
        if options.get('to'):
            raise ValueError("cannot replace root node using a 'to' option")

        code        = code_as_all(code, self.parse_params)
        self._lines = code._lines

        self._set_ast(code.a, True)

        return self

    def remove(self, **options) -> None:
        """Delete this node if possible, equivalent to `replace(None, ...)`. Cannot delete root node.

        **Parameters:**
        - `options`: See `options()`.

        **Examples:**
        ```py
        >>> (f := FST('[0, 1, 2, 3]')).elts[1].remove(); f.src
        '[0, 2, 3]'
        ```
        """

        if parent := self.parent:
            return parent._put_one(None, (pf := self.pfield).idx, pf.name, options)

        raise ValueError('cannot delete root node')

    def get(self, idx: int | Literal['end'] | None = None, stop: int | None | Literal[False] = False,
            field: builtins.str | None = None, *, cut: bool = False, **options) -> FST | None | builtins.str | constant:
        r"""Copy or cut an individual child node or a slice of child nodes from `self` if possible. This function can do
        everything that `get_slice()` can.

        **Parameters:**
        - `idx`: The index of the child node to get if the field being gotten from contains multiple elements or the
            start of the slice to get if getting a slice (by specifying `stop`). If the field being gotten from is
            an individual element then this should be `None`. If `stop` is specified and getting a slice then a `None`
            here means copy from the start of the list.
        - `stop`: The end index (exclusive) of the child node to get if getting a slice from a field that contains
            multiple elements. This should be one past the last element to get (like python list indexing). If this is
            `False` then it indicates that a single element is being requested and not a slice. If this is `None` then
            it indicates a slice operation to the end of the list (like python `a[start:]`).
        - `field`: The name of the field to get the element(s) from, which can be an individual element like a `value`
            or a list like `body`. If this is `None` then the default field for the node type is used. Most node types
            have a common-sense default field, e.g. `body` for all block statements, `value` for things like `Return`
            and `Yield`. `Dict`, `MatchMapping` and `Compare` nodes have special-case handling for a `None` field.
        - `cut`: Whether to cut out the child node (if possible) or not (just copy).
        - `options`: See `options()`.

        **Note:** The `field` value can be passed positionally in either the `idx` or `stop` parameter. If passed in
        `idx` then the field is assumed individual and if passed in `stop` then it is a list and an individual element
        is being gotten from `idx` and not a slice.

        **Returns:**
        - `FST`: When getting an actual node (most situations).
        - `str`: When getting am identifier, like from `Name.id`.
        - `constant`: When getting a constant (`fst.astutil.constant`), like from `MatchSingleton.value`.

        **Examples:**
        ```py
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

        >>> FST('[0, 1, 2, 3]').get(None, 3).src
        '[0, 1, 2]'

        >>> FST('[0, 1, 2, 3]').get(-3, None).src
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
        ```
        """

        ast              = self.a
        idx, stop, field = swizzle_getput_params(idx, stop, field, False)
        field_, body     = fixup_field_body(ast, field, False)

        if isinstance(body, list):
            if stop is not False:
                return self._get_slice(idx, stop, field_, cut, options)
            if idx is None:
                return self._get_slice(None, None, field_, cut, options)

            if idx == 'end':
                raise IndexError("cannot get() non-slice from index 'end'")

        elif stop is not False or idx is not None:
            raise IndexError(f'{ast.__class__.__name__}{f".{field_}" if field_ else ""} does not take an index')

        return self._get_one(idx, field_, cut, options)

    def put(self, code: Code | builtins.str | constant | None, idx: int | Literal['end'] | None = None,
            stop: int | None | Literal[False] = False, field: builtins.str | None = None, *, one: bool = True,
            **options) -> Self:
        r"""Put an individual node or a slice of nodes to `self` if possible. This function can do everything that
        `put_slice()` can. The node is passed as an existing top-level `FST`, `AST`, string or list of string lines. If
        passed as an `FST` then it should be considered "consumed" after this function returns and is no logner valid,
        even on failure. `AST` is copied.

        **WARNING!** The original `self` node may be invalidated during the operation if using raw mode (either
        specifically or as a fallback), so make sure to swap it out for the return value of this function if you will
        keep using the variable you called this method on. It will be changed accordingly in the tree but any other
        outside references to the node may become invalid.

        **Parameters:**
        - `code`: The node to put as an `FST` (must be root node), `AST`, a string or list of line strings. If putting
            to an identifier field then this should be a string and it will be taken literally (no parsing). If putting
            to a constant likew `MatchSingleton.value` or `Constant.value` then this should be an appropriate primitive
            constant value.
        - `idx`: The index of the field node to put to if the field being put to contains multiple elements or the start
            of the slice to put if putting a slice (by specifying `stop`). If the field being put to is an individual
            element then this should be `None`. If `stop` is specified and putting a slice then a `None` here means put
            starting from the beginning of the list.
        - `stop`: The end index (exclusive) of the field node to put to if putting a slice to a field that contains
            multiple elements. This should be one past the last element to put (like python list indexing). If this is
            `False` then it indicates that a single element is being put and not a slice. If this is `None` then it
            indicates a slice operation to the end of the list (like python `a[start:]`).
        - `field`: The name of the field to put the element(s) to, which can be an individual element like a `value` or
            a list like `body`. If this is `None` then the default field for the node type is used. Most node types have
            a common-sense default field, e.g. `body` for all block statements, `value` for things like `Return` and
            `Yield`. `Dict`, `MatchMapping` and `Compare` nodes have special-case handling for a `None` field.
        - `one`: Only has meaning if putting a slice, and in this case `True` specifies that the source should be  put
            as a single element to the range specified even if it is a valid slice. `False` indicates a true slice
            operation replacing the range with the slice passed, which must in this case be a compatible slice type.
        - `options`: See `options()`.
            - `to`: Special option which only applies when putting a single element in `raw` mode (either through `True`
                or `'auto'`). Instead of replacing just the target node, will replace the entire span from the target
                node to the node specified in `to` with the `code` passed.

        **Note:** The `field` value can be passed positionally in either the `idx` or `stop` parameter. If passed in
        `idx` then the field is assumed individual and if passed in `stop` then it is a list and an individual element
        is being gotten from `idx` and not a slice.

        **Returns:**
        - `self`

        **Examples:**
        ```py
        >>> FST('[0, 1, 2, 3]').put('4', 1).src
        '[0, 4, 2, 3]'

        >>> FST('[0, 1, 2, 3]').put('4, 5', 1, 3).src
        '[0, (4, 5), 3]'

        >>> FST('[0, 1, 2, 3]').put('4, 5', 1, 3, one=False).src
        '[0, 4, 5, 3]'

        >>> FST('[0, 1, 2, 3]').put('4, 5', None, 3).src
        '[(4, 5), 3]'

        >>> (f := FST('[0, 1, 2, 3]')).put('4, 5', -3, None, one=False).src
        '[0, 4, 5]'

        >>> print(FST('if 1: i = 1\nelse: j = 2').put('z = -1', 0).src)
        if 1:
            z = -1
        else: j = 2

        >>> print(FST('if 1: i = 1\nelse: j = 2').put('z = -1', 0, 'orelse').src.rstrip())
        if 1: i = 1
        else:
            z = -1

        >>> print(FST('if 1: i = 1\nelse: j = 2')
        ...       .put('z = -1\ny = -2\nx = -3', 'orelse', one=False).src.rstrip())
        if 1: i = 1
        else:
            z = -1
            y = -2
            x = -3

        >>> print((f := FST('if 1: i = 1\nelse: j = 2'))
        ...       .put('z = -1', 0, raw=True, to=f.orelse[0]).root.src)
        if 1: z = -1
        ```
        """

        ast              = self.a
        idx, stop, field = swizzle_getput_params(idx, stop, field, False)
        field_, body     = fixup_field_body(ast, field, False)

        if isinstance(body, list):
            if stop is not False:
                return self._put_slice(code, idx, stop, field_, one, options)
            if idx is None:
                return self._put_slice(code, None, None, field_, one, options)

            if idx == 'end':
                raise IndexError("cannot put() non-slice to index 'end'")

        elif stop is not False or idx is not None:
            raise IndexError(f'{ast.__class__.__name__}{f".{field_}" if field_ else ""} does not take an index')

        if not one:
            raise ValueError("cannot use 'one=False' in non-slice put()")

        self._put_one(code, idx, field_, options)

        return self.repath()

    def get_slice(self, start: int | Literal['end'] | None = None, stop: int | None = None,
                  field: builtins.str | None = None, *, cut: bool = False, **options) -> FST:
        r"""Copy or cut a slice of child nodes from `self` if possible.

        **Parameters:**
        - `start`: The start of the slice to get, or `None` for the beginning of the entire range.
        - `stop`: The end index (exclusive) of the slice to get. This should be one past the last element to get (like
            python list indexing). If this is `None` then it indicates a slice operation to the end of the list (like
            python `a[start:]`).
        - `field`: The name of the field to get the elements from, which can be an individual element like a `value` or
            a list like `body`. If this is `None` then the default field for the node type is used. Most node types
            have a common-sense default field, e.g. `body` for all block statements, `elts` for things like `List` and
            `Tuple`. `MatchMapping` and `Compare` nodes have special-case handling for a `None` field.
        - `cut`: Whether to cut out the slice or not (just copy).
        - `options`: See `options()`.

        **Note:** The `field` value can be passed positionally in either the `start` or `stop` parameter. If passed in
        `start` then the slice is assumed to be the entire range, and if passed in `stop` then the slice goes from
        `start` to the end of the range.

        **Returns:**
        - `FST`: Slice node of nodes gotten.

        **Examples:**
        ```py
        >>> FST('[0, 1, 2, 3]').get_slice(1).src
        '[1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').get_slice(None, -1).src
        '[0, 1, 2]'

        >>> (f := FST('[0, 1, 2, 3]')).get_slice(1, 3, cut=True).src
        '[1, 2]'

        >>> f.src
        '[0, 3]'

        >>> f = FST('if 1: i = 1\nelse: j = 2; k = 3; l = 4; m = 5')
        >>> s = f.get_slice(1, 3, 'orelse', cut=True)
        >>> print(f.src)
        if 1: i = 1
        else: j = 2; m = 5

        >>> print(s.src)
        k = 3; l = 4
        ```
        """

        ast                = self.a
        start, stop, field = swizzle_getput_params(start, stop, field, None)
        field_, body       = fixup_field_body(ast, field)

        if not isinstance(body, list):
            raise ValueError(f'cannot get slice from non-list field {ast.__class__.__name__}.{field_}')

        return self._get_slice(start, stop, field_, cut, options)

    def put_slice(self, code: Code | None, start: int | Literal['end'] | None = None, stop: int | None = None,
                  field: builtins.str | None = None, *, one: bool = False, **options) -> Self:
        r"""Put a slice of nodes to `self` if possible.  The node is passed as an existing top-level `FST`, `AST`, string
        or list of string lines. If passed as an `FST` then it should be considered "consumed" after this function
        returns and is no logner valid, even on failure. `AST` is copied.

        **WARNING!** The original `self` node may be invalidated during the operation if using raw mode (either
        specifically or as a fallback), so make sure to swap it out for the return value of this function if you will
        keep using the variable you called this method on. It will be changed accordingly in the tree but any other
        outside references to the node may become invalid.

        **Parameters:**
        - `code`: The slice to put as an `FST` (must be root node), `AST`, a string or list of line strings.
        - `start`: The start of the slice to put, or `None` for the beginning of the entire range.
        - `stop`: The end index (exclusive) of the slice. This should be one past the last element to put (like python
            list indexing). If this is `None` then it indicates a slice operation to the end of the list (like python
            `a[start:]`).
        - `field`: The name of the field to put the elements to. If this is `None` then the default field for the node
            type is used. Most node types have a common-sense default field, e.g. `body` for all block statements,
            `elts` for things like `List` and `Tuple`. `MatchMapping` and `Compare` nodes have special-case handling for
            a `None` field.
        - `options`: See `options()`.

        **Note:** The `field` value can be passed positionally in either the `start` or `stop` parameter. If passed in
        `start` then the slice is assumed to be the entire range, and if passed in `stop` then the slice goes from
        `start` to the end of the range.

        **Returns:**
        - `self`

        **Examples:**
        ```py
        >>> FST('[0, 1, 2, 3]').put('4', 1).src
        '[0, 4, 2, 3]'

        >>> FST('[0, 1, 2, 3]').put('4, 5', 1, 3).src
        '[0, (4, 5), 3]'

        >>> FST('[0, 1, 2, 3]').put('4, 5', 1, 3, one=False).src
        '[0, 4, 5, 3]'

        >>> FST('[0, 1, 2, 3]').put('4, 5', None, 3).src
        '[(4, 5), 3]'

        >>> (f := FST('[0, 1, 2, 3]')).put('4, 5', -3, None, one=False).src
        '[0, 4, 5]'

        >>> print(FST('if 1: i = 1\nelse: j = 2').put('z = -1', 0).src)
        if 1:
            z = -1
        else: j = 2

        >>> print(FST('if 1: i = 1\nelse: j = 2').put('z = -1', 0, 'orelse').src.rstrip())
        if 1: i = 1
        else:
            z = -1

        >>> print(FST('if 1: i = 1\nelse: j = 2')
        ...       .put('z = -1\ny = -2\nx = -3', 'orelse', one=False).src.rstrip())
        if 1: i = 1
        else:
            z = -1
            y = -2
            x = -3

        >>> print((f := FST('if 1: i = 1\nelse: j = 2'))
        ...       .put('z = -1', 0, raw=True, to=f.orelse[0]).root.src)
        if 1: z = -1
        ```
        """

        ast                = self.a
        start, stop, field = swizzle_getput_params(start, stop, field, None)
        field_, body       = fixup_field_body(ast, field)

        if not isinstance(body, list):
            raise ValueError(f'cannot put slice to non-list field {ast.__class__.__name__}.{field_}')

        return self._put_slice(code, start, stop, field_, one, options)

    def get_src(self, ln: int, col: int, end_ln: int, end_col: int, as_lines: bool = False,
                ) -> builtins.str | list[builtins.str]:
        r"""Get source at location, without dedenting or any other modification, returned as a string or individual
        lines. The first and last lines are cropped to start `col` and `end_col`.

        Can call on any node in tree to access source for the whole tree.

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
        ```py
        >>> FST('if 1:\n  i = 2').get_src(0, 3, 1, 5)
        '1:\n  i ='

        >>> FST('if 1:\n  i = 2').get_src(0, 3, 1, 5, as_lines=True)
        ['1:', '  i =']

        >>> (f := FST('if 1:\n  i = 2')).get_src(*f.body[0].bloc)
        'i = 2'
        ```
        """

        ls = self.root._lines

        if as_lines:
            return ([bistr(ls[ln][col : end_col])]  # no real reason for bistr, just to be consistent and minor optimization if passed back into put_src()
                    if end_ln == ln else
                    [bistr(ls[ln][col:])] + ls[ln + 1 : end_ln] + [bistr(ls[end_ln][:end_col])])
        else:
            return (ls[ln][col : end_col]
                    if end_ln == ln else
                    '\n'.join([ls[ln][col:]] + ls[ln + 1 : end_ln] + [ls[end_ln][:end_col]]))

    def put_src(self, code: Code | None, ln: int, col: int, end_ln: int, end_col: int, *,
                exact: bool | None = True) -> FST | None:
        r"""Put source and reparse. There are no rules on what is put, it is simply put and parse is attempted. If the
        `code` is passed as an `AST` then it is unparsed to a string and that string is put into the location. If `FST`
        then the exact source of the `FST` is put. If passed as a string or lines then that is put directly.

        The reparse that is triggered is of at least a statement level node or a statement block header, and can be
        multiple statements if the location spans those or even statements outside of the location if the reparse
        affects things like `elif`. `FST` nodes in the region of the put or even outside of it can become invalid. The
        only `FST` node guaranteed not to change is the root node (identity, the `AST` it holds can change).

        When putting source raw by location like this there are no automatic modifications made to the source or
        destination. No parenthesization, prefixes or suffixes or indentation, the source is just put and parsed so you
        are responsible for the correct indentation and precedence.

        After put and successful reparse the location of the put is examined and an appropriate node is returned which
        fits best for a node which may have been added or replaced. It is possible that `None` is returned if no good
        candidate is found (since this can be used to delete or merge nodes).

        Can call on any node in tree to modify source for the whole tree.

        **Parameters:**
        - `code`: The code to put as an `FST` (must be root node), `AST`, a string or list of line strings.
        - `ln`: Start line of span to put (0 based).
        - `col`: Start column (character) on start line.
        - `end_ln`: End line of span to put (0 based, inclusive).
        - `end_col`: End column (character, exclusive) on end line.
        - `exact`: This specifies how the node check after a successful reparse is done. `True` means allow return of
            node which matches location exactly. Otherwise if `False`, the location must be inside the node but cannot
            be touching BOTH ends of the node. This basically determines whether you can get the exact node of the
            location or its parent. If passed as `None` then the check is even more restricted.

        **Returns:**
        - `FST | None`: FIRST highest level node contained entirely within replacement source location (there may be
            others following), or `None` if no such candidate and `exact=None`. If no candidate and `exact` is `True`
            or `False` then will attempt to return a node which encloses the location using `find_loc(..., exact)`.

        **Examples:**
        ```py
        >>> FST('i = 1').put_src('2', 0, 4, 0, 5).root.src
        'i = 2'

        >>> FST('i = 1').put_src('+= 3', 0, 2, 0, 5).root.src
        'i += 3'

        >>> FST('{a: b, c: d, e: f}').put_src('**', 0, 7, 0, 10).root.src
        '{a: b, **d, e: f}'

        >>> f = FST('i = 1')
        >>> g = f.targets[0]
        >>> print(type(g.a))
        <class 'ast.Name'>

        >>> f.put_src('4', 0, 4, 0, 5).src
        '4'

        >>> print(g.a)
        None

        >>> print(type(f.targets[0].a))
        <class 'ast.Name'>

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
        <If 3,2..4,9>

        >>> print(f.src)
        if a:
          i = 2
        else:
          if b:
            k = 4
        ```
        """

        parent = self.root.find_loc(ln, col, end_ln, end_col, False) or self.root

        return parent._reparse_raw(code, ln, col, end_ln, end_col, exact)

    def pars(self, shared: bool | None = True) -> fstloc | None:
        """Return the location of enclosing GROUPING parentheses if present. Will balance parentheses if `self` is an
        element of a tuple and not return the parentheses of the tuple. Likwise will not normally return the parentheses
        of an enclosing `arguments` parent or class bases list (unless `shared=None`, but that is mostly for internal
        use).

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
            `None` then returns ANY directly enclosing parentheses, whether they belong to this node or not.

        **Returns:**
        - `fstloc | None`: Location of enclosing parentheses if present else `self.bloc` (which can be `None`). Negative
            parentheses count (from shared parens solo call arg generator expression) can also be checked in the case of
            `shared=False` via `fst.pars() > fst.bloc`. If only loc is returned, it will be an `fstloc` which will
            still have the count of parentheses in an attribute `.n`.

        **Examples:**
        ```py
        >>> FST('i').pars()
        fstlocns(0, 0, 0, 1, n=0)

        >>> FST('(i)').pars()
        fstlocns(0, 0, 0, 3, n=1)

        >>> FST('((i))').pars()
        fstlocns(0, 0, 0, 5, n=2)

        >>> FST('(1, 2)').pars()  # tuple pars are not considered grouping pars
        fstlocns(0, 0, 0, 6, n=0)

        >>> FST('((1, 2))').pars()
        fstlocns(0, 0, 0, 8, n=1)

        >>> FST('call(a)').args[0].pars()  # any node, not just root
        fstlocns(0, 5, 0, 6, n=0)

        >>> FST('call((a))').args[0].pars()
        fstlocns(0, 5, 0, 8, n=1)

        >>> FST('call(i for i in j)').args[0].pars()
        fstlocns(0, 4, 0, 18, n=0)

        >>> FST('call(i for i in j)').args[0].pars(shared=False)  # exclude shared pars
        fstlocns(0, 5, 0, 17, n=-1)

        >>> FST('call((i for i in j))').args[0].pars(shared=False)
        fstlocns(0, 5, 0, 19, n=0)
        ```
        """

        key = f'pars_{None if shared is None else bool(shared)}'

        try:
            cached = self._cache[key]
        except KeyError:
            pass
        else:
            return cached

        if not self.is_parenthesizable() and shared is not None:
            self._cache[key] = locn = None if (l := self.bloc) is None else fstlocns(l[0], l[1], l[2], l[3], n=0)

            return locn

        ln, col, end_ln, end_col = self.bloc

        rpars = next_delims(self.root._lines, end_ln, end_col, *self._next_bound())

        if (lrpars := len(rpars)) == 1:  # no pars on right
            if not shared and self.is_solo_call_arg_genexp():
                locn = fstlocns(ln, col + 1, end_ln, end_col - 1, n=-1)
            else:
                locn = fstlocns(ln, col, end_ln, end_col, n=0)

            self._cache[key] = locn

            return locn

        lpars = prev_delims(self.root._lines, *self._prev_bound(), ln, col)

        if (llpars := len(lpars)) == 1:  # no pars on left
            self._cache[key] = locn = fstlocns(ln, col, end_ln, end_col, n=0)

            return locn

        if (llpars <= lrpars and shared is not None and
            (self.is_solo_call_arg() or self.is_solo_class_base() or self.is_solo_matchcls_pat())
        ):
            llpars -= 1

        if llpars != lrpars:  # unbalanced pars so we know we can safely use the lower count
            locn = fstlocns(*lpars[npars := min(llpars, lrpars) - 1], *rpars[npars], n=npars)
        else:
            locn = fstlocns(*lpars[npars := llpars - 1], *rpars[npars], n=npars)

        self._cache[key] = locn

        return locn

    def par(self, force: bool = False, *, whole: bool = True) -> Self:
        """Parenthesize node if it MAY need it. Will not parenthesize atoms which are always enclosed like `List`, or
        nodes which are not `is_parenthesizable()`, unless `force=True`. Will add parentheses to unparenthesized `Tuple`
        and brackets to unbracketed `MatchSequence` adjusting the node location. If dealing with a `Starred` then the
        parentheses are applied to the child.

        **WARNING!** This function doesn't do any higher level syntactic validation. So if you parenthesize something
        that shouldn't be parenthesized, and you wind up poking an eye out, that's on you.

        **Parameters:**
        - `force`: If `True` then will add another layer of parentheses regardless if any already present.
        - `whole`: If at root then parenthesize whole source instead of just node, if `False` then only node.

        **Returns:**
        - `self`

        **Examples:**
        ```py
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

        >>> # parethesize MatchSequence puts brackets like ast.unparse()
        >>> FST('1, 2', 'pattern').par().src
        '[1, 2]'

        >>> FST('*a or b').par().src  # par() a Starred parenthesizes its child
        '*(a or b)'

        >>> FST('call(i = 1 + 2)').keywords[0].value.par().root.src  # not just root node
        'call(i = (1 + 2))'
        ```
        """

        if not force:
            if (not self.is_parenthesizable() or (is_atom := self.is_atom()) in (True, 'pars') or
                ((is_atom or
                  (isinstance(self.a, Starred) and self.a.value.f.is_atom() in (True, 'pars'))) and
                 self.is_enclosed_or_line())  # is_enclosed_or_line() can return 'unenclosable'
            ):
                return self

        with self._modifying():
            if isinstance(self.a, Tuple):
                self._delimit_node(whole)
            elif isinstance(self.a, MatchSequence):
                self._delimit_node(whole, '[]')
            else:
                self._parenthesize_grouping(whole)

        return self

    def unpar(self, node: bool = False, *, shared: bool | None = True) -> Self:
        """Remove all parentheses if present. Normally removes just grouping parentheses but can also remove `Tuple`
        parentheses and `MatchSequence` parentheses or brackets intrinsic to the node if `node=True`. If dealing with a
        `Starred` then the parentheses are checked in and removed from the child. If `shared=None` then will also remove
        parentheses which do not belong to this node but enclose it directly, this is mostly for internal use.

        **WARNING!** This function doesn't do any higher level syntactic validation. So if you unparenthesize something
        that shouldn't be unparenthesized, and you wind up poking an eye out, that's on you.

        **Parameters:**
        - `node`: If `True` then will remove intrinsic parentheses from a parenthesized `Tuple` and parentheses /
            brackets from parenthesized / bracketed `MatchSequence`, otherwise only removes grouping parentheses if
            present.
        - `shared`: Whether to allow merge of parentheses of single call argument generator expression with `Call`
            parentheses or not. If `None` then will attempt to unparenthesize any enclosing parentheses, whether they
            belong to this node or not (meant for internal use).

        **Returns:**
        - `self`

        **Examples:**
        ```py
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

        >>> FST('*(a or b)').unpar().src  # unpar() a Starred unparenthesizes its child
        '*a or b'

        >>> # not just root node
        >>> FST('call(i = (1 + 2))').keywords[0].value.unpar().root.src
        'call(i = 1 + 2)'

        >>> # by default allows sharing
        >>> FST('call(((i for i in j)))').args[0].unpar().root.src
        'call(i for i in j)'

        >>> # unless told not to
        >>> FST('call(((i for i in j)))').args[0].unpar(shared=False).root.src
        'call((i for i in j))'
        ```
        """

        if isinstance(a := self.a, Starred):
            if (value := a.value.f).pars().n:
                with self._modifying():
                    value._unparenthesize_grouping(shared)

            return self

        modifying = None

        if self.pars(None if shared is None else True).n:
            modifying = self._modifying().enter()

            self._unparenthesize_grouping(shared)

        if node:
            if isinstance(self.a, Tuple):
                modifying = modifying or self._modifying().enter()

                self._undelimit_node()

            elif isinstance(self.a, MatchSequence):
                modifying = modifying or self._modifying().enter()

                self._undelimit_node('patterns')

        if modifying:
            modifying.done()

        return self  # ret

    # ------------------------------------------------------------------------------------------------------------------
    # Structure stuff

    def next(self, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:  # TODO: refactor
        """Get next sibling of `self` in syntactic order, only within parent.

        **Parameters:**
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
                present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.

        **Returns:**
        - `None` if last valid sibling in parent, otherwise next node.

        **Examples:**
        ```py
        >>> f = FST('[[1, 2], [3, 4]]')
        >>> f.elts[0].next().src
        '[3, 4]'

        >>> print(f.elts[1].next())
        None
        ```
        """

        if not (parent := self.parent):
            return None

        aparent   = parent.a
        name, idx = self.pfield

        while True:
            next = AST_FIELDS_NEXT[(aparent.__class__, name)]

            if isinstance(next, int):  # special case?
                while True:
                    match next:
                        case 0:  # from Dict.keys
                            next = 1
                            a    = aparent.values[idx]

                        case 1:  # from Dict.values
                            next = 0

                            try:
                                if not (a := aparent.keys[(idx := idx + 1)]):
                                    continue
                            except IndexError:
                                return None

                        case 2:  # from Compare.ops
                            next = 3
                            a    = aparent.comparators[idx]

                        case 6:  # all the logic for Call.args and Call.keywords
                            if not (keywords := aparent.keywords):  # no keywords
                                try:
                                    a = aparent.args[(idx := idx + 1)]
                                except IndexError:
                                    return None

                            elif not (args := aparent.args):  # no args
                                try:
                                    a = keywords[(idx := idx + 1)]
                                except IndexError:
                                    return None

                            elif not isinstance(star := args[-1], Starred):  # both args and keywords but no Starred
                                if name == 'args':
                                    try:
                                        a = args[(idx := idx + 1)]

                                    except IndexError:
                                        name = 'keywords'
                                        a    = keywords[(idx := 0)]

                                else:
                                    try:
                                        a = keywords[(idx := idx + 1)]
                                    except IndexError:
                                        return None

                            else:  # args, keywords AND Starred
                                if name == 'args':
                                    try:
                                        a = args[(idx := idx + 1)]

                                        if (a is star and ((kw := keywords[0]).lineno, kw.col_offset) <
                                            (star.lineno, star.col_offset)
                                        ):  # reached star and there is a keyword before it
                                            name = 'keywords'
                                            idx  = 0
                                            a    = kw

                                            break

                                    except IndexError:  # ran off the end of args, past star, find first kw after it (if any)
                                        star_pos = (star.lineno, star.col_offset)

                                        for a in keywords:
                                            if (a.lineno, a.col_offset) > star_pos:
                                                break
                                        else:
                                            return None

                                else:  # name == 'keywords'
                                    try:
                                        a = keywords[(idx := idx + 1)]

                                    except IndexError:  # ran off the end of keywords, now need to check if star lives here
                                        if ((sa := self.a).lineno, sa.col_offset) < (star.lineno, star.col_offset):
                                            name = 'args'
                                            idx  = len(args) - 1
                                            a    = star

                                        else:
                                            return None

                                    else:
                                        star_pos = (star.lineno, star.col_offset)

                                        if (((sa := self.a).lineno, sa.col_offset) < star_pos and
                                            (a.lineno, a.col_offset) > star_pos
                                        ):  # crossed star, jump back to it
                                            name = 'args'
                                            idx  = len(args) - 1
                                            a    = star

                        case 3:  # from Compare.comparators or Compare.left (via comparators)
                            next = 2

                            try:
                                a = aparent.ops[(idx := idx + 1)]
                            except IndexError:
                                return None

                        case 7:  # all the logic arguments
                            while True:
                                match name:
                                    case 'posonlyargs':
                                        posonlyargs = aparent.posonlyargs
                                        defaults    = aparent.defaults

                                        if (not defaults or (didx := (idx + ((ldefaults := len(defaults)) -
                                            len(args := aparent.args) - len(posonlyargs)))) < 0 or didx >= ldefaults
                                        ):
                                            try:
                                                a = posonlyargs[(idx := idx + 1)]

                                            except IndexError:
                                                name = 'args'
                                                idx  = -1

                                                continue

                                        else:
                                            name = 'defaults'
                                            a    = defaults[idx := didx]

                                    case 'args':
                                        args     = aparent.args
                                        defaults = aparent.defaults

                                        if (not defaults or (didx := (idx + ((ldefaults := len(defaults)) -
                                            len(args := aparent.args)))) < 0  # or didx >= ldefaults
                                        ):
                                            try:
                                                a = args[(idx := idx + 1)]

                                            except IndexError:
                                                name = 'vararg'

                                                if not (a := aparent.vararg):
                                                    continue

                                        else:
                                            name = 'defaults'
                                            a    = defaults[idx := didx]

                                    case 'defaults':
                                        if idx == (ldefaults := len(aparent.defaults)) - 1:  # end of defaults
                                            name = 'vararg'

                                            if not (a := aparent.vararg):
                                                continue

                                        elif (idx := idx + len(args := aparent.args) - ldefaults + 1) >= 0:
                                            name = 'args'
                                            a    = args[idx]

                                        else:
                                            name = 'posonlyargs'
                                            a    = (posonlyargs := aparent.posonlyargs)[(idx := idx + len(posonlyargs))]

                                    case 'vararg':
                                        if kwonlyargs := aparent.kwonlyargs:
                                            name = 'kwonlyargs'
                                            a    = kwonlyargs[(idx := 0)]

                                        elif a := aparent.kwarg:
                                            name = 'kwarg'
                                        else:
                                            return None

                                    case 'kwonlyargs':
                                        kwonlyargs = aparent.kwonlyargs

                                        if a := aparent.kw_defaults[idx]:
                                            name = 'kw_defaults'

                                        else:
                                            try:
                                                a = kwonlyargs[(idx := idx + 1)]

                                            except IndexError:
                                                if a := aparent.kwarg:
                                                    name = 'kwarg'
                                                else:
                                                    return None

                                    case 'kw_defaults':
                                        try:
                                            a = aparent.kwonlyargs[(idx := idx + 1)]

                                        except IndexError:
                                            if a := aparent.kwarg:
                                                name = 'kwarg'
                                            else:
                                                return None

                                        name = 'kwonlyargs'

                                    case 'kwarg':
                                        raise RuntimeError('should not get here')

                                break

                        case 4:  # from MatchMapping.keys
                            next = 5
                            a    = aparent.patterns[idx]

                        case 5:  # from MatchMapping.patterns
                            next = 4

                            try:
                                a = aparent.keys[(idx := idx + 1)]
                            except IndexError:
                                return None

                    if check_with_loc(f := a.f, with_loc):
                        return f

            elif idx is not None:
                sibling = getattr(aparent, name)

                while True:
                    try:
                        if not (a := sibling[(idx := idx + 1)]):  # who knows where a `None` might pop up "next" these days... xD
                            continue

                    except IndexError:
                        break

                    if check_with_loc(f := a.f, with_loc):
                        return f

            while next is not None:
                if isinstance(next, str):
                    name = next

                    if isinstance(sibling := getattr(aparent, next, None), AST):  # None because we know about fields from future python versions
                        if check_with_loc(f := sibling.f, with_loc):
                            return f

                    elif isinstance(sibling, list) and sibling:
                        idx = -1

                        break

                    next = AST_FIELDS_NEXT[(aparent.__class__, name)]

                    continue

                # non-str next, special case

                match next:
                    case 2:  # from Compare.left
                        name = 'comparators'  # will cause to get .ops[0]
                        idx  = -1

                    case 6:  # from Call.func
                        idx  = -1  # will cause to get .args[0]

                break

            else:
                break

            continue

        return None

    def prev(self, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:  # TODO: refactor
        """Get previous sibling of `self` in syntactic order, only within parent.

        **Parameters:**
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
                arguments present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.

        **Returns:**
        - `None` if first valid sibling in parent, otherwise previous node.

        **Examples:**
        ```py
        >>> f = FST('[[1, 2], [3, 4]]')
        >>> f.elts[1].prev().src
        '[1, 2]'

        >>> print(f.elts[0].prev())
        None
        ```
        """

        if not (parent := self.parent):
            return None

        aparent   = parent.a
        name, idx = self.pfield

        while True:
            prev = AST_FIELDS_PREV[(aparent.__class__, name)]

            if isinstance(prev, int):  # special case?
                while True:
                    match prev:
                        case 0:  # from Dict.keys
                            if not idx:
                                return None

                            else:
                                prev = 1
                                a    = aparent.values[(idx := idx - 1)]

                        case 1:  # from Dict.values
                            prev = 0

                            if not (a := aparent.keys[idx]):
                                continue

                        case 6:
                            if not (keywords := aparent.keywords):  # no keywords
                                if idx:
                                    a = aparent.args[(idx := idx - 1)]

                                else:
                                    name = 'func'
                                    a    = aparent.func

                            elif not (args := aparent.args):  # no args
                                if idx:
                                    a = keywords[(idx := idx - 1)]

                                else:
                                    name = 'func'
                                    a    = aparent.func

                            elif not isinstance(star := args[-1], Starred):  # both args and keywords but no Starred
                                if name == 'args':
                                    if idx:
                                        a = aparent.args[(idx := idx - 1)]

                                    else:
                                        name = 'func'
                                        a    = aparent.func

                                else:
                                    if idx:
                                        a = keywords[(idx := idx - 1)]

                                    else:
                                        name = 'args'
                                        a    = args[(idx := len(args) - 1)]

                            else:  # args, keywords AND Starred
                                if name == 'args':
                                    if idx == len(args) - 1:  # is star
                                        star_pos = (star.lineno, star.col_offset)

                                        for i in range(len(keywords) - 1, -1, -1):
                                            if ((kw := keywords[i]).lineno, kw.col_offset) < star_pos:
                                                name = 'keywords'
                                                idx  = i
                                                a    = kw

                                                break

                                        else:
                                            if idx:
                                                a = args[(idx := idx - 1)]

                                            else:
                                                name = 'func'
                                                a    = aparent.func

                                    elif idx:
                                        a = args[(idx := idx - 1)]

                                    else:
                                        name = 'func'
                                        a    = aparent.func

                                else:  # name == 'keywords'
                                    star_pos = (star.lineno, star.col_offset)

                                    if not idx:
                                        name = 'args'

                                        if ((sa := self.a).lineno, sa.col_offset) > star_pos:  # all keywords above star so pass on to star
                                            idx  = len(args) - 1
                                            a    = star

                                        elif (largs := len(args)) < 2:  # no args left, we done here
                                            name = 'func'
                                            a    = aparent.func

                                        else:  # some args left, go to those
                                            a = args[(idx := largs - 2)]

                                    else:
                                        a = keywords[(idx := idx - 1)]

                                        if ((a.lineno, a.col_offset) < star_pos and
                                            ((sa := self.a).lineno, sa.col_offset) > star_pos
                                        ):  # crossed star walking back, return star
                                            name = 'args'
                                            idx  = len(args) - 1
                                            a    = star

                        case 2:  # from Compare.ops
                            if not idx:
                                prev = 'left'

                                break

                            else:
                                prev = 3
                                a    = aparent.comparators[(idx := idx - 1)]

                        case 3:  # from Compare.comparators
                            prev = 2
                            a    = aparent.ops[idx]

                        case 7:
                            while True:
                                match name:
                                    case 'posonlyargs':
                                        posonlyargs = aparent.posonlyargs
                                        defaults    = aparent.defaults

                                        if ((didx := idx - len(aparent.args) - len(posonlyargs) + len(defaults) - 1) >=
                                            0
                                        ):
                                            name = 'defaults'
                                            a    = defaults[(idx := didx)]

                                        elif idx > 0:
                                            a = posonlyargs[(idx := idx - 1)]
                                        else:
                                            return None

                                    case 'args':
                                        args     = aparent.args
                                        defaults = aparent.defaults

                                        if (didx := idx - len(args) + len(defaults) - 1) >= 0:
                                            name = 'defaults'
                                            a    = defaults[(idx := didx)]

                                        elif idx > 0:
                                            a = args[(idx := idx - 1)]

                                        elif posonlyargs := aparent.posonlyargs:
                                            name = 'posonlyargs'
                                            a    = posonlyargs[(idx := len(posonlyargs) - 1)]

                                        else:
                                            return None

                                    case 'defaults':
                                        args     = aparent.args
                                        defaults = aparent.defaults

                                        if (idx := idx + len(args) - len(defaults)) >= 0:
                                            name = 'args'
                                            a    = args[idx]

                                        else:
                                            name = 'posonlyargs'
                                            a    = (posonlyargs := aparent.posonlyargs)[idx + len(posonlyargs)]

                                    case 'vararg':
                                        if defaults := aparent.defaults:
                                            name = 'defaults'
                                            a    = defaults[(idx := len(defaults) - 1)]

                                        elif args := aparent.args:
                                            name = 'args'
                                            a    = args[(idx := len(args) - 1)]

                                        elif posonlyargs := aparent.posonlyargs:
                                            name = 'posonlyargs'
                                            a    = posonlyargs[(idx := len(posonlyargs) - 1)]

                                        else:
                                            return None

                                    case 'kwonlyargs':
                                        if not idx:
                                            name = 'vararg'

                                            if not (a := aparent.vararg):
                                                continue

                                        elif a := aparent.kw_defaults[(idx := idx - 1)]:
                                            name = 'kw_defaults'

                                        else:
                                            a = aparent.kwonlyargs[idx]

                                    case 'kw_defaults':
                                        name = 'kwonlyargs'
                                        a    = aparent.kwonlyargs[idx]

                                    case 'kwarg':
                                        if kw_defaults := aparent.kw_defaults:
                                            if a := kw_defaults[(idx := len(kw_defaults) - 1)]:
                                                name = 'kw_defaults'

                                            else:
                                                name = 'kwonlyargs'
                                                a    = (kwonlyargs := aparent.kwonlyargs)[(idx := len(kwonlyargs) - 1)]

                                        else:
                                            name = 'vararg'

                                            if not (a := aparent.vararg):
                                                continue

                                break

                        case 4:  # from Keys.keys
                            if not idx:
                                return None

                            else:
                                prev = 5
                                a    = aparent.patterns[(idx := idx - 1)]

                        case 5:  # from Keys.patterns
                            prev = 4
                            a    = aparent.keys[idx]

                    if check_with_loc(f := a.f, with_loc):
                        return f

            else:
                sibling = getattr(aparent, name)

                while idx:
                    if not (a := sibling[(idx := idx - 1)]):
                        continue

                    if check_with_loc(f := a.f, with_loc):
                        return f

            while prev is not None:
                if isinstance(prev, str):
                    name = prev

                    if isinstance(sibling := getattr(aparent, prev, None), AST):  # None because could have fields from future python versions
                        if check_with_loc(f := sibling.f, with_loc):
                            return f

                    elif isinstance(sibling, list) and (idx := len(sibling)):
                        break

                    prev = AST_FIELDS_PREV[(aparent.__class__, name)]

                    continue

                # non-str prev, special case

                raise RuntimeError('should not get here')  # break  # when entrable special cases from ahead appear in future py versions add them here

            else:
                break

            continue

        return None

    def first_child(self, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:
        """Get first valid child in syntactic order.

        **Parameters:**
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
                arguments present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.

        **Returns:**
        - `None` if no valid children, otherwise first valid child.

        **Examples:**
        ```py
        >>> f = FST('def f(a: list[str], /, reject: int, *c, d=100, **e): pass')
        >>> f.first_child().src
        'a: list[str], /, reject: int, *c, d=100, **e'

        >>> f.args.first_child().src
        'a: list[str]'

        >>> f.args.first_child().first_child().src
        'list[str]'
        ```
        """

        for name in AST_FIELDS[(a := self.a).__class__]:
            if (child := getattr(a, name, None)):
                if isinstance(child, AST):
                    if check_with_loc(f := child.f, with_loc):
                        return f

                elif isinstance(child, list):
                    if (c := child[0]) and check_with_loc(f := c.f, with_loc):
                        return f

                    return FST(Pass(), self, astfield(name, 0)).next(with_loc)  # Pass() is a hack just to have a simple AST node

        return None

    def last_child(self, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:
        """Get last valid child in syntactic order.

        **Parameters:**
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
                arguments present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.

        **Returns:**
        - `None` if no valid children, otherwise last valid child.

        **Examples:**
        ```py
        >>> f = FST('def f(a: list[str], /, reject: int, *c, d=100, **e): pass')
        >>> f.last_child().src
        'pass'

        >>> f.args.last_child().src
        'e'
        ```
        """

        if (isinstance(a := self.a, Call)) and a.args and (keywords := a.keywords) and isinstance(a.args[-1], Starred):  # super-special case Call with args and keywords and a Starred, it could be anywhere in there, including after last keyword, defer to prev() logic
            fst_         = FST(f := Pass(), self, astfield('keywords', len(keywords)))
            f.lineno     = 0x7fffffffffffffff
            f.col_offset = 0

            return fst_.prev(with_loc)

        for name in reversed(AST_FIELDS[(a := self.a).__class__]):
            if (child := getattr(a, name, None)):
                if isinstance(child, AST):
                    if check_with_loc(f := child.f, with_loc):
                        return f

                elif isinstance(child, list):
                    if (c := child[-1]) and check_with_loc(f := c.f, with_loc):
                        return f

                    return FST(Pass(), self, astfield(name, len(child) - 1)).prev(with_loc)  # Pass() is a hack just to have a simple AST node

        return None

    def last_header_child(self, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:
        r"""Get last valid child in syntactic order in a block header (before the `:`), e.g. the `something` in
        `if something: pass`.

        **Parameters:**
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
                arguments present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.

        **Returns:**
        - `None` if no valid children or if `self` is not a block statement, otherwise last valid child in the block
            header.

        **Examples:**
        ```py
        >>> print(FST('if something:\n    i = 2\n    i = 3')
        ...       .last_header_child().src)
        something

        >>> print(FST('try: pass\nexcept Exception as exc: pass').handlers[0]
        ...       .last_header_child().src)
        Exception

        >>> print(FST('with a, b: pass').last_header_child().src)
        b

        >>> print(FST('try: pass\nfinally: pass').last_header_child())
        None

        >>> print(FST('i = 1').last_header_child())
        None
        ```
        """

        if not (child := last_block_header_child(self.a)):
            return None

        if check_with_loc(f := child.f, with_loc):
            return f

        return self.prev_child(f, with_loc)

    def next_child(self, from_child: FST | None, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:
        """Get the next child in syntactic order, meant for simple iteration.

        This is a slower way to iterate vs. `walk()`, but will work correctly if ANYTHING in the tree is modified during
        the walk as long as the replaced node and its parent is used for the following call.

        **Parameters:**
        - `from_child`: Child node we are coming from which may or may not have location.
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
                arguments present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.

        **Returns:**
        - `None` if last valid child in `self`, otherwise next child node.

        **Examples:**
        ```py
        >>> f = FST('[[1, 2], [3, 4]]')
        >>> f.next_child(f.elts[0]).src
        '[3, 4]'

        >>> print(f.next_child(f.elts[1]))
        None

        >>> f = FST('[this, is_, reparsed, each, step, and_, still, walks, ok]')
        >>> n = None
        >>> while n := f.next_child(n):
        ...     if isinstance(n.a, Name):
        ...         n = n.replace(n.id[::-1], raw=True)  # raw here reparses all nodes
        >>> f.src
        '[siht, _si, desraper, hcae, pets, _dna, llits, sklaw, ko]'
        ```
        """

        return self.first_child(with_loc) if from_child is None else from_child.next(with_loc)

    def prev_child(self, from_child: FST | None, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:
        """Get the previous child in syntactic order, meant for simple iteration.

        This is a slower way to iterate vs. `walk()`, but will work correctly if ANYTHING in the tree is modified during the
        walk as long as the replaced node and its parent is used for the following call.

        **Parameters:**
        - `from_child`: Child node we are coming from which may or may not have location.
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
                present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
                not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
                with calculated locations.

        **Returns:**
        - `None` if first valid child in `self`, otherwise previous child node.

        **Examples:**
        ```py
        >>> f = FST('[[1, 2], [3, 4]]')
        >>> f.prev_child(f.elts[1]).src
        '[1, 2]'

        >>> print(f.prev_child(f.elts[0]))
        None

        >>> f = FST('[this, is_, reparsed, each, step, and_, still, walks, ok]')
        >>> n = None
        >>> while n := f.prev_child(n):
        ...     if isinstance(n.a, Name):
        ...         n = n.replace(n.id[::-1], raw=True)  # raw here reparses all nodes
        >>> f.src
        '[siht, _si, desraper, hcae, pets, _dna, llits, sklaw, ko]'
        ```
        """

        return self.last_child(with_loc) if from_child is None else from_child.prev(with_loc)

    def step_fwd(self, with_loc: bool | Literal['all', 'own', 'allown'] = True, *, recurse_self: bool = True,
                 ) -> FST | None:
        """Step forward in the tree in syntactic order, as if `walk()`ing forward, NOT the inverse of `step_back()`. Will
        walk up parents and down children to get the next node, returning `None` only when we are at the end of the whole
        thing.

        **Parameters:**
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
                arguments present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.
            - `'allown'` Same as `'own'` but recurse into nodes with non-own locations (even though those nodes are not
                returned). This is only really meant for internal use to safely call from `.loc` location calculation.
        - `recurse_self`: Whether to allow recursion into `self` to return children or move directly to next nodes of
            `self` on start.

        **Returns:**
        - `None` if last valid node in tree, otherwise next node in order.

        **Examples:**
        ```py
        >>> f = FST('[[1, 2], [3, 4]]')
        >>> f.elts[0].src
        '[1, 2]'

        >>> f.elts[0].step_fwd().src
        '1'

        >>> f.elts[0].step_fwd(recurse_self=False).src
        '[3, 4]'

        >>> f.elts[0].elts[1].src
        '2'

        >>> f.elts[0].elts[1].step_fwd().src
        '[3, 4]'

        >>> f = FST('[this, [is_, [reparsed, each], step, and_, still], walks, ok]')
        >>> n = f.elts[0]
        >>> while True:
        ...     if isinstance(n.a, Name):
        ...         n = n.replace(n.id[::-1], raw=True)  # raw here reparses all nodes
        ...     if not (n := n.step_fwd()):
        ...         break
        >>> f.src
        '[siht, [_si, [desraper, hcae], pets, _dna, llits], sklaw, ko]'
        ```
        """

        if allown := with_loc == 'allown':
            with_loc = True

        while True:
            if not recurse_self or not (fst_ := self.first_child(with_loc)):
                recurse_self = True

                while not (fst_ := self.next(with_loc)):
                    if not (self := self.parent):
                        return None

            if not allown or fst_.has_own_loc:
                break

            self = fst_

        return fst_

    def step_back(self, with_loc: bool | Literal['all', 'own', 'allown'] = True, *, recurse_self: bool = True,
                  ) -> FST | None:
        """Step backward in the tree in syntactic order, as if `walk()`ing backward, NOT the inverse of `step_fwd()`.
        Will walk up parents and down children to get the next node, returning `None` only when we are at the beginning
        of the whole thing.

        **Parameters:**
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
                arguments present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.
            - `'allown'` Same as `'own'` but recurse into nodes with non-own locations (even though those nodes are not
                returned). This is only really meant for internal use to safely call from `.loc` location calculation.
        - `recurse_self`: Whether to allow recursion into `self` to return children or move directly to previous nodes
            of `self` on start.

        **Returns:**
        - `None` if first valid node in tree, otherwise previous node in order.

        **Examples:**
        ```py
        >>> from fst import *

        >>> f = FST('[[1, 2], [3, 4]]')
        >>> f.elts[1].src
        '[3, 4]'

        >>> f.elts[1].step_back().src
        '4'

        >>> f.elts[1].step_back(recurse_self=False).src
        '[1, 2]'

        >>> f.elts[1].elts[0].src
        '3'

        >>> f.elts[1].elts[0].step_back().src
        '[1, 2]'

        >>> f = FST('[this, [is_, [reparsed, each], step, and_, still], walks, ok]')
        >>> n = f.elts[-1]
        >>> while True:
        ...     if isinstance(n.a, Name):
        ...         n = n.replace(n.id[::-1], raw=True)  # raw here reparses all nodes
        ...     if not (n := n.step_back()):
        ...         break
        >>> f.src
        '[siht, [_si, [desraper, hcae], pets, _dna, llits], sklaw, ko]'
        ```
        """

        if allown := with_loc == 'allown':
            with_loc = True

        while True:
            if not recurse_self or not (fst_ := self.last_child(with_loc)):
                recurse_self = True

                while not (fst_ := self.prev(with_loc)):
                    if not (self := self.parent):
                        return None

            if not allown or fst_.has_own_loc:
                break

            self = fst_

        return fst_

    def walk(self, with_loc: bool | Literal['all', 'own'] = False, *, self_: bool = True, recurse: bool = True,
              scope: bool = False, back: bool = False) -> Generator[FST, bool, None]:
        r"""Walk `self` and descendants in syntactic order. When walking, you can `send(False)` to the generator to skip
        recursion into the current child. `send(True)` to allow recursion into child if called with `recurse=False` or
        `scope=True` would otherwise disallow it. Can send multiple times, last value sent takes effect.

        The walk is defined forwards or backwards in that it returns a parent, then recurses into the children and walks
        those in the given direction, recursing into each child's children before continuing with siblings. Walking
        backwards will not generate the same sequence as `list(walk())[::-1]` due to this behavior.

        It is safe to modify the nodes (or previous nodes) as they are being walked as long as those modifications don't
        touch the parent or following nodes. This means normal `.replace()` is fine as long as `raw=False`.

        The walk is relatively efficient but if all you need to do is just walk ALL the `AST` children without any bells
        or whistles then `ast.walk()` will be a bit faster.

        **Parameters:**
        - `with_loc`: Return nodes depending on their location information.
            - `False`: All nodes with or without location.
            - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
                `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
                arguments present).
            - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
                do not always have a well defined location).
            - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger
                nodes with calculated locations.
        - `self_`: If `True` then self will be returned first with the possibility to skip children with `send(False)`,
            otherwise will start directly with children.
        - `recurse`: Whether to recurse into children by default, `send(True)` for a given node will always override
            this.
        - `scope`: If `True` then will walk only within the scope of `self`. Meaning if called on a `FunctionDef` then
            will only walk children which are within the function scope. Will yield children which have their own
            scopes, and the parts of them which are visible in this scope (like default argument values), but will not
            recurse into
            them unless `send(True)` is done for that child.
        - `back`: If `True` then walk every node in reverse syntactic order. This is not the same as a full forwards
            walk reversed due to recursion (parents are still returned before children, only in reverse sibling order).

        **Examples:**
        ```py
        >>> import ast

        >>> f = FST('def f(a: list[str], /, reject: int, *c, d=100, **e): pass')
        >>> for g in (gen := f.walk(with_loc=True)):
        ...     if isinstance(g.a, ast.arg) and g.a.arg == 'reject':
        ...         _ = gen.send(False)
        ...     else:
        ...         print(f'{g!r:<30}{g.src[:50]!r}')
        <FunctionDef ROOT 0,0..0,57>  'def f(a: list[str], /, reject: int, *c, d=100, **e'
        <arguments 0,6..0,50>         'a: list[str], /, reject: int, *c, d=100, **e'
        <arg 0,6..0,18>               'a: list[str]'
        <Subscript 0,9..0,18>         'list[str]'
        <Name 0,9..0,13>              'list'
        <Name 0,14..0,17>             'str'
        <arg 0,37..0,38>              'c'
        <arg 0,40..0,41>              'd'
        <Constant 0,42..0,45>         '100'
        <arg 0,49..0,50>              'e'
        <Pass 0,53..0,57>             'pass'

        >>> f = FST('''
        ... def f():
        ...     def g(arg=1) -> int:
        ...         pass
        ...     val = [i for i in iterator]
        ... '''.strip())

        >>> for g in f.walk(True, scope=True):
        ...     print(f'{g!r:<30}{g.src[:47]!r}')
        <FunctionDef ROOT 0,0..3,31>  'def f():\n    def g(arg=1) -> int:\n        pass\n'
        <FunctionDef 1,4..2,12>       'def g(arg=1) -> int:\n        pass'
        <Constant 1,14..1,15>         '1'
        <Assign 3,4..3,31>            'val = [i for i in iterator]'
        <Name 3,4..3,7>               'val'
        <ListComp 3,10..3,31>         '[i for i in iterator]'
        <Name 3,22..3,30>             'iterator'

        >>> for g in f.walk(True, back=True):
        ...     print(f'{g!r:<30}{g.src[:47]!r}')
        <FunctionDef ROOT 0,0..3,31>  'def f():\n    def g(arg=1) -> int:\n        pass\n'
        <Assign 3,4..3,31>            'val = [i for i in iterator]'
        <ListComp 3,10..3,31>         '[i for i in iterator]'
        <comprehension 3,13..3,30>    'for i in iterator'
        <Name 3,22..3,30>             'iterator'
        <Name 3,17..3,18>             'i'
        <Name 3,11..3,12>             'i'
        <Name 3,4..3,7>               'val'
        <FunctionDef 1,4..2,12>       'def g(arg=1) -> int:\n        pass'
        <Pass 2,8..2,12>              'pass'
        <Name 1,20..1,23>             'int'
        <arguments 1,10..1,15>        'arg=1'
        <Constant 1,14..1,15>         '1'
        <arg 1,10..1,13>              'arg'
        ```
        """

        if self_:
            if not check_with_loc(self, with_loc):
                return

            recurse_ = 1

            while (sent := (yield self)) is not None:
                recurse_ = sent

            if not self.a:
                self = self.repath()

            if not recurse_:
                return

            elif recurse_ is True:  # user changed their mind?!?
                recurse = True
                scope   = False

        stack = None
        ast   = self.a

        if scope:  # some parts of a FunctionDef or ClassDef are outside its scope
            if isinstance(ast, list):
                stack = ast[:] if back else ast[::-1]

            elif isinstance(ast, (ClassDef, Module, Interactive)):
                if back:
                    stack = []

                    if type_params := getattr(ast, 'type_params', None):
                        stack.extend(type_params)

                    stack.extend(ast.body)

                else:
                    stack = ast.body[::-1]

                    if type_params := getattr(ast, 'type_params', None):
                        stack.extend(type_params[::-1])

            elif (is_func := isinstance(ast, (FunctionDef, AsyncFunctionDef))) or isinstance(ast, Lambda):
                if back:
                    stack = []

                    if type_params := getattr(ast, 'type_params', None):
                        stack.extend(type_params)

                    stack.append(ast.args)

                    if is_func:
                        stack.extend(ast.body)
                    else:
                        stack.append(ast.body)

                else:
                    stack = ast.body[::-1] if is_func else [ast.body]

                    stack.append(ast.args)

                    if type_params := getattr(ast, 'type_params', None):
                        stack.extend(type_params[::-1])

            elif (is_elt := isinstance(ast, (ListComp, SetComp, GeneratorExp))) or isinstance(ast, DictComp):
                if back:
                    stack = ([ast.elt] if is_elt else [ast.key, ast.value]) + (generators := ast.generators)
                else:
                    stack = (generators := ast.generators)[::-1] + ([ast.elt] if is_elt else [ast.value, ast.key])

                skip_iter = generators[0].iter

            elif isinstance(ast, Expression):
                stack = [ast.body]

        if stack is None:
            stack = syntax_ordered_children(ast)

            if not back:
                stack = stack[::-1]

        while stack:
            if not (ast := stack.pop()):
                continue

            fst_ = ast.f

            if not check_with_loc(fst_, with_loc):
                continue

            recurse_ = recurse

            while (sent := (yield fst_)) is not None:
                recurse_ = 1 if sent else False

            if not fst_.a:  # has been changed by the player
                fst_ = fst_.repath()

            ast = fst_.a  # could have just modified the ast

            if recurse_ is not True:
                if recurse_:  # user did send(True), walk this child unconditionally
                    yield from fst_.walk(with_loc, self_=False, back=back)

            else:
                if scope:
                    recurse_ = False

                    if isinstance(ast, ClassDef):
                        if back:
                            stack.extend(ast.decorator_list)
                            stack.extend(ast.bases)
                            stack.extend(ast.keywords)

                        else:
                            stack.extend(ast.keywords[::-1])
                            stack.extend(ast.bases[::-1])
                            stack.extend(ast.decorator_list[::-1])

                    elif isinstance(ast, (FunctionDef, AsyncFunctionDef)):
                        if back:
                            stack.extend(ast.decorator_list)
                            stack.extend(ast.args.defaults)
                            stack.extend(ast.args.kw_defaults)

                        else:
                            stack.extend(ast.args.kw_defaults[::-1])
                            stack.extend(ast.args.defaults[::-1])
                            stack.extend(ast.decorator_list[::-1])

                    elif isinstance(ast, Lambda):
                        if back:
                            stack.extend(ast.args.defaults)
                            stack.extend(ast.args.kw_defaults)
                        else:
                            stack.extend(ast.args.kw_defaults[::-1])
                            stack.extend(ast.args.defaults[::-1])

                    elif isinstance(ast, (ListComp, SetComp, DictComp, GeneratorExp)):
                        comp_first_iter = ast.generators[0].iter
                        gen             = fst_.walk(with_loc, self_=False, back=back)

                        for f in gen:  # all NamedExpr assignments below are visible here, yeah, its ugly
                            if (a := f.a) is comp_first_iter or (f.pfield.name == 'target' and isinstance(a, Name) and
                                                                isinstance(f.parent.a, NamedExpr)):
                                subrecurse = recurse

                                while (sent := (yield f)) is not None:
                                    subrecurse = sent

                                if not subrecurse:
                                    gen.send(False)

                    elif isinstance(ast, comprehension):  # this only comes from top level comprehension, not ones encountered here
                        if back:
                            stack.append(ast.target)

                            if (a := ast.iter) is not skip_iter:
                                stack.append(a)

                            if a := ast.ifs:
                                stack.extend(a)

                        else:
                            if a := ast.ifs:
                                stack.extend(a)

                            if (a := ast.iter) is not skip_iter:
                                stack.append(a)

                            stack.append(ast.target)

                    else:
                        recurse_ = True

                if recurse_:
                    children = syntax_ordered_children(ast)

                    stack.extend(children if back else children[::-1])

    def parents(self, self_: bool = False) -> Generator[FST, None, None]:
        """Generator which yields parents all the way up to root. If `self_` is `True` then will yield `self` first.

        **Parameters:**
        - `self_`: Whether to yield `self` first.

        **Examples:**
        ```py
        >>> list(FST('i = (f(), g())', 'exec').body[0].value.elts[0].parents())
        [<Tuple 0,4..0,14>, <Assign 0,0..0,14>, <Module ROOT 0,0..0,14>]

        >>> list(FST('i = (f(), g())', 'exec').body[0].value.elts[0].parents(self_=True))
        [<Call 0,5..0,8>, <Tuple 0,4..0,14>, <Assign 0,0..0,14>, <Module ROOT 0,0..0,14>]
        ```
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

        **Examples:**
        ```py
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
        ```
        """

        types = (stmt, ast_mod) if mod else stmt

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_stmtish(self, self_: bool = False, mod: bool = True) -> FST | None:
        r"""The first parent which is a `stmt`, `ExceptHandler`, `match_case` or optionally `mod` node (if any). If
        `self_` is `True` then will check `self` first, otherwise only checks parents.

        **Examples:**
        ```py
        >>> (FST('try: pass\nexcept: pass', 'exec')
        ...  .body[0].handlers[0].body[0].parent_stmtish())
        <ExceptHandler 1,0..1,12>

        >>> FST('try: pass\nexcept: pass', 'exec').body[0].handlers[0].parent_stmtish()
        <Try 0,0..1,12>

        >>> FST('try: pass\nexcept: pass', 'exec').body[0].parent_stmtish()
        <Module ROOT 0,0..1,12>

        >>> FST('match a:\n  case 1: pass').cases[0].body[0].parent_stmtish()
        <match_case 1,2..1,14>

        >>> FST('match a:\n  case 1: pass').cases[0].pattern.parent_stmtish()
        <match_case 1,2..1,14>
        ```
        """

        types = STMTISH_OR_MOD if mod else STMTISH

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_block(self, self_: bool = False, mod: bool = True) -> FST | None:
        """The first parent which opens a block that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `For`, `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`,
        `TryStar`, `ExceptHandler`, `match_case` or optionally `mod` node (if any). If `self_` is `True` then will check
        `self` first, otherwise only checks parents.

        **Examples:**
        ```py
        >>> FST('if 1: i = 1', 'exec').body[0].body[0].value.parent_block()
        <If 0,0..0,11>

        >>> FST('if 1: i = 1', 'exec').body[0].parent_block()
        <Module ROOT 0,0..0,11>
        ```
        """

        types = BLOCK_OR_MOD if mod else BLOCK

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_scope(self, self_: bool = False, mod: bool = True) -> FST | None:
        r"""The first parent which opens a scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `Lambda`, `ListComp`, `SetComp`, `DictComp`, `GeneratorExp` or optionally `mod`
        node (if any). If `self_` is `True` then will check `self` first, otherwise only checks parents.

        **Examples:**
        ```py
        >>> FST('if 1: i = 1', 'exec').body[0].body[0].value.parent_scope()
        <Module ROOT 0,0..0,11>

        >>> (FST('def f():\n  if 1: i = 1', 'exec')
        ...  .body[0].body[0].body[0].value.parent_scope())
        <FunctionDef 0,0..1,13>

        >>> FST('lambda: None', 'exec').body[0].value.body.parent_scope()
        <Lambda 0,0..0,12>

        >>> FST('[i for i in j]', 'exec').body[0].value.elt.parent_scope()
        <ListComp 0,0..0,14>
        ```
        """

        types = SCOPE_OR_MOD if mod else SCOPE

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_named_scope(self, self_: bool = False, mod: bool = True) -> FST | None:
        r"""The first parent which opens a named scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef` or optionally `mod` node (if any). If `self_` is `True` then will check `self`
        first, otherwise only checks parents.

        **Examples:**
        ```py
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
        ```
        """

        types = NAMED_SCOPE_OR_MOD if mod else NAMED_SCOPE

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_non_expr(self, self_: bool = False, strict: bool = False) -> FST | None:
        r"""The first parent which is not an `expr`. If `self_` is `True` then will check `self` first (possibly
        returning `self`), otherwise only checks parents.

        **Parameters:**
        - `self_`: Whether to include `self` in the search, if so and `self` matches criteria then it is returned.
        - `strict`: `False` means consider `comprehension`, `arguments`, `arg` and `keyword` nodes as `expr` for the
            sake of the walk up since these nodes can have other `expr` parents. `True` means only `expr` nodes, which
            means you could get an `arg` or `comprehension` node for example which still has `expr` parents. Also
            `expr_context`, `boolop`, `operator`, `unaruop` and `cmpop` are included if `strict=False` but this only
            makes sense if `self_=True` and you are calling this function on one of those.

        **Examples:**
        ```py
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
        ```
        """

        types = expr if strict else EXPRISH_ALL  # ops because of maybe self_

        if self_ and not isinstance(self.a, types):
            return self

        while (self := self.parent) and isinstance(self.a, types):
            pass

        return self

    def parent_pattern(self, self_: bool = False) -> FST | None:
        r"""The first parent which is a `pattern`. If `self_` is `True` then will check `self` first (possibly returning
        `self`), otherwise only checks parents.

        **Parameters:**
        - `self_`: Whether to include `self` in the search, if so and `self` matches criteria then it is returned.

        **Examples:**
        ```py
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
        ```
        """

        if self_ and isinstance(self.a, pattern):
            return self

        while (self := self.parent) and not isinstance(a := self.a, pattern):
            if isinstance(a, (match_case, stmt)):
                return None

        return self

    def child_path(self, child: FST, as_str: bool = False) -> list[astfield] | builtins.str:
        """Get path to `child` node from `self` which can later be used on a copy of this tree to get to the  same
        relative child node.

        **Parameters:**
        - `child`: Child node to get path to, can be `self` in which case an empty path is returned.
        - `as_str`: If `True` will return the path as a python-ish string suitable for attribute access, else a list of
            `astfield`s which can be used more directly.

        **Returns:**
        - `list[astfield] | str`: Path to child if exists, otherwise raises.

        **Examples:**
        ```py
        >>> (f := FST('[i for i in j]', 'exec')).child_path(f.body[0].value.elt)
        [astfield('body', 0), astfield('value'), astfield('elt')]

        >>> ((f := FST('[i for i in j]', 'exec'))
        ...  .child_path(f.body[0].value.elt, as_str=True))
        'body[0].value.elt'

        >>> (f := FST('i')).child_path(f)
        []

        >>> (f := FST('i')).child_path(f, as_str=True)
        ''
        ```
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
        ```py
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
        ```
        """

        if isinstance(path, str):
            path = [astfield(p[:i], int(p[i + 1 : -1])) if (i := p.find('[')) != -1 else astfield(p)
                    for p in path.split('.')] if path else []

        for p in path:
            if (next := p.get_no_raise(self)) is False:
                return self if last_valid else False

            self = next

        return self

    def repath(self) -> FST:
        """Recalculate `self` from path from root. Useful if `self` has been replaced by another node by some operation.
        When nodes are deleted the corresponding `FST.a` and `AST.f` attributes are set to `None`. The `root`, `parent`
        and `pfield` attributes are left so that things like this can work. Useful when a node has been deleted but you
        want to know where it was and what may be there now.

        **Returns:**
        - `FST`: Possibly `self` or the node which took our place at our relative position from `root`.

        **Examples:**
        ```py
        >>> f = FST('[0, 1, 2, 3]')
        >>> g = f.elts[1]
        >>> print(type(g.a), g.root)
        <class 'ast.Constant'> <List ROOT 0,0..0,12>

        >>> f.put('x', 1, raw=True)  # raw forces reparse at List
        <List ROOT 0,0..0,12>

        >>> print(g.a, g.root)
        None <List ROOT 0,0..0,12>

        >>> g = g.repath()
        >>> print(type(g.a), g.root)
        <class 'ast.Name'> <List ROOT 0,0..0,12>
        ```
        """

        return (root := self.root).child_from_path(root.child_path(self))

    def find_loc(self, ln: int, col: int, end_ln: int, end_col: int, exact: bool = True) -> FST | None:
        r"""Find the lowest level node which entirely contains location (starting search at `self`). To reiterate, the
        search will only find nodes at self or below, no parents.

        **Parameters:**
        - `ln`: Start line of location to search for (0 based).
        - `col`: Start column (character) on start line.
        - `end_ln`: End line of location to search for (0 based, inclusive).
        - `end_col`: End column (character, inclusive with `FST.end_col`, exclusive with `FST.col`) on end line.
        - `exact`: Whether to allow return of exact location match with node or not. `True` means allow return of node
            which matches location exactly. Otherwise the location must be inside the node but cannot be touching BOTH
            ends of the node. This basically determines whether you can get the exact node of the location or its
            parent.

        **Returns:**
        - `FST | None`: Node which entirely contains location, either exactly or not, or `None` if no such node.

        **Examples:**
        ```py
        >>> FST('i = val', 'exec').find_loc(0, 6, 0, 7)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_loc(0, 4, 0, 7)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_loc(0, 4, 0, 7, exact=False)
        <Assign 0,0..0,7>

        >>> FST('i = val', 'exec').find_loc(0, 5, 0, 7, exact=False)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_loc(0, 4, 0, 6, exact=False)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_loc(0, 3, 0, 7)
        <Assign 0,0..0,7>

        >>> FST('i = val', 'exec').find_loc(0, 3, 0, 7, exact=False)
        <Assign 0,0..0,7>

        >>> print(FST('i = val', 'exec').find_loc(0, 0, 0, 7, exact=False))
        None

        >>> FST('i = val\n', 'exec').find_loc(0, 0, 0, 7, exact=False)
        <Module ROOT 0,0..1,0>
        ```
        """

        fln, fcol, fend_ln, fend_col = self.loc

        if ((((same_ln := fln == ln) and fcol <= col) or fln < ln) and
            (((same_end_ln := fend_ln == end_ln) and fend_col >= end_col) or fend_ln > end_ln)
        ):
            if not exact and same_ln and same_end_ln and fcol == col and fend_col == end_col:
                return None

        else:
            return None

        while True:
            for f in self.walk('all', self_=False):
                fln, fcol, fend_ln, fend_col = f.loc

                if fend_ln < ln or (fend_ln == ln and fend_col <= col):
                    continue

                if (fln > ln or ((same_ln := fln == ln) and fcol > col) or
                    fend_ln < end_ln or ((same_end_ln := fend_ln == end_ln) and fend_col < end_col)
                ):
                    return self

                if not exact and same_ln and same_end_ln and fcol == col and fend_col == end_col:
                    return self

                self = f

                break

            else:
                return self

    def find_in_loc(self, ln: int, col: int, end_ln: int, end_col: int) -> FST | None:
        """Find the first highest level node which is contained entirely in location (inclusive, starting search at
        `self`). To reiterate, the search will only find nodes at self or below, no parents.

        **Parameters:**
        - `ln`: Start line of location to search (0 based).
        - `col`: Start column (character) on start line.
        - `end_ln`: End line of location to search (0 based, inclusive).
        - `end_col`: End column (character, inclusive with `FST.end_col`, exclusive with `FST.col`) on end line.

        **Returns:**
        - `FST | None`: First node which is entirely contained in the location or `None` if no such node.

        **Examples:**
        ```py
        >>> FST('i = val', 'exec').find_in_loc(0, 0, 0, 7)
        <Module ROOT 0,0..0,7>

        >>> FST('i = val', 'exec').find_in_loc(0, 1, 0, 7)
        <Name 0,4..0,7>

        >>> FST('i = val', 'exec').find_in_loc(0, 4, 0, 7)
        <Name 0,4..0,7>

        >>> print(FST('i = val', 'exec').find_in_loc(0, 5, 0, 7))
        None
        ```
        """

        fln, fcol, fend_ln, fend_col = self.loc

        if ((fln > ln or (fln == ln and fcol >= col)) and
            (fend_ln < end_ln or (fend_ln == end_ln and fend_col <= end_col))
        ):
            return self

        while True:
            for f in self.walk('all', self_=False):
                fln, fcol, fend_ln, fend_col = f.loc

                if fln < ln or (fln == ln and fcol < col):
                    continue

                if fend_ln < end_ln or (fend_ln == end_ln and fend_col <= end_col):
                    return f

                self = f

                break

            else:
                return None

    # ------------------------------------------------------------------------------------------------------------------
    # Low level

    def get_parse_mode(self) -> builtins.str | type[AST] | None:
        r"""Determine the parse mode for this node. This is the extended parse mode as per `Mode`, not the `ast.parse()`
        mode. Returns a mode which is guaranteed to reparse this assumed-valid element to an exact copy of itself. This
        mode is not guaranteed to be the same as was used to create the `FST`, just guaranteed to be able to recreate
        it. Mostly it just returns the `AST` type, but in cases where that won't parse to this `FST` it will return
        a string mode. This is a quick just a check, doesn't verify everything.

        **Returns:**
        - `str`: One of the special text specifiers. Will be returned for most slices and special cases like an `*a`
            which is actually a `Tuple` (which it only is inside a slice).
        - `type[AST]`: Will be returned for nodes which can be reparsed correctly using only the `AST` type.
        - `None`: If invalid or cannot be determined.

        **Examples:**
        ```py
        >>> FST('a | b').get_parse_mode()
        <class 'ast.BinOp'>

        >>> FST('a | b', 'pattern').get_parse_mode()
        <class 'ast.MatchOr'>

        >>> FST('except ValueError: pass\nexcept: pass', 'ExceptHandlers').get_parse_mode()
        'ExceptHandlers'
        ```
        """

        ast = self.a

        if mode := get_special_parse_mode(ast):
            return mode

        # now we check the cases that need source code

        if isinstance(ast, Tuple) and (elts := ast.elts):
            if isinstance(e0 := elts[0], Starred):
                if len(elts) == 1:
                    _, _, ln, col         = e0.f.loc
                    _, _, end_ln, end_col = self.loc

                    if not next_find(self.root._lines, ln, col, end_ln, end_col, ','):  # if lone Starred in Tuple with no comma then is expr_slice (py 3.11+)
                        return 'expr_slice'

        return ast.__class__  # otherwise regular parse by AST type is valid

    def get_indent(self) -> builtins.str:
        r"""Determine proper indentation of node at `stmt` (or other similar) level at or above `self`. Even if it is a
        continuation or on same line as block header. If indentation is impossible to determine because is solo
        statement on same line as parent block then the current tree default indentation is added to the parent block
        indentation and returned.

        **Returns:**
        - `str`: Entire indentation string for the block this node lives in (not just a single level).

        **Examples:**
        ```py
        >>> FST('i = 1').get_indent()
        ''

        >>> FST('if 1:\n  i = 1').body[0].get_indent()
        '  '

        >>> FST('if 1: i = 1').body[0].get_indent()
        '    '

        >>> FST('if 1: i = 1; j = 2').body[1].get_indent()
        '    '

        >>> FST('if 1:\n  i = 1\n  j = 2').body[1].get_indent()
        '  '

        >>> FST('if 2:\n    if 1:\n      i = 1\n      j = 2').body[0].body[1].get_indent()
        '      '

        >>> FST('if 1:\n\\\n  i = 1').body[0].get_indent()
        '  '

        >>> FST('if 1:\n \\\n  i = 1').body[0].get_indent()
        ' '
        ```
        """

        while (parent := self.parent) and not isinstance(self.a, STMTISH):
            self = parent

        root   = self.root
        lines  = root._lines
        indent = ''

        while parent:
            f             = getattr(parent.a, self.pfield.name)[0].f
            ln, col, _, _ = f.loc
            prev          = f.prev(True)  # there may not be one ("try" at start of module)
            prev_end_ln   = prev.end_ln if prev else -2  # -2 so it never hits it
            good_line     = ''

            while ln > prev_end_ln and re_empty_line.match(line_start := lines[ln], 0, col):
                end_col = 0 if (preceding_ln := ln - 1) != prev_end_ln else prev.end_col

                if not ln or not re_line_continuation.match((l := lines[preceding_ln]), end_col):
                    return (line_start[:col] if col else good_line) + indent

                if col:  # we do this to skip backslashes at the start of line as those are just a noop
                    good_line = line_start[:col]

                ln  = preceding_ln
                col = len(l) - 1  # was line continuation so last char is '\' and rest should be empty

            indent += root.indent
            self    = parent
            parent  = self.parent

        return indent

    def is_parsable(self) -> bool:
        r"""Whether the source for this node is parsable by `FST` or not (if properly dedented for top level). This is
        different from `astutil.is_parsable` because that one indicates what is parsable by the python `ast` module,
        while `FST` can parse more things. For example, an unparenthesized `NamedExpr` is considered parsable even
        though it would not parse directly using `ast.parse()`.

        **Returns:**
        - `bool`: Whether is parsable by `FST` from a string or not.

        **Examples:**
        ```py
        >>> from fst import astutil
        >>> FST('i').is_parsable()
        True

        >>> FST('a[b]').slice.is_parsable()
        True

        >>> FST('a[b:c]').slice.is_parsable()
        True

        >>> astutil.is_parsable(FST('a[b:c]').slice.a)
        False

        >>> FST('f"{a!r:<8}"').values[0].is_parsable()
        False

        >>> FST('f"{a!r:<8}"').values[0].value.is_parsable()
        True

        >>> FST('f"{a!r:<8}"').values[0].format_spec.is_parsable()
        False

        >>> FST('try: pass\nexcept: pass').body[0].is_parsable()
        True

        >>> FST('try: pass\nexcept: pass').handlers[0].is_parsable()
        True

        >>> astutil.is_parsable(FST('try: pass\nexcept: pass').handlers[0].a)
        False

        >>> FST('try: pass\nexcept: pass').handlers[0].body[0].is_parsable()
        True

        >>> FST('match a:\n  case 1: pass').cases[0].is_parsable()
        True

        >>> astutil.is_parsable(FST('match a:\n  case 1: pass').cases[0].a)
        False
        ```
        """

        if not self.loc:
            return False

        ast = self.a

        if isinstance(ast, (expr_context, TypeIgnore, FormattedValue, Interpolation)):
            return False

        if parent := self.parent:
            if isinstance(ast, JoinedStr):  # TemplateStr doesn't go into a .format_spec, '.1f' type strings without quote delimiters
                if self.pfield.name == 'format_spec':  # isinstance(parent.a, (FormattedValue, Interpolation)):
                    return False

            elif isinstance(ast, Constant):  # string parts of f-string without quote delimiters (probably, unless parts of implicit strings)
                if self.pfield.name == 'values' and isinstance(parent.a, (JoinedStr, TemplateStr)):  # isinstance(ast.value, str)
                    return False

        return True

    def is_parenthesizable(self) -> bool:
        """Whether `self` is parenthesizable with grouping parentheses or not. Essentially all `expr`s and `pattern`s
        except for `Slice`.

        **Note:** `Starred` returns `True` even though the `Starred` itself is not parenthesizable but rather its child.

        **Returns:**
        - `bool`: Whether is syntactically legal to add grouping parentheses or not. Can always be forced.

        **Examples:**
        ```py
        >>> FST('i + j').is_parenthesizable()  # expr
        True

        >>> FST('{a.b: c, **d}', 'pattern').is_parenthesizable()
        True

        >>> FST('a:b:c').is_parenthesizable()  # Slice
        False

        >>> FST('for i in j').is_parenthesizable()  # comprehension
        False

        >>> FST('a: int, b=2').is_parenthesizable()  # arguments
        False

        >>> FST('a: int', 'arg').is_parenthesizable()
        False

        >>> FST('key="word"', 'keyword').is_parenthesizable()
        False

        >>> FST('a as b', 'alias').is_parenthesizable()
        False

        >>> FST('a as b', 'withitem').is_parenthesizable()
        False
        ```
        """

        return not isinstance(a, Slice) if isinstance(a := self.a, expr) else isinstance(a, pattern)

    def is_atom(self, *, pars: bool = True, always_enclosed: bool = False) -> bool | Literal['unenclosable', 'pars']:
        r"""Whether `self` is innately atomic precedence-wise like `Name`, `Constant`, `List`, etc... Or otherwise
        optionally enclosed in parentheses so that it functions as a parsable atom and cannot be split up by precedence
        rules when reparsed.

        Node types where this doesn't normally apply like `stmt` or `alias` return `True`.

        Being atomic precedence-wise does not guarantee parsability as an otherwise atomic node could be spread across
        multiple lines without line continuations or grouping parentheses. In the case that the node is one of these
        (precedence atomic but MAY be split across lines) then `'unenclosable'` is returned (if these nodes are not
        excluded altogether with `always_enclosed=True`). Also see `is_enclosed_or_line()`.

        If this function returns `'pars'` then `self` is enclosed due to the grouping parentheses.

        **Parameters:**
        - `pars`: Whether to check for grouping parentheses or not for node types which are not innately atomic
            (`NamedExpr`, `BinOp`, `Yield`, etc...). If `True` then `(a + b)` is considered atomic, if `False` then it
            is not.
        - `always_enclosed`: If `True` then will only consider nodes innately atomic which are always enclosed like
            `List` or parenthesized `Tuple`. Nodes which may be split up across multiple lines like `Call` or
            `Attribute` will not be considered atomic and will return `False` unless `pars=True` and grouping
            parentheses present, in which case `'pars'` is returned.

        **Returns:**
        - `True`: Is atomic and no combination of changes in the source will make it parse to a different node.
        - `'unenclosable'`: Is atomic precedence-wise but may be made non-parsable by being spread over multiple lines.
        - `'pars'`: Is atomic due to enclosing grouping parentheses and would not be otherwise, can not be returned for
            `'unenclosable'` nodes if `always_enclosed=False`.
        - `False`: Not atomic.

        **Examples:**
        ```py
        >>> FST('a').is_atom()
        True

        >>> FST('a + b').is_atom()
        False

        >>> FST('(a + b)').is_atom()
        'pars'

        >>> FST('(a + b)').is_atom(pars=False)
        False

        >>> FST('a.b').is_atom()
        'unenclosable'

        >>> FST('a.b').is_atom(always_enclosed=True)  # because of "a\n.b"
        False

        >>> FST('(a.b)').is_atom(always_enclosed=True)
        'pars'

        >>> FST('[]').is_atom(always_enclosed=True)  # because List is always enclosed
        True
        ```
        """

        ast = self.a

        if isinstance(ast, (List, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp, Name,
                            MatchValue, MatchSingleton, MatchMapping,
                            expr_context, boolop, operator, unaryop, ExceptHandler,
                            stmt, match_case, mod, TypeIgnore)):
            return True

        if not always_enclosed:
            if isinstance(ast, Constant):
                return 'unenclosable' if isinstance(ast.value, (str, bytes)) else True

            elif isinstance(ast, (Call, JoinedStr, TemplateStr, Constant, Attribute, Subscript,
                                  MatchClass, MatchStar,
                                  cmpop, comprehension, arguments,
                                  arg, keyword, alias, withitem, type_param)):
                return 'unenclosable'

        elif isinstance(ast, (comprehension, arguments, arg, keyword, alias, type_param)):  # can't be parenthesized
            return False

        elif isinstance(ast, Constant):
            if not isinstance(ast.value, (str, bytes)):  # str and bytes can be multiline implicit needing parentheses
                return True

        elif isinstance(ast, withitem):  # isn't atom on its own and can't be parenthesized directly but if only has context_expr then take on value of that if starts and ends on same lines
            return (not ast.optional_vars and self.loc[::2] == (ce := ast.context_expr.f).pars()[::2] and
                    ce.is_atom(pars=pars, always_enclosed=always_enclosed))

        elif isinstance(ast, cmpop):
            return not isinstance(ast, (IsNot, NotIn))  # could be spread across multiple lines

        if (ret := self.is_parenthesized_tuple()) is not None:  # if this is False then cannot be enclosed in grouping pars because that would reparse to a parenthesized Tuple and so is inconsistent
            return ret

        if (ret := self.is_delimited_matchseq()) is not None:  # like Tuple, cannot be enclosed in grouping pars
            return bool(ret)

        assert isinstance(ast, (expr, pattern))

        return 'pars' if pars and self.pars().n else False

    def is_enclosed_or_line(self, *, pars: bool = True, whole: bool = False, out_lns: set | None = None,
                            ) -> bool | Literal['pars']:
        r"""Whether `self` lives on a single line or logical line (entirely terminated with line continuations) or is
        otherwise enclosed in some kind of delimiters `()`, `[]`, `{}` so that it can be parsed without error due to
        being spread across multiple lines. If logical line then internal enclosed elements spread over multiple lines
        without line continuations are fine. This does not mean it can't have other errors, such as a `Slice` outside of
        `Subscript.slice`.

        Node types where this doesn't or can't ever normally apply like `boolop`, `expr_context` or `Name`, etc...
        return `True`. Node types that are not enclosed but which are never used without being enclosed by a parent like
        `Slice`, `keyword` or `type_param` will also return `True`. Other node types which cannot be enclosed
        individually and are not on a single line or not parenthesized and do not have line continuations but would need
        a parent to enclose them like `arguments` (enclosable in `FunctionDef` but unenclosed in a `Lambda`) or the
        `cmpop`s `is not` or `not in` will return `False`.

        This function does NOT check whether `self` is enclosed by some parent up the tree if it is not enclosed itself,
        for that see `is_enclosed_in_parents()`.

        **Parameters:**
        - `pars`: Whether to check for grouping parentheses or not for nodes which are not enclosed or otherwise
            multiline-safe. Grouping parentheses are different from tuple parentheses which are always checked.
        - `whole`: Whether entire source should be checked and not just the lines corresponding to the node. This is
            only valid for a root node.
        - `out_lns`: If this is not `None` then it is expected to be a `Set` which will get the line numbers added of
            all the lines that would need line continuation backslashes in order to make this function True.

        **Returns:**
        - `True`: Node is enclosed or single logical line.
        - `'pars'` Enclosed by grouping parentheses.
        - `False`: Not enclosed or single logical line and should be parenthesized or put into an enclosed parent or
            have line continuations added for successful parse.

        **Examples:**
        ```py
        >>> FST('a').is_enclosed_or_line()
        True

        >>> FST('a + \\\n b').is_enclosed_or_line()  # because of the line continuation
        True

        >>> FST('(a + \n b)').is_enclosed_or_line()
        'pars'

        >>> FST('a + \n b').is_enclosed_or_line()
        False

        >>> FST('[a + \n b]').elts[0].is_enclosed_or_line()
        False

        >>> FST('[a + \n b]').elts[0].is_enclosed_in_parents()
        True

        >>> FST('def f(a, b): pass').args.is_enclosed_or_line()
        True

        >>> # because the parentheses belong to the FunctionDef
        >>> FST('def f(a,\n b): pass').args.is_enclosed_or_line()
        False

        >>> FST('def f(a,\n b): pass').args.is_enclosed_in_parents()
        True

        >>> FST('(a is not b)').ops[0].is_enclosed_or_line()
        True

        >>> FST('(a is \n not b)').ops[0].is_enclosed_or_line()
        False
        ```
        """

        lines = self.root._lines
        ast   = self.a
        loc   = self.loc

        if whole:
            if not self.is_root:
                raise ValueError("'whole=True' can only be specified on root nodes")

            whole_end_ln = len(lines) - 1

            if loc and not loc.ln and loc.end_ln == whole_end_ln:  # if location spans over whole range of lines then is just normal check
                whole = False

            else:  # if something doesn't have a loc or loc doesn't span over entire range of lines then we need to check the whole source
                end_ln   = whole_end_ln
                last_ln  = 0
                children = [ast]

        if not whole:
            if not loc:  # this catches empty `arguments` mostly
                return True

            if isinstance(ast, (List, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp,
                                FormattedValue, Interpolation, Name,
                                MatchValue, MatchSingleton, MatchMapping,
                                boolop, operator, unaryop,  # cmpop is not here because of #*^% like 'is \n not'
                                Slice, keyword, type_param,  # these can be unenclosed by themselves but are never used without being enclosed by a parent
                                expr_context, TypeIgnore)):
                return True

            if isinstance(ast, (Module, Interactive, FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If,
                                With, AsyncWith, Match, Try, TryStar, ExceptHandler, match_case)):
                raise NotImplementedError("we don't do block statements yet")  # TODO: this

            ln, col, end_ln, end_col = loc

            if end_ln == ln:
                return True

            if pars:
                if self.pars().n:
                    return 'pars'

                pars = False

            if (is_const := isinstance(ast, Constant)) or isinstance(ast, (JoinedStr, TemplateStr)):
                if is_const:
                    if not isinstance(ast.value, (str, bytes)):
                        return True

                    lns = multiline_str_continuation_lns(self.root._lines, ln, col, end_ln, end_col)

                else:
                    lns = multiline_fstr_continuation_lns(self.root._lines, ln, col, end_ln, end_col)

                if (ret := len(lns) == end_ln - ln) or out_lns is None:
                    return ret

                out_lns.update(continuation_to_uncontinued_lns(lns, ln, col, end_ln, end_col))

                return False

            if (ret := self.is_parenthesized_tuple()) is not None:
                if ret:
                    return True

            elif (ret := self.is_delimited_matchseq()) is not None:
                if ret:
                    return True

            last_ln = ln

            if isinstance(ast, Call):
                children = [ast.func,
                            nspace(f=nspace(pars=lambda: self._loc_call_pars(),
                                            is_enclosed_or_line=lambda **kw: True))]
            elif isinstance(ast, Subscript):
                children = [ast.value,
                            nspace(f=nspace(pars=lambda: self._loc_subscript_brackets(),
                                            is_enclosed_or_line=lambda **kw: True))]
            elif isinstance(ast, MatchClass):
                children = [ast.cls,
                            nspace(f=nspace(pars=lambda: self._loc_matchcls_pars(),
                                            is_enclosed_or_line=lambda **kw: True))]
            else:  # we don't check always-enclosed statement fields here because statements will never get here
                children = syntax_ordered_children(ast)

        failed = False

        for child in children:
            if not child or not (loc := (childf := child.f).pars()) or (child_end_ln := loc.end_ln) == last_ln:
                continue

            for ln in range(last_ln, loc.ln):
                if re_line_end_cont_or_comment.match(lines[ln]).group(1) != '\\':
                    if out_lns is None:
                        return False

                    else:
                        failed = True

                        out_lns.add(ln)

            if not getattr(loc, 'n', 0) and not childf.is_enclosed_or_line(pars=pars, out_lns=out_lns):
                if out_lns is None:
                    return False
                else:
                    failed = True

            pars    = False
            last_ln = child_end_ln

        for ln in range(last_ln, end_ln):  # tail
            if re_line_end_cont_or_comment.match(lines[ln]).group(1) != '\\':
                if out_lns is None:
                    return False

                else:
                    failed = True

                    out_lns.add(ln)

        if failed:
            return False

        return True

    def is_enclosed_in_parents(self, field: builtins.str | None = None) -> bool:
        """Whether `self` is enclosed by some parent up the tree. This is different from `is_enclosed_or_line()` as it
        does not check for line continuations or anyting like that, just enclosing delimiters like from `Call` or
        `FunctionDef` arguments parentheses, `List` brackets, `FormattedValue`, parent grouping parentheses, etc...
        Statements do not generally enclose except for a few parts of things like `FunctionDef.args` or `type_params`,
        `ClassDef.bases`, etc...

        **Parameters:**
        - `field`: This is meant to allow check for nonexistent child which would go into this field of `self`. If this
            is not `None` then `self` is considered the first parent with an imaginary child being checked at `field`.

        **WARNING!** This will not pick up parentheses which belong to `self` and the rules for this can be confusing.
        E.g. in `with (x): pass` the parentheses belong to the variable `x` while `with (x as y): pass` they belong to
        the `with` because `alias`es cannot be parenthesized.

        Will pick up parentheses which belong to `self` if `field` is passed because in that case `self` is considered
        the first parent and we are really considering the node which would live at `field`, whether it exists or not.

        **Examples:**
        ```py
        >>> FST('1 + 2').left.is_enclosed_in_parents()
        False

        >>> FST('(1 + 2)').left.is_enclosed_in_parents()
        True

        >>> FST('(1 + 2)').is_enclosed_in_parents()  # because owns the parentheses
        False

        >>> FST('[1 + 2]').elts[0].left.is_enclosed_in_parents()
        True

        >>> FST('[1 + 2]').elts[0].is_enclosed_in_parents()
        True

        >>> FST('f(1)').args[0].is_enclosed_in_parents()
        True

        >>> FST('f"{1}"').values[0].value.is_enclosed_in_parents()
        True

        >>> FST('[]').is_enclosed_in_parents()
        False

        >>> FST('[]').is_enclosed_in_parents(field='elts')
        True

        >>> FST('with (x): pass').items[0].is_enclosed_in_parents()
        False

        >>> FST('with (x as y): pass').items[0].is_enclosed_in_parents()
        True
        ```
        """

        if field:
            if field != 'ctx':  # so that the `ctx` of a List is not considered enclosed
                self = nspace(parent=self, pfield=astfield(field))

        elif isinstance(self.a, expr_context):  # so that the `ctx` of a List is not considered enclosed
            if not (self := self.parent):
                return False

        while parent := self.parent:
            parenta = parent.a

            if isinstance(parenta, (List, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp,
                                    FormattedValue, Interpolation, JoinedStr, TemplateStr,
                                    MatchMapping)):
                return True

            if isinstance(parenta, (FunctionDef, AsyncFunctionDef)):
                return self.pfield.name in ('type_params', 'args')

            if isinstance(parenta, ClassDef):
                return self.pfield.name in ('type_params', 'bases', 'keywords')

            if isinstance(parenta, TypeAlias):
                return self.pfield.name == 'type_params'

            if isinstance(parenta, ImportFrom):
                return parent._is_parenthesized_ImportFrom_names()  # we know we are in `names`

            if isinstance(parenta, (With, AsyncWith)):
                return parent._is_parenthesized_With_items()  # we know we are in `names`

            if isinstance(parenta, (stmt, ExceptHandler, match_case, mod, TypeIgnore)):
                return False

            if isinstance(parenta, Call):
                if self.pfield.name in ('args', 'keywords'):
                    return True

            elif isinstance(parenta, Subscript):
                if self.pfield.name == 'slice':
                    return True

            elif isinstance(parenta, MatchClass):
                if self.pfield.name in ('patterns', 'kwd_attrs', 'kwd_patterns'):
                    return True

            elif (ret := parent.is_parenthesized_tuple()) is not None:
                if ret:
                    return True

            elif (ret := parent.is_delimited_matchseq()) is not None:
                if ret:
                    return True

            if getattr(parent.pars(), 'n', 0):  # could be empty args which has None for a loc
                return True

            self = parent

        return False

    def is_parenthesized_tuple(self) -> bool | None:
        """Whether `self` is a parenthesized `Tuple` or not, or not a `Tuple` at all.

        **Returns:**
        - `True` if is parenthesized `Tuple`, `False` if is unparenthesized `Tuple`, `None` if is not `Tuple` at all.

        **Examples:**
        ```py
        >>> FST('1, 2').is_parenthesized_tuple()
        False

        >>> FST('(1, 2)').is_parenthesized_tuple()
        True

        >>> print(FST('1').is_parenthesized_tuple())
        None
        ```
        """

        return self._is_delimited_seq() if isinstance(self.a, Tuple) else None

    def is_delimited_matchseq(self) -> Literal['', '[]', '()'] | None:
        r"""Whether `self` is a delimited `MatchSequence` or not (parenthesized or bracketed), or not a `MatchSequence`
        at all.

        **Returns:**
        - `None`: If is not `MatchSequence` at all.
        - `''`: If is undelimited `MatchSequence`.
        - `'()'` or `'[]'`: Is delimited with these delimiters.

        **Examples:**
        ```py
        >>> FST('match a:\n  case 1, 2: pass').cases[0].pattern.is_delimited_matchseq()
        ''

        >>> FST('match a:\n  case [1, 2]: pass').cases[0].pattern.is_delimited_matchseq()
        '[]'

        >>> FST('match a:\n  case (1, 2): pass').cases[0].pattern.is_delimited_matchseq()
        '()'

        >>> print(FST('match a:\n  case 1: pass').cases[0].pattern.is_delimited_matchseq())
        None
        ```
        """

        if not isinstance(self.a, MatchSequence):
            return None

        ln, col, _, _ = self.loc
        lpar          = self.root._lines[ln][col : col + 1]  # could be end of line

        if lpar == '(':
            return '()' if self._is_delimited_seq('patterns', '()') else ''
        if lpar == '[':
            return '[]' if self._is_delimited_seq('patterns', '[]') else ''

        return ''

    def is_except_star(self) -> bool | None:
        """Whether `self` is an `except*` `ExceptHandler` or a normal `ExceptHandler`, or not and `ExceptHandler` at
        all.

        **Returns:**
        - `True` if is `except*` `ExceptHandler`, `False` if is normal `ExceptHandler`, `None` if is not `ExceptHandler`
        at all.

        **Examples:**
        ```py
        >>> import sys

        >>> if sys.version_info[:2] >= (3, 11):
        ...     print(FST('try: pass\\nexcept* Exception: pass').handlers[0].is_except_star())
        ... else:
        ...     print(True)
        True

        >>> if sys.version_info[:2] >= (3, 11):
        ...     print(FST('try: pass\\nexcept Exception: pass').handlers[0].is_except_star())
        ... else:
        ...     print(False)
        False

        >>> print(FST('i = 1').is_except_star())
        None
        ```
        """

        if not isinstance(self.a, ExceptHandler):
            return None

        ln, col, end_ln, end_col = self.loc

        return next_frag(self.root._lines, ln, col + 6, end_ln, end_col).src.startswith('*')  # something must be there

    def is_empty_set_call(self) -> bool:
        """Whether `self` is an empty `set()` call.

        **Examples:**
        ```py
        >>> FST('{1}').is_empty_set_call()
        False

        >>> FST('set()').is_empty_set_call()
        True

        >>> FST('frozenset()').is_empty_set_call()
        False

        >>> FST('{*()}').is_empty_set_call()
        False
        ```
        """

        return (isinstance(ast := self.a, Call) and not ast.args and not ast.keywords and
                isinstance(func := ast.func, Name) and func.id == 'set' and isinstance(func.ctx, Load))

    def is_empty_set_star(self) -> bool:
        """Whether `self` is an empty `Set` from an empty `Starred` `Constant` sequence, recognized are `{*()}`, `{*[]}`
        and `{*{}}`.

        **Examples:**
        ```py
        >>> FST('{1}').is_empty_set_star()
        False

        >>> FST('{*()}').is_empty_set_star()
        True

        >>> FST('set()').is_empty_set_star()
        False
        ```
        """

        return (isinstance(ast := self.a, Set) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and
                ((isinstance(v := e0.value, (Tuple, List)) and not v.elts) or (isinstance(v, Dict) and not v.keys)))

    def is_elif(self) -> bool | None:
        r"""Whether `self` is an `elif` or not, or not an `If` at all.

        **Returns:**
        - `True` if is `elif` `If`, `False` if is normal `If`, `None` if is not `If` at all.

        **Examples:**
        ```py
        >>> FST('if 1: pass\nelif 2: pass').orelse[0].is_elif()
        True

        >>> FST('if 1: pass\nelse:\n  if 2: pass').orelse[0].is_elif()
        False

        >>> print(FST('if 1: pass\nelse:\n  i = 2').orelse[0].is_elif())
        None
        ```
        """

        return self.root._lines[(loc := self.loc).ln].startswith('elif', loc.col) if isinstance(self.a, If) else None

    def is_solo_class_base(self) -> bool | None:
        """Whether `self` is a solo `ClassDef` base in list without any keywords, or not a class base at all.

        **Returns:**
        - `True` if is solo class base, `False` if is class base, but not solo and `None` if is not class base at all.

        **Examples:**
        ```py
        >>> FST('class cls(b1): pass').bases[0].is_solo_class_base()
        True

        >>> FST('class cls(b1, b2): pass').bases[0].is_solo_class_base()
        False

        >>> FST('class cls(b1, meta=m): pass').bases[0].is_solo_class_base()
        False

        >>> print(FST('class cls(b1, meta=m): pass').keywords[0].is_solo_class_base())
        None
        ```
        """

        if not (parent := self.parent) or self.pfield.name != 'bases':
            return None

        return len((parenta := parent.a).bases) == 1 and not parenta.keywords

    def is_solo_call_arg(self) -> bool:
        """Whether `self` is a solo `Call` non-keyword argument.

        **Examples:**
        ```py
        >>> FST('call(a)').args[0].is_solo_call_arg()
        True

        >>> FST('call(a, b)').args[0].is_solo_call_arg()
        False

        >>> FST('call(i for i in range(3))').args[0].is_solo_call_arg()
        True
        ```
        """

        return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(parenta := parent.a, Call) and
                not parenta.keywords and len(parenta.args) == 1)

    def is_solo_call_arg_genexp(self) -> bool:
        """Whether `self` is the dreaded solo call non-keyword argument generator expression in `sum(i for i in a)`.
        This function doesn't say if it shares its parentheses or not, so it could still be `sum((i for i in a))` or
        even `sum(((i for i in a)))`. To differentiate that see `pars(shared=False)`.

        **Examples:**
        ```py
        >>> FST('call(i for i in range(3))').args[0].is_solo_call_arg_genexp()
        True

        >>> FST('call((i for i in range(3)))').args[0].is_solo_call_arg_genexp()
        True

        >>> FST('call((i for i in range(3)), b)').args[0].is_solo_call_arg_genexp()
        False

        >>> FST('call(a)').args[0].is_solo_call_arg_genexp()
        False
        ```
        """

        return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(self.a, GeneratorExp) and
                isinstance(parenta := parent.a, Call) and not parenta.keywords and len(parenta.args) == 1)

    def is_solo_matchcls_pat(self) -> bool:
        r"""Whether `self` is a solo `MatchClass` non-keyword pattern. The solo `Constant` held by a `MatchValue`
        qualifies as `True` for this check if the `MatchValue` does.

        **Examples:**
        ```py
        >>> (FST('match a:\n  case cls(a): pass')
        ...  .cases[0].pattern.patterns[0].is_solo_matchcls_pat())
        True

        >>> (FST('match a:\n  case cls(a, b): pass')
        ...  .cases[0].pattern.patterns[0].is_solo_matchcls_pat())
        False
        ```
        """

        if not (parent := self.parent):
            return False

        if isinstance(parenta := parent.a, MatchValue):
            self = parent

        return ((parent := self.parent) and self.pfield.name == 'patterns' and
                isinstance(parenta := parent.a, MatchClass) and not parenta.kwd_patterns and len(parenta.patterns) == 1)

    def is_augop(self) -> bool | None:
        """Whether `self` is an augmented `operator` or not, or not an `operator` at all.

        **Returns:**
        - `True` if is augmented `operator`, `False` if non-augmented `operator` and `None` if is not `operator` at all.

        **Examples:**
        ```py
        >>> FST('+').is_augop()
        False

        >>> FST('+=').is_augop()
        True

        >>> repr(FST('~').is_augop())
        'None'
        ```
        """

        return None if not isinstance(self.a, operator) else self.get_src(*self.loc) in OPSTR2CLS_AUG

    def has_Slice(self) -> bool:
        """Whether self is a `Slice` or a `Tuple` which directly contains any `Slice`.

        **Examples:**
        ```py
        >>> FST('a:b:c', 'expr_slice').has_Slice()
        True

        >>> FST('1, d:e', 'expr_slice').has_Slice()  # Tuple contains at least one Slice
        True

        >>> # b is in the .slice field but is not a Slice or Slice Tuple
        >>> FST('a[b]').slice.has_Slice()
        False
        ```
        """

        return isinstance(a := self.a, Slice) or (isinstance(a, Tuple) and
                                                  any(isinstance(e, Slice) for e in a.elts))

    def has_Starred(self) -> bool:
        """Whether self is a `Starred` or a `Tuple`, `List` or `Set` which directly contains any `Starred`.

        **Examples:**
        ```py
        >>> FST('*a').has_Starred()
        True

        >>> FST('1, *a').has_Starred()  # Tuple contains at least one Starred
        True
        ```
        """

        return isinstance(a := self.a, Starred) or (isinstance(a, (Tuple, List, Set)) and
                                                    any(isinstance(e, Starred) for e in a.elts))

    # ------------------------------------------------------------------------------------------------------------------
    # Private and other misc stuff

    from .fst_misc import (
        _new_empty_module,
        _new_empty_tuple,
        _new_empty_list,
        _new_empty_dict,
        _new_empty_set_star,
        _new_empty_set_call,
        _new_empty_set_curlies,
        _new_empty_matchseq,
        _new_empty_matchmap,
        _new_empty_matchor,
        _make_fst_tree,
        _unmake_fst_tree,
        _unmake_fst_parents,
        _set_ast,
        _set_ctx,
        _repr_tail,
        _dump,
        _next_bound,
        _prev_bound,
        _next_bound_step,
        _prev_bound_step,
        _loc_block_header_end,
        _loc_operator,
        _loc_comprehension,
        _loc_arguments,
        _loc_arguments_empty,
        _loc_lambda_args_entire,
        _loc_withitem,
        _loc_match_case,
        _loc_ImportFrom_names_pars,
        _loc_call_pars,
        _loc_subscript_brackets,
        _loc_matchcls_pars,
        _loc_funcdef_type_params_brackets,
        _loc_classdef_type_params_brackets,
        _loc_typealias_type_params_brackets,
        _loc_global_nonlocal_names,
        _loc_maybe_dict_key,
        _is_arguments_empty,
        _is_parenthesized_ImportFrom_names,
        _is_parenthesized_With_items,
        _is_delimited_seq,
        _set_end_pos,
        _set_block_end_from_last_child,
        _update_loc_up_parents,
        _maybe_add_line_continuations,
        _maybe_del_separator,
        _maybe_ins_separator,
        _maybe_add_singleton_tuple_comma,
        _maybe_fix_joined_alnum,
        _maybe_fix_undelimited_seq,
        _maybe_fix_tuple,
        _maybe_fix_matchseq,
        _maybe_fix_matchor,
        _maybe_fix_set,
        _maybe_fix_elif,
        _maybe_fix_with_items,
        _maybe_fix_copy,
        _touch,
        _sanitize,
        _parenthesize_grouping,
        _unparenthesize_grouping,
        _delimit_node,
        _undelimit_node,
        _normalize_block,
        _elif_to_else_if,
        _reparse_docstrings,
        _make_fst_and_dedent,
        _get_fmtval_interp_strs,
        _get_indentable_lns,
        _modifying,
        _touchall,
        _put_src,
        _offset,
        _offset_lns,
        _indent_lns,
        _dedent_lns,
        _redent_lns,
        _get_trivia_params,
    )

    from .fst_raw import (
        _reparse_raw,
    )

    from .fst_slice_old import (
        _get_slice_stmtish,
        _put_slice_stmtish,
    )

    from .fst_slice import (
        _is_slice_compatible,
        _get_slice,
        _put_slice,
    )

    from .fst_one import (
        _get_one,
        _put_one,
    )


# ----------------------------------------------------------------------------------------------------------------------
# Make AST field accessors

def _make_AST_field_accessor(field: str, cardinality: Literal[1, 2, 3]) -> property:
    if cardinality == 1:
        @property
        def accessor(self: FST) -> FST | None | constant:
            """@private"""

            return getattr(child, 'f', None) if isinstance(child := getattr(self.a, field), AST) else child

        @accessor.setter
        def accessor(self: FST, code: Code | builtins.str | constant | None) -> None:
            """@private"""

            self.put(code, field)

        @accessor.deleter
        def accessor(self: FST) -> None:
            """@private"""

            self.put(None, field)

    elif cardinality == 2:
        @property
        def accessor(self: FST) -> fstview:
            """@private"""

            return fstview(self, field, 0, len(getattr(self.a, field)))

        @accessor.setter
        def accessor(self: FST, code: Code | builtins.str | None) -> None:
            """@private"""

            self.put_slice(code, field)

        @accessor.deleter
        def accessor(self: FST) -> None:
            """@private"""

            self.put_slice(None, field)

    else:  # cardinality == 3  # can be single element or list depending on the AST type
        @property
        def accessor(self: FST) -> fstview | FST | None | constant:
            """@private"""

            if isinstance(child := getattr(self.a, field), list):
                return fstview(self, field, 0, len(child))
            elif isinstance(child, AST):
                return getattr(child, 'f', None)

            return child

        @accessor.setter
        def accessor(self: FST, code: Code | builtins.str | None) -> None:
            """@private"""

            if isinstance(getattr(self.a, field), list):
                self.put_slice(code, field)
            else:
                self.put(code, field)

        @accessor.deleter
        def accessor(self: FST) -> None:
            """@private"""

            if isinstance(getattr(self.a, field), list):
                self.put_slice(None, field)
            else:
                self.put(None, field)

    return accessor


def _make_AST_field_accessors() -> None:
    FST_dict    = FST.__dict__
    cardinality = {}  # {'field': 1 means single element | 2 means list (3 means can be either)}

    for fields in FIELDS.values():
        for f, t in fields:
            if f == 'lineno':
                continue

            if f in FST_dict:
                raise RuntimeError(f'AST field name {f!r} already taken in FST class')

            cardinality[f] = cardinality.get(f, 0) | (2 if t.endswith('*') else 1)

    for f, c in cardinality.items():
        setattr(FST, f, _make_AST_field_accessor(f, c))


_make_AST_field_accessors()
