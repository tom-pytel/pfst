import ast as ast_
import inspect
from ast import *
from ast import parse as ast_parse, unparse as ast_unparse
from io import TextIOBase
from typing import Any, Callable, Literal, Optional, TextIO

from .astutil import *
from .astutil import TryStar, TemplateStr, Interpolation

from .shared import (
    astfield, fstloc,
    STMTISH, STMTISH_OR_MOD, STMTISH_OR_STMTMOD, BLOCK, BLOCK_OR_MOD, SCOPE, SCOPE_OR_MOD, NAMED_SCOPE,
    NAMED_SCOPE_OR_MOD, ANONYMOUS_SCOPE, PARENTHESIZABLE, HAS_DOCSTRING,
    STMTISH_FIELDS,
    re_empty_line_start, re_empty_line, re_line_continuation,
    re_oneline_str, re_contline_str_start, re_contline_str_end_sq, re_contline_str_end_dq, re_multiline_str_start,
    re_multiline_str_end_sq, re_multiline_str_end_dq,
    Code, NodeTypeError,
    _next_src, _params_offset, _fixup_field_body, _fixup_one_index)

__all__ = [
    'parse', 'unparse', 'FST',
]

_REPR_SRC_LINES = 0  # for debugging

_DEFAULT_PARSE_PARAMS = dict(filename='<unknown>', type_comments=False, feature_version=None)
_DEFAULT_INDENT       = '    '

_OPTIONS = {
    'docstr':    True,    # True | False | 'strict'
    'precomms':  True,    # True | False | 'all'
    'postcomms': True,    # True | False | 'all' | 'block'
    'prespace':  False,   # True | False | int
    'postspace': False,   # True | False | int
    'pep8space': True,    # True | False | 1
    'pars':      'auto',  # True | False | 'auto'
    'elif_':     False,   # True | False
    'fix':       True,    # True | False
    'raw':       'auto',  # True | False | 'auto'
}


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


class _FSTCircularImportStandinMeta(type):
    """Class attribute getter for temporary circular import standin class for FST."""

    def __getattr__(cls, name):
        inspect.currentframe().f_back.f_globals['FST'] = FST

        return getattr(FST, name)

    def __instancecheck__(cls, instance):
        inspect.currentframe().f_back.f_globals['FST'] = FST

        return isinstance(instance, FST)

class _FSTCircularImportStandin(metaclass=_FSTCircularImportStandinMeta):
    """Temporary standin for circular import of `FST`. Proxies `FST()` and `FST.attr` and sets `FST` in caller globals
    to the actual `FST` class on first access. The import will also resolve to the actual `FST` class for static type
    analysis in IDEs due to the later override with the real `FST` class."""

    def __new__(cls, *args, **kwargs):
        inspect.currentframe().f_back.f_globals['FST'] = FST

        return FST(*args, **kwargs)

FST = _FSTCircularImportStandin  # predefined so that imports in the real `FST` class get this


