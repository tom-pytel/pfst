"""`FST` options stuff.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from types import MappingProxyType
from typing import Any, Iterator, Mapping

from . import fst

__all__ = ['check_options', 'filter_options']


class _ThreadOptions(threading.local):
    def __init__(self) -> None:
        self.__dict__.update(_DEFAULT_OPTIONS)


_DEFAULT_OPTIONS = {
    'raw':           False,   # True | False | 'auto'
    'trivia':        True,    # True | False | 'all?' | 'block?' | 'none?' | (True | False | 'all?' | 'block?' | 'none?', True | False | 'all?' | 'block?' | 'none?' | 'line')  - 'all', 'block' and 'none' may be followed by a '+|-[int]' ('all+1', 'block-10', 'block+')
    'coerce':        True,    # True | False
    'elif_':         True,    # True | False
    'pep8space':     True,    # True | False | 1
    'docstr':        True,    # True | False | 'strict'
    'pars':          'auto',  # True | False | 'auto'
    'pars_walrus':   False,   # True | False | None
    'pars_arglike':  True,    # True | False | None
    'norm':          False,   # True | False
    'norm_self':     None,    # True | False | None
    'norm_get':      None,    # True | False | None
    'set_norm':      'star',  # False | 'star' | 'call'
    'op_side':       'left',  # 'left' | 'right'
    'args_as':       None,    # 'pos' |'arg' |'kw' |'arg_only' |'kw_only' |'pos_maybe' |'arg_maybe' |'kw_maybe' | None
}

_ALL_OPTIONS = {*_DEFAULT_OPTIONS, 'to', 'op', 'ins_ln'}  # including dynamic non-global options

_OPTIONS = _ThreadOptions()

_SENTINEL = object()


def check_options(options: Mapping[str, Any]) -> None:
    """Make sure all options are actual options. Does not validate their actual values, just that there are no unknown
    options."""

    for o in options:
        if o not in _ALL_OPTIONS:
            raise ValueError(f'invalid option {o!r}')


def filter_options(options: Mapping[str, Any]) -> dict[str, Any]:
    """Copy just actual options from `options` and return."""

    return {o: v for o, v in options.items() if o in _ALL_OPTIONS}


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

@staticmethod
def _get_opt_eff_pars_arglike(options: Mapping[str, Any] = {}) -> object:
    """Get a the effective `pars_arglike` option if present from `options` dict or global default if option not in dict.
    Otherwise use the `pars` option, again from `options` or global default if not in `options`.

    **Parameters:**
    - `options`: Dictionary which may or may not contain the requested option.

    **Returns:**
    - `object`: The effective `pars_arglike` option. Will intentionally return the `'auto'` value from `pars` if is that
        and `pars_arglike` is `None`, so make sure to check for truthy value and not `is True`.
    """

    if (o := options.get('pars_arglike', _SENTINEL)) is not _SENTINEL:
        if o is not None:
            return o

    elif (o := _OPTIONS.pars_arglike) is not None:
        return o

    if (o := options.get('pars', _SENTINEL)) is not _SENTINEL:
        return o

    return _OPTIONS.pars


@staticmethod
def _get_opt_eff_norm_self(options: Mapping[str, Any] = {}) -> object:
    """Get a the effective `norm_self` option if present from `options` dict or global default if option not in dict.
    Otherwise use the `norm` option, again from `options` or global default if not in `options`.

    **Parameters:**
    - `options`: Dictionary which may or may not contain the requested option.

    **Returns:**
    - `object`: The effective `norm_self` option.
    """

    if (o := options.get('norm_self', _SENTINEL)) is not _SENTINEL:
        if o is not None:
            return o

    elif (o := _OPTIONS.norm_self) is not None:
        return o

    if (o := options.get('norm', _SENTINEL)) is not _SENTINEL:
        return o

    return _OPTIONS.norm


@staticmethod
def _get_opt_eff_norm_get(options: Mapping[str, Any] = {}) -> object:
    """Get a the effective `norm_get` option if present from `options` dict or global default if option not in dict.
    Otherwise use the `norm` option, again from `options` or global default if not in `options`.

    **Parameters:**
    - `options`: Dictionary which may or may not contain the requested option.

    **Returns:**
    - `object`: The effective `norm_get` option.
    """

    if (o := options.get('norm_get', _SENTINEL)) is not _SENTINEL:
        if o is not None:
            return o

    elif (o := _OPTIONS.norm_get) is not None:
        return o

    if (o := options.get('norm', _SENTINEL)) is not _SENTINEL:
        return o

    return _OPTIONS.norm


@staticmethod
def _get_opt_eff_set_norm_self(options: Mapping[str, Any] = {}) -> object:
    """Same as `_get_opt_eff_norm_self()` but if `True` then will return the value of the `set_norm` option, again from
    `options` first and global if not in `options`. A non-`True` truthy value in any of the `norm` options will prevent
    the `set_norm` value from being returned to allow override of this directly by the `norm` options.

    **Parameters:**
    - `options`: Dictionary which may or may not contain the requested option.

    **Returns:**
    - `object`: The effective `set_norm` if effective `norm_self` is `True`.
    """

    if (o := _get_opt_eff_norm_self(options)) is not True:
        return o

    if (o := options.get('set_norm', _SENTINEL)) is not _SENTINEL:
        return o

    return _OPTIONS.set_norm


@staticmethod
def _get_opt_eff_set_norm_get(options: Mapping[str, Any] = {}) -> object:
    """Same as `_get_opt_eff_norm_get()` but if `True` then will return the value of the `set_norm` option, again from
    `options` first and global if not in `options`. A non-`True` truthy value in any of the `norm` options will prevent
    the `set_norm` value from being returned to allow override of this directly by the `norm` options.

    **Parameters:**
    - `options`: Dictionary which may or may not contain the requested option.

    **Returns:**
    - `object`: The effective `set_norm` if effective `norm_get` is `True`.
    """

    if (o := _get_opt_eff_norm_get(options)) is not True:
        return o

    if (o := options.get('set_norm', _SENTINEL)) is not _SENTINEL:
        return o

    return _OPTIONS.set_norm


# ----------------------------------------------------------------------------------------------------------------------
# public FST class methods

@staticmethod
def get_options() -> dict[str, Any]:
    """Get a dictionary of **ALL** global options. These are the same `options` that can be passed to operations and
    this function returns their global defaults which are used when those options are not passed to operations or if
    they are passed with a value of `None`

    **Returns:**
    - `{option: value, ...}`: Dictionary of all global default options.

    **Examples:**

    >>> from pprint import pp
    >>> pp(FST.get_options())
    {'raw': False,
     'trivia': True,
     'coerce': True,
     'elif_': True,
     'pep8space': True,
     'docstr': True,
     'pars': 'auto',
     'pars_walrus': False,
     'pars_arglike': True,
     'norm': False,
     'norm_self': None,
     'norm_get': None,
     'set_norm': 'star',
     'op_side': 'left',
     'args_as': None}
    """

    return _OPTIONS.__dict__.copy()


@staticmethod
def get_option(option: str, options: Mapping[str, Any] = {}) -> object:
    """Get a single option from `options` dict or global default if option not in dict or is `None` there. For a
    list of options used see `options()`.

    **Parameters:**
    - `option`: Name of option to get.
    - `options`: Dictionary which may or may not contain the requested option.

    **Returns:**
    - `object`: The `option` value from the passed `options` dict, if passed and not `None` there, else the global
        default value for `option`.

    **Examples:**

    >>> FST.get_option('pars')
    'auto'

    >>> FST.get_option('pars', {'pars': True})
    True
    """

    return _OPTIONS.__dict__.get(option) if (o := options.get(option, _SENTINEL)) is _SENTINEL else o


@staticmethod
def set_options(**options) -> dict[str, Any]:
    """Set global defaults for `options` parameters.

    **Parameters:**
    - `options`: Names / values of parameters to set. These can also be passed to various methods to override the
        defaults set here for those individual operations, see `options()`.

    **Returns:**
    - `old_options`: `dict` of previous values of changed parameters, reset with `set_options(**old_options)`.

    **Examples:**

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
    """

    _options = _OPTIONS.__dict__

    try:
        old_options = {(bad := o): _options[o] for o in options}
    except KeyError:
        raise ValueError(f'invalid option {bad!r}') from None

    _options.update(options)

    return old_options


@staticmethod
@contextmanager
def options(**options) -> Iterator[dict[str, Any]]:
    """Context manager to temporarily set specified global options defaults for a group of operations.

    **WARNING!** Only the options specified in the call to this function will be returned to their original values
    when the context manager exits. Any other global options changed inside the context block will continue to have
    those values on context manager exit.

    **Options:**
    - `raw`: When to do raw source operations. This may result in more nodes changed than just the targeted one(s).
        - `False`: Do not do raw source operations. **DEFAULT**
        - `True`: Only do raw source operations.
        - `'auto'`: Only do raw source operations if the normal operation fails in a way that raw might not.
    - `trivia`: What comments and empty lines to copy / delete / overwrite when doing operations on elements which may
        have leading or trailing comments and / or empty lines. These are the values as interpreted **WHEN SET
        GLOBALLY**. If passed as a parameter to a function then if a non-tuple is passed then that becomes the leading
        trivia parameter. If a tuple is passed then both the leading and trailing from the tuple are used, unless they
        are `None` in which case the global value for that particular parameter is used.
        - `False`: Same as `(False, 'line')`.
        - `True`: Same as `('block', 'line')`. **DEFAULT**
        - `'all'`: Same as `('all', 'line')`.
        - `'block'`: Same as `('block', 'line')`.
        - `(leading, trailing)`: Tuple specifying individual behavior for leading and trailing trivia. The text
            options can also have a suffix of the form `'+/-[#]'`, meaning plus or minus an optional integer which
            indicates to include this number of leading / trailing empty lines in the trivia. The values for each
            element of the tuple can be:
            - `False`: Don't copy / delete / overwrite any trivia.
            - `True`: Means `'block'` for leading trivia, `'line'` for trailing.
            - `'all[+/-[#]]'`: Copy / delete / overwrite all leading or trailing comments regardless of if they are
                contiguous or not.
            - `'block[+/-[#]]'`: Copy / delete / overwrite a single contiguous leading or trailing block of comments
                where an empty line ends the block.
            - `'line'`: Only valid for trailing trivia, means just the comment on the last line of the element. Except
                for block statements where the last line is a child node where that comment belongs to the child
                regardless of this parameter and so will be copied / deleted / overwritten along with the block.
            - `int`: A specific line number (starting at 0) indicating the first or last line that can be copied /
                deleted / overwritten. If not interrupted by other code, will always return from / to this line
                inclusive. For trailing trivia, if this number is the last line of the element (where the line comment
                resides) then it will include that tail line comment. If it is **BEFORE** that line then the line
                comment will not be included.
    - `coerce`: Whether to allow coercion between compatible `AST` / `FST` node types on put. For example allow put a
        non-slice `expr` as a slice to something that expects a slice of `expr`s or allowing use of `arg` where
        `arguments` is expected.
        - `False`: Do not allow node type coercion, meant for strict type control.
        - `True`: Allow coercion between similar types. **DEFAULT**
    - `elif_`: How to handle lone `If` statements as the only statements in an `If` statement `orelse` field.
        - `False`: Always put as a standalone `If` statement on put.
        - `True`: If putting a single `If` statement to an `orelse` field of a parent `If` statement then
            put it as an `elif`. **DEFAULT**
    - `pep8space`: Preceding and trailing empty lines for function and class definitions.
        - `False`: No empty lines.
        - `True`: Two empty lines at module scope and one empty line in other scopes. **DEFAULT**
        - `1`: One empty line in all scopes.
    - `docstr`: Which docstrings are indentable / dedentable.
        - `False`: None.
        - `True`: All `Expr` string constants (as they serve no other coding purpose). **DEFAULT**
        - `'strict'`: Only string constants in expected docstring positions (functions, classes and top of module).
    - `pars`: How parentheses are handled, can be `False`, `True` or `'auto'`. This is for individual element
        operations, slice operations ignore this for the most part as parentheses usually cannot be removed or may need
        to be added to keep the slices usable. Raw puts generally do not have parentheses added or removed
        automatically, except maybe removed according to this from the destination node if putting to a node instead of
        a pure location. See below for `pars` behavior matrix.
        - `False`: Parentheses are not **MODIFIED**, doesn't mean remove all parentheses. Not copied with nodes or
            removed on put from destination or source. Using incorrectly can result in invalid trees.
        - `True`: Parentheses are copied with nodes, added to copies if needed and not present and removed from
            destination on put if not needed there (but not removed from source).
        - `'auto'`: Same as `True` except they are not copied with nodes and possibly removed from source on put if not
            needed (removed from destination first if needed and present on both). **DEFAULT**
    - `pars_walrus`: Whether to **ADD** parentheses to top level cut / copied `NamedExpr` nodes or not. If parentheses
        were already copied due to `pars=True` then setting this to `False` will not remove them. This is more of an
        aesthetic option as `fst` can deal with unparenthesized walruses at root level.
        - `True`: Parenthesize cut / copied `NamedExpr` walrus expressions.
        - `False`: Do not parenthesize cut / copied `NamedExpr` walrus expressions. **DEFAULT**
        - `None`: Parenthesize according to the `pars` option (`True` and `'auto'` parenthesize, `False` does not).
    - `pars_arglike`: Whether to **ADD** parentheses to argumentlike-only expressions (`*not a`, `*b or c`) when cut /
        copied either as single element or as part of a slice. If parentheses were already present then setting this
        to `False` will not remove them. Unlike `pars_walrus` this is **NOT** mostly an aesthetic option as
        unparenthesized arglike-only expressions are invalid everywhere except in `Call.args`, `ClassDef.bases` or an
        unparenthesized `Subscript.slice` `Tuple`.
        - `True`: Parenthesize cut / copied argumentlike expressions. **DEFAULT**
        - `False`: Do not parenthesize cut / copied argumentlike expressions.
        - `None`: Parenthesize according to the `pars` option (`True` and `'auto'` parenthesize, `False` does not).
    - `norm`: Default normalize option for return from `get()` functions and `self` target. Determines how `AST`s which
        would otherwise be invalid because of an operation are handled. Mostly how zero or sometimes one-length
        sequences which normally cannot be zero or one length are left or returned, e.g. zero-length `Set`. This option
        can be overridden individually for the two cases of `norm_self` (target) and `norm_get` (return from any get
        operation).
        - `False`: Allow the `AST` to go to an unsupported length or state and become invalid. A `Set` will result
            in empty curlies which reparse to a `Dict`. A `MatchOr` can go to 1 or zero length. Other `AST` types
            can also go to zero length. Useful for easier editing. **DEFAULT**
        - `True`: Do not allow the `AST` to go to an unsupported length or state. Can result in an exception being
            thrown if no alternative exists. A `Set` which results in zero length gets converted to `{*()}`.
        - `str`: In some cases an alternate representation can be specified instead of just `True`, e.g. `'call'`
            for `Set` operations.
    - `norm_self`: Override for `norm` which only applies to a target `self` on which an operation is being carried
        out. If this is `None` then `norm` is used.
    - `norm_get`: Override for `norm` which only applies to the return value from any get operation. If this is `None`
        then `norm` is used.
    - `set_norm`: The alternate representation for an empty `Set` normalization by `norm`. This can also be set to
        `False` to disable normalization for all operations on a `Set` (unless one of the `norm` options is set to
        one of these string modes).
        - `'star'`: Starred sequence `{*()}` returned or used for empty `self`. **DEFAULT**
        - `'call'`: `set()` call returned and used for empty `self`.
        - `False`: No `Set` normalization regardless of `norm` or `norm_*` options, just leave or return an invalid
            `Set` object.
    - `op_side`: When doing slice operations on a `BoolOp` or a `Compare` it may be necessary to specify which side
        operator is to be deleted or inserted before or after. This can take the values of `'left'` or `'right'` and
        specifies which side operator to delete for delete operations. For insert operations this specifies whether
        to insert before an operator `'left'` or operand `'right'`, roughly translating to which side operator is
        treated as part of the operator+operand unit. This option is treated as a hint and may be overridden by
        source code passed to the slice operation or slice position constraints, it will never raise an error if
        set incompatible with what the operation needs. When inserting into a `Compare` a non-global `op` option
        may be necessary to specify extra missing operator to add if a dangling operator is not passed in the source
        to insert.
        - `'left'`: Delete preceding operator on left side of slice or insert before preceding operator. **DEFAULT**
        - `'right'`: Delete trailing operator on right side of slice or insert after preceding operator.
    - `args_as`: Conversion for argument types on `argument` node slice operations. This is mostly meant for per-call
        use but is a global option in order to allow `with options(args_as=?): ...`. When used on a slice get it
        converts the gotten slice. When used on a slice put, it converts the slice being put before the attempted put.
        - `'pos'`: Convert all arguments to `posonlyargs` if possible, if not then error. If `vararg` or `kwarg` present
            then will error.
        - `'arg'`: Convert all arguments to `args` if possible, if not then error. A `vararg` is allowed but if present
            then will prevent any present `kwonlyargs` from being converted and in this case will error. If `kwarg` is
            present then will error.
        - `'kw'`: Convert all arguments to `kwonlyargs` if possible, if not then error. A `kwarg` is allowed and
            will not prevent any conversion as it is always follows all other arguments. If `vararg` is present then
            will error.
        - `'arg_only'`: Same as `arg` except does not allow a `vararg` and if present will error.
        - `'kw_only'`: Same as `kw` except does not allow a `kwarg` and if present will error.
        - `'pos_maybe'`: Attempt to convert all arguments to `posonlyargs`. `args` can always be converted but if
            `kwonlyargs` cannot be because of a `vararg` or default value incompatibilities then they will not be
            converted and there will not be an error. `kwarg` is left in place.
        - `'arg_maybe'`: Attempt to convert all arguments to `args`. `posonlyargs` can always be converted but if
            `kwonlyargs` cannot be because of a `vararg` or default value incompatibilities then they will not be
            converted and there will not be an error. `kwarg` is left in place.
        - `'kw_maybe'`: Attempt to convert all arguments to `kwonlyargs`. If `vararg` is present the `posonlyargs` and
            `args` are not converted, but `posonlyargs` will be converted in this case to `args`. `kwarg` is left in
            place.

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
    - `'+[#]'` On copy and delete an extra number of lines after any comments specified by the `#`. If no number is
        specified and just a `'+'` then all empty lines will be copied / deleted.
    - `'-[#]'` On delete but not copy, an extra number of lines after any comments specified by the `#`. If no
        number is specified and just a `'-'` then all empty lines will be deleted.

    **Examples:**

    >>> print(FST.get_option('pars'), FST.get_option('elif_'))
    auto True

    >>> with FST.options(pars=False, elif_=False):
    ...     print(FST.get_option('pars'), FST.get_option('elif_'))
    False False

    >>> print(FST.get_option('pars'), FST.get_option('elif_'))
    auto True
    """

    old_options = fst.FST.set_options(**options)

    try:
        yield MappingProxyType(old_options)  # if user messed with these it could get confusing
    finally:
        _OPTIONS.__dict__.update(old_options)
