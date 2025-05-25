import ast as ast_
import inspect
from ast import *
from ast import parse as ast_parse, unparse as ast_unparse
from io import TextIOBase
from typing import Any, Callable, Literal, Optional, TextIO, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, TemplateStr, Interpolation, type_param

from .shared import (
    astfield, fstloc, mock,
    STMTISH, STMTISH_OR_MOD, BLOCK, BLOCK_OR_MOD, SCOPE, SCOPE_OR_MOD, NAMED_SCOPE,
    NAMED_SCOPE_OR_MOD, ANONYMOUS_SCOPE, PARENTHESIZABLE, HAS_DOCSTRING,
    re_empty_line_start, re_empty_line, re_line_continuation, re_line_end_cont_or_comment,
    Code,
    _next_pars, _prev_pars,
    _params_offset, _fixup_field_body, _multiline_str_continuation_lns, _multiline_fstr_continuation_lns,
)

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
    'raw':       'auto',  # True | False | 'auto'
}


def _swizzle_getput_params(start: int | Literal['end'] | None, stop: int | None | Literal[False], field: str | None,
                           default_stop: Literal[False] | None,
                           ) -> tuple[int | Literal['end'] | None,int | None | Literal[False], str | None]:
    """Allow passing `stop` and `field` positionally."""

    if isinstance(start, str) and start != 'end':
        return None, default_stop, start
    if isinstance(stop, str):
        return start, default_stop, stop

    return start, stop, field


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


