import ast as ast_
import inspect
import re
from ast import *
from ast import parse as ast_parse, unparse as ast_unparse
from io import TextIOBase
from itertools import takewhile
from typing import Any, Callable, Generator, Literal, NamedTuple, Optional, TextIO, TypeAlias, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, type_param, TypeVar, ParamSpec, TypeVarTuple, TemplateStr, Interpolation

from .shared import (
    astfield, fstloc, srcwpos,
    AST_FIELDS_NEXT, AST_FIELDS_PREV, AST_DEFAULT_BODY_FIELD, EXPRESSIONISH,
    STATEMENTISH, STATEMENTISH_OR_MOD, STATEMENTISH_OR_STMTMOD, BLOCK, BLOCK_OR_MOD, SCOPE, SCOPE_OR_MOD, NAMED_SCOPE,
    NAMED_SCOPE_OR_MOD, ANONYMOUS_SCOPE, PARENTHESIZABLE, HAS_DOCSTRING,
    STATEMENTISH_FIELDS,
    PATH_BODY, PATH_BODY2, PATH_BODYORELSE, PATH_BODY2ORELSE, PATH_BODYHANDLERS, PATH_BODY2HANDLERS, PATH_BODYCASES,
    DEFAULT_PARSE_PARAMS, DEFAULT_INDENT,
    DEFAULT_DOCSTR, DEFAULT_PRECOMMS, DEFAULT_POSTCOMMS, DEFAULT_PRESPACE, DEFAULT_POSTSPACE, DEFAULT_PEP8SPACE,
    DEFAULT_PARS, DEFAULT_ELIF_, DEFAULT_FIX, DEFAULT_RAW,
    re_empty_line_start, re_empty_line, re_comment_line_start, re_line_continuation, re_line_trailing_space,
    re_oneline_str, re_contline_str_start, re_contline_str_end_sq, re_contline_str_end_dq, re_multiline_str_start,
    re_multiline_str_end_sq, re_multiline_str_end_dq, re_empty_line_cont_or_comment, re_next_src,
    re_next_src_or_comment, re_next_src_or_lcont, re_next_src_or_comment_or_lcont,
    Code, NodeTypeError,
    _with_loc, _next_src, _prev_src, _next_find, _prev_find, _next_pars, _prev_pars, _params_offset, _fixup_field_body,
    _fixup_slice_index, _reduce_ast
)


class _FSTCircularImportStandinMeta(type):
    """Class attribute getter for temporary circular import standin for FST."""

    def __getattr__(cls, name):
        inspect.currentframe().f_back.f_globals['FST'] = FST = globals()['FST']

        return getattr(FST, name)

class _FSTCircularImportStandin(metaclass=_FSTCircularImportStandinMeta):
    """Temporary standin for circular import of `FST`. Proxies `FST()` and `FST.static/classmethod()` and sets `FST` in
    caller globals to the actual `FST` class for subsequent calls. The import will also resolve to the actual `FST`
    class for static type analysis in IDEs."""

    def __new__(cls, *args, **kwargs):
        inspect.currentframe().f_back.f_globals['FST'] = FST = globals()['FST']

        return FST(*args, **kwargs)

FST = _FSTCircularImportStandin


from . import fst_misc

__all__ = [
    'parse', 'unparse', 'FST',
    'fstlist', 'fstloc', 'astfield',
    'NodeTypeError',
]


REPR_SRC_LINES = 0  # for debugging


def parse(source, filename='<unknown>', mode='exec', *, type_comments=False, feature_version=None, **kwargs) -> AST:
    """Executes `ast.parse()` and then adds `FST` nodes to the parsed tree. Drop-in replacement for `ast.parse()`. For
    parameters, see `ast.parse()`. Returned `AST` tree has added `.f` attribute at each node which accesses the parallel
    `FST` tree."""

    return FST.fromsrc(source, filename, mode, type_comments=type_comments, feature_version=feature_version, **kwargs).a


def unparse(ast_obj) -> str:
    """Returns the formatted source that is kept for this tree. Drop-in replacement for `ast.unparse()`."""

    if (f := getattr(ast_obj, 'f', None)) and isinstance(f, FST) and f.loc:
        if f.is_root:
            return f.src

        try:
            return f.copy().src
        except Exception:
            pass

    return ast_unparse(ast_obj)