class FST:
    """Preserve AST formatting information and easy manipulation."""

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

        return isinstance(self.a, STMTISH)

    @property
    def is_stmtish_or_mod(self) -> bool:
        """Is a `stmt`, `ExceptHandler`, `match_case` or `mod` node."""

        return isinstance(self.a, STMTISH_OR_MOD)

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
        nodes have locations (like `expr_context`). Other nodes which normally don't have locations like `arguments` or
        most operators have this location calculated from their children or source."""

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
        """Whole source location if at root, regardless of actual root node location which may only span part of the
        source due to parentheses or comments. If not root node then is just `bloc`."""

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
        """Line number of the first line of this node or the first decorator if present (0 based)."""

        return (l := self.bloc) and l[0]

    bcol     = col  # for symmetry, also may eventually be distinct
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
        """AST-style CHARACTER index one past the end of this node (0 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and self.root._lines[loc[2]].c2b(loc[3])

    # ------------------------------------------------------------------------------------------------------------------
    # Management functions

    def __repr__(self) -> str:
        tail = self._repr_tail()
        head = f'<fst.{(a := self.a).__class__.__name__} 0x{id(a):x}{tail}>'

        if not _REPR_SRC_LINES:
            return head

        try:
            ln, col, end_ln, end_col = self.loc

            if end_ln - ln + 1 <= _REPR_SRC_LINES:
                ls = self.root._lines[ln : end_ln + 1]
            else:
                ls = (self.root._lines[ln : ln + ((_REPR_SRC_LINES + 1) // 2)] + ['...'] +
                      self.root._lines[end_ln - ((_REPR_SRC_LINES - 2) // 2) : end_ln + 1])

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
            self.parse_params = kwargs.get('parse_params', _DEFAULT_PARSE_PARAMS)
            self.indent       = kwargs.get('indent', '?')

        self._make_fst_tree()

        if self.indent == '?':  # infer indentation from source, just use first indentation found for performance, don't try to find most common or anything like that
            if not isinstance(ast_or_src, Module):
                self.indent = _DEFAULT_INDENT

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
                    self.indent = _DEFAULT_INDENT

        return self

    @staticmethod
    def new(filename: str = '<unknown>', mode: Literal['exec', 'eval', 'single'] = 'exec', *,
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
    def fromsrc(source: str | bytes | list[str], filename: str = '<unknown>',
                mode: Literal['exec', 'eval', 'single'] = 'exec', *,
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
    def fromast(ast: AST, filename: str = '<unknown>', mode: Literal['exec', 'eval', 'single'] | None = None, *,
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
    def get_option(option: str, options: dict[str, Any] = {}) -> Any:
        """Get option from options dict or default if option not in dict or is `None` there.

        **Parameters:**
        - `option`: Name of option to get.
        - `options`: Dictionary which may or may not contain the requested option.

        **Returns:**
        - `Any`: Default option of if not found in `options` or is `None` there, otherwise the value from `options`.
        """

        return _OPTIONS.get(option) if (o := options.get(option)) is None else o

    @staticmethod
    def set_options(**options) -> dict[str, Any]:
        """Set defaults for `options` parameters.

        **Parameters:**
        - `options`: Key / values of parameters to set.
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

        **Returns:**
        - `options`: `dict` of previous values of changed parameters, reset with `set_options(**options)`.
        """

        ret = {o: _OPTIONS[o] for o in options}

        _OPTIONS.update(options)

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
        - `eol`: What to put at the end of each text line, `None` means newline for `TextIO` out and nothing for other.
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
    # High level operations

    def copy(self, **options) -> 'FST':
        """Copy an individual node to a top level tree, dedenting and fixing as necessary."""

        fix    = FST.get_option('fix', options)
        ast    = self.a
        newast = copy_ast(ast)

        if self.is_root:
            return FST(newast, lines=self._lines[:], from_=self)

        if isinstance(ast, STMTISH):
            loc = self.comms(options.get('precomms'), options.get('postcomms'))
        elif isinstance(ast, PARENTHESIZABLE):
            loc = self.pars(options.get('pars') is True)
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

        if isinstance(ast, STMTISH):
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


        # TODO: special case indexed stuff like Compare


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
                start         = _fixup_one_index(len(ast.comparators) + 1, start)  # need to do this because of compound body including 'left'
                field_, start = ('comparators', start - 1) if start else ('left', None)

        if is_dict and field == 'keys' and (keys := ast.keys)[start] is None:  # '{**d}' with key=None
            if not FST.get_option('raw', options):
                raise ValueError(f"cannot put() non-raw to '**' Dict.key")

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

        if isinstance(ast, STMTISH_OR_STMTMOD):
            if field_ in STMTISH_FIELDS:
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
                if isinstance(ast, STMTISH_OR_STMTMOD):
                    if field_ in STMTISH_FIELDS:
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
    # Structure stuff

    from .fst_walk import (
        next,
        prev,
        first_child,
        last_child,
        next_child,
        prev_child,
        next_step,
        prev_step,
        walk,)

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

        types = STMTISH_OR_MOD if mod else STMTISH

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
    # Low level queries

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
        """Whether `self` is an empty `Set` from an empty sequence, recognized are `{*()}`, `{*[]}` and `{*{}}`."""

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
            docstr = self.get_option('docstr')

        strict = docstr == 'strict'
        lines  = self.root.lines
        lns    = set(range(skip, len(self._lines))) if self.is_root else set(range(self.bln + skip, self.bend_ln + 1))

        while (parent := self.parent) and not isinstance(self.a, STMTISH):
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

    def comms(self, precomms: bool | str | None = None, postcomms: bool | str | None = None, **options) -> fstloc:
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
            precomms = self.get_option('precomms')
        if postcomms is None:
            postcomms = self.get_option('postcomms')

        if not (precomms or postcomms) or not isinstance(self.a, STMTISH):
            return self.bloc

        lines = self.root._lines
        loc   = self.bloc

        return fstloc(
            *(_src_edit.pre_comments(lines, *self._prev_ast_bound(), loc.ln, loc.col, precomms) or loc[:2]),
            *(_src_edit.post_comments(lines, loc.end_ln, loc.end_col, *self._next_ast_bound(), postcomms) or loc[2:]),
        )

    # ------------------------------------------------------------------------------------------------------------------
    # Low level modifications

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

        +2, tail=False      -2, tail=False      +2, tail=None       -2, tail=None
            head=False          head=False          head=None           head=None
              V                   V                   V                   V
          |===|               |===|               |===|               |===|
              |-----|             |-|                 |-----|             |-|
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

    def offset_lns(self, lns: set[int] | dict[int, int], dcol_offset: int | None = None):
        """Offset ast column byte offsets in `lns` by `dcol_offset` if present, otherwise `lns` must be a dict with an
        individual `dcol_offset` per line. Only modifies `AST`, not lines. Does not modify parent locations but
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
            docstr = self.get_option('docstr')

        if not ((lns := self.get_indentable_lns(skip, docstr=docstr)) if lns is None else lns) or not indent:
            return lns

        self.offset_lns(lns, len(indent.encode()))

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
            docstr = self.get_option('docstr')

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
            self.offset_lns(dcol_offsets)
        else:
            self.offset_lns(lns, -lindent)

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

    # ------------------------------------------------------------------------------------------------------------------
    # Private and other misc stuff

    from .fst_misc import (
        _normalize_code,
        _new_empty_module,
        _new_empty_tuple,
        _new_empty_list,
        _new_empty_dict,
        _new_empty_set,
        _new_empty_set_curlies,
        _make_tree_fst,
        _make_fst_tree,
        _unmake_fst_tree,
        _set_ast,
        _repr_tail,
        _dump,
        _prev_ast_bound,
        _next_ast_bound,
        _lpars,
        _rpars,
        _loc_block_opener_end,
        _loc_operator,
        _loc_comprehension,
        _loc_arguments,
        _loc_withitem,
        _loc_match_case,
        _dict_key_or_mock_loc,
        _touch,
        _set_end_pos,
        _maybe_add_comma,
        _maybe_add_singleton_tuple_comma,
        _maybe_fix_tuple,
        _maybe_fix_set,
        _maybe_fix_elif,
        _fix_block_del_last_child,
        _fix,
        _is_parenthesized_seq,
        _parenthesize_grouping,
        _parenthesize_tuple,
        _unparenthesize_grouping,
        _unparenthesize_tuple,
        _normalize_block,
        _elif_to_else_if,
        _reparse_docstrings,
        _make_fst_and_dedent,)

    from .fst_raw import (
        _reparse_raw,
        _reparse_raw_stmtish,
        _reparse_raw_loc,
        _reparse_raw_node,
        _put_slice_raw,)

    from .fst_slice import (
        _get_slice_tuple_list_or_set,
        _get_slice_empty_set,
        _get_slice_dict,
        _get_slice_stmtish,
        _put_slice_tuple_list_or_set,
        _put_slice_empty_set,
        _put_slice_dict,
        _put_slice_stmtish,)

    from .fst_one import (
        _put_one,)

    @property
    def f(self):
        """@private"""

        raise RuntimeError("you probably think you're accessing an AST node, but you're not, "
                           "you're accessing an FST node")


from .fstlist import fstlist
from .srcedit import _src_edit  # , SrcEdit