# ----------------------------------------------------------------------------------------------------------------------

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
    """Preserve AST formatting information and easy manipulation."""

    a:            AST              ; """The actual `AST` node."""
    parent:       Optional['FST']  ; """Parent `FST` node, `None` in root node."""
    pfield:       astfield | None  ; """The `astfield` location of this node in the parent, `None` in root node."""
    root:         'FST'            ; """The root node of this tree, `self` in root node."""
    _cache:       dict

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
    def whole_loc(self) -> fstloc:
        """Whole source location, from 0,0 to end of entire source, regardless of node being checked."""

        return fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))

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

        self._cache['loc'] = loc

        return loc

    @property
    def bloc(self) -> fstloc | None:
        """Entire location of node, including any preceding decorators. Not all nodes have locations but any node which
        has a `.loc` will have a `.bloc`."""

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
        """Line number of the first line of this node or the first decorator if present (0 based)."""

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
        """AST-style CHARACTER index one past the end of this node (0 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and self.root._lines[loc[2]].c2b(loc[3])

    # ------------------------------------------------------------------------------------------------------------------
    # Management functions

    def __repr__(self) -> str:
        tail = self._repr_tail()
        head = f'<{self.a.__class__.__name__}{tail}>'

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
                parent_or_lines: Union['FST', list[str], None] = None, pfield: astfield | None = None, **kwargs):
        """Create a new individual `FST` node or full tree from `AST` with `lines` or create from just an `AST` or just
        source.

        **Parameters:**
        - `ast_or_src`: `AST` node for `FST` or source code in the form of a `str`, encoded `bytes` or a list of lines.
            If an `AST` then will be processed differently depending on if creating child node, top level node or using
            this as a shortcut.
        - `parent_or_lines`: Parent node for this child node or lines for a root node creating a new tree. If `pfield`
            is none and this as well then the call is a shortcut to create a full tree from an `AST` node or source
            provided in `ast_or_src`.
        - `pfield`: `astfield` indication position in parent of this node. If provided then creating a simple child node
            and it is created with the `self.parent_or_lines` node as parent and `self.pfield` set to passed params. If
            `None` then it means the creation of a full new `FST` tree and this is the root node with `parent_or_lines`
            providing the source.
        - `kwargs`: Contextual parameters:
            - `from_`: If this is provided then it must be an `FST` node from which this node is being created. This
                allows to copy parse parameters and already determined default indentation.
            - `parse_params`: A `dict` with values for 'filename', 'type_comments' and 'feature_version' which will be
                used for any `AST` reparse done on this tree. Only valid when creating a root node.
            - `indent`: Indentation string to use as default indentation. If not provided and not gotten from `from_`
                then indentation will be inferred from source. Only valid when creating a root node.
            - `filename`, `mode`, `type_comments` and `feature_version`: If creating from an `AST` or source only then
                these are the parameteres passed to the respective `.new()`, `.fromsrc()` or `.fromast()` functions.
                Only valid when `parent_or_lines` and `pfield` are `None`.
        """

        if pfield is None and parent_or_lines is None:  # top level shortcut
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
        self.pfield = pfield
        self._cache = {}

        if pfield is not None:
            self.parent = parent_or_lines
            self.root   = parent_or_lines.root

            return self

        # ROOT

        self.parent = None
        self.root   = self
        self._lines = [bistr(s) for s in parent_or_lines] if kwargs.get('copy_lines', True) else parent_or_lines

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

        return FST(ast, [''], parse_params=parse_params)

    @staticmethod
    def fromsrc(src: str | bytes | list[str], filename: str = '<unknown>',
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

        if isinstance(src, bytes):
            src = src.decode()

        if isinstance(src, str):
            lines = src.split('\n')

        else:
            lines = src
            src   = '\n'.join(lines)

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)
        ast          = ast_parse(src, mode=mode, **parse_params)

        return FST(ast, lines, parse_params=parse_params)  # not just convert to bistr but to make a copy at the same time

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
            astp = ast_parse(src, **parse_params)
            cls  = ast.__class__

            if not (astp.__class__ is cls or (len(astp.body) == 1 and (astp := astp.body[0]).__class__ is cls) or
                    (isinstance(astp, Expr) and (astp := astp.value).__class__ is cls)):
                raise RuntimeError('could not reproduce ast')

            if calc_loc == 'copy':
                if not compare_asts(astp, ast, type_comments=type_comments, raise_=False):
                    raise RuntimeError('could not reparse ast identically')

                ast = astp

            elif not copy_attributes(astp, ast, compare=True, type_comments=type_comments, raise_=False):
                raise RuntimeError('could not reparse ast identically')

        return FST(ast, lines, parse_params=parse_params)

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
    def set_option(**options) -> dict[str, Any]:
        """Set defaults for `options` parameters.

        **Parameters:**
        - `options`: Key / values of parameters to set. These can also be passed to various methods and override the
            defaults set here.
            - `docstr`: Which docstrings are indentable / dedentable.
                - `False`: None.
                - `True`: All `Expr` multiline strings (as they serve no coding purpose).
                - `'strict'`: Only multiline strings in expected docstring positions (functions and classes).
                - `None`: Use default.
            - `precomms`: Preceding comments.
                - `False`: No preceding comments.
                - `True`: Single contiguous comment block immediately preceding position.
                - `'all'`: Comment blocks (possibly separated by empty lines) preceding position.
                - `None`: Use default.
            - `postcomms`: Trailing comments.
                - `False`: No trailing comments.
                - `True`: Only comment trailing on line of position, nothing past that on its own lines.
                - `'block'`: Single contiguous comment block following position.
                - `'all'`: Comment blocks (possibly separated by empty lines) following position.
                - `None`: Use default.
            - `prespace`: Preceding empty lines (max of this and `pep8space` used).
                - `False`: No empty lines.
                - `True`: All empty lines.
                - `int`: A maximum number of empty lines.
                - `None`: Use default.
            - `postspace`: Same as `prespace` except for trailing empty lines.
            - `pep8space`: Preceding and trailing empty lines for function and class definitions.
                - `False`: No empty lines.
                - `True`: Two empty lines at module scope and one empty line in other scopes.
                - `1`: One empty line in all scopes.
                - `None`: Use default.
            - `pars`: How parentheses are handled, can be `False`, `True` or `'auto'`. This is for individual puts, for
                slices parentheses are always unchanged.
                - `False`: Parentheses are not MODIFIED, doesn't mean remove all parentheses. Not copied with nodes or
                    removed on put from source or destination.
                - `True`: Parentheses are copied with nodes, added to copies if needed and not present, removed from
                    destination on put if not needed there (but not source). For raw put this only applies to `AST` or
                    `FST` nodes passed since those allow enough information for deciding parenthesization.
                - `'auto'`: Same as `True` except they are not returned with a copy and possibly removed from source
                    on put if not needed (removed from destination first if needed and present on both).
                - `None`: Use default.
            - `elif_`: `True` or `False`, if putting a single `If` statement to an `orelse` field of a parent `If` statement then
                put it as an `elif`. `None` means use default.
            - `raw`: How to attempt at raw source operations. This may result in more nodes changed than just the targeted
                one(s).
                - `False`: Do not do raw source operations.
                - `True`: Only do raw source operations.
                - `'auto'`: Only do raw source operations if the normal operation fails in a way that raw might not.
                - `None`: Use default.

        **Returns:**
        - `options`: `dict` of previous values of changed parameters, reset with `set_option(**options)`.

        **Notes:**
        `pars` behavior:
        ```
                                                                False      True    'auto'
        Copy pars from source on copy/cut:                         no       yes        no
        Add pars needed for parsability to copy:                   no       yes       yes
        Remove unneeded pars from destination on put:              no       yes       yes
        Remove unneeded pars from source on put:                   no        no       yes
        Add pars needed for parse/precedence to source on put:     no       yes       yes
        ```
        """

        ret = {o: _OPTIONS[o] for o in options}

        _OPTIONS.update(options)

        return ret

    def dump(self, compact: bool = False, full: bool = False, *, indent: int = 2, out: Callable | TextIO = print,
             eol: str | None = None) -> str | list[str] | None:
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
            astp = ast_parse(self.src, **parse_params)

        except SyntaxError:
            if raise_:
                raise

            return None

        cls = ast.__class__

        if not (astp.__class__ is cls or (len(astp.body) == 1 and (astp := astp.body[0]).__class__ is cls) or
                (isinstance(astp, Expr) and (astp := astp.value).__class__ is cls)):
            if raise_:
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

        if not (parent := self.parent):
            return FST(copy_ast(self.a), self._lines[:], from_=self, copy_lines=False)

        return parent._get_one((pf := self.pfield).idx, pf.name, False, **options)

    def cut(self, **options) -> 'FST':
        """Cut out an individual node to a top level tree (if possible), dedenting and fixing as necessary."""

        if not (parent := self.parent):
            raise ValueError('cannot cut root node')

        return parent._get_one((pf := self.pfield).idx, pf.name, True, **options)

    def replace(self, code: Code | None, **options) -> Optional['FST']:  # -> Self (replaced) or None if deleted
        """Replace or delete (`code=None`) an individual node. Returns the new node for `self`, not the old replaced
        node, or `None` if was deleted or raw replaced and old node disappeared.
        """

        if not (parent := self.parent):
            raise ValueError('cannot replace root node')

        return parent._put_one(code, (pf := self.pfield).idx, pf.name, **options)

    def get(self, start: int | Literal['end'] | None = None, stop: int | None | Literal[False] = False,
            field: str | None = None, *, cut: bool = False, **options) -> Any:
        """Copy or cut an individual child node or a slice of child nodes from `self`."""

        start, stop, field = _swizzle_getput_params(start, stop, field, False)

        ast          = self.a
        field_, body = _fixup_field_body(ast, field, False)

        if isinstance(body, list):
            if stop is not False:
                return self._get_slice(start, stop, field, cut, **options)
            if start is None:
                return self._get_slice(None, None, field, cut, **options)

            if start == 'end':
                raise IndexError(f"cannot get() non-slice from index 'end'")

        elif stop is not False or start is not None:
            raise IndexError(f"cannot pass index for non-slice get() to {ast.__class__.__name__}" +
                             (f".{field}" if field else ""))

        return self._get_one(start, field_, cut, **options)

    def put(self, code: Code | None, start: int | Literal['end'] | None = None,
            stop: int | None | Literal[False] = False, field: str | None = None, *,
            one: bool = True, **options) -> 'FST':  # -> Self
        """Put an individual child node or a slice of child nodes to `self`.

        WARNING! If the `code` being put is an `AST` or `FST` then it is consumed and should be considered invalid after
        this call, whether it succeeds or fails.
        """

        start, stop, field = _swizzle_getput_params(start, stop, field, False)

        ast          = self.a
        field_, body = _fixup_field_body(ast, field, False)

        if isinstance(body, list):
            if stop is not False:
                return self._put_slice(code, start, stop, field, one, **options)
            if start is None:
                return self._put_slice(code, None, None, field, one, **options)

            if start == 'end':
                raise IndexError(f"cannot put() non-slice to index 'end'")

        elif stop is not False or start is not None:
            raise IndexError(f'{ast.__class__.__name__}.{field_} does not take an index')

        if not one:
            raise ValueError(f"cannot use 'one=False' in non-slice put()")

        self._put_one(code, start, field_, **options)

        return self.repath()

    def get_slice(self, start: int | Literal['end'] | None = None, stop: int | None = None, field: str | None = None, *,
                  cut: bool = False, **options) -> 'FST':
        """Get a slice of child nodes from `self`."""

        start, stop, field = _swizzle_getput_params(start, stop, field, None)

        ast     = self.a
        _, body = _fixup_field_body(ast, field)

        if not isinstance(body, list):
            raise ValueError(f'cannot get slice from non-list field {ast.__class__.__name__}.{field}')

        return self._get_slice(start, stop, field, cut, **options)

    def put_slice(self, code: Code | None, start: int | Literal['end'] | None = None, stop: int | None = None,
                  field: str | None = None, *, one: bool = False, **options) -> 'FST':  # -> Self
        """Put an a slice of child nodes to `self`.

        If the `code` being put is an `AST` or `FST` then it is consumed and should not be considered valid after this
        call whether it succeeds or fails.

        Can reparse.
        """

        start, stop, field = _swizzle_getput_params(start, stop, field, None)

        ast     = self.a
        _, body = _fixup_field_body(ast, field)

        if not isinstance(body, list):
            raise ValueError(f'cannot put slice to non-list field {ast.__class__.__name__}.{field}')

        return self._put_slice(code, start, stop, field, one, **options)

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
        elif not isinstance(src[0], bistr):  # lines is list[str]
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
        walk,
    )

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

    def child_from_path(self, path: list[astfield] | str, last_valid: bool = False) -> Union['FST', Literal[False]]:
        """Get child node specified by `path` if it exists. If succeeds then the child node is not guaranteed to be the
        same type as was originally used to get the path, just the path is valid.

        **Parameters:**
        - `path`: Path to child as a list of `astfield`s or string.
        - `last_valid`: If `True` then return the last valid node along the path, will not fail, can return `self`.

        **Returns:**
        - `FST`: Child node if path is valid, otherwise `False` if path invalid. `False` and not `None` because `None`
            can be in a field that can hold an `AST` but `False` can not.
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
        """Really means the AST is `ast.unparse()`able and then re`ast.parse()`able which will get it to this top level
        AST node (surrounded by an `ast.mod`). The source may change a bit though, parentheses, 'if' <-> 'elif'."""

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

    def is_atom(self, *, pars: bool = True, enclosed: bool = False) -> bool | Literal['pars']:
        """Whether `self` is innately atomic precedence-wise like `Name`, `Constant`, `List`, etc... Or otherwise
        optionally enclosed in parentheses so that it functions as a parsable atom and cannot be split up by precedence
        rules when reparsed.

        Node types where this doesn't normally apply like `stmt` or 'alias' return `True`. This does not guarantee
        parsability as an otherwise atomic node could be spread across multiple lines without line continuations or
        grouping parentheses, see `is_enclosed()` for that. Though if this function returns `'pars'` then `self` is
        enclosed due to the grouping parentheses.

        **Parameters:**
        - `pars`: Whether to check for grouping parentheses or not for node types which are not innately atomic
            (`NamedExpr`, `BinOp`, `Yield`, etc...). If `True` then '(a + b)' is considered atomic, if `False` then it
            is not.
        - `enclosed': If `True` then will only consider nodes atomic which are definitely enclosed like `List` or
            parenthesized tuple. Nodes which may be split up across multiple lines like `Call` or `Attribute` will not
            be considered atomic and will return `False` unless `pars=True` and grouping parentheses present.

        **Returns:**
        - `True` if node is atomic and no combination in the source will make it parse to a different node. `'pars'` if
            is atomic due to enclosing grouping parentheses and would not be otherwise. `False` means not atomic.
        """

        ast = self.a

        if isinstance(ast, (List, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp, Name,
                            MatchValue, MatchSingleton, MatchMapping,
                            expr_context, boolop, operator, unaryop, ExceptHandler,
                            stmt, match_case, mod, TypeIgnore)):
            return True

        if not enclosed:
            if isinstance(ast, (Call, JoinedStr, TemplateStr, Constant, Attribute, Subscript,
                                MatchClass, MatchStar,
                                cmpop, comprehension, arguments,
                                arg, keyword, alias, withitem, type_param)):
                return True

        elif isinstance(ast, (comprehension, arguments, arg, keyword, alias, type_param)):  # can't be parenthesized
            return False

        elif isinstance(ast, Constant):
            if not isinstance(ast.value, (str, bytes)):  # str and bytes can be multiline implicit needing parentheses
                return True

        elif isinstance(ast, withitem):  # isn't atom on its own and can't be parenthesized directly but if only has context_expr then take on value of that if starts and ends on same lines
            return (not ast.optional_vars and self.loc[::2] == (ce := ast.context_expr.f).pars()[::2] and
                    ce.is_atom(pars=pars, enclosed=enclosed))

        elif isinstance(ast, cmpop):
            return not isinstance(ast, (IsNot, NotIn))  # could be spread across multiple lines

        if (ret := self.is_parenthesized_tuple()) is not None:  # if this is False then cannot be enclosed in grouping pars because that would reparse to a parenthesized Tuple and so is inconsistent
            return ret

        if (ret := self.is_enclosed_matchseq()) is not None:  # like Tuple, cannot be enclosed in grouping pars
            return ret

        assert isinstance(ast, (expr, pattern))

        return 'pars' if pars and self.pars(True)[1] else False

    def is_enclosed(self, *, pars: bool = True) -> bool | Literal['pars']:
        """Whether `self` lives on a single line or is otherwise enclosed in some kind of delimiters '()', '[]', '{}' or
        entirely terminated with line continuations so that it can be parsed without error due to being spread across
        multiple lines. This does not mean it can't have other errors, such as a `Slice` outside of `Subscript.slice`.

        Node types where this doesn't normally apply like `stmt`, `ExceptHandler`, `boolop`, `expr_context`, etc...
        return `True`. Node types that are not enclosed but which are never used without being enclosed by a parent like
        `Slice`, `keyword` or `type_param` will also return `True`. Other node types which cannot be enclosed
        individually and do not have line continuations but would need a parent to enclose them like `arguments` or the
        `cmpop`s `is not` or `not in` will return `False` if not on a single line or not parenthesized.

        This function does NOT check whether `self` is enclosed by some parent up the tree if it is not enclosed itself,
        for that see `is_enclosed_in_parents()`.

        **Parameters:**
        - `pars`: Whether to check for grouping parentheses or not for nodes which are not enclosed or otherwise
            multiline-safe. Grouping parentheses are different from tuple parentheses which are always checked.

        **Returns:**
        - `True` if node is enclosed. `'pars'` if is enclosed by grouping parentheses and would not be otherwise.
            `False` means not enclosed and should be parenthesized or put into an enclosed parent for successful parse.
        """

        ast = self.a

        if isinstance(ast, (List, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp, FormattedValue, Interpolation,
                            Name, Slice,
                            MatchValue, MatchSingleton, MatchMapping,
                            expr_context, boolop, operator, unaryop, ExceptHandler, keyword, type_param,
                            stmt, match_case, mod, TypeIgnore)):
            return True

        if not (loc := self.loc):  # this catches empty `arguments` mostly
            return True

        ln, col, end_ln, end_col = loc

        if end_ln == ln:
            return True

        if pars and self.pars(True)[1]:
            return 'pars'

        if isinstance(ast, Constant):
            if not isinstance(ast.value, (str, bytes)):
                return True

            return len(_multiline_str_continuation_lns(self.root._lines, ln, col, end_ln, end_col)) == end_ln - ln

        if isinstance(ast, (JoinedStr, TemplateStr)):
            return len(_multiline_fstr_continuation_lns(self.root._lines, ln, col, end_ln, end_col)) == end_ln - ln

        if (ret := self.is_parenthesized_tuple()) is not None:
            if ret:
                return True

        elif (ret := self.is_enclosed_matchseq()) is not None:
            if ret:
                return True

        last_ln = ln
        lines   = self.root._lines

        if isinstance(ast, Call):
            children = [ast.func, mock(f=mock(loc=self._loc_Call_pars(), is_enclosed=lambda: True))]
        elif isinstance(ast, Subscript):
            children = [ast.value, mock(f=mock(loc=self._loc_Subscript_brackets(), is_enclosed=lambda: True))]
        elif isinstance(ast, MatchClass):
            children = [ast.cls, mock(f=mock(loc=self._loc_MatchClass_pars(), is_enclosed=lambda: True))]
        else:  # we don't check always-enclosed statement fields here because statements will never get here
            children = syntax_ordered_children(ast)

        for child in children:
            if not child or not (loc := (childf := child.f).loc) or (child_end_ln := loc.end_ln) == last_ln:
                continue

            for ln in range(last_ln, loc.ln):
                if re_line_end_cont_or_comment.match(lines[ln]).group(1) != '\\':
                    return False

            if not childf.is_enclosed():
                return False

            last_ln = child_end_ln

        for ln in range(last_ln, end_ln):  # tail
            if re_line_end_cont_or_comment.match(lines[ln]).group(1) != '\\':
                return False

        return True

    def is_enclosed_in_parents(self, field: str | None = None) -> bool:
        """Whether `self` is enclosed by some parent up the tree. This is different from `is_enclosed()` as it does not
        check for line continuations or anyting like that, just enclosing delimiters like from `Call` or `arguments`
        parentheses, `List` brackets, `FormattedValue`, parent grouping parentheses, etc... Statements do not generally
        enclose except for a few parts of things like `FunctionDef` `args` or `type_params`, `ClassDef` `bases`, etc...

        **Parameters:**
        - `field`: This is meant to allow check for nonexistent child which would go into this field of `self`. If this
            is not `None` then `self` is considered the first parent with an imaginary child being checked at `field`.

        WARNING! This will not pick up parentheses which belong to `self` and the rules for this can be confusing. E.g.
        In 'with (a): pass` the parentheses belong to the variable `a` while `with (a as b): pass` they belong to the
        `with` because `alias`es cannot be parenthesized.

        Will pick up parentheses which belong to `self` if `field` is passed because in that case `self` is considered
        the first parent and we are really considering the node which would live at `field`, whether it exists or not.
        """

        if field:
            if field != 'ctx':  # so that the `ctx` of a List is not considered enclosed
                self = mock(parent=self, pfield=astfield(field))

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

            elif (ret := parent.is_enclosed_matchseq()) is not None:
                if ret:
                    return True

            if parent.pars(True)[1]:
                return True

            self = parent

        return False

    def is_parenthesized_tuple(self) -> bool | None:
        """Whether `self` is a parenthesized `Tuple` or not, or not a `Tuple` at all.

        **Returns:**
        - `True` if is parenthesized `Tuple`, `False` if is unparenthesized `Tuple`, `None` if is not `Tuple` at all.
        """

        return self._is_parenthesized_seq() if isinstance(self.a, Tuple) else None

    def is_enclosed_matchseq(self) -> bool | None:
        """Whether `self` is an enclosed `MatchSequence` or not, or not a `MatchSequence` at all (can be pars '()' or
        brackets '[]').

        **Returns:**
        - `True` if is enclosed `MatchSequence`, `False` if is unparenthesized `MatchSequence`, `None` if is not
            `MatchSequence` at all.
        """

        if not isinstance(self.a, MatchSequence):
            return None

        ln, col, _, _ = self.loc
        lpar          = self.root._lines[ln][col]

        if lpar == '(':
            return self._is_parenthesized_seq('patterns')
        if lpar == '[':
            return self._is_parenthesized_seq('patterns', '[', ']')

        return False

    def is_empty_set_call(self) -> bool:
        """Whether `self` is an empty `set()` call."""

        return (isinstance(ast := self.a, Call) and not ast.args and not ast.keywords and
                isinstance(func := ast.func, Name) and func.id == 'set' and isinstance(func.ctx, Load))

    def is_empty_set_seq(self) -> bool:
        """Whether `self` is an empty `Set` from an empty sequence, recognized are `{*()}`, `{*[]}` and `{*{}}`."""

        return (isinstance(ast := self.a, Set) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and
                ((isinstance(v := e0.value, (Tuple, List)) and not v.elts) or (isinstance(v, Dict) and not v.keys)))

    def is_elif(self) -> bool | None:
        """Whether `self` is an `elif` or not, or not an `If` at all.

        **Returns:**
        - `True` if is 'elif' `If`, `False` if is normal `If`, `None` if is not `If` at all.
        """

        return self.root._lines[(loc := self.loc).ln].startswith('elif', loc.col) if isinstance(self.a, If) else None

    def is_solo_class_base(self) -> bool:
        """Whether `self` is a solo `ClassDef` base in list without any keywords."""

        return ((parent := self.parent) and self.pfield.name == 'bases' and len((parenta := parent.a).bases) == 1 and
                not parenta.keywords)

    def is_solo_call_arg(self) -> bool:
        """Whether `self` is a solo `Call` non-keyword argument."""

        return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(parenta := parent.a, Call) and
                not parenta.keywords and len(parenta.args) == 1)

    def is_solo_call_arg_genexp(self) -> bool:
        """Whether `self` is the dreaded solo call non-keyword argument generator expression in `sum(i for i in a)`.
        This function doesn't say it shares its parentheses or not, so could still be `sum((i for i in a))` or even
        `sum(((i for i in a)))`."""

        return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(self.a, GeneratorExp) and
                isinstance(parenta := parent.a, Call) and not parenta.keywords and len(parenta.args) == 1)

    def is_solo_matchcls_pat(self) -> bool:
        """Whether `self` is a solo `MatchClass` non-keyword pattern. The solo `Constant` held by a `MatchValue`
        qualifies as `True` for this check if the `MatchValue` does."""

        if not (parent := self.parent):
            return False

        if isinstance(parenta := parent.a, MatchValue):
            self = parent

        return ((parent := self.parent) and self.pfield.name == 'patterns' and
                isinstance(parenta := parent.a, MatchClass) and not parenta.kwd_patterns and len(parenta.patterns) == 1)

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

        if docstr is None:
            docstr = self.get_option('docstr')

        strict = docstr == 'strict'
        lines  = self.root._lines
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
                    lns.difference_update(_multiline_str_continuation_lns(lines, *f.loc))

            elif isinstance(a, (JoinedStr, TemplateStr)):
                lns.difference_update(_multiline_fstr_continuation_lns(lines, *f.loc))

                walking.send(False)  # skip everything inside regardless, because it is evil

        return lns

    def pars(self, count: bool = False, *, shared: bool = True, pars: bool = True,
             ) -> fstloc | tuple[fstloc | None, int] | None:
        """Return the location of enclosing grouping parentheses if present. Will balance parentheses if `self` is an
        element of a tuple and not return the parentheses of the tuple. Likwise will not return the parentheses of an
        enclosing `arguments` parent or class bases list. Only works on (and makes sense for) `expr` or `pattern` nodes,
        otherwise returns `self.bloc`. Also handles special case of a single generator expression argument to a function
        sharing parameters with the call arguments.

        **Parameters:**
        - `count`: `True` means return the number of parentheses along with the location, otherwise just the location.
        - `shared`: If `True` then will include parentheses of a single call argument generator expression if they are
            shared with the call arguments enclosing parentheses, return -1 count in this case. If `False` then Does not
            return these, and thus not a full valid `GeneratorExp` location. Is not checked at all if `pars=False`.
        - `pars`: `True` means return parentheses if present and `self.bloc` otherwise, `False` always `self.bloc`. This
            parameter exists purely for convenience.

        **Returns:**
        - `fstloc | None`: Location of enclosing parentheses if present else `self.bloc` (which can be `None`). If you
            don't need an exact count of parentheses and just need to know if there are or not then the return can be
            checked if `fst.pars() is fst.bloc`. If there are no parentheses then `.bloc` is guaranteed to be returned
            identically. This can also be used to check for negative count in the case of `shared=False` via
            `fst.pars() > fst.bloc`.
        - `(fstloc, count)`: Location of enclosing parentheses or `self.bloc` and number of nested parenthesess found
            (if requested with `count`). `count` can be -1 in the case of a `GeneratorExp` sharing parentheses with
            `Call` `arguments` if it is the only argument, but only if these parentheses are explicitly excluded with
            `shared=False`.
        """

        if not pars or not isinstance(self.a, PARENTHESIZABLE):  # pars around all `alias`es or `withitem`s are considered part of the parent even if there is only one of those elements which looks parenthesized
            return (self.bloc, 0) if count else self.bloc

        key = 'parsS' if shared else 'parsN'

        try:
            cached = self._cache[key]
        except KeyError:
            pass
        else:
            return cached if count else cached[0]

        rpars = _next_pars(self.root._lines, *self.bloc[2:], *self._next_bound())

        if (lrpars := len(rpars)) == 1:  # no pars on right
            if not shared and self.is_solo_call_arg_genexp():
                ln, col, end_ln, end_col = self.bloc
                locncount                = (fstloc(ln, col + 1, end_ln, end_col - 1), -1)

            else:
                locncount = (self.bloc, 0)

            self._cache[key] = locncount

            return locncount if count else locncount[0]

        lpars = _prev_pars(self.root._lines, *self._prev_bound(), *self.bloc[:2])

        if (llpars := len(lpars)) == 1:  # no pars on left
            locncount = self._cache[key] = (self.bloc, 0)

            return locncount if count else self.bloc

        if llpars <= lrpars and (self.is_solo_call_arg() or self.is_solo_class_base() or self.is_solo_matchcls_pat()):
            llpars -= 1

        if llpars != lrpars:  # unbalanced pars so we know we can safely use the lower count
            loc = fstloc(*lpars[npars], *rpars[npars]) if (npars := min(llpars, lrpars) - 1) else self.bloc
        else:
            loc = fstloc(*lpars[npars], *rpars[npars]) if (npars := llpars - 1) else self.bloc

        locncount = self._cache[key] = (loc, npars)

        return locncount if count else loc

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
        """Offset `AST` node positions in the tree on or after (ln, col) by (delta line, col_offset) (column byte
        offset).

        This only offsets the positions in the `AST` nodes, doesn't change any text, so make sure that is correct before
        getting any `FST` locations from affected nodes otherwise they will be wrong.

        Other nodes outside this tree might need offsetting so use only on root unless special circumstances.

        If offsetting a zero-length node (which can result from deleting elements of an unparenthesized tuple), both the
        start and end location will be moved according to `tail` and `head` rules if exactly at offset point, see
        "Behavior" below.

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
        - `self_`: Whether to offset self or not (will recurse into children regardless unless is `self` is `exclude`).

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
        colo = (-col if col <= 0 else  # yes, -0 to not look up 0
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

    def parenthesize(self, *, force: bool = False) -> bool:
        """Parenthesize node if it MAY need it. Will not parenthesize atoms which are always enclosed like `List` unless
        `force=True`. Will add parentheses to unparenthesized `Tuple` adjusting the node location.

        **Parameters:**
        - `force`: If `True` then will add another layer of parentheses regardless if any already present.

        **Returns:**
        - `bool`: Whether parentheses added or not.
        """

        if self.is_atom(enclosed=True):
            if not force:
                return False

            self._parenthesize_grouping()

            return True

        if isinstance(self.a, Tuple):
            self._parenthesize_tuple()
        else:
            self._parenthesize_grouping()

        return True

    def unparenthesize(self, *, tuple_: bool = False) -> bool:
        """Remove all parentheses from node if present. Normally removes just grouping parentheses but can also remove
        tuple parentheses if `tuple_=True`.

        **Parameters:**
        - `tuple_`: If `True` then will remove parentheses from a parenthesized `Tuple`, otherwise only removes grouping
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
        _loc_withitem,
        _loc_match_case,
        _loc_Call_pars,
        _loc_Subscript_brackets,
        _loc_MatchClass_pars,
        _dict_key_or_mock_loc,
        _touch,
        _set_end_pos,
        _set_block_end_from_last_child,
        _maybe_add_comma,
        _maybe_add_singleton_tuple_comma,
        _maybe_fix_tuple,
        _maybe_fix_set,
        _maybe_fix_elif,
        _maybe_fix,
        _is_parenthesized_ImportFrom_names,
        _is_parenthesized_With_items,
        _is_parenthesized_seq,
        _parenthesize_grouping,
        _parenthesize_tuple,
        _unparenthesize_grouping,
        _unparenthesize_tuple,
        _normalize_block,
        _elif_to_else_if,
        _reparse_docstrings,
        _make_fst_and_dedent,
    )

    from .fst_parse import (
        _parse_expr,
        _parse_slice,
        _parse_comprehension,
        _parse_arguments,
        _parse_arguments_lambda,
        _parse_arg,
        _parse_keyword,
        _parse_alias_maybe_star,
        _parse_alias_dotted,
        _parse_withitem,
        _parse_pattern,
        _parse_type_param,
        _code_as_expr,
        _code_as_slice,
        _code_as_comprehension,
        _code_as_arguments,
        _code_as_arguments_lambda,
        _code_as_arg,
        _code_as_keyword,
        _code_as_alias_maybe_star,
        _code_as_alias_dotted,
        _code_as_withitem,
        _code_as_pattern,
        _code_as_type_param,
        _code_as_identifier,
        _code_as_identifier_dotted,
        _code_as_identifier_maybe_star,
        _code_as_identifier_alias,
        _code_as_op,
    )

    from .fst_raw import (
        _reparse_raw,
        _reparse_raw_stmtish,
        _reparse_raw_loc,
        _reparse_raw_node,
        _reparse_raw_slice,
    )

    from .fst_slice_old import (
        _get_slice_tuple_list_or_set,
        _get_slice_empty_set,
        _get_slice_dict,
        _get_slice_stmtish,
        _put_slice_tuple_list_or_set,
        _put_slice_empty_set,
        _put_slice_dict,
        _put_slice_stmtish,
    )

    from .fst_slice import (
        _get_slice,
        _put_slice,
    )

    from .fst_one import (
        _get_one,
        _put_one,
    )

    @property
    def f(self):
        """@private"""

        raise RuntimeError("you probably think you're accessing an AST node, but you're not, "
                           "you're accessing an FST node")


from .fstlist import fstlist
from .srcedit import _src_edit  # , SrcEdit