class FST:
    """Preserve AST formatting information and easy manipulation.

    **Source editing `options`**: These are mostly for editing statements, though some can apply to other sequences.
    - `docstr`: Which docstrings are indentable / dedentable.
        - `False`: None.
        - `True`: All `Expr` multiline strings (as they serve no coding purpose).
        - `'strict'`: Only multiline strings in expected docstring positions (functions and classes).
        - `None`: Use default (`True`).
    - `precomms`: Preceding comments.
        - `False`: No preceding comments.
        - `True`: Single contiguous comment block immediately preceding position.
        - `'all'`: Comment blocks (possibly separated by empty lines) preceding position.
        - `None`: Use default (`True`).
    - `postcomms`: Trailing comments.
        - `False`: No trailing comments.
        - `True`: Only comment trailing on line of position, nothing past that on its own lines.
        - `'block'`: Single contiguous comment block following position.
        - `'all'`: Comment blocks (possibly separated by empty lines) following position.
        - `None`: Use default (`True`).
    - `prespace`: Preceding empty lines (max of this and `pep8space` used).
        - `False`: No empty lines.
        - `True`: All empty lines.
        - `int`: A maximum number of empty lines.
        - `None`: Use default (`False`).
    - `postspace`: Same as `prespace` except for trailing empty lines.
    - `pep8space`: Preceding and trailing empty lines for function and class definitions.
        - `False`: No empty lines.
        - `True`: Two empty lines at module scope and one empty line in other scopes.
        - `1`: One empty line in all scopes.
        - `None`: Use default (`True`).
    - `pars`: How parentheses are handled.
        - `False`: Parentheses are not modified generally. Not copied with nodes or removed on cut or automatically
            modified on put, except added if needed for precedence. They are removed on slice cut due to starting and
            ending on different elements.
        - `True`: Parentheses are handled automatically and cut from and copied with nodes. They are added or removed
            as needed for precedence when putting nodes (for raw put that means must be `AST` or `FST` nodes passed to
            raw put to node, not location).
        - `'auto'`: Same as `True` except they are not returned with a cut or copied node, though they are still removed
             on cut.
        - `None`: Use default (`'auto'`).
    - `elif_`: `True` or `False`, if putting a single `If` statement to an `orelse` field of a parent `If` statement then
        put it as an `elif`. `None` means use default of `False`.
    - `fix`: Attempt to carry out basic fixes on operands like parenthesizing multiline expressions so they are
        parsable, adding commas to singleton tuples, changing `elif` to `if` for cut or copied `elif` statements, etc...
    - `raw`: How to attempt at raw source operations. This may result in more nodes changed than just the targeted
        one(s).
        - `False`: Do not do raw source operations.
        - `True`: Only do raw source operations.
        - `'auto'`: Only do raw source operations if the normal operation fails in a way that raw might not.
        - `None`: Use default (`'auto'`).
    """

    a:            AST              ; """The actual `AST` node."""
    parent:       Optional['FST']  ; """Parent `FST` node, `None` in root node."""
    pfield:       astfield | None  ; """The `astfield` location of this node in the parent, `None` in root node."""
    root:         'FST'            ; """The root node of this tree, `self` in root node."""
    _loc:         fstloc | None    # cache, MAY NOT EXIST!
    _bloc:        fstloc | None    # cache, MAY NOT EXIST! bounding location, including preceding decorators

    # ROOT ONLY
    parse_params: dict[str, Any]   ; """The parameters to use for any `ast.parse()` that needs to be done (filename, type_comments, feature_version), root node only."""
    indent:       str              ; """The default single level of block indentation string for this tree when not available from context, root node only."""
    _lines:       list[bistr]

    # class attributes
    is_FST:       bool = True      ; """@private"""  # for quick checks vs. `fstloc`

    OPTIONS = {
        'docstr':    DEFAULT_DOCSTR,     # True | False | 'strict'
        'precomms':  DEFAULT_PRECOMMS,   # True | False | 'all'
        'postcomms': DEFAULT_POSTCOMMS,  # True | False | 'all' | 'block'
        'prespace':  DEFAULT_PRESPACE,   # True | False | int
        'postspace': DEFAULT_POSTSPACE,  # True | False | int
        'pep8space': DEFAULT_PEP8SPACE,  # True | False | 1
        'pars':      DEFAULT_PARS,       # True | False | 'auto'
        'elif_':     DEFAULT_ELIF_,      # True | False
        'fix':       DEFAULT_FIX,        # True | False
        'raw':       DEFAULT_RAW,        # True | False | 'auto'
    }  ; """@private"""

    @property
    def lines(self) -> list[str] | None:
        """Whole lines which contain this node, may also contain parts of enclosing nodes. If gotten at root then the
        entire source is returned, regardless of whether the actual top level node location includes it or not."""

        if self.is_root:
            return self._lines
        elif loc := self.bloc:
            return self.root._lines[loc.ln : loc.end_ln + 1]
        else:
            return None

    @property
    def src(self) -> str | None:
        """Source code of this node clipped out of as a single string, without any dedentation will have indentation as
        it appears in the top level source if multiple lines. If gotten at root then the entire source is returned,
        regardless of whether the actual top level node location includes it or not."""

        if self.is_root:
            return '\n'.join(self._lines)
        elif loc := self.bloc:
            return self.get_src(*loc)
        else:
            return None

    @property
    def is_root(self) -> bool:
        """`True` for the root node, `False` otherwise."""

        return self.parent is None

    @property
    def is_mod(self) -> bool:
        """Is a `mod` node."""

        return isinstance(self.a, mod)

    @property
    def is_stmtish(self) -> bool:
        """Is a `stmt`, `ExceptHandler` or `match_case` node."""

        return isinstance(self.a, STATEMENTISH)

    @property
    def is_stmtish_or_mod(self) -> bool:
        """Is a `stmt`, `ExceptHandler`, `match_case` or `mod` node."""

        return isinstance(self.a, STATEMENTISH_OR_MOD)

    @property
    def is_stmt(self) -> bool:
        """Is a `stmt`."""

        return isinstance(self.a, stmt)

    @property
    def is_stmt_or_mod(self) -> bool:
        """Is a `stmt` or `mod` node."""

        return isinstance(self.a, (stmt, mod))

    @property
    def is_block(self) -> bool:
        """Is a node which opens a block. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `For`,
        `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`, `TryStar`, `ExceptHandler` or `match_case`."""

        return isinstance(self.a, BLOCK)

    @property
    def is_block_or_mod(self) -> bool:
        """Is a node which opens a block. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `For`,
        `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`, `TryStar`, `ExceptHandler`, `match_case` or
        `mod`."""

        return isinstance(self.a, BLOCK_OR_MOD)

    @property
    def is_scope(self) -> bool:
        """Is a node which opens a scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Lambda`,
        `ListComp`, `SetComp`, `DictComp` or `GeneratorExp`."""

        return isinstance(self.a, SCOPE)

    @property
    def is_scope_or_mod(self) -> bool:
        """Is a node which opens a scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Lambda`,
        `ListComp`, `SetComp`, `DictComp`, `GeneratorExp` or `mod`."""

        return isinstance(self.a, SCOPE_OR_MOD)

    @property
    def is_named_scope(self) -> bool:
        """Is a node which opens a named scope. Types include `FunctionDef`, `AsyncFunctionDef` or `ClassDef`."""

        return isinstance(self.a, NAMED_SCOPE)

    @property
    def is_named_scope_or_mod(self) -> bool:
        """Is a node which opens a named scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef` or `mod`."""

        return isinstance(self.a, NAMED_SCOPE_OR_MOD)

    @property
    def is_anon_scope(self) -> bool:
        """Is a node which opens an anonymous scope. Types include `Lambda`, `ListComp`, `SetComp`, `DictComp` or
        `GeneratorExp`."""

        return isinstance(self.a, ANONYMOUS_SCOPE)

    @property
    def has_own_loc(self) -> bool:
        """`True` when the node has its own location which comes directly from AST `lineno` and other location fields.
        Otherwise `False` if no `loc` or `loc` is calculated."""

        return hasattr(self.a, 'end_col_offset')

    @property
    def loc(self) -> fstloc | None:
        """Zero based character indexed location of node (may not be entire location if node has decorators). Not all
        nodes have locations, specifically leaf nodes like operations and `expr_context`. Other nodes which normally
        don't have locations like `arguments` have this location calculated from their children or source."""

        try:
            return self._loc
        except AttributeError:
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
            elif not self.parent:
                loc = fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))
            elif isinstance(ast, (operator, unaryop, cmpop)):
                loc = self._loc_operator()
            else:
                loc = None

        else:
            col     = self.root._lines[ln].b2c(col_offset)
            end_col = self.root._lines[end_ln].b2c(end_col_offset)
            loc     = fstloc(ln, col, end_ln, end_col)

        self._loc = loc

        return loc

    @property
    def bloc(self) -> fstloc | None:
        """Entire location of node, including any preceding decorators. Not all nodes have locations but any node which
        has a `.loc` will have a `.bloc`."""

        try:
            return self._bloc
        except AttributeError:
            pass

        if (bloc := self.loc) and (decos := getattr(self.a, 'decorator_list', None)):
            bloc = fstloc(decos[0].f.ln, bloc[1], bloc[2], bloc[3])  # column of deco '@' will be same as our column

        self._bloc = bloc

        return bloc

    @property
    def wbloc(self) -> fstloc | None:
        """Return whole source location if at root, regardless of actual root node location, otherwise node `bloc`."""

        return fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1])) if self.is_root else self.bloc

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
        """Line number of the first line of this node or the first preceding decorator (0 based)."""

        return (l := self.bloc) and l[0]

    bcol     = col  # for symmetry, also may eventually be distinct
    bend_ln  = end_ln
    bend_col = end_col

    @property
    def lineno(self) -> int:  # 1 based
        """Line number of the first line of this node (1 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and loc[0] + 1

    @property
    def col_offset(self) -> int:  # byte index
        """BYTE index of the start of this node (0 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and self.root._lines[loc[0]].c2b(loc[1])

    @property
    def end_lineno(self) -> int:  # 1 based
        """Line number of the LAST LINE of this node (1 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and loc[2] + 1

    @property
    def end_col_offset(self) -> int:  # byte index
        """CHARACTER index one past the end of this node (0 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and self.root._lines[loc[2]].c2b(loc[3])

    @property
    def f(self):
        """@private"""

        raise RuntimeError("you probably think you're accessing an AST node, but you're not, "
                           "you're accessing an FST node")

    # ------------------------------------------------------------------------------------------------------------------

    _normalize_code                  = fst_misc._normalize_code
    _new_empty_module                = fst_misc._new_empty_module
    _new_empty_tuple                 = fst_misc._new_empty_tuple
    _new_empty_list                  = fst_misc._new_empty_list
    _new_empty_dict                  = fst_misc._new_empty_dict
    _new_empty_set                   = fst_misc._new_empty_set
    _new_empty_set_curlies           = fst_misc._new_empty_set_curlies
    _make_tree_fst                   = fst_misc._make_tree_fst
    _make_fst_tree                   = fst_misc._make_fst_tree
    _unmake_fst_tree                 = fst_misc._unmake_fst_tree
    _set_ast                         = fst_misc._set_ast
    _repr_tail                       = fst_misc._repr_tail
    _dump                            = fst_misc._dump
    _prev_ast_bound                  = fst_misc._prev_ast_bound
    _next_ast_bound                  = fst_misc._next_ast_bound
    _lpars                           = fst_misc._lpars
    _rpars                           = fst_misc._rpars
    _loc_block_opener_end            = fst_misc._loc_block_opener_end
    _loc_operator                    = fst_misc._loc_operator
    _loc_comprehension               = fst_misc._loc_comprehension
    _loc_arguments                   = fst_misc._loc_arguments
    _loc_withitem                    = fst_misc._loc_withitem
    _loc_match_case                  = fst_misc._loc_match_case
    _dict_key_or_mock_loc            = fst_misc._dict_key_or_mock_loc
    _touch                           = fst_misc._touch
    _set_end_pos                     = fst_misc._set_end_pos
    _maybe_add_comma                 = fst_misc._maybe_add_comma
    _maybe_add_singleton_tuple_comma = fst_misc._maybe_add_singleton_tuple_comma
    _maybe_fix_tuple                 = fst_misc._maybe_fix_tuple
    _maybe_fix_set                   = fst_misc._maybe_fix_set
    _maybe_fix_elif                  = fst_misc._maybe_fix_elif
    _fix_block_del_last_child        = fst_misc._fix_block_del_last_child
    _fix                             = fst_misc._fix
    _is_parenthesized_seq            = fst_misc._is_parenthesized_seq
    _parenthesize_grouping           = fst_misc._parenthesize_grouping
    _parenthesize_tuple              = fst_misc._parenthesize_tuple
    _unparenthesize_grouping         = fst_misc._unparenthesize_grouping
    _unparenthesize_tuple            = fst_misc._unparenthesize_tuple
    _normalize_block                 = fst_misc._normalize_block
    _elif_to_else_if                 = fst_misc._elif_to_else_if
    _reparse_docstrings              = fst_misc._reparse_docstrings

    # ------------------------------------------------------------------------------------------------------------------

    def _raw_slice_loc(self, start: int | Literal['end'] | None = None, stop: int | None = None,
                       field: str | None = None) -> fstloc:
        """Get location of a raw slice. Sepcial cases for decorators, comprehension ifs and other weird nodes."""

        def fixup_slice_index_for_raw(len_, start, stop):
            start, stop = _fixup_slice_index(len_, start, stop)

            if stop == start:
                raise ValueError(f"invalid slice for raw operation")

            return start, stop

        ast = self.a

        if isinstance(ast, Dict):
            if field is not None:
                raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

            keys        = ast.keys
            values      = ast.values
            start, stop = fixup_slice_index_for_raw(len(keys), start, stop)
            start_loc   = self._dict_key_or_mock_loc(keys[start], values[start].f)

            if start_loc.is_FST:
                start_loc = start_loc.pars()

            return fstloc(start_loc.ln, start_loc.col, *values[stop - 1].f.pars()[2:])

        if isinstance(ast, Compare):
            if field is not None:
                raise ValueError(f"cannot specify a field '{field}' to assign slice to a Compare")

            comparators  = ast.comparators  # virtual combined body of [Compare.left] + Compare.comparators
            start, stop  = fixup_slice_index_for_raw(len(comparators) + 1, start, stop)
            stop        -= 1

            return fstloc(*(comparators[start - 1] if start else ast.left).f.pars()[:2],
                          *(comparators[stop - 1] if stop else ast.left).f.pars()[2:])

        if isinstance(ast, MatchMapping):
            if field is not None:
                raise ValueError(f"cannot specify a field '{field}' to assign slice to a MatchMapping")

            keys        = ast.keys
            start, stop = fixup_slice_index_for_raw(len(keys), start, stop)

            return fstloc(*keys[start].f.loc[:2], *ast.patterns[stop - 1].f.pars()[2:])

        if isinstance(ast, comprehension):
            ifs         = ast.ifs
            start, stop = fixup_slice_index_for_raw(len(ifs), start, stop)
            ffirst      = ifs[start].f
            start_pos   = _prev_find(self.root._lines, *ffirst._prev_ast_bound(), ffirst.ln, ffirst.col, 'if')

            return fstloc(*start_pos, *ifs[stop - 1].f.pars()[2:])

        if field == 'decorator_list':
            decos       = ast.decorator_list
            start, stop = fixup_slice_index_for_raw(len(decos), start, stop)
            ffirst      = decos[start].f
            start_pos   = _prev_find(self.root._lines, 0, 0, ffirst.ln, ffirst.col, '@')  # we can use '0, 0' because we know "@" starts on a newline

            return fstloc(*start_pos, *decos[stop - 1].f.pars()[2:])

        _, body     = _fixup_field_body(ast, field)
        start, stop = fixup_slice_index_for_raw(len(body), start, stop)

        return fstloc(*body[start].f.pars(exc_genexpr_solo=True)[:2],
                      *body[stop - 1].f.pars(exc_genexpr_solo=True)[2:])

    def _reparse_raw(self, new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
                          copy_lines: list[str], path: list[astfield] | str, set_ast: bool = True) -> 'FST':
        """Actually do the reparse."""

        copy_root = FST(Pass(), lines=copy_lines)  # we don't need the ASTs here, just the lines

        copy_root.put_src(new_lines, ln, col, end_ln, end_col)

        root      = self.root
        copy_root = FST.fromsrc(copy_root.src, mode=get_parse_mode(root.a) or 'exec', **root.parse_params)

        if path == 'root':
            self._lines = copy_root._lines
            copy        = copy_root

        else:
            copy = copy_root.child_from_path(path)

            if not copy:
                raise RuntimeError(f'could not find node after raw reparse')

            root.put_src(new_lines, ln, col, end_ln, end_col, True, self if set_ast else None)  # we do this again in our own tree to offset our nodes which aren't being moved over from the modified copy, can exclude self if setting ast because it overrides self locations

            copy.pfield.set(copy.parent.a, None)  # remove from copy tree so that copy_root unmake doesn't zero out new node
            copy_root._unmake_fst_tree()

        if set_ast:
            self._set_ast(copy.a)
            self.touch(True)

        return copy

    def _reparse_raw_stmtish(self, new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> bool:
        """Reparse only statementish or block opener part of statementish containing changes."""

        if not (stmtish := self.parent_stmtish(True, False)):
            return False

        pln, pcol, pend_ln, pend_col = stmtish.bloc

        root     = self.root
        lines    = root._lines
        stmtisha = stmtish.a

        if in_blkopen := (blkopen_end := stmtish._loc_block_opener_end()) and (end_ln, end_col) <= blkopen_end:  # block statement with modification limited to block opener
            pend_ln, pend_col = blkopen_end

        if isinstance(stmtisha, match_case):
            copy_lines = ([bistr('')] * (pln - 1) +
                          [bistr('match a:'), bistr(' ' * pcol + lines[pln][pcol:])] +
                          lines[pln + 1 : pend_ln + 1])
            path       = PATH_BODYCASES

        else:
            indent = stmtish.get_indent()

            if not indent:
                copy_lines = [bistr('')] * pln + lines[pln : pend_ln + 1]

            elif pln:
                copy_lines = ([bistr('if 1:')] +
                              [bistr('')] * (pln - 1) +
                              [bistr(' ' * pcol + lines[pln][pcol:])] +
                              lines[pln + 1 : pend_ln + 1])
            else:
                copy_lines = ([bistr(f"try:{' ' * (pcol - 4)}{lines[pln][pcol:]}")] +
                              lines[pln + 1 : pend_ln + 1] +
                              [bistr('finally: pass')])

            if isinstance(stmtisha, ExceptHandler):
                assert pln > bool(indent)

                copy_lines[pln - 1] = bistr(indent + 'try: pass')
                path                = PATH_BODY2HANDLERS if indent else PATH_BODYHANDLERS

            elif not indent:
                if stmtish.is_elif():
                    copy_lines[0] = bistr('if 2: pass')
                    path          = PATH_BODYORELSE
                else:
                    path = PATH_BODY

            else:
                if stmtish.is_elif():
                    copy_lines[1] = bistr(indent + 'if 2: pass')
                    path          = PATH_BODY2ORELSE
                else:
                    path = PATH_BODY2

        if not in_blkopen:  # non-block statement or modifications not limited to block opener part
            copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

            stmtish._reparse_raw(new_lines, ln, col, end_ln, end_col, copy_lines, path)

            return True

        # modifications only to block opener line(s) of block statement

        if isinstance(stmtisha, Match):
            copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

            copy_lines.append(bistr(indent + ' case 1: pass'))

        else:
            copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col] + ' pass')

            if isinstance(stmtisha, (Try, TryStar)):  # this one is just silly, nothing to put there, but we cover it
                copy_lines.append(bistr(indent + 'finally: pass'))

        copy  = stmtish._reparse_raw(new_lines, ln, col, end_ln, end_col, copy_lines, path, False)
        copya = copy.a

        if not isinstance(stmtisha, match_case):  # match_case doesn't have AST location
            copya.end_lineno     = stmtisha.end_lineno
            copya.end_col_offset = stmtisha.end_col_offset

        for field in STATEMENTISH_FIELDS:
            if (body := getattr(stmtisha, field, None)) is not None:
                setattr(copya, field, body)

        stmtish._set_ast(copya)
        stmtish.touch(True)

        return True

    def _reparse_raw_loc(self, code: Code | None, ln: int, col: int, end_ln: int, end_col: int,
                         exact: bool | None = None) -> Optional['FST']:
        """Reparse this node which entirely contatins the span which is to be replaced with `code` source. `self` must
        be a node which entirely contains the location and is guaranteed not to be deleted. `self` and some of its
        parents going up may be replaced (root node `FST` will never change, the `AST` it points to may though). Not
        safe to use in a `walk()`.

        **Returns:**
        - `FST | None`: FIRST highest level node contained entirely within replacement source or `None` if no candidate.
            This could wind up being just an operator like '+' depending on the replacement. If `exact` is passed and
            not `None` then will attempt a `find_loc(..., exact)` if could not find candidate node with `find_in_loc()`.
        """

        if isinstance(code, str):
            new_lines = code.split('\n')
        elif isinstance(code, list):
            new_lines = code
        elif isinstance(code, AST):
            new_lines = ast_unparse(code).split('\n')
        elif code is None:
            new_lines = [bistr('')]
        elif not code.is_root:  # isinstance(code, FST)
            raise ValueError('expecting root FST')
        else:
            new_lines = code._lines

        if not self._reparse_raw_stmtish(new_lines, ln, col, end_ln, end_col):  # attempt to reparse only statement (or even only block opener)
            assert self.root.is_mod  # TODO: allow with non-mod root

            root = self.root

            self._reparse_raw(new_lines, ln, col, end_ln, end_col, root._lines[:],  # fallback to reparse all source
                              'root' if self is root else root.child_path(self))

        if code is None:
            return None

        if len(new_lines) == 1:
            end_ln  = ln
            end_col = col + len(new_lines[0])

        else:
            end_ln  = ln + len(new_lines) - 1
            end_col = len(new_lines[-1])

        return (self.root.find_in_loc(ln, col, end_ln, end_col) or  # `self.root` instead of `self` because some changes may propagate farther up the tree, like 'elif' -> 'else'
                (self.root.find_loc(ln, col, end_ln, end_col, exact) if exact is not None else None))

    def _reparse_raw_node(self, code: Code | None, to: Optional['FST'] = None, **options) -> 'FST':
        """Attempt a replacement by using str as source and attempting to parse into location of node(s) being
        replaced."""

        multi = to and to is not self
        pars  = True if multi else bool(FST.get_option('pars', options))
        loc   = self.pars(pars, exc_genexpr_solo=True)  # we don't check for unparenthesized Tuple code FST here because if it is then will just be parsed into a Tuple anyway

        if not loc:
            raise ValueError('node being reparsed must have a location')


        # TODO: allow all options for removing comments and space, not just pars


        if not multi:
            if not (parent := self.parent):  # we want parent which will not change or root node
                parent = self

            else:  # the checks below require a parent and don't make sense if there isn't one
                if isinstance(self.a, PARENTHESIZABLE):
                    if isinstance(code, AST):
                        if pars and isinstance(code, PARENTHESIZABLE):
                            if not (is_atom_ := is_atom(code, tuple_as_atom=None)):
                                if precedence_require_parens(code, parent.a, *self.pfield):
                                    code = ast_unparse(code) if is_atom_ is None else f'({ast_unparse(code)})'
                                elif is_atom_ is None:  # strip `unparse()` parens
                                    code = ast_unparse(code)[1:-1]

                    elif isinstance(code, FST):
                        if isinstance(a := code.a, (Module, Interactive)):
                            a = a.body[0] if len(a.body) == 1 else None
                        elif isinstance(a, Expression):
                            a = a.body

                        if isinstance(a, Expr):
                            a = a.value

                        if isinstance(a, PARENTHESIZABLE):
                            effpars = pars or a.f.is_parenthesized_tuple() is False
                            loc     = self.pars(effpars, exc_genexpr_solo=True)  # TODO: need to redo here with new `a`, should refactor to avoid this

                            if precedence_require_parens(a, parent.a, *self.pfield):
                                if not a.f.is_atom() and (effpars or not self.pars(ret_npars=True)[1]):
                                    a.f.parenthesize()

                            elif pars:  # remove parens only if allowed to
                                a.f.unparenthesize()

                            code = code._lines

                if (pars or not self.is_solo_call_arg_genexpr() or  # if original loc included `arguments` parentheses shared with solo GeneratorExp call arg then need to leave those in place
                    (to_loc := self.pars(True, exc_genexpr_solo=True))[:2] <= loc[:2]
                ):
                    to_loc = loc
                else:
                    loc = to_loc

            # elif pars:  # precedence parenthesizing
            #     if isinstance(code, FST):
            #         if not code.is_atom() and precedence_require_parens(code.a, parent.a, *self.pfield):
            #             code.parenthesize()

            #     elif isinstance(code, AST):
            #         if not (is_atom_ := is_atom(code, tuple_as_atom=None)):
            #             if precedence_require_parens(code, parent.a, *self.pfield):
            #                 code = ast_unparse(code) if is_atom_ is None else f'({ast_unparse(code)})'
            #             elif is_atom_ is None:  # strip `unparse()` parens
            #                 code = ast_unparse(code)[1:-1]

            if (pars or not self.is_solo_call_arg_genexpr() or  # if original loc included `arguments` parentheses shared with solo GeneratorExp call arg then need to leave those in place
                (to_loc := self.pars(True, exc_genexpr_solo=True))[:2] <= loc[:2]
            ):
                to_loc = loc
            else:
                loc = to_loc

        elif not (to_loc := to.pars(pars, exc_genexpr_solo=True)):  # pars is True here
            raise ValueError(f"'to' node must have a location")
        elif (root := self.root) is not to.root:
            raise ValueError(f"'to' node not part of same tree")
        elif to_loc[:2] < loc[:2]:
            raise ValueError(f"'to' node must follow self")

        else:
            self_path = root.child_path(self)[:-1]  # [:-1] makes sure we get parent of whatever combination of paths
            to_path   = root.child_path(to)[:-1]
            path      = list(p for p, _ in takewhile(lambda st: st[0] == st[1], zip(self_path, to_path)))
            parent    = root.child_from_path(path)

        return parent._reparse_raw_loc(code, loc.ln, loc.col, to_loc.end_ln, to_loc.end_col)

    # ------------------------------------------------------------------------------------------------------------------

    def _make_fst_and_dedent(self, indent: Union['FST', str], ast: AST, copy_loc: fstloc,
                             prefix: str = '', suffix: str = '',
                             put_loc: fstloc | None = None, put_lines: list[str] | None = None, *,
                             docstr: bool | Literal['strict'] | None = None) -> 'FST':
        if not isinstance(indent, str):
            indent = indent.get_indent()

        lines = self.root._lines
        fst   = FST(ast, lines=lines, from_=self)  # we use original lines for nodes offset calc before putting new lines

        fst.offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix.encode()) - lines[copy_loc.ln].c2b(copy_loc.col))

        fst._lines = fst_lines = self.get_src(*copy_loc, True)

        if suffix:
            fst_lines[-1] = bistr(fst_lines[-1] + suffix)

        if prefix:
            fst_lines[0] = bistr(prefix + fst_lines[0])

        fst.dedent_lns(indent, skip=bool(copy_loc.col), docstr=docstr)  # if copy location starts at column 0 then we apply dedent to it as well (preceding comment or something)

        if put_loc:
            self.put_src(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0

        return fst

    def _get_slice_seq_and_dedent(self, get_ast: AST, cut: bool, seq_loc: fstloc,
                            ffirst: Union['FST', fstloc], flast: Union['FST', fstloc],
                            fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                            prefix: str, suffix: str) -> 'FST':
        copy_loc, put_loc, put_lines = _src_edit.get_slice_seq(self, cut, seq_loc, ffirst, flast, fpre, fpost)

        copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

        if not cut:
            put_loc = None

        lines                  = self.root._lines
        get_ast.lineno         = copy_ln + 1
        get_ast.col_offset     = lines[copy_ln].c2b(copy_col)
        get_ast.end_lineno     = copy_end_ln + 1
        get_ast.end_col_offset = lines[copy_end_ln].c2b(copy_end_col)

        get_fst = self._make_fst_and_dedent(self, get_ast, copy_loc, prefix, suffix, put_loc, put_lines)

        get_ast.col_offset     = 0  # before prefix
        get_ast.end_col_offset = get_fst._lines[-1].lenbytes  # after suffix

        get_ast.f._touch()

        return get_fst

    def _get_slice_tuple_list_or_set(self, start: int | Literal['end'] | None, stop: int | None, field: str | None,
                                     cut: bool, **options) -> 'FST':
        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

        fix         = FST.get_option('fix', options)
        ast         = self.a
        elts        = ast.elts
        is_set      = isinstance(ast, Set)
        is_tuple    = not is_set and isinstance(ast, Tuple)
        start, stop = _fixup_slice_index(len(elts), start, stop)

        if start == stop:
            if is_set:
                return self._new_empty_set(from_=self)
            elif is_tuple:
                return self._new_empty_tuple(from_=self)
            else:
                return self._new_empty_list(from_=self)

        is_paren = is_tuple and self._is_parenthesized_seq()
        ffirst   = elts[start].f
        flast    = elts[stop - 1].f
        fpre     = elts[start - 1].f if start else None
        fpost    = elts[stop].f if stop < len(elts) else None

        if not cut:
            asts = [copy_ast(elts[i]) for i in range(start, stop)]

        else:
            asts = elts[start : stop]

            del elts[start : stop]

            for i in range(start, len(elts)):
                elts[i].f.pfield = astfield('elts', i)

        if is_set:
            get_ast = Set(elts=asts)  # location will be set later when span is potentially grown
            prefix  = '{'
            suffix  = '}'

        else:
            ctx     = ast.ctx.__class__
            get_ast = ast.__class__(elts=asts, ctx=ctx())

            if fix and not issubclass(ctx, Load):
                set_ctx(get_ast, Load)

            if is_tuple:
                prefix = '('
                suffix = ')'

            else:  # list
                prefix = '['
                suffix = ']'

        if not is_tuple:
            seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

            assert self.root._lines[self.ln].startswith(prefix, self.col)
            assert self.root._lines[seq_loc.end_ln].startswith(suffix, seq_loc.end_col)

        else:
            if not is_paren:
                seq_loc = self.loc

            else:
                seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

                assert self.root._lines[seq_loc.end_ln].startswith(')', seq_loc.end_col)

        fst = self._get_slice_seq_and_dedent(get_ast, cut, seq_loc, ffirst, flast, fpre, fpost, prefix, suffix)

        if fix:
            if is_set:
                self._maybe_fix_set()

            elif is_tuple:
                fst._maybe_add_singleton_tuple_comma(False)  # maybe need to add a postfix comma to copied single element tuple if is not already there
                self._maybe_fix_tuple(is_paren)

        return fst

    def _get_slice_empty_set(self, start: int | Literal['end'] | None, stop: int | None, field: str | None,
                                  cut: bool, **options) -> 'FST':
        fix = FST.get_option('fix', options)

        if not fix:
            raise ValueError(f"cannot get slice from an empty Set without specifying 'fix=True'")

        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

        if stop or (start and start != 'end'):
            raise IndexError(f"Set.{field} index out of range")

        return self._new_empty_set(from_=self)

    def _get_slice_dict(self, start: int | Literal['end'] | None, stop: int | None, field: str | None, cut: bool,
                        **options) -> 'FST':
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to slice from a Dict")

        fix         = FST.get_option('fix', options)
        ast         = self.a
        values      = ast.values
        start, stop = _fixup_slice_index(len(values), start, stop)

        if start == stop:
            return self._new_empty_dict(from_=self)

        keys   = ast.keys
        ffirst = self._dict_key_or_mock_loc(keys[start], values[start].f)
        flast  = values[stop - 1].f
        fpre   = values[start - 1].f if start else None
        fpost  = self._dict_key_or_mock_loc(keys[stop], values[stop].f) if stop < len(keys) else None

        if not cut:
            akeys   = [copy_ast(keys[i]) for i in range(start, stop)]
            avalues = [copy_ast(values[i]) for i in range(start, stop)]

        else:
            akeys   = keys[start : stop]
            avalues = values[start : stop]

            del keys[start : stop]
            del values[start : stop]

            for i in range(start, len(keys)):
                values[i].f.pfield = astfield('values', i)

                if key := keys[i]:  # could be None from **
                    key.f.pfield = astfield('keys', i)

        get_ast = Dict(keys=akeys, values=avalues)
        seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

        assert self.root._lines[self.ln].startswith('{', self.col)
        assert self.root._lines[seq_loc.end_ln].startswith('}', seq_loc.end_col)

        return self._get_slice_seq_and_dedent(get_ast, cut, seq_loc, ffirst, flast, fpre, fpost, '{', '}')

    def _get_slice_stmtish(self, start: int | Literal['end'] | None, stop: int | None, field: str | None, cut: bool,
                        one: bool = False, **options) -> 'FST':
        fix         = FST.get_option('fix', options)
        ast         = self.a
        field, body = _fixup_field_body(ast, field)
        start, stop = _fixup_slice_index(len(body), start, stop)

        if start == stop:
            return self._new_empty_module(from_=self)

        ffirst = body[start].f
        flast  = body[stop - 1].f
        fpre   = body[start - 1].f if start else None
        fpost  = body[stop].f if stop < len(body) else None
        indent = ffirst.get_indent()

        block_loc = fstloc(*(fpre.bloc[2:] if fpre else ffirst._prev_ast_bound()),
                           *(fpost.bloc[:2] if fpost else flast._next_ast_bound()))

        copy_loc, put_loc, put_lines = (
            _src_edit.get_slice_stmt(self, field, cut, block_loc, ffirst, flast, fpre, fpost, **options))

        if not cut:
            asts    = [copy_ast(body[i]) for i in range(start, stop)]
            put_loc = None

        else:
            is_last_child = not fpost and not flast.next()
            asts          = body[start : stop]

            del body[start : stop]

            for i in range(start, len(body)):
                body[i].f.pfield = astfield(field, i)

        if not one:
            get_ast = Module(body=asts, type_ignores=[])
        elif len(asts) == 1:
            get_ast = asts[0]
        else:
            raise ValueError(f'cannot specify `one=True` if getting multiple statements')

        fst = self._make_fst_and_dedent(indent, get_ast, copy_loc, '', '', put_loc, put_lines,
                                        docstr=options.get('docstr'))

        if cut and is_last_child:  # correct for removed last child nodes or last nodes past the block open colon
            self._fix_block_del_last_child(block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)

        if fix:
            if len(asts) == 1 and isinstance(a := asts[0], If):
                a.f._maybe_fix_elif()

        return fst

    def _put_slice_seq_and_indent(self, put_fst: Optional['FST'], seq_loc: fstloc,
                            ffirst: Union['FST', fstloc, None], flast: Union['FST', fstloc, None],
                            fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                            pfirst: Union['FST', fstloc, None], plast: Union['FST', fstloc, None],
                            docstr: bool | Literal['strict']) -> 'FST':
        root = self.root

        if not put_fst:  # delete
            # put_ln, put_col, put_end_ln, put_end_col = (
            #     _src_edit.put_slice_seq(self, None, '', seq_loc, ffirst, flast, fpre, fpost, None, None))
            _, (put_ln, put_col, put_end_ln, put_end_col), _ = (
                _src_edit.get_slice_seq(self, True, seq_loc, ffirst, flast, fpre, fpost))

            put_lines = None

        else:  # replace or insert
            assert put_fst.is_root

            indent = self.get_indent()

            put_fst.indent_lns(indent, docstr=docstr)

            put_ln, put_col, put_end_ln, put_end_col = (
                _src_edit.put_slice_seq(self, put_fst, indent, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast))

            lines           = root._lines
            put_lines       = put_fst._lines
            fst_dcol_offset = lines[put_ln].c2b(put_col)

            put_fst.offset(0, 0, put_ln, fst_dcol_offset)

        self_ln, self_col, _, _ = self.loc

        if put_col == self_col and put_ln == self_ln:  # unenclosed sequence
            self.offset(
                *root.put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, not fpost, False, self),
                True, True, self_=False)

        elif fpost:
            root.put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, False)
        else:
            root.put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, True, self)  # because of insertion at end and unparenthesized tuple

    def _put_slice_tuple_list_or_set(self, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                     field: str | None, one: bool, **options):
        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to assign slice to a {self.a.__class__.__name__}")

        fix = FST.get_option('fix', options)

        if code is None:
            put_fst = None

        else:
            put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)

            if one:
                if put_fst.is_parenthesized_tuple() is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
                    put_fst._parenthesize_tuple()

                put_ast  = Set(elts=[put_fst.a], lineno=1, col_offset=0, end_lineno=len(ls := put_fst._lines),
                               end_col_offset=ls[-1].lenbytes)
                put_fst  = FST(put_ast, lines=ls)
                is_tuple = is_set = False  # that's right, an `ast.Set` with `is_set=False` because in this case all we need is the `elts` container (without `ctx`)

            else:
                if put_fst.is_empty_set_call() or put_fst.is_empty_set_seq():
                    if fix:
                        put_fst = self._new_empty_set_curlies(from_=self)
                    else:
                        raise ValueError(f"cannot put empty Set as a slice without specifying 'fix=True'")

                put_ast  = put_fst.a
                is_tuple = isinstance(put_ast, Tuple)
                is_set   = not is_tuple and isinstance(put_ast, Set)

                if not is_tuple and not is_set and not isinstance(put_ast, List):
                    raise NodeTypeError(f"slice being assigned to a {self.a.__class__.__name__} "
                                        f"must be a Tuple, List or Set, not a '{put_ast.__class__.__name__}'")

        ast         = self.a
        elts        = ast.elts
        start, stop = _fixup_slice_index(len(elts), start, stop)
        slice_len   = stop - start

        if not slice_len and (not put_fst or not put_ast.elts):  # deleting or assigning empty seq to empty slice of seq, noop
            return

        is_self_tuple    = isinstance(ast, Tuple)
        is_self_set      = not is_self_tuple and isinstance(ast, Set)
        is_self_enclosed = not is_self_tuple or self._is_parenthesized_seq()
        fpre             = elts[start - 1].f if start else None
        fpost            = None if stop == len(elts) else elts[stop].f
        seq_loc          = fstloc(self.ln, self.col + is_self_enclosed, self.end_ln, self.end_col - is_self_enclosed)

        if not slice_len:
            ffirst = flast = None

        else:
            ffirst = elts[start].f
            flast  = elts[stop - 1].f

        if not put_fst:
            self._put_slice_seq_and_indent(None, seq_loc, ffirst, flast, fpre, fpost, None, None, options.get('docstr'))
            self._unmake_fst_tree(elts[start : stop])

            del elts[start : stop]

            put_len = 0

        else:
            put_lines = put_fst._lines

            if one:
                pass  # noop

            elif not is_tuple:
                put_ast.end_col_offset -= 1  # strip enclosing curlies or brackets from source set or list

                put_fst.offset(0, 1, 0, -1)

                assert put_lines[0].startswith('[{'[is_set])
                assert put_lines[-1].endswith(']}'[is_set])

                put_lines[-1] = bistr(put_lines[-1][:-1])
                put_lines[0]  = bistr(put_lines[0][1:])

            elif put_fst._is_parenthesized_seq():
                put_ast.end_col_offset -= 1  # strip enclosing parentheses from source tuple

                put_fst.offset(0, 1, 0, -1)

                put_lines[-1] = bistr(put_lines[-1][:-1])
                put_lines[0]  = bistr(put_lines[0][1:])

            if not (selts := put_ast.elts):
                pfirst = plast = None

            else:
                pfirst = selts[0].f
                plast  = selts[-1].f

            self._put_slice_seq_and_indent(put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast, options.get('docstr'))
            self._unmake_fst_tree(elts[start : stop], put_fst)

            elts[start : stop] = put_ast.elts

            put_len = len(put_ast.elts)
            stack   = [FST(elts[i], self, astfield('elts', i)) for i in range(start, start + put_len)]

            if fix and stack and not is_set:
                set_ctx([f.a for f in stack], Load if is_self_set else ast.ctx.__class__)

            self._make_fst_tree(stack)

        for i in range(start + put_len, len(elts)):
            elts[i].f.pfield = astfield('elts', i)

        if fix:
            if is_self_tuple:
                self._maybe_fix_tuple(is_self_enclosed)
            elif is_self_set:
                self._maybe_fix_set()

    def _put_slice_empty_set(self, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                  field: str | None, one: bool, **options):
        fix = FST.get_option('fix', options)

        if not fix:
            raise ValueError(f"cannot put slice to an empty Set without specifying 'fix=True'")

        ln, col, end_ln, end_col = self.loc

        empty   = self._new_empty_set_curlies(False, (a := self.a).lineno, a.col_offset, from_=self)
        old_src = self.get_src(ln, col, end_ln, end_col, True)
        old_ast = self._set_ast(empty.a)

        self.put_src(empty._lines, ln, col, end_ln, end_col, True, True, self, offset_excluded=False)

        try:
            self._put_slice_tuple_list_or_set(code, start, stop, field, one, **options)

        finally:
            if not self.a.elts:
                self.put_src(old_src, *self.loc, True)  # restore previous empty set representation
                self._set_ast(old_ast)

    def _put_slice_dict(self, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                        field: str | None, one: bool, **options):
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")
        if one:
            raise ValueError(f'cannot put a single item to a Dict slice')

        if code is None:
            put_fst = None

        else:
            put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)
            put_ast = put_fst.a

            if not isinstance(put_ast, Dict):
                raise ValueError(f"slice being assigned to a Dict must be a Dict, not a '{put_ast.__class__.__name__}'")

        ast         = self.a
        values      = ast.values
        start, stop = _fixup_slice_index(len(values), start, stop)
        slice_len   = stop - start

        if not slice_len and (not put_fst or not put_ast.keys):  # deleting or assigning empty dict to empty slice of dict, noop
            return

        keys    = ast.keys
        fpre    = values[start - 1].f if start else None
        fpost   = None if stop == len(keys) else self._dict_key_or_mock_loc(keys[stop], values[stop].f)
        seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

        if not slice_len:
            ffirst = flast = None

        else:
            ffirst = self._dict_key_or_mock_loc(keys[start], values[start].f)
            flast  = values[stop - 1].f

        if not put_fst:
            self._put_slice_seq_and_indent(None, seq_loc, ffirst, flast, fpre, fpost, None, None, options.get('docstr'))
            self._unmake_fst_tree(keys[start : stop] + values[start : stop])

            del keys[start : stop]
            del values[start : stop]

            put_len = 0

        else:
            put_lines               = put_fst._lines
            put_ast.end_col_offset -= 1  # strip enclosing curlies from source dict

            put_fst.offset(0, 1, 0, -1)

            assert put_lines[0].startswith('{')
            assert put_lines[-1].endswith('}')

            put_lines[-1] = bistr(put_lines[-1][:-1])
            put_lines[0]  = bistr(put_lines[0][1:])

            if not (skeys := put_ast.keys):
                pfirst = plast = None

            else:
                pfirst = put_fst._dict_key_or_mock_loc(skeys[0], put_ast.values[0].f)
                plast  = put_ast.values[-1].f

            self._put_slice_seq_and_indent(put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast, options.get('docstr'))
            self._unmake_fst_tree(keys[start : stop] + values[start : stop], put_fst)

            keys[start : stop]   = put_ast.keys
            values[start : stop] = put_ast.values
            put_len              = len(put_ast.keys)
            stack                = []

            for i in range(put_len):
                startplusi = start + i

                stack.append(FST(values[startplusi], self, astfield('values', startplusi)))

                if key := keys[startplusi]:
                    stack.append(FST(key, self, astfield('keys', startplusi)))

            self._make_fst_tree(stack)

        for i in range(start + put_len, len(keys)):
            values[i].f.pfield = astfield('values', i)

            if key := keys[i]:  # could be None from **
                key.f.pfield = astfield('keys', i)

    def _put_slice_stmtish(self, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                        field: str | None, one: bool, **options):
        ast         = self.a
        field, body = _fixup_field_body(ast, field)

        if code is None:
            put_fst = None

        else:
            put_fst  = self._normalize_code(code, 'mod', parse_params=self.root.parse_params)
            put_ast  = put_fst.a
            put_body = put_ast.body

            if one and len(put_body) != 1:
                raise ValueError('expecting a single statement')

            node_type = ExceptHandler if field == 'handlers' else match_case if field == 'cases' else stmt

            if any(not isinstance(bad_node := n, node_type) for n in put_body) and options.get('check_node_type', True):  # TODO: `check_node_type` is for some previously written tests, but really should fix those tests instead
                raise ValueError(f"cannot put {bad_node.__class__.__qualname__} node to '{field}' field")

        start, stop = _fixup_slice_index(len(body), start, stop)
        slice_len   = stop - start

        if not slice_len and (not put_fst or (not put_body and len(ls := put_fst._lines) == 1 and not ls[0])):  # deleting empty slice or assigning empty fst to empty slice, noop
            return

        root  = self.root
        lines = root._lines
        fpre  = body[start - 1].f if start else None
        fpost = body[stop].f if stop < len(body) else None

        if put_fst:
            opener_indent = self.get_indent()

            if not body:
                block_indent = opener_indent if self.is_root else opener_indent + root.indent
            elif not (b0 := body[0]).f.is_elif():
                block_indent = b0.f.get_indent()
            elif (bb := b0.body) or (bb := b0.orelse):
                block_indent = bb[0].f.get_indent()
            else:
                block_indent = opener_indent + root.indent

            if fpre or fpost:
                self._normalize_block(field, indent=block_indent)  # don't want to bother figuring out if valid to insert to statements on single block logical line

        if slice_len:  # replacement
            ffirst = body[start].f
            flast  = body[stop - 1].f

            block_loc = fstloc(*(fpre.bloc[2:] if fpre else ffirst._prev_ast_bound()),
                               *(fpost.bloc[:2] if fpost else flast._next_ast_bound()))

            is_last_child = not fpost and not flast.next()

        else:  # insertion
            ffirst = flast = None

            if field == 'orelse' and len(body) == 1 and (f := body[0].f).is_elif():
                f._elif_to_else_if()

            if fpre:
                block_loc     = fstloc(*fpre.bloc[2:], *(fpost.bloc[:2] if fpost else fpre._next_ast_bound()))
                is_last_child = not fpost and not fpre.next()

            elif fpost:
                if isinstance(ast, mod):  # put after all header stuff in module
                    ln, col, _, _ = fpost.bloc
                    block_loc     = fstloc(ln, col, ln, col)

                elif field != 'handlers' or ast.body:
                    block_loc = fstloc(*fpost._prev_ast_bound(), *fpost.bloc[:2])

                else:  # special case because 'try:' doesn't have ASTs inside it and each 'except:' lives at the 'try:' indentation level
                    end_ln, end_col = fpost.bloc[:2]
                    ln, col         = _prev_find(lines, *fpost._prev_ast_bound(), end_ln, end_col, ':')
                    block_loc       = fstloc(ln, col + 1, end_ln, end_col)

                is_last_child = False

            else:  # insertion into empty block (or nonexistent 'else' or 'finally' block)
                if not put_body and field in ('orelse', 'finalbody'):
                    raise ValueError(f"cannot insert empty statement into empty '{field}' field")

                if isinstance(ast, (FunctionDef, AsyncFunctionDef, ClassDef, With, AsyncWith, Match, ExceptHandler,
                                    match_case)):  # only one block possible, 'body' or 'cases'
                    block_loc     = fstloc(*self.bloc[2:], *self._next_ast_bound())  # end of bloc will be just past ':'
                    is_last_child = True

                elif isinstance(ast, mod):  # put after all header stuff in module
                    _, _, end_ln, end_col = self.bloc

                    block_loc     = fstloc(end_ln, end_col, end_ln, end_col)
                    is_last_child = True

                elif isinstance(ast, (For, AsyncFor, While, If)):  # 'body' or 'orelse'
                    if field == 'orelse':
                        is_last_child = True

                        if not (body_ := ast.body):
                            block_loc = fstloc(*self.bloc[2:], *self._next_ast_bound())
                        else:
                            block_loc = fstloc(*body_[-1].f.bloc[2:], *self._next_ast_bound())

                    else:  # field == 'body':
                        if orelse := ast.orelse:
                            ln, col       = _next_find(lines, *(f := orelse[0].f).prev().bloc[2:], *f.bloc[:2], ':')  # we know its there
                            block_loc     = fstloc(ln, col + 1, *orelse[0].f.bloc[:2])
                            is_last_child = False

                        else:
                            block_loc     = fstloc(*self.bloc[2:], *self._next_ast_bound())
                            is_last_child = True

                else:  # isinstance(ast, (Try, TryStar))
                    assert isinstance(ast, (Try, TryStar))

                    if field == 'finalbody':
                        is_last_child = True

                        if not (block := ast.orelse) and not (block := ast.handlers) and not (block := ast.body):
                            block_loc = fstloc(*self.bloc[2:], *self._next_ast_bound())
                        else:
                            block_loc = fstloc(*block[-1].f.bloc[2:], *self._next_ast_bound())

                    elif field == 'orelse':
                        if finalbody := ast.finalbody:
                            end_ln, end_col = _prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')  # we can use bloc[:2] even if there are ASTs between that and here because 'finally' must be on its own line
                            is_last_child   = False

                        else:
                            end_ln, end_col = self._next_ast_bound()
                            is_last_child   = True

                        if not (block := ast.handlers) and not (block := ast.body):
                            ln, col   = _prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                            block_loc = fstloc(ln, col + 1, end_ln, end_col)

                        else:
                            block_loc = fstloc(*block[-1].f.bloc[2:], end_ln, end_col)

                    elif field == 'handlers':
                        if orelse := ast.orelse:
                            end_ln, end_col = _prev_find(lines, *self.bloc[:2], *orelse[0].f.bloc[:2], 'else')
                            is_last_child   = False

                        elif finalbody := ast.finalbody:
                            end_ln, end_col = _prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')
                            is_last_child   = False

                        else:
                            end_ln, end_col = self._next_ast_bound()
                            is_last_child   = True

                        if not (body_ := ast.body):
                            ln, col   = _prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                            block_loc = fstloc(ln, col + 1, end_ln, end_col)

                        else:
                            block_loc = fstloc(*body_[-1].f.bloc[2:], end_ln, end_col)

                    else:  # field == 'body'
                        if handlers := ast.handlers:
                            end_ln, end_col = handlers[0].f.bloc[:2]
                            is_last_child   = False

                        elif orelse := ast.orelse:
                            end_ln, end_col = _prev_find(lines, *self.bloc[:2], *orelse[0].f.bloc[:2], 'else')
                            is_last_child   = False

                        elif finalbody := ast.finalbody:
                            end_ln, end_col = _prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')
                            is_last_child   = False

                        else:
                            end_ln, end_col = self._next_ast_bound()
                            is_last_child   = True

                        ln, col   = _prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                        block_loc = fstloc(ln, col + 1, end_ln, end_col)

        if not put_fst:
            _, put_loc, put_lines = (
                _src_edit.get_slice_stmt(self, field, True, block_loc, ffirst, flast, fpre, fpost, **options))

            if put_loc:
                self.put_src(put_lines, *put_loc, True)

            self._unmake_fst_tree(body[start : stop])

            del body[start : stop]

            put_len = 0

        else:
            put_loc = _src_edit.put_slice_stmt(self, put_fst, field, block_loc, opener_indent, block_indent,
                                               ffirst, flast, fpre, fpost, **options)

            put_fst.offset(0, 0, put_loc.ln, 0 if put_fst.bln or put_fst.bcol else lines[put_loc.ln].c2b(put_loc.col))
            self.put_src(put_fst.lines, *put_loc, False)
            self._unmake_fst_tree(body[start : stop], put_fst)

            body[start : stop] = put_body

            put_len = len(put_body)
            stack   = [FST(body[i], self, astfield(field, i)) for i in range(start, start + put_len)]

            self._make_fst_tree(stack)

        for i in range(start + put_len, len(body)):
            body[i].f.pfield = astfield(field, i)

        if is_last_child:  # correct parent for modified / removed last child nodes
            if not put_fst:
                self._fix_block_del_last_child(block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)
            elif put_body:
                self._set_end_pos((last_child := self.last_child()).end_lineno, last_child.end_col_offset)

    def _put_slice_raw(self, code: Code | None, start: int | Literal['end'] | None = None, stop: int | None = None,
                       field: str | None = None, *, one: bool = False, **options) -> 'FST':  # -> Self
        """Put a raw slice of child nodes to `self`."""

        if isinstance(code, AST):
            if not one:
                try:
                    ast = _reduce_ast(code, 'exprish')
                except Exception:
                    pass

                else:
                    if isinstance(ast, Tuple):  # strip delimiters because we want CONTENTS of slice for raw put, not the slice object itself
                        code = ast_unparse(ast)[1 : (-2 if len(ast.elts) == 1 else -1)]  # also remove singleton Tuple trailing comma
                    elif isinstance(ast, (List, Dict, Set, MatchSequence, MatchMapping)):
                        code = ast_unparse(ast)[1 : -1]

        elif isinstance(code, FST):
            if not code.is_root:
                raise ValueError('expecting root FST')

            try:
                ast = _reduce_ast(code.a, 'exprish')
            except Exception:
                pass

            else:
                fst = ast.f

                if one:
                    if (is_par_tup := fst.is_parenthesized_tuple()) is None:  # only need to parenthesize this, others are already enclosed
                        if isinstance(ast, MatchSequence) and not fst._is_parenthesized_seq('patterns'):
                            fst._parenthesize_grouping()

                    elif is_par_tup is False:
                        fst._parenthesize_tuple()

                elif ((is_dict := isinstance(ast, Dict)) or
                      (is_match := isinstance(ast, (MatchSequence, MatchMapping))) or
                      isinstance(ast, (Tuple, List, Set))
                ):
                    if not ((is_par_tup := fst.is_parenthesized_tuple()) is False or  # don't strip nonexistent delimiters if is unparenthesized Tuple or MatchSequence
                            (is_par_tup is None and isinstance(ast, MatchSequence) and
                             not fst._is_parenthesized_seq('patterns'))
                    ):
                        code.put_src(None, end_ln := code.end_ln, (end_col := code.end_col) - 1, end_ln, end_col, True)  # strip enclosing delimiters
                        code.put_src(None, ln := code.ln, col := code.col, ln, col + 1, False)

                    if elts := ast.values if is_dict else ast.patterns if is_match else ast.elts:
                        if comma := _next_find(code.root._lines, (l := elts[-1].f.loc).end_ln, l.end_col, code.end_ln,
                                               code.end_col, ','):  # strip trailing comma
                            ln, col = comma

                            code.put_src(None, ln, col, ln, col + 1, False)

        self._reparse_raw_loc(code, *self._raw_slice_loc(start, stop, field))

        return self.repath()

    # ------------------------------------------------------------------------------------------------------------------

    def _to_to_slice_idx(self, idx: int, field: str, to: Optional['FST']):
        """If a `to` parameter is passed then try to convert it to an index in the same body list as `self`."""

        if not to:
            return idx + 1 or len(getattr(self.a, field))  # or for negative indices

        elif to.parent is self.parent is not None and (pf := to.pfield).name == self.pfield.name:
            if (to_idx := pf.idx) < idx:
                raise ValueError("invalid 'to' node, must follow self in body")

            return to_idx + 1

        raise NodeTypeError(f"invalid 'to' node")

    def _put_one_stmtish(self, code: Code | None, idx: int | None, field: str, child: Any, **options,
                         ) -> Optional['FST']:
        """Put or delete a single statementish node to a list of them (body, orelse, handlers, finalbody or cases)."""

        self._put_slice_stmtish(code, idx, self._to_to_slice_idx(idx, field, options.get('to')), field, True, **options)

        return None if code is None else getattr(self.a, field)[idx].f

    def _put_one_tuple_list_or_set(self, code: Code | None, idx: int | None, field: str, child: Any, **options,
                                   ) -> Optional['FST']:
        """Put or delete a single expression to a Tuple, List or Set elts."""

        self._put_slice_tuple_list_or_set(code, idx, self._to_to_slice_idx(idx, field, options.get('to')), field, True,
                                          **options)

        return None if code is None else getattr(self.a, field)[idx].f

    def _put_one_expr_required(self, code: Code | None, idx: int | None, field: str, child: Any, **options,
                               ) -> Optional['FST']:
        """Put a single required expression node."""

        if code is None:
            raise ValueError(f'cannot delete a {self.a.__class__.__name__}.{field}')
        if idx is not None:
            raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')
        if options.get('to'):
            raise NodeTypeError(f"cannot put with 'to' to {self.a.__class__.__name__}.{field}")

        ast     = self.a
        put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)
        put_ast = put_fst.a
        childf  = child.f
        pars    = bool(FST.get_option('pars', options))
        effpars = pars or put_fst.is_parenthesized_tuple() is False  # need tuple check because otherwise location would be wrong after
        loc     = childf.pars(effpars)  # don't need exc_genexpr_solo=True here because guaranteed not to be this

        if precedence_require_parens(put_ast, ast, field, None):
            if not put_fst.is_atom() and (effpars or not childf.pars(ret_npars=True)[1]):
                put_fst.parenthesize()

        elif pars:  # remove parens only if allowed to
            put_fst.unparenthesize()

        put_fst.indent_lns(childf.get_indent(), docstr=options.get('docstr'))

        ln, col, end_ln, end_col = loc

        lines       = self.root._lines
        put_lines   = put_fst._lines
        dcol_offset = lines[ln].c2b(col)

        put_fst.offset(0, 0, ln, dcol_offset)
        self.put_src(put_lines, ln, col, end_ln, end_col, True)
        childf._set_ast(put_ast)

        return put_ast.f

    def _put_one(self, code: Code | None, idx: int | None, field: str, **options) -> Optional['FST']:
        """Put new, replace or delete a node (or limited non-node) to a field of `self`."""

        if isinstance(child := getattr(self.a, field), list):
            child = child[idx]

        ast = self.a
        raw = FST.get_option('raw', options)

        if raw is not True:
            if raw and raw != 'auto':
                raise ValueError(f"invalid value for raw parameter '{raw}'")

            try:
                if handler := FST._PUT_ONE_HANDLERS.get((ast.__class__, field)):
                    return handler(self, code, idx, field, child, **options)

            except (SyntaxError, NodeTypeError):
                if not raw:
                    raise

            else:
                if not raw:
                    raise ValueError(f"cannot replace in {ast.__class__.__name__}.{field}")

        ret = child.f._reparse_raw_node(code, **options)

        return None if code is None else ret


    # TODO: finish these


    _PUT_ONE_HANDLERS = {
        (Module, 'body'):                     _put_one_stmtish, # stmt*
        # (Module, 'type_ignores'):             _put_one_default, # type_ignore*
        (Interactive, 'body'):                _put_one_stmtish, # stmt*
        (Expression, 'body'):                 _put_one_expr_required, # expr
        # (FunctionType, 'argtypes'):           _put_one_default, # expr*
        # (FunctionType, 'returns'):            _put_one_default, # expr
        # (FunctionDef, 'decorator_list'):      _put_one_default, # expr*
        # (FunctionDef, 'name'):                _put_one_default, # identifier
        # (FunctionDef, 'type_params'):         _put_one_default, # type_param*
        # (FunctionDef, 'args'):                _put_one_default, # arguments
        # (FunctionDef, 'returns'):             _put_one_default, # expr?
        (FunctionDef, 'body'):                _put_one_stmtish, # stmt*
        # (FunctionDef, 'type_comment'):        _put_one_default, # string?
        # (AsyncFunctionDef, 'decorator_list'): _put_one_default, # expr*
        # (AsyncFunctionDef, 'name'):           _put_one_default, # identifier
        # (AsyncFunctionDef, 'type_params'):    _put_one_default, # type_param*
        # (AsyncFunctionDef, 'args'):           _put_one_default, # arguments
        # (AsyncFunctionDef, 'returns'):        _put_one_default, # expr?
        (AsyncFunctionDef, 'body'):           _put_one_stmtish, # stmt*
        # (AsyncFunctionDef, 'type_comment'):   _put_one_default, # string?
        # (ClassDef, 'decorator_list'):         _put_one_default, # expr*
        # (ClassDef, 'name'):                   _put_one_default, # identifier
        # (ClassDef, 'type_params'):            _put_one_default, # type_param*
        # (ClassDef, 'bases'):                  _put_one_default, # expr*
        # (ClassDef, 'keywords'):               _put_one_default, # keyword*
        (ClassDef, 'body'):                   _put_one_stmtish, # stmt*
        # (Return, 'value'):                    _put_one_default, # expr?
        # (Delete, 'targets'):                  _put_one_default, # expr*
        # (Assign, 'targets'):                  _put_one_default, # expr*
        (Assign, 'value'):                    _put_one_expr_required, # expr
        # (Assign, 'type_comment'):             _put_one_default, # string?
        # (TypeAlias, 'name'):                  _put_one_default, # expr
        # (TypeAlias, 'type_params'):           _put_one_default, # type_param*
        # (TypeAlias, 'value'):                 _put_one_default, # expr
        # (AugAssign, 'target'):                _put_one_default, # expr
        # (AugAssign, 'op'):                    _put_one_default, # operator
        (AugAssign, 'value'):                 _put_one_expr_required, # expr
        # (AnnAssign, 'target'):                _put_one_default, # expr
        # (AnnAssign, 'annotation'):            _put_one_default, # expr
        # (AnnAssign, 'value'):                 _put_one_default, # expr?
        # (AnnAssign, 'simple'):                _put_one_default, # int
        # (For, 'target'):                      _put_one_default, # expr
        (For, 'iter'):                        _put_one_expr_required, # expr
        (For, 'body'):                        _put_one_stmtish, # stmt*
        (For, 'orelse'):                      _put_one_stmtish, # stmt*
        # (For, 'type_comment'):                _put_one_default, # string?
        # (AsyncFor, 'target'):                 _put_one_default, # expr
        (AsyncFor, 'iter'):                   _put_one_expr_required, # expr
        (AsyncFor, 'body'):                   _put_one_stmtish, # stmt*
        (AsyncFor, 'orelse'):                 _put_one_stmtish, # stmt*
        # (AsyncFor, 'type_comment'):           _put_one_default, # string?
        (While, 'test'):                      _put_one_expr_required, # expr
        (While, 'body'):                      _put_one_stmtish, # stmt*
        (While, 'orelse'):                    _put_one_stmtish, # stmt*
        (If, 'test'):                         _put_one_expr_required, # expr
        (If, 'body'):                         _put_one_stmtish, # stmt*
        (If, 'orelse'):                       _put_one_stmtish, # stmt*
        # (With, 'items'):                      _put_one_default, # withitem*
        (With, 'body'):                       _put_one_stmtish, # stmt*
        # (With, 'type_comment'):               _put_one_default, # string?
        # (AsyncWith, 'items'):                 _put_one_default, # withitem*
        (AsyncWith, 'body'):                  _put_one_stmtish, # stmt*
        # (AsyncWith, 'type_comment'):          _put_one_default, # string?
        (Match, 'subject'):                   _put_one_expr_required, # expr
        (Match, 'cases'):                     _put_one_stmtish, # match_case*
        # (Raise, 'exc'):                       _put_one_default, # expr?
        # (Raise, 'cause'):                     _put_one_default, # expr?
        (Try, 'body'):                        _put_one_stmtish, # stmt*
        (Try, 'handlers'):                    _put_one_stmtish, # excepthandler*
        (Try, 'orelse'):                      _put_one_stmtish, # stmt*
        (Try, 'finalbody'):                   _put_one_stmtish, # stmt*
        (TryStar, 'body'):                    _put_one_stmtish, # stmt*
        (TryStar, 'handlers'):                _put_one_stmtish, # excepthandler*
        (TryStar, 'orelse'):                  _put_one_stmtish, # stmt*
        (TryStar, 'finalbody'):               _put_one_stmtish, # stmt*
        (Assert, 'test'):                     _put_one_expr_required, # expr
        # (Assert, 'msg'):                      _put_one_default, # expr?
        # (Import, 'names'):                    _put_one_default, # alias*
        # (ImportFrom, 'module'):               _put_one_default, # identifier?
        # (ImportFrom, 'names'):                _put_one_default, # alias*
        # (ImportFrom, 'level'):                _put_one_default, # int?
        # (Global, 'names'):                    _put_one_default, # identifier*
        # (Nonlocal, 'names'):                  _put_one_default, # identifier*
        (Expr, 'value'):                      _put_one_expr_required, # expr
        # (BoolOp, 'op'):                       _put_one_default, # boolop
        # (BoolOp, 'values'):                   _put_one_default, # expr*
        # (NamedExpr, 'target'):                _put_one_default, # expr
        (NamedExpr, 'value'):                 _put_one_expr_required, # expr
        (BinOp, 'left'):                      _put_one_expr_required, # expr
        # (BinOp, 'op'):                        _put_one_default, # operator
        (BinOp, 'right'):                     _put_one_expr_required, # expr
        # (UnaryOp, 'op'):                      _put_one_default, # unaryop
        (UnaryOp, 'operand'):                 _put_one_expr_required, # expr
        # (Lambda, 'args'):                     _put_one_default, # arguments
        (Lambda, 'body'):                     _put_one_expr_required, # expr
        (IfExp, 'body'):                      _put_one_expr_required, # expr
        (IfExp, 'test'):                      _put_one_expr_required, # expr
        (IfExp, 'orelse'):                    _put_one_expr_required, # expr
        # (Dict, 'keys'):                       _put_one_default, # expr*           - takes idx, handle special key=None?
        # (Dict, 'values'):                     _put_one_default, # expr*           - takes idx,
        (Set, 'elts'):                        _put_one_tuple_list_or_set, # expr*
        (ListComp, 'elt'):                    _put_one_expr_required, # expr
        # (ListComp, 'generators'):             _put_one_default, # comprehension*
        (SetComp, 'elt'):                     _put_one_expr_required, # expr
        # (SetComp, 'generators'):              _put_one_default, # comprehension*
        (DictComp, 'key'):                    _put_one_expr_required, # expr
        (DictComp, 'value'):                  _put_one_expr_required, # expr
        # (DictComp, 'generators'):             _put_one_default, # comprehension*
        (GeneratorExp, 'elt'):                _put_one_expr_required, # expr
        # (GeneratorExp, 'generators'):         _put_one_default, # comprehension*
        (Await, 'value'):                     _put_one_expr_required, # expr
        # (Yield, 'value'):                     _put_one_default, # expr?
        (YieldFrom, 'value'):                 _put_one_expr_required, # expr
        # (Compare, 'left'):                    _put_one_default, # expr
        # (Compare, 'ops'):                     _put_one_default, # cmpop*
        # (Compare, 'comparators'):             _put_one_default, # expr*
        # (Call, 'func'):                       _put_one_default, # expr            - identifier
        # (Call, 'args'):                       _put_one_default, # expr*
        # (Call, 'keywords'):                   _put_one_default, # keyword*
        (FormattedValue, 'value'):            _put_one_expr_required, # expr
        # (FormattedValue, 'format_spec'):      _put_one_default, # expr?
        # (FormattedValue, 'conversion'):       _put_one_default, # int
        # (Interpolation, 'value'):             _put_one_default, # expr            - need to change .str as well as expr
        # (Interpolation, 'constant'):          _put_one_default, # str
        # (Interpolation, 'conversion'):        _put_one_default, # int
        # (Interpolation, 'format_spec'):       _put_one_default, # expr?
        # (JoinedStr, 'values'):                _put_one_default, # expr*
        # (TemplateStr, 'values'):              _put_one_default, # expr*
        # (Constant, 'value'):                  _put_one_default, # constant
        # (Constant, 'kind'):                   _put_one_default, # string?
        (Attribute, 'value'):                 _put_one_expr_required, # expr
        # (Attribute, 'attr'):                  _put_one_default, # identifier
        # (Attribute, 'ctx'):                   _put_one_default, # expr_context
        (Subscript, 'value'):                 _put_one_expr_required, # expr
        # (Subscript, 'slice'):                 _put_one_default, # expr
        # (Subscript, 'ctx'):                   _put_one_default, # expr_context
        (Starred, 'value'):                   _put_one_expr_required, # expr
        # (Starred, 'ctx'):                     _put_one_default, # expr_context
        # (Name, 'id'):                         _put_one_default, # identifier
        # (Name, 'ctx'):                        _put_one_default, # expr_context
        (List, 'elts'):                       _put_one_tuple_list_or_set, # expr*
        # (List, 'ctx'):                        _put_one_default, # expr_context
        (Tuple, 'elts'):                      _put_one_tuple_list_or_set, # expr*
        # (Tuple, 'ctx'):                       _put_one_default, # expr_context
        # (Slice, 'lower'):                     _put_one_default, # expr?
        # (Slice, 'upper'):                     _put_one_default, # expr?
        # (Slice, 'step'):                      _put_one_default, # expr?
        # (comprehension, 'target'):            _put_one_default, # expr            - Name or Tuple (maybe empty?)
        (comprehension, 'iter'):              _put_one_expr_required, # expr
        # (comprehension, 'ifs'):               _put_one_default, # expr*
        # (comprehension, 'is_async'):          _put_one_default, # int
        # (ExceptHandler, 'type'):              _put_one_default, # expr?
        # (ExceptHandler, 'name'):              _put_one_default, # identifier?
        (ExceptHandler, 'body'):              _put_one_stmtish, # stmt*
        # (arguments, 'posonlyargs'):           _put_one_default, # arg*
        # (arguments, 'args'):                  _put_one_default, # arg*
        # (arguments, 'defaults'):              _put_one_default, # expr*
        # (arguments, 'vararg'):                _put_one_default, # arg?
        # (arguments, 'kwonlyargs'):            _put_one_default, # arg*
        # (arguments, 'kw_defaults'):           _put_one_default, # expr*
        # (arguments, 'kwarg'):                 _put_one_default, # arg?
        # (arg, 'arg'):                         _put_one_default, # identifier
        # (arg, 'annotation'):                  _put_one_default, # expr?
        # (arg, 'type_comment'):                _put_one_default, # string?
        # (keyword, 'arg'):                     _put_one_default, # identifier?
        (keyword, 'value'):                   _put_one_expr_required, # expr
        # (alias, 'name'):                      _put_one_default, # identifier
        # (alias, 'asname'):                    _put_one_default, # identifier?
        (withitem, 'context_expr'):           _put_one_expr_required, # expr
        # (withitem, 'optional_vars'):          _put_one_default, # expr?
        # (match_case, 'pattern'):              _put_one_default, # pattern
        # (match_case, 'guard'):                _put_one_default, # expr?
        (match_case, 'body'):                 _put_one_stmtish, # stmt*
        # (MatchValue, 'value'):                _put_one_default, # expr            - limited values, Constant? Name becomes MatchAs
        # (MatchSingleton, 'value'):            _put_one_default, # constant
        # (MatchSequence, 'patterns'):          _put_one_default, # pattern*
        # (MatchMapping, 'keys'):               _put_one_default, # expr*
        # (MatchMapping, 'patterns'):           _put_one_default, # pattern*
        # (MatchMapping, 'rest'):               _put_one_default, # identifier?
        # (MatchClass, 'cls'):                  _put_one_default, # expr
        # (MatchClass, 'patterns'):             _put_one_default, # pattern*
        # (MatchClass, 'kwd_attrs'):            _put_one_default, # identifier*
        # (MatchClass, 'kwd_patterns'):         _put_one_default, # pattern*
        # (MatchStar, 'name'):                  _put_one_default, # identifier?
        # (MatchAs, 'pattern'):                 _put_one_default, # pattern?
        # (MatchAs, 'name'):                    _put_one_default, # identifier?
        # (MatchOr, 'patterns'):                _put_one_default, # pattern*
        # (TypeIgnore, 'lineno'):               _put_one_default, # int
        # (TypeIgnore, 'tag'):                  _put_one_default, # string
        # (TypeVar, 'name'):                    _put_one_default, # identifier
        # (TypeVar, 'bound'):                   _put_one_default, # expr?
        # (TypeVar, 'default_value'):           _put_one_default, # expr?
        # (ParamSpec, 'name'):                  _put_one_default, # identifier
        # (ParamSpec, 'default_value'):         _put_one_default, # expr?
        # (TypeVarTuple, 'name'):               _put_one_default, # identifier
        # (TypeVarTuple, 'default_value'):      _put_one_default, # expr?
    }

    # ------------------------------------------------------------------------------------------------------------------

    def __repr__(self) -> str:
        tail = self._repr_tail()
        head = f'<fst.{(a := self.a).__class__.__name__} 0x{id(a):x}{tail}>'

        if not REPR_SRC_LINES:
            return head

        try:
            ln, col, end_ln, end_col = self.loc

            if end_ln - ln + 1 <= REPR_SRC_LINES:
                ls = self.root._lines[ln : end_ln + 1]
            else:
                ls = (self.root._lines[ln : ln + ((REPR_SRC_LINES + 1) // 2)] + ['...'] +
                      self.root._lines[end_ln - ((REPR_SRC_LINES - 2) // 2) : end_ln + 1])

            ls[-1] = ls[-1][:end_col]
            ls[0]  = ' ' * col + ls[0][col:]

            return '\n'.join([head] + ls)

        except Exception:
            pass

        return head + '\n???'

    def __getattr__(self, name) -> Any:
        if isinstance(child := getattr(self.a, name), list):
            return fstlist(self, name, 0, len(child))
        elif isinstance(child, AST):
            return child.f

        return child

    # ------------------------------------------------------------------------------------------------------------------

    def __new__(cls, ast_or_src: AST | str | bytes | list[str] | None = None,
                parent: Optional['FST'] = None, pfield: astfield | None = None, **kwargs):
        """Create a new individual `FST` node or full tree from `AST` with `lines` or create from just an `AST` or just
        source.

        **Parameters:**
        - `ast_or_src`: `AST` node for `FST` or source code in the form of a `str`, encoded `bytes` or a list of lines.
            If an `AST` then will be processed differently depending on if `lines` is provided or not.
        - `parent`: Parent node for this node. If provided then this is just a simple node and it is created with the
            `self.parent` and `self.pfield` set to passed params. If `None` then it means the creation of a full new
            `FST` tree.
        - `pfield`: `astfield` indication position in parent of this node. If `parent` is provided then this is assumed
            to exist and set as `self.pfield`.
        - `kwargs`: Contextual parameters:
            - `lines`: If this is provided and `parent` is `None` then this will be a new root `FST` node and the
                children of the provided `ast_or_src` (as `AST`) are walked to create `FST` nodes and the full tree.
                Only valid when creating a root node.
            - `from_`: If this is provided then it must be an `FST` node from which this node is being created. This
                allows to copy parse parameters and already determined default indentation.
            - `parse_params`: A `dict` with values for 'filename', 'type_comments' and 'feature_version' which will be
                used for any `AST` reparse done on this tree. Only valid when creating a root node.
            - `indent`: Indentation string to use as default indentation. If not provided and not gotten from `from_`
                then indentation will be inferred from source. Only valid when creating a root node.
            - `filename`, `mode`, `type_comments` and `feature_version`: If creating from an `AST` or source only then
                these are the parameteres passed to the respective `.new()`, `.fromsrc()` or `.fromast()` functions.
                Only valid when `parent=None` and no `lines`.
        """

        if parent is None:  # creating top level shortcut
            if (lines := kwargs.get('lines')) is None:  # if lines missing then is shortcut create from source or AST
                params = {k: v for k in ('filename', 'mode', 'type_comments', 'feature_version')
                          if (v := kwargs.get(k, k)) is not k}  # k used as sentinel

                if from_ := kwargs.get('from_'): # copy parse params from source tree
                    params = {**from_.root.parse_params, **params}

                if ast_or_src is None:
                    return FST.new(**params)
                if isinstance(ast_or_src, AST):
                    return FST.fromast(ast_or_src, **params)

                return FST.fromsrc(ast_or_src, **params)

        # creating actual node

        if self := getattr(ast_or_src, 'f', None):  # reuse FST node assigned to AST node (because otherwise it isn't valid anyway)
            self._touch()
        else:
            self = ast_or_src.f = object.__new__(cls)

        self.a      = ast_or_src  # we don't assume `self.a` is `ast_or_src` if `.f` exists
        self.parent = parent
        self.pfield = pfield

        if parent is not None:
            self.root = parent.root

            return self

        # ROOT

        self.root   = self
        self._lines = lines if lines[0].__class__ is bistr else [bistr(s) for s in lines]

        if from_ := kwargs.get('from_'):  # copy params from source tree
            from_root         = from_.root
            self.parse_params = kwargs.get('parse_params', from_root.parse_params)
            self.indent       = kwargs.get('indent', from_root.indent)

        else:
            self.parse_params = kwargs.get('parse_params', DEFAULT_PARSE_PARAMS)
            self.indent       = kwargs.get('indent', '?')

        self._make_fst_tree()

        if self.indent == '?':  # infer indentation from source, just use first indentation found for performance, don't try to find most common or anything like that
            if not isinstance(ast_or_src, Module):
                self.indent = DEFAULT_INDENT

            else:
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
                    self.indent = DEFAULT_INDENT

        return self

    @staticmethod
    def new(filename: str = '<unknown>', mode: str = 'exec', *,
            type_comments: bool = False, feature_version: tuple[int, int] | None = None) -> 'FST':
        """Create a new empty `FST` tree with the top level node dictated by the `mode` parameter.

        **Parameters:**
        - `filename`: `ast.parse()` parameter.
        - `mode`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.

        **Returns:**
        - `FST`: The new empty top level `FST` node.
        """

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)

        if mode == 'exec':
            ast = Module(body=[], type_ignores=[])
        elif mode == 'eval':
            ast = Expression(body=Constant(value=None, lineno=1, col_offset=0, end_lineno=1, end_col_offset=4))
        elif mode == 'single':
            ast = Interactive(body=[])
        else:
            raise ValueError(f"invalid mode '{mode}'")

        return FST(ast, lines=[bistr('')], parse_params=parse_params)

    @staticmethod
    def fromsrc(source: str | bytes | list[str], filename: str = '<unknown>', mode: str = 'exec', *,
                type_comments: bool = False, feature_version: tuple[int, int] | None = None) -> 'FST':
        """Parse and create a new `FST` tree from source, preserving the original source and locations.

        **Parameters:**
        - `source`: The source to parse as a single `str`, `bytes` or list of individual line strings (without
            newlines).
        - `filename`: `ast.parse()` parameter.
        - `mode`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.

        **Returns:**
        - `FST`: The parsed tree with `.f` attributes added to each `AST` node for `FST` access.
        """

        if isinstance(source, bytes):
            source = source.decode()

        if isinstance(source, str):
            lines  = source.split('\n')

        else:
            lines  = source
            source = '\n'.join(lines)

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)
        ast          = ast_parse(source, mode=mode, **parse_params)

        return FST(ast, lines=[bistr(s) for s in lines], parse_params=parse_params)  # not just convert to bistr but to make a copy at the same time

    @staticmethod
    def fromast(ast: AST, filename: str = '<unknown>', mode: str | None = None, *,
                type_comments: bool | None = False, feature_version=None,
                calc_loc: bool | Literal['copy'] = True) -> 'FST':
        """Add `FST` to existing `AST` tree, optionally copying positions from reparsed `AST` (default) or whole `AST`
        for new `FST`.

        WARNING! Do not set `calc_loc` to `False` unless you parsed the `AST` from a previous output of `ast.unparse()`,
        otherwise there will almost certainly be problems!

        **Parameters:**
        - `ast`: The root `AST` node.
        - `filename`: `ast.parse()` parameter.
        - `mode`: `ast.parse()` parameter. Can be `exec`, `eval, `single` or `None`, in which case the appropriate mode
            is determined from the structure of the tree itself.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.
        - `calc_loc`: Get actual node positions by unparsing then parsing again. Use when you are not certain node
            positions are correct or even present. Updates original `AST` unless set to "copy", in which case a copied
            `AST` is used. Set to `False` when you know positions are correct and want to use given `AST`

        **Returns:**
        - `FST`: The augmented tree with `.f` attributes added to each `AST` node for `FST` access.
        """

        src   = ast_unparse(ast)
        lines = src.split('\n')


        # TODO: unparenthesize unnecessarily parenthesized expressions (NamedExpr, Yield, YieldFrom)?


        if type_comments is None:
            type_comments = has_type_comments(ast)

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)

        if calc_loc:
            astp = ast_parse(src, mode=get_parse_mode(ast) or 'exec' if mode is None else mode, **parse_params)

            if astp.__class__ is not ast.__class__:
                astp = astp.body if isinstance(astp, Expression) else astp.body[0]

                if astp.__class__ is not ast.__class__:
                    raise RuntimeError('could not reproduce ast')

            if calc_loc == 'copy':
                if not compare_asts(astp, ast, type_comments=type_comments, raise_=False):
                    raise RuntimeError('could not reparse ast identically')

                ast = astp

            elif not copy_attributes(astp, ast, compare=True, type_comments=type_comments, raise_=False):
                raise RuntimeError('could not reparse ast identically')

        return FST(ast, lines=[bistr(s) for s in lines], parse_params=parse_params)

    @staticmethod
    def get_option(option: str, options: dict[str, Any]) -> Any:
        """Get option from options dict or default if option not in dict or is `None` there.

        **Parameters:**
        - `option`: Name of option to get.
        - `options`: Dictionary which may or may not contain the requested option.

        **Returns:**
        - `Any`: Default option of if not found in `options` else that option.
        """

        return FST.OPTIONS.get(option) if (o := options.get(option)) is None else o

    @staticmethod
    def set_options(**options) -> dict[str, Any]:
        """Set defaults for `options` parameters.

        **Parameters:**
        - `options`: Key / values of parameters to set.

        **Returns:**
        - `options`: `dict` of previous values of changed parameters, reset with `set_options(**options)`.
        """

        fstopts = FST.OPTIONS
        ret     = {o: fstopts[o] for o in options}

        fstopts.update(options)

        return ret

    def dump(self, compact: bool = False, full: bool = False, *, indent: int = 2, out: Callable | TextIO = print,
             eol: str | None = None) -> list[str] | None:
        """Dump a representation of the tree to stdout or return as a list of lines.

        **Parameters:**
        - `compact`: If `True` then the dump is compacted a bit by listing `Name` and `Constant` nodes on a single
            line.
        - `full`: If `True` then will list all fields in nodes including empty ones, otherwise will exclude most empty
            fields.
        - `indent`: The average airspeed of an unladen swallow.
        - `out`: `print` means print to stdout, `list` returns a list of lines and `str` returns a whole string.
            Otherwise a `Callable[[str], None]` which is called for each line of output individually.
        - 'eol': What to put at the end of each text line, `None` means newline for `TextIO` out and nothing for other.
        """

        if isinstance(out, TextIOBase):
            out = out.write

            if eol is None:
                eol = '\n'

        elif eol is None:
            eol = ''

        if out in (str, list):
            lines = []

            self._dump(full, indent, linefunc=lines.append, compact=compact, eol=eol)

            return lines if out is list else '\n'.join(lines)

        return self._dump(full, indent, linefunc=out, compact=compact, eol=eol)

    def verify(self, raise_: bool = True) -> Optional['FST']:  # -> Self | None:
        """Sanity check, reparse source and make sure parsed tree matches currently stored tree (locations and
        everything).

        **Parameters:**
        - `raise_`: Whether to raise an exception on verify failed or return `None`.

        **Returns:**
        - `None` on failure to verify (if not `raise_`), otherwise `self`.
        """

        if not self.is_root:
            raise RuntimeError('can only be called on root node')

        ast          = self.a
        parse_params = self.parse_params

        try:
            astp = ast_parse(self.src, mode=get_parse_mode(ast) or 'exec', **parse_params)

        except SyntaxError:
            if raise_:
                raise

            return None

        if not isinstance(ast, mod):
            if isinstance(astp, Expression):
                astp = astp.body
            elif len(astp.body) == 1:
                astp = astp.body[0]
            elif raise_:
                raise ValueError('verify failed reparse')
            else:
                return None

        if not compare_asts(astp, ast, locs=True, type_comments=parse_params['type_comments'], raise_=raise_):
            return None

        return self

    # ------------------------------------------------------------------------------------------------------------------

    def copy(self, **options) -> 'FST':
        """Copy an individual node to a top level tree, dedenting and fixing as necessary."""

        fix    = FST.get_option('fix', options)
        ast    = self.a
        newast = copy_ast(ast)

        if self.is_root:
            return FST(newast, lines=self._lines[:], from_=self)

        if isinstance(ast, STATEMENTISH):
            loc = self.comms(options.get('precomms'), options.get('postcomms'))
        elif isinstance(ast, PARENTHESIZABLE):
            loc = self.pars((DEFAULT_PARS if (o := options.get('pars')) is None else o) is True)
        else:
            loc = self.bloc

        if not loc:
            raise ValueError('cannot copy node which does not have location')

        fst = self._make_fst_and_dedent(self, newast, loc, docstr=options.get('docstr'))

        return fst._fix(inplace=True) if fix else fst

    def cut(self, **options) -> 'FST':
        """Cut out an individual node to a top level tree (if possible), dedenting and fixing as necessary."""

        if self.is_root:
            raise ValueError('cannot cut root node')

        ast        = self.a
        parent     = self.parent
        field, idx = self.pfield
        parenta    = parent.a

        if isinstance(ast, STATEMENTISH):
            return parent._get_slice_stmtish(idx, idx + 1, field, cut=True, one=True, **options)

        if isinstance(parenta, (Tuple, List, Set)):
            fst = self.copy(**options)

            parent._put_slice_tuple_list_or_set(None, idx, idx + 1, field, False, **options)

            return fst


        # TODO: individual nodes
        # TODO: other sequences?


        raise ValueError(f"cannot cut from a {parenta.__class__.__name__}.{field}")

    def replace(self, code: Code | None, **options) -> Optional['FST']:  # -> Self (replaced) or None if deleted
        """Replace or delete (`code=None`) an individual node. Returns the new node for `self`, not the old replaced
        node, or `None` if was deleted or raw replaced and old node disappeared.
        """

        if not (parent := self.parent):
            raise ValueError('cannot replace root node')

        return parent._put_one(code, (pf := self.pfield).idx, pf.name, **options)

    def get(self, start: int | Literal['end'] | None = None, stop: int | None | Literal[False] = False,
            field: str | None = None, *, cut: bool = False, **options) -> Optional['FST']:
        """Copy or cut an individual child node or a slice of child nodes from `self`."""

        ast     = self.a
        _, body = _fixup_field_body(ast, field, False)

        if not isinstance(body, list):  # get from individual field
            if stop is not False or start is not None:
                raise IndexError(f"cannot pass index for non-slice get() to {ast.__class__.__name__}" +
                                 f".{field}" if field else "")

            raise NotImplementedError


            # TODO: get single-field non-indexed stuff


        if stop is not False:
            return self.get_slice(start, stop, field, cut=cut, **options)
        elif start is None:
            return self.get_slice(None, None, field, cut=cut, **options)

        if cut:
            return body[start].f.cut(**options)
        else:
            return body[start].f.copy(**options)

    def put(self, code: Code | None, start: int | Literal['end'] | None = None,
            stop: int | None | Literal[False] = False, field: str | None = None, *,
            one: bool = True, **options) -> 'FST':  # -> Self
        """Put an individual child node or a slice of child nodes to `self`.

        WARNING! If the `code` being put is an `AST` or `FST` then it is consumed and should be considered invalid after
        this call, whether it succeeds or fails.
        """

        ast          = self.a
        field_, body = _fixup_field_body(ast, field, False)

        if not isinstance(body, list):  # put to individual field
            if stop is not False or start is not None:
                raise IndexError(f"cannot pass index for non-slice put() to {ast.__class__.__name__}" +
                                 f".{field}" if field else "")

            self._put_one(code, start, field_, **options)

            return self.repath()

        if stop is not False:
            return self.put_slice(code, start, stop, field, one=one, **options)
        if start is None:
            return self.put_slice(code, None, None, field, one=one, **options)

        if start == 'end':
            raise IndexError(f"cannot put() non-slice to index 'end'")
        if not one:
            raise ValueError(f"cannot use 'one=False' in non-slice put()")

        is_dict = isinstance(ast, Dict)

        if field is None:  # maybe putting to special case field?
            if is_dict or isinstance(ast, MatchMapping):
                if not FST.get_option('raw', options):
                    raise ValueError(f"cannot put() non-raw without field to {ast.__class__.__name__}")

                key = key.f if (key := ast.keys[start]) else self._dict_key_or_mock_loc(key, ast.values[start].f)
                end = (ast.values if is_dict else ast.patterns)[start].f

                self._reparse_raw_loc(code, key.ln, key.col, end.end_ln, end.end_col)

                return self.repath()

            if isinstance(ast, Compare):
                if start < 0:  # need to do this because of compound body including 'left'
                    start += len(ast.comparators) + 1

                    if start < 0:
                        raise IndexError('invalid index')

                field_, start = ('comparators', start - 1) if start else ('left', None)

        if is_dict and field == 'keys' and (keys := ast.keys)[start] is None:  # '{**d}' with key=None
            if not FST.get_option('raw', options):
                raise ValueError(f"cannot put() non-raw to ** Dict.key")

            start_loc = self._dict_key_or_mock_loc(keys[start], ast.values[start].f)

            ln, col, end_ln, end_col = start_loc.loc if start_loc.is_FST else start_loc

            self.put_src([': '], ln, col, end_ln, end_col)
            self._reparse_raw_loc(code, ln, col, ln, col)

        else:
            self._put_one(code, start, field_, **options)

        return self.repath()

    def get_slice(self, start: int | Literal['end'] | None = None, stop: int | None = None, field: str | None = None, *,
                  cut: bool = False, **options) -> 'FST':
        """Get a slice of child nodes from `self`."""

        ast       = self.a
        field_, _ = _fixup_field_body(ast, field)

        if isinstance(ast, STATEMENTISH_OR_STMTMOD):
            if field_ in STATEMENTISH_FIELDS:
                return self._get_slice_stmtish(start, stop, field, cut, **options)

        elif isinstance(ast, (Tuple, List, Set)):
            return self._get_slice_tuple_list_or_set(start, stop, field, cut, **options)

        elif isinstance(ast, Dict):
            return self._get_slice_dict(start, stop, field, cut, **options)

        elif self.is_empty_set_call() or self.is_empty_set_seq():
            return self._get_slice_empty_set(start, stop, field, cut, **options)


        # TODO: more individual specialized slice gets


        raise ValueError(f"cannot get slice from a '{ast.__class__.__name__}'")

    def put_slice(self, code: Code | None, start: int | Literal['end'] | None = None, stop: int | None = None,
                  field: str | None = None, *, one: bool = False, **options) -> 'FST':  # -> Self
        """Put an a slice of child nodes to `self`.

        If the `code` being put is an `AST` or `FST` then it is consumed and should not be considered valid after this
        call whether it succeeds or fails.

        Can reparse.
        """

        ast       = self.a
        field_, _ = _fixup_field_body(ast, field)
        raw       = FST.get_option('raw', options)

        if raw is not True:
            if raw and raw != 'auto':
                raise ValueError(f"invalid value '{raw}' for raw parameter")

            try:
                if isinstance(ast, STATEMENTISH_OR_STMTMOD):
                    if field_ in STATEMENTISH_FIELDS:
                        self._put_slice_stmtish(code, start, stop, field, one, **options)

                        return self

                elif isinstance(ast, (Tuple, List, Set)):
                    self._put_slice_tuple_list_or_set(code, start, stop, field, one, **options)

                    return self

                elif isinstance(ast, Dict):
                    self._put_slice_dict(code, start, stop, field, one, **options)

                    return self

                elif self.is_empty_set_call() or self.is_empty_set_seq():
                    self._put_slice_empty_set(code, start, stop, field, one, **options)

                    return self


                # TODO: more individual specialized slice puts


            except (SyntaxError, NodeTypeError):
                if not raw:
                    raise

            else:
                if not raw:
                    raise ValueError(f"cannot put slice to a '{ast.__class__.__name__}'")

        return self._put_slice_raw(code, start, stop, field, one=one, **options)

    def put_raw(self, code: Code | None, ln: int, col: int, end_ln: int, end_col: int, *,
                exact: bool | None = True, **options) -> Optional['FST']:
        """Put raw code and reparse. Can call on any node in tree for same effect.

        **Returns:**
        - `FST | None`: FIRST highest level node contained entirely within replacement source location (there may be
            others following), or `None` or if no such candidate and `exact=None`. If no candidate and `exact` is `True`
            or `False` then will attempt to return a node which encloses the location using `find_loc(..., exact)`.
        """

        parent = self.root.find_loc(ln, col, end_ln, end_col, False) or self.root

        return parent._reparse_raw_loc(code, ln, col, end_ln, end_col, exact)

    def get_src(self, ln: int, col: int, end_ln: int, end_col: int, as_lines: bool = False) -> str | list[str]:
        """Get source at location, without dedenting or any other modification, Returned as a string or individual
        lines. The first and last lines are cropped to start `col` and `end_col`. Can call on any node in tree for same
        effect.

        **Returns:**
        - `str | list[str]`: A single string or a list of lines if `as_lines=True`.
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

    def put_src(self, src: str | list[str] | None, ln: int, col: int, end_ln: int, end_col: int,
                tail: bool | None = ..., head: bool | None = True, exclude: Optional['FST'] = None, *,
                offset_excluded: bool = True) -> tuple[int, int, int, int] | None:
        """Put or delete new source to currently stored source, optionally offsetting all nodes for the change. Must
        specify `tail` as `True`, `False` or `None` to enable offset of nodes according to source put. `...` ellipsis
        value is used as sentinel for `tail` to mean don't offset. Otherwise `tail` and params which followed are passed
        to `self.offset()` with calculated offset location and deltas.

        **Returns:**
        - `(ln: int, col: int, dln: int, dcol_offset: int) | None`: If `tail` was not `...` then the calculated
            `offset()` parameters are returned for any potential followup offsetting. The `col` parameter in this case
            is returned as a byte offset so that `offset()` doesn't attempt to calculate it from already modified
            source."""

        ret = None
        ls  = self.root._lines

        if is_del := src is None:
            lines = [bistr('')]
        elif isinstance(src, str):
            lines = [bistr(s) for s in src.split('\n')]
        elif not src[0].__class__ is bistr:  # lines is list[str]
            lines = [bistr(s) for s in src]
        else:
            lines = src

        if tail is not ...:  # possibly offset nodes
            ret = _params_offset(ls, lines, ln, col, end_ln, end_col)

            self.root.offset(*ret, tail, head, exclude, offset_excluded=offset_excluded)

        if is_del:  # delete lines
            if end_ln == ln:
                ls[ln] = bistr((l := ls[ln])[:col] + l[end_col:])

            else:
                ls[end_ln] = bistr(ls[ln][:col] + ls[end_ln][end_col:])

                del ls[ln : end_ln]

        else:  # put lines
            dln = end_ln - ln

            if (nnew_ln := len(lines)) <= 1:
                s = lines[0] if nnew_ln else ''

                if not dln:  # replace single line with single or no line
                    ls[ln] = bistr(f'{(l := ls[ln])[:col]}{s}{l[end_col:]}')

                else:  # replace multiple lines with single or no line
                    ls[ln] = bistr(f'{ls[ln][:col]}{s}{ls[end_ln][end_col:]}')

                    del ls[ln + 1 : end_ln + 1]

            elif not dln:  # replace single line with multiple lines
                lend                 = bistr(lines[-1] + (l := ls[ln])[end_col:])
                ls[ln]               = bistr(l[:col] + lines[0])
                ls[ln + 1 : ln + 1]  = lines[1:]
                ls[ln + nnew_ln - 1] = lend

            else:  # replace multiple lines with multiple lines
                ls[ln]              = bistr(ls[ln][:col] + lines[0])
                ls[end_ln]          = bistr(lines[-1] + ls[end_ln][end_col:])
                ls[ln + 1 : end_ln] = lines[1:-1]

        return ret

# ------------------------------------------------------------------------------------------------------------------

    def parent_stmt(self, self_: bool = False, mod: bool = True) -> Optional['FST']:
        """The first parent which is a `stmt` or `mod` node (if any). If `self_` is `True` then will check `self` first,
        otherwise only checks parents."""

        types = (stmt, ast_.mod) if mod else stmt

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_stmtish(self, self_: bool = False, mod: bool = True) -> Optional['FST']:
        """The first parent which is a `stmt`, `ExceptHandler`, `match_case` or `mod` node (if any). If `self_` is
        `True` then will check `self` first, otherwise only checks parents."""

        types = STATEMENTISH_OR_MOD if mod else STATEMENTISH

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_block(self, self_: bool = False, mod: bool = True) -> Optional['FST']:
        """The first parent which opens a block that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `For`, `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`,
        `TryStar`, `ExceptHandler`, `match_case` or `mod`. If `self_` is `True` then will check `self` first, otherwise
        only checks parents."""

        types = BLOCK_OR_MOD if mod else BLOCK

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_scope(self, self_: bool = False, mod: bool = True) -> Optional['FST']:
        """The first parent which opens a scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `Lambda`, `ListComp`, `SetComp`, `DictComp`, `GeneratorExp` or `mod`. If `self_`
        is `True` then will check `self` first, otherwise only checks parents."""

        types = SCOPE_OR_MOD if mod else SCOPE

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def parent_named_scope(self, self_: bool = False, mod: bool = True) -> Optional['FST']:
        """The first parent which opens a named scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef` or `mod`. If `self_` is `True` then will check `self` first, otherwise only
        checks parents."""

        types = NAMED_SCOPE_OR_MOD if mod else NAMED_SCOPE

        if self_ and isinstance(self.a, types):
            return self

        while (self := self.parent) and not isinstance(self.a, types):
            pass

        return self

    def next(self, with_loc: bool | Literal['all', 'own'] = True) -> Optional['FST']:  # TODO: refactor maybe
        """Get next sibling in syntactic order, only within parent.

        **Parameters:**
        - `with_loc`: If `True` then only non-operator nodes with locations, `'all'` means all nodes with locations,
            `'own'` means only nodes with own location, otherwise all nodes.

        **Returns:**
        - `None` if last valid sibling in parent, otherwise next node.
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

                    if _with_loc(f := a.f, with_loc):
                        return f

            elif idx is not None:
                sibling = getattr(aparent, name)

                while True:
                    try:
                        if not (a := sibling[(idx := idx + 1)]):  # who knows where a `None` might pop up "next" these days... xD
                            continue

                    except IndexError:
                        break

                    if _with_loc(f := a.f, with_loc):
                        return f

            while next is not None:
                if isinstance(next, str):
                    name = next

                    if isinstance(sibling := getattr(aparent, next, None), AST):  # None because we know about fields from future python versions
                        if _with_loc(f := sibling.f, with_loc):
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

    def prev(self, with_loc: bool | Literal['all', 'own'] = True) -> Optional['FST']:  # TODO: refactor maybe
        """Get previous sibling in syntactic order, only within parent.

        **Parameters:**
        - `with_loc`: If `True` then only non-operator nodes with locations, `'all'` means all nodes with locations,
            `'own'` means only nodes with own location, otherwise all nodes.

        **Returns:**
        - `None` if first valid sibling in parent, otherwise previous node.
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

                    if _with_loc(f := a.f, with_loc):
                        return f

            else:
                sibling = getattr(aparent, name)

                while idx:
                    if not (a := sibling[(idx := idx - 1)]):
                        continue

                    if _with_loc(f := a.f, with_loc):
                        return f

            while prev is not None:
                if isinstance(prev, str):
                    name = prev

                    if isinstance(sibling := getattr(aparent, prev, None), AST):  # None because could have fields from future python versions
                        if _with_loc(f := sibling.f, with_loc):
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

    def first_child(self, with_loc: bool | Literal['all', 'own'] = True) -> Optional['FST']:
        """Get first valid child in syntactic order.

        **Parameters:**
        - `with_loc`: If `True` then only non-operator nodes with locations, `'all'` means all nodes with locations,
            `'own'` means only nodes with own location, otherwise all nodes.

        **Returns:**
        - `None` if no valid children, otherwise first valid child.
        """

        for name in AST_FIELDS[(a := self.a).__class__]:
            if (child := getattr(a, name, None)):
                if isinstance(child, AST):
                    if _with_loc(f := child.f, with_loc):
                        return f

                elif isinstance(child, list):
                    if (c := child[0]) and _with_loc(f := c.f, with_loc):
                        return f

                    return FST(Pass(), self, astfield(name, 0)).next(with_loc)  # Pass() is a hack just to have a simple AST node

        return None

    def last_child(self, with_loc: bool | Literal['all', 'own'] = True) -> Optional['FST']:
        """Get last valid child in syntactic order.

        **Parameters:**
        - `with_loc`: If `True` then only non-operator nodes with locations, `'all'` means all nodes with locations,
            `'own'` means only nodes with own location, otherwise all nodes.

        **Returns:**
        - `None` if no valid children, otherwise last valid child.
        """

        if (isinstance(a := self.a, Call)) and a.args and (keywords := a.keywords) and isinstance(a.args[-1], Starred):  # super-special case Call with args and keywords and a Starred, it could be anywhere in there, including after last keyword, defer to prev() logic
            fst          = FST(f := Pass(), self, astfield('keywords', len(keywords)))
            f.lineno     = 0x7fffffffffffffff
            f.col_offset = 0

            return fst.prev(with_loc)

        for name in reversed(AST_FIELDS[(a := self.a).__class__]):
            if (child := getattr(a, name, None)):
                if isinstance(child, AST):
                    if _with_loc(f := child.f, with_loc):
                        return f

                elif isinstance(child, list):
                    if (c := child[-1]) and _with_loc(f := c.f, with_loc):
                        return f

                    return FST(Pass(), self, astfield(name, len(child) - 1)).prev(with_loc)  # Pass() is a hack just to have a simple AST node

        return None

    def next_child(self, from_child: Optional['FST'], with_loc: bool | Literal['all', 'own'] = True
                   ) -> Optional['FST']:
        """Get next child in syntactic order. Meant for simple iteration. This is a slower way to iterate, `walk()` is
        faster.

        **Parameters:**
        - `from_child`: Child node we are coming from which may or may not have location.
        - `with_loc`: If `True` then only non-operator nodes with locations, `'all'` means all nodes with locations,
            `'own'` means only nodes with own location, otherwise all nodes.

        **Returns:**
        - `None` if last valid child in `self`, otherwise next child node.
        """

        return self.first_child(with_loc) if from_child is None else from_child.next(with_loc)

    def prev_child(self, from_child: Optional['FST'], with_loc: bool | Literal['all', 'own'] = True
                   ) -> Optional['FST']:
        """Get previous child in syntactic order. Meant for simple iteration. This is a slower way to iterate, `walk()`
        is faster.

        **Parameters:**
        - `from_child`: Child node we are coming from which may or may not have location.
        - `with_loc`: If `True` then only non-operator nodes with locations, `'all'` means all nodes with locations,
            `'own'` means only nodes with own location, otherwise all nodes.

        **Returns:**
        - `None` if first valid child in `self`, otherwise previous child node.
        """

        return self.last_child(with_loc) if from_child is None else from_child.prev(with_loc)

    def next_step(self, with_loc: bool | Literal['all', 'own', 'allown'] = True, *,
                  recurse_self: bool = True) -> Optional['FST']:
        """Get next node in syntactic order over entire tree. Will walk up parents and down children to get the next
        node, returning `None` only when we are at the end of the whole thing.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'all'` means all nodes with locations, `'own'`
            means only nodes with own location (does not recurse into non-own nodes), `'allown'` means return `'own'`
            nodes but recurse into nodes with non-own locations. Otherwise `False` means all nodes.
        - `recurse_self`: Whether to allow recursion of `self` to return children or move directly to next nodes.

        **Returns:**
        - `None` if last valid node in tree, otherwise next node in order.
        """

        if allown := with_loc == 'allown':
            with_loc = True

        while True:
            if not recurse_self or not (fst := self.first_child(with_loc)):
                recurse_self = True

                while not (fst := self.next(with_loc)):
                    if not (self := self.parent):
                        return None

            if not allown or fst.has_own_loc:
                break

            self = fst

        return fst

    def prev_step(self, with_loc: bool | Literal['all', 'own', 'allown'] = True, *,
                  recurse_self: bool = True) -> Optional['FST']:
        """Get prev node in syntactic order over entire tree. Will walk up parents and down children to get the next
        node, returning `None` only when we are at the beginning of the whole thing.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'all'` means all nodes with locations, `'own'`
            means only nodes with own location (does not recurse into non-own nodes), `'allown'` means return `'own'`
            nodes but recurse into nodes with non-own locations. Otherwise `False` means all nodes.
        - `recurse_self`: Whether to allow recursion of `self` to return children or move directly to prev nodes.

        **Returns:**
        - `None` if first valid node in tree, otherwise prev node in order.
        """

        if allown := with_loc == 'allown':
            with_loc = True

        while True:
            if not recurse_self or not (fst := self.last_child(with_loc)):
                recurse_self = True

                while not (fst := self.prev(with_loc)):
                    if not (self := self.parent):
                        return None

            if not allown or fst.has_own_loc:
                break

            self = fst

        return fst

    def walk(self, with_loc: bool | Literal['all', 'own'] = False, *, self_: bool = True,
             recurse: bool = True, scope: bool = False, back: bool = False) -> Generator['FST', bool, None]:
        """Walk self and descendants in syntactic order, `send(False)` to skip recursion into child. `send(True)` to
        allow recursion into child if called with `recurse=False` or `scope=True` would otherwise disallow it. Can send
        multiple times, last value sent takes effect.

        The walk is defined forwards or backwards in that it returns a parent then recurses into the children and walks
        those in the given direction, recursing into each child's children before continuing with siblings. Walking
        backwards will not generate the same sequence as `list(walk())[::-1]` due to this behavior.

        Walked nodes can be modified or replaced as long as their parent is not changed.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'all'` means all nodes with locations, `'own'`
            means only nodes with own location (does not recurse into non-own nodes), otherwise `False` means all nodes.
        - `self_`: If `True` then self will be returned first with the possibility to skip children with `send()`.
        - `recurse`: Whether to recurse into children by default, `send()` for a given node will always override this.
            Will always attempt first level of children unless walking self and `False` is sent first.
        - `scope`: If `True` then will walk only within the scope of `self`. Meaning if called on a `FunctionDef` then
            will only walk children which are within the function scope. Will yield children which have with their own
            scopes, and the parts of them which are visible in this scope (like default argument values), but will not
            recurse into them unless `send(True)` is done for that child.
        - `back`: If `True` then walk every node in reverse syntactic order. This is not the same as a full forwards
            walk reversed due to recursion (parents are still returned before children, only in reverse sibling order).

        **Example:**
        ```py
        for node in (walking := target.walk()):
            ...
            if i_dont_like_the_node:
                walking.send(False)  # skip walking this node's children, don't use return value here, keep using for loop as normal
        ```
        """

        if self_:
            if not _with_loc(self, with_loc):
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

            fst = ast.f

            if not _with_loc(fst, with_loc):
                continue

            recurse_ = recurse

            while (sent := (yield fst)) is not None:
                recurse_ = 1 if sent else False

            if not fst.a:  # has been changed by the player
                fst = fst.repath()

            ast = fst.a  # could have just modified the ast

            if recurse_ is not True:
                if recurse_:  # user did send(True), walk this child unconditionally
                    yield from fst.walk(with_loc, self_=False, back=back)

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
                        gen             = fst.walk(with_loc, self_=False, back=back)

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

    def child_path(self, child: 'FST', as_str: bool = False) -> list[astfield] | str:
        """Get path to `child` node from `self` which can later be used on a copy of this tree to get to the same
        relative child node.

        **Parameters:**
        - `child`: Child node to get path to.
        - `as_str`: If `True` will return the path as a python-ish string, else a list of `astfield`s which can be used
            more directly.

        **Returns:**
        - `list[astfield] | str`: Path to child if exists, otherwise raises.
        """

        path = []

        while child is not self:
            path.append(child.pfield)

            if not (child := child.parent):
                raise ValueError('invalid child')

        path.reverse()

        return path if not as_str else '.'.join(af.name if (i := af.idx) is None else f'{af.name}[{i}]' for af in path)

    def child_from_path(self, path: list[astfield] | str, last_valid: bool = False) -> 'FST':
        """Get child node specified by `path` if it exists. If succeeds then the child node is not guaranteed to be the
        same type as was originally used to get the path, just the path is valid.

        **Parameters:**
        - `path`: Path to child as a list of `astfield`s or string.
        - `last_valid`: If `True` then return the last valid node along the path, will not fail, can return `self`.

        **Returns:**
        - `FST`: Child node if path is valid, otherwise `False` if path invalid.
        """

        if isinstance(path, str):
            path = [astfield(p[:i], int(p[i + 1 : -1])) if (i := p.find('[')) != -1 else astfield(p)
                    for p in path.split('.')]

        for p in path:
            if (next := p.get_no_raise(self)) is False:
                return self if last_valid else False

            self = next

        return self

    def repath(self) -> 'FST':
        """Recalculate `self` from path from root. Useful if `self` has been replaced by another node by some operation.

        **Returns:**
        - `FST`: Possibly `self` or the node which took our place at our position from `root`."""

        return (root := self.root).child_from_path(root.child_path(self))

    def find_loc(self, ln: int, col: int, end_ln: int, end_col: int, exact: bool = True) -> Optional['FST']:
        """Find lowest level node which entirely contains location (starting search at `self`).

        **Parameters:**
        - `exact`: Whether to allow return of exact location match with node or not. `True` means allow return of node
            which matches location exactly. Otherwise the location must be inside the node but cannot be touching BOTH
            ends of the node. This basically determines whether you can get the exact node of the location or its
            parent.
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

    def find_in_loc(self, ln: int, col: int, end_ln: int, end_col: int) -> Optional['FST']:
        """Find highest level first node which is contained entirely in location (inclusive, starting search at
        `self`)."""

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

    def is_parsable(self) -> bool:
        """Really means the AST is `unparse()`able and then re`parse()`able which will get it to this top level AST node
        surrounded by the appropriate `ast.mod`. The source may change a bit though, parentheses, 'if' <-> 'elif'."""

        if not is_parsable(self.a) or not self.loc:
            return False

        ast    = self.a
        parent = self.parent

        if isinstance(ast, Tuple):  # tuple of slices used in indexing (like numpy)
            for e in ast.elts:
                if isinstance(e, Slice):
                    return False

        elif parent:
            if isinstance(ast, (JoinedStr, TemplateStr)):  # formatspec '.1f' type strings without quote delimiters
                if self.pfield.name == 'format_spec' and isinstance(parent.a, (FormattedValue, Interpolation)):
                    return False

            elif isinstance(ast, Constant):  # string parts of f-string without quote delimiters
                if (self.pfield.name == 'values' and isinstance(parent.a, (JoinedStr, TemplateStr)) and
                    isinstance(ast.value, str)
                ):
                    return False

        return True

    def is_atom(self) -> bool:
        """Whether `self` is enclosed in some kind of delimiters '()', '[]', '{}' or otherwise atomic like `Name`,
        `Constant`, etc... Node types where this doesn't normally apply like `stmt` will return `True`.

        **Returns:**
        - `True` if is enclosed and no combination with another node can change its precedence, `False` otherwise.
        """

        ast = self.a

        if isinstance(ast, (Dict, Set, ListComp, SetComp, DictComp, GeneratorExp, Constant, Attribute, Subscript, Name,  # , Await
                            List, MatchValue, MatchSingleton, MatchMapping, MatchClass, MatchStar, MatchAs)):
            return True

        if isinstance(ast, Tuple):
            if self._is_parenthesized_seq():  # if this is False, can still be enclosed in grouping parens which is checked below
                return True

        elif isinstance(ast, MatchSequence):  # could be enclosed with '()' or '[]' which is included in the ast location
            ln, col, _, _ = self.loc
            lpar          = self.root._lines[ln][col]

            if lpar == '(':
                if self._is_parenthesized_seq('patterns'):
                    return True

            elif lpar == '[':
                if self._is_parenthesized_seq('patterns', '[', ']'):
                    return True

        if isinstance(ast, (expr, pattern)):  # , alias, withitem
            return bool(self.pars(ret_npars=True)[1])

        return True

    def is_parenthesized_tuple(self) -> bool | None:
        """Whether `self` is a parenthesized `Tuple` or not, or not a `Tuple` at all.

        **Returns:**
        - `True` if is parenthesized `Tuple`, `False` if is unparenthesized `Tuple`, `None` if is not `Tuple`.
        """

        return self._is_parenthesized_seq() if isinstance(self.a, Tuple) else None

    def is_empty_set_call(self) -> bool:
        """Whether `self` is an empty `set()` call."""

        return (isinstance(ast := self.a, Call) and not ast.args and not ast.keywords and
                isinstance(func := ast.func, Name) and func.id == 'set' and isinstance(func.ctx, Load))

    def is_empty_set_seq(self) -> bool:
        """Whether `self` is an empty Set from an empty sequence, recognized are `{*()}`, `{*[]}` and `{*{}}`."""

        return (isinstance(ast := self.a, Set) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and
                ((isinstance(v := e0.value, (Tuple, List)) and not v.elts) or (isinstance(v, Dict) and not v.keys)))

    def is_elif(self) -> bool:
        """Whether `self` is an `elif`."""

        return isinstance(self.a, If) and self.root._lines[(loc := self.loc).ln].startswith('elif', loc.col)

    def is_solo_call_arg(self) -> bool:
        """Whether `self` is a solo Call non-keyword argument."""

        return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(parenta := parent.a, Call) and
                not parenta.keywords and len(parenta.args) == 1)

    def is_solo_call_arg_genexpr(self) -> bool:
        """Whether `self` is the dreaded solo call non-keyword argument generator expression in `sum(i for i in a)`.
        Doesn't say it shares parentheses or not, so could still be `sum((i for i in a))` or even
        `sum(((i for i in a)))`."""

        return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(self.a, GeneratorExp) and
                isinstance(parenta := parent.a, Call) and not parenta.keywords and len(parenta.args) == 1)

    def get_indent(self) -> str:
        """Determine proper indentation of node at `stmt` (or other similar) level at or above `self`. Even if it is a
        continuation or on same line as block statement. If indentation is impossible to determine because is solo
        statement on same line as parent block and cannot get from other block fields then the current tree default
        indentation is added to the parent block indentation and returned.

        **Returns:**
        - `str`: Entire indentation string for the block this node lives in (not just a single level).
        """

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
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

    def get_indentable_lns(self, skip: int = 0, *, docstr: bool | Literal['strict'] | None = None) -> set[int]:
        """Get set of indentable lines within this node.

        **Parameters:**
        - `skip`: The number of lines to skip from the start of this node. Useful for skipping the first line for edit
            operations (since the first line is normally joined to an existing line on add or copied directly from start
            on cut).
        - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
            multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
            in expected docstring positions are indentable. `None` means use default.

        **Returns:**
        - `set[int]`: Set of line numbers (zero based) which are sytactically indentable.
        """

        def walk_multiline(cur_ln, end_ln, m, re_str_end):
            nonlocal lns, lines

            col = m.end()

            for ln in range(cur_ln, end_ln + 1):
                if m := re_str_end.match(lines[ln], col):
                    break

                col = 0

            else:
                raise RuntimeError('should not get here')

            lns -= set(range(cur_ln + 1, ln + 1))  # specifically leave out first line of multiline string because that is indentable

            return ln, m.end()

        def multiline_str(f: 'FST'):
            nonlocal lns, lines

            cur_ln, cur_col, end_ln, end_col = f.loc

            while True:
                if not (m := re_multiline_str_start.match(l := lines[cur_ln], cur_col)):
                    if m := re_oneline_str.match(l, cur_col):
                        cur_col = m.end()

                    else:  # UGH! a line continuation string, pffft...
                        m               = re_contline_str_start.match(l, cur_col)
                        re_str_end      = re_contline_str_end_sq if m.group(1) == "'" else re_contline_str_end_dq
                        cur_ln, cur_col = walk_multiline(cur_ln, end_ln, m, re_str_end)  # find end of multiline line continuation string

                else:
                    re_str_end      = re_multiline_str_end_sq if m.group(1) == "'''" else re_multiline_str_end_dq
                    cur_ln, cur_col = walk_multiline(cur_ln, end_ln, m, re_str_end)  # find end of multiline string

                if cur_ln == end_ln and cur_col == end_col:
                    break

                cur_ln, cur_col, _ = _next_src(lines, cur_ln, cur_col, end_ln, end_col)  # there must be a next one

        def multiline_fstr(f: 'FST'):  # TODO: p3.12+ has locations for there, might make it easier
            """Lets try to find indentable lines by incrementally attempting to parse parts of multiline f-string."""

            nonlocal lns, lines

            cur_ln, cur_col, end_ln, _ = f.loc

            while True:
                ls = [lines[cur_ln][cur_col:].lstrip()]

                for ln in range(cur_ln + 1, end_ln + 1):
                    try:
                        ast_parse('\n'.join(ls))

                    except SyntaxError:
                        lns.remove(ln)
                        ls.append(lines[ln])

                    else:
                        break

                if (cur_ln := ln) >= end_ln:
                    assert cur_ln == end_ln

                    break

                cur_col = 0

        if docstr is None:
            docstr = DEFAULT_DOCSTR

        strict = docstr == 'strict'
        lines  = self.root.lines
        lns    = set(range(skip, len(self._lines))) if self.is_root else set(range(self.bln + skip, self.bend_ln + 1))

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
            self = parent

        for f in (walking := self.walk(False)):  # find multiline strings and exclude their unindentable lines
            if f.bend_ln == f.bln:  # everything on one line, don't need to recurse
                walking.send(False)

            elif isinstance(a := f.a, Constant):
                if (  # isinstance(f.a.value, (str, bytes)) is a given if bend_ln != bln
                    not docstr or
                    not ((parent := f.parent) and isinstance(parent.a, Expr) and
                         (not strict or ((pparent := parent.parent) and parent.pfield == ('body', 0) and
                                         isinstance(pparent.a, HAS_DOCSTRING)
                )))):
                    multiline_str(f)

            elif isinstance(a, (JoinedStr, TemplateStr)):
                multiline_fstr(f)

                walking.send(False)  # skip everything inside regardless, because it is evil

        return lns

    def pars(self, pars: bool = True, *, ret_npars: bool = False, exc_genexpr_solo: bool = False,
             ) -> fstloc | tuple[fstloc, int]:
        """Return the location of enclosing grouping parentheses if present. Will balance parentheses if `self` is an
        element of a tuple and not return the parentheses of the tuple. Likwise will not return the parentheses of an
        enclosing `arguments` parent. Only works on (and makes sense for) `expr` or `pattern` nodes, otherwise
        `self.bloc`. Also handles special case of a single generator expression argument to a function sharing
        parameters with the call arguments.

        **Parameters:**
        - `pars`: `True` means return parentheses if present and `self.bloc` otherwise, `False` always `self.bloc`.
        - `ret_npars`: `True` means return the count of parentheses along with the location.
        - `exc_genexpr_solo`: If `True` then will exclude parentheses of a single call argument generator expression if
            they is shared with the call arguments enclosing parentheses, return -1 npars in this case. Is not checked
            at all if `pars=False`.

        **Returns:**
        - `fstloc`: Location of enclosing parentheses if present else `self.bloc`.
        """

        if not pars or not isinstance(self.a, PARENTHESIZABLE):
            return (self.bloc, 0) if ret_npars else self.bloc

        pars_end_ln, pars_end_col, ante_end_ln, ante_end_col, nrpars = self._rpars(exc_genexpr_solo=exc_genexpr_solo)

        if not nrpars:
            return (self.loc, 0) if ret_npars else self.loc

        pars_ln, pars_col, ante_ln, ante_col, nlpars = self._lpars(exc_genexpr_solo=exc_genexpr_solo)

        if not nlpars:
            return (self.loc, 0) if ret_npars else self.loc

        dpars = nlpars - nrpars

        if dpars == 1:  # unbalanced due to enclosing tuple, will always be unbalanced if at ends of parenthesized tuple (even if solo element) due to commas
            npars    = nrpars
            pars_ln  = ante_ln
            pars_col = ante_col

        elif dpars == -1:
            npars        = nlpars
            pars_end_ln  = ante_end_ln
            pars_end_col = ante_end_col

        elif dpars:
            raise RuntimeError('should not get here')
        else:
            npars = nrpars

        loc = fstloc(pars_ln, pars_col, pars_end_ln, pars_end_col)

        return (loc, npars) if ret_npars else loc

    def comms(self, precomms: bool | str | None = DEFAULT_PRECOMMS, postcomms: bool | str | None = DEFAULT_POSTCOMMS,
              **options) -> fstloc:
        """Return the location of preceding and trailing comments if present. Only works on (and makes sense for)
        `stmt`, 'ExceptHandler' or `match_case` nodes, otherwise returns `self.bloc`.

        **Parameters:**
        - `precomms`: Preceding comments to get. See `FST` source editing `options`.
        - `postcomms`: Trailing comments to get. See `FST` source editing `options`.
        - `options`: Ignored.

        **Returns:**
        - `fstloc`: Location from start of preceding comments to end of trailing comments, else `self.bloc` or start or
            end from it if preceding or trailing comment(s) not found.
        """

        if precomms is None:
            precomms = DEFAULT_PRECOMMS

        if postcomms is None:
            postcomms = DEFAULT_POSTCOMMS

        if not (precomms or postcomms) or not isinstance(self.a, STATEMENTISH):
            return self.bloc

        lines = self.root._lines
        loc   = self.bloc

        return fstloc(
            *(_src_edit.pre_comments(lines, *self._prev_ast_bound(), loc.ln, loc.col, precomms) or loc[:2]),
            *(_src_edit.post_comments(lines, loc.end_ln, loc.end_col, *self._next_ast_bound(), postcomms) or loc[2:]),
        )

    # ------------------------------------------------------------------------------------------------------------------

    def touch(self, parents: bool = False, self_: bool = True, children: bool = False) -> 'FST':  # -> Self
        """Touch self, parents and children, optionally. Flushes location cache so that changes to AST locations will
        get picked up."""

        if children:
            stack = [self.a] if self_ else list(iter_child_nodes(self.a))

            while stack:
                child = stack.pop()

                child.f._touch()
                stack.extend(iter_child_nodes(child))

        elif self_:
            self._touch()

        if parents:
            parent = self

            while parent := parent.parent:
                parent._touch()

        return self

    def offset(self, ln: int, col: int, dln: int, dcol_offset: int,
               tail: bool | None = False, head: bool | None = True, exclude: Optional['FST'] = None, *,
               offset_excluded: bool = True, self_: bool = True,
               ) -> 'FST':  # -> Self
        """Offset ast node positions in the tree on or after (ln, col) by (delta line, col_offset) (column byte offset).

        This only offsets the positions in the `AST` nodes, doesn't change any text, so make sure that is correct before
        getting any `FST` locations from affected nodes otherwise they will be wrong.

        Other nodes outside this tree might need offsetting so use only on root unless special circumstances.

        If offsetting a zero-length node (which can result from deleting elements of an unparenthesized tuple), both the
        start and end location will be moved if exactly at offset point if `tail` is `False`. Otherwise if `tail` is
        `True` then the start position will remain and the end position will be expanded, see "Behavior" below.

        **Parameters:**
        - `ln`: Line of offset point (0 based).
        - `col`: Column of offset point (char index if positive). If this is negative then is treated as a byte offset
            in the line so that the source is not used for calculations (which could be wrong if the source was already
            changed).
        - `dln`: Number of lines to offset everything on or after offset point, can be 0.
        - `dcol_offset`: Column offset to apply to everything ON the offset point line `ln` (in bytes). Columns not on
            line `ln` will not be changed.
        - `tail`: Whether to offset end endpoint if it FALLS EXACTLY AT (ln, col) or not. If `False` then tail will not
            be moved backward if at same location as head and can stop head from moving forward past it if at same
            location. If `None` then can be moved forward with head if head at same location.
        - `head`: Whether to offset start endpoint if it FALLS EXACTLY AT (ln, col) or not. If `False` then head will
            not be moved forward if at same location as tail and can stop tail from moving backward past it if at same
            location. If `None` then can be moved backward with tail if tail at same location.
        - `exclude`: `FST` node to stop recursion at and not go into its children (recursion in siblings will not be
            affected).
        - `offset_excluded`: Whether to apply offset to `exclude`d node or not.
        - `self_`: Whether to offset self or not (will recurse into children unless is `exclude`).

        **Behavior:**
        ```
        start offset here
              V
          |===|
              |---|
              |        <- special zero length span which doesn't normally exist
        0123456789ABC

        +2, tail=False      -2, tail=False      +2, tail=None       -2, tail=False
            head=True           head=True           head=True           head=None
              V                   V                   V                   V
          |===|               |===|               |===|               |===|
                |---|           |---|                   |---|             |-|
              |                 |.|                     |                 |
        0123456789ABC       0123456789ABC       0123456789ABC       0123456789ABC

        +2, tail=True       -2, tail=True       +2, tail=None       -2, tail=True
            head=True           head=True           head=False          head=None
              V                   V                   V                   V
          |=====|             |=|                 |===|               |=|
                |---|           |---|                 |-----|             |-|
                |               |                     |                 |
        0123456789ABC       0123456789ABC       0123456789ABC       0123456789ABC

        +2, tail=False      -2, tail=False      -2, tail=None       +2, tail=None
            head=False          head=False          head=None           head=None
              V                   V                   V                   V
          |===|               |===|               |===|               |===|
              |-----|             |-|                 |-|                 |-----|
              |                   |                   |                   |
        0123456789ABC       0123456789ABC       0123456789ABC       0123456789ABC

        +2, tail=True       -2, tail=True
            head=False          head=False
              V                   V
          |=====|             |=|
              |-----|             |-|
              |.|                 |
        0123456789ABC       0123456789ABC
        ```
        """

        if self_:
            stack = [self.a]
        elif self is exclude:
            return
        else:
            stack = list(iter_child_nodes(self.a))

        lno  = ln + 1
        colo = (-col if col < 0 else
                (l := ls[ln]).c2b(min(col, len(l))) if ln < len(ls := self.root._lines) else 0x7fffffffffffffff)
        fwd  = dln > 0 or (not dln and dcol_offset >= 0)

        while stack:
            a = stack.pop()
            f = a.f

            if f is not exclude:
                children = iter_child_nodes(a)
            elif offset_excluded:
                children = ()
            else:
                continue

            f._touch()

            if (fend_colo := getattr(a, 'end_col_offset', None)) is not None:
                flno  = a.lineno
                fcolo = a.col_offset

                if (fend_lno := a.end_lineno) < lno:
                    continue  # no need to walk into something which ends before offset point
                elif fend_lno > lno:
                    a.end_lineno = fend_lno + dln
                elif fend_colo < colo:
                    continue

                elif (fend_colo > colo or
                      (tail and (fwd or head is not False or fcolo != fend_colo or flno != fend_lno)) or  # at (ln, col), moving tail allowed and not blocked by head?
                      (tail is None and head and fwd and fcolo == fend_colo and flno == fend_lno)):  # allowed to be and being moved by head?
                    a.end_lineno     = fend_lno + dln
                    a.end_col_offset = fend_colo + dcol_offset

                if flno > lno:
                    if not dln and (not (decos := getattr(a, 'decorator_list', None)) or decos[0].lineno > lno):
                        continue  # no need to walk into something past offset point if line change is 0, don't need to touch either could not have been changed above

                    a.lineno = flno + dln

                elif (flno == lno and (fcolo > colo or (fcolo == colo and (
                      (head and (not fwd or tail is not False or fcolo != fend_colo or flno != fend_lno)) or  # at (ln, col), moving head allowed and not blocked by tail?
                      (head is None and tail and not fwd and fcolo == fend_colo and flno == fend_lno))))):  # allowed to be and being moved by tail?
                    a.lineno     = flno + dln
                    a.col_offset = fcolo + dcol_offset

            stack.extend(children)

        self.touch(True, False)

        return self

    def offset_cols(self, lns: set[int] | dict[int, int], dcol_offset: int | None = None):
        """Offset ast column byte offsets in `lns` by `dcol_offset` if present, otherwise `lns` must be a dict with an
        individual `dcol_offset` per line. Only modifies ast, not lines. Does not modify parent locations but
        `touch()`es parents."""

        if dcol_offset is None:  # lns is dict[int, int]
            for a in walk(self.a):
                if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                    if dcol_offset := lns.get(a.lineno - 1):
                        a.col_offset += dcol_offset

                    if dcol_offset := lns.get(a.end_lineno - 1):
                        a.end_col_offset = end_col_offset + dcol_offset

                a.f._touch()

            self.touch(True, False)

        elif dcol_offset:  # lns is set[int] OR dict[int, int] (overriding with a single dcol_offset)
            for a in walk(self.a):
                if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                    if a.lineno - 1 in lns:
                        a.col_offset += dcol_offset

                    if a.end_lineno - 1 in lns:
                        a.end_col_offset = end_col_offset + dcol_offset

                a.f._touch()

            self.touch(True, False)

    def indent_lns(self, indent: str | None = None, lns: set[int] | None = None, *,
                   skip: int = 1, docstr: bool | Literal['strict'] | None = None) -> set[int]:
        """Indent all indentable lines specified in `lns` with `indent` and adjust node locations accordingly.

        WARNING! This does not offset parent nodes.

        **Parameters:**
        - `indent`: The indentation string to prefix to each indentable line.
        - `lns`: A `set` of lines to apply identation to. If `None` then will be gotten from
            `get_indentable_lns(skip=skip)`.
        - `skip`: If not providing `lns` then this value is passed to `get_indentable_lns()`.
        - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
            multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
            in expected docstring positions are indentable. `None` means use default.

        **Returns:**
        - `set[int]`: `lns` passed in or otherwise set of line numbers (zero based) which are sytactically indentable.
        """

        root = self.root

        if indent is None:
            indent = root.indent
        if docstr is None:
            docstr = DEFAULT_DOCSTR

        if not ((lns := self.get_indentable_lns(skip, docstr=docstr)) if lns is None else lns) or not indent:
            return lns

        self.offset_cols(lns, len(indent.encode()))

        lines = root._lines

        for ln in lns:
            if l := lines[ln]:  # only indent non-empty lines
                lines[ln] = bistr(indent + l)

        self._reparse_docstrings(docstr)

        return lns

    def dedent_lns(self, indent: str | None = None, lns: set[int] | None = None, *,
                   skip: int = 1, docstr: bool | Literal['strict'] | None = None) -> set[int]:
        """Dedent all indentable lines specified in `lns` by removing `indent` prefix and adjust node locations
        accordingly. If cannot dedent entire amount, will dedent as much as possible.

        WARNING! This does not offset parent nodes.

        **Parameters:**
        - `indent`: The indentation string to remove from the beginning of each indentable line (if possible).
        - `lns`: A `set` of lines to apply dedentation to. If `None` then will be gotten from
            `get_indentable_lns(skip=skip)`.
        - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
            multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
            in expected docstring positions are indentable. `None` means use default.
        - `skip`: If not providing `lns` then this value is passed to `get_indentable_lns()`.

        **Returns:**
        - `set[int]`: `lns` passed in or otherwise set of line numbers (zero based) which are sytactically indentable.
        """

        root = self.root

        if indent is None:
            indent = root.indent
        if docstr is None:
            docstr = DEFAULT_DOCSTR

        if not ((lns := self.get_indentable_lns(skip, docstr=docstr)) if lns is None else lns) or not indent:
            return lns

        lines        = root._lines
        lindent      = len(indent)
        dcol_offsets = None
        newlines     = []

        def dedent(l, lindent):
            if dcol_offsets is not None:
                dcol_offsets[ln] = -lindent

            return bistr(l[lindent:])

        lns_seq = list(lns)

        for ln in lns_seq:
            if l := lines[ln]:  # only dedent non-empty lines
                if l.startswith(indent) or (lempty_start := re_empty_line_start.match(l).end()) >= lindent:
                    l = dedent(l, lindent)

                else:
                    if not dcol_offsets:
                        dcol_offsets = {}

                        for ln2 in lns_seq:
                            if ln2 is ln:
                                break

                            dcol_offsets[ln2] = -lindent

                    l = dedent(l, lempty_start)

            newlines.append(l)

        for ln, l in zip(lns_seq, newlines):
            lines[ln] = l

        if dcol_offsets:
            self.offset_cols(dcol_offsets)
        else:
            self.offset_cols(lns, -lindent)

        self._reparse_docstrings(docstr)

        return lns

    def parenthesize(self, force: bool = False) -> bool:
        """Parenthesize node if is not `.is_atom()`. Will add parentheses to unparenthesized `Tuple` adjusting the
        node location and otherwise grouping parentheses where needed.

        **Parameters:**
        - `force`: If `True` then will add another layher of parentheses regardless if already present.

        **Returns:**
        - `bool`: Whether parentheses added or not.
        """

        if self.is_atom():
            if not force:
                return False

            self._parenthesize_grouping()

            return True

        if isinstance(self.a, Tuple):
            self._parenthesize_tuple()
        else:
            self._parenthesize_grouping()

        return True

    def unparenthesize(self, tuple_: bool = False) -> bool:
        """Unparenthesize node if is `.is_atom()`. Can remove parentheses from parenthesized tuple and adjust its
        location but will not do so by default.

        **Parameters:**
        - `tuple`: If `True` then will remove parentheses from a parenthesized `Tuple`, otherwise only removes grouping
            parentheses if present.

        **Returns:**
        - `bool`: Whether parentheses were removed or not.
        """

        if not self.is_atom():
            return False

        ret = self._unparenthesize_grouping()

        if tuple_ and isinstance(self.a, Tuple):
            ret = self._unparenthesize_tuple() or ret

        return ret


from .fstlist import fstlist
from .srcedit import SrcEdit

_src_edit = SrcEdit()










