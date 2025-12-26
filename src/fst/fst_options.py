"""`FST` options stuff.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from types import MappingProxyType
from typing import Any, Iterator, Mapping

from . import fst

__all__ = ['check_options']


class _ThreadOptions(threading.local):
    def __init__(self) -> None:
        self.__dict__.update(_DEFAULT_OPTIONS)


_DEFAULT_OPTIONS = {
    'raw':           False,   # True | False | 'auto'
    'trivia':        True,    # True | False | 'all?' | 'block?' | (True | False | 'all?' | 'block?', True | False | 'all?' | 'block?' | 'line')  - 'all' and 'block' may be followed by a '+|-[int]' ('all+1', 'block-10', 'block+')
    'coerce':        True,    # True | False
    'elif_':         True,    # True | False
    'pep8space':     True,    # True | False | 1
    'docstr':        True,    # True | False | 'strict'
    'pars':          'auto',  # True | False | 'auto'
    'pars_walrus':   True,    # True | False | None
    'pars_arglike':  True,    # True | False | None
    'norm':          False,   # True | False
    'norm_self':     None,    # True | False | None
    'norm_get':      None,    # True | False | None
    'norm_put':      None,    # True | False | None
    'set_norm':     'both',   # False | 'star' | 'call' | 'both'
    'op_side':      'left',   # 'left' | 'right'
}

_ALL_OPTIONS = {*_DEFAULT_OPTIONS, 'to', 'op', 'ins_ln'}  # including dynamic non-global options

_OPTIONS = _ThreadOptions()


def check_options(options: Mapping[str, Any]) -> None:
    """Make sure all options are actual options. Does not validate their actual values, just that there are no unknown
    options."""

    for o in options:
        if o not in _ALL_OPTIONS:
            raise ValueError(f'invalid option {o!r}')


# ----------------------------------------------------------------------------------------------------------------------
# FST class methods

@staticmethod
def get_options() -> dict[str, Any]:
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

    >>> from pprint import pp
    >>> pp(FST.get_options())
    {'raw': False,
     'trivia': True,
     'coerce': True,
     'elif_': True,
     'pep8space': True,
     'docstr': True,
     'pars': 'auto',
     'pars_walrus': True,
     'pars_arglike': True,
     'norm': False,
     'norm_self': None,
     'norm_get': None,
     'norm_put': None,
     'set_norm': 'both',
     'op_side': 'left'}
    """

    return _OPTIONS.__dict__.copy()


@staticmethod
def get_option(option: str, options: Mapping[str, Any] = {}) -> object:
    """Get a single option from `options` dict or global default if option not in dict or is `None` there. For a
    list of options used see `options()`.

    **Parameters:**
    - `option`: Name of option to get, see `options()`.
    - `options`: Dictionary which may or may not contain the requested option.

    **Returns:**
    - `Any`: The `option` value from the passed `options` dict, if passed and not `None` there, else the global
        default value for `option`.

    **Examples:**

    >>> FST.get_option('pars')
    'auto'

    >>> FST.get_option('pars', {'pars': True})
    True

    >>> FST.get_option('pars', {'pars': None})
    'auto'
    """

    return _OPTIONS.__dict__.get(option) if (o := options.get(option)) is None else o


@staticmethod
def set_options(**options) -> dict[str, Any]:
    """Set global defaults for `options` parameters.

    **Parameters:**
    - `options`: Names / values of parameters to set. These can also be passed to various methods to override the
        defaults set here for those individual operations, see `options()`.

    **Returns:**
    - `options`: `dict` of previous values of changed parameters, reset with `set_options(**options)`.

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
        - `False`: Do not do raw source operations.
        - `True`: Only do raw source operations.
        - `'auto'`: Only do raw source operations if the normal operation fails in a way that raw might not.
    - `trivia`: What comments and empty lines to copy / delete / overwrite when doing operations on elements which may
        have leading or trailing comments and / or empty lines. These are the values as interpreted when set globally.
        If passed as a parameter to a function then if a non-tuple is passed then that becomes the leading trivia
        parameter. If a tuple is passed then both the leading and trailing from the tuple are used, unless they are
        `None` in which case the global value for that particular parameter is used.
        - `False`: Same as `(False, 'line')`.
        - `True`: Same as `('block', 'line')`.
        - `'all'`: Same as `('all', 'line')`.
        - `'block'`: Same as `('block', 'line')`.
        - `(leading, trailing)`: Tuple specifying individual behavior for leading and trailing trivia. The text
            options can also have a suffix of the form `'+/-[#]'`, meaning plus or minus an optional integer which
            adds behavior for leading or trailing empty lines, explained below. The values for each element of the
            tuple can be:
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
                inclusive. For trailing trivia, if this number is the same line as the element starts then it will
                include any comment present on the element line. If it is **BEFORE** that line then the line comment
                will not be included.
    - `coerce`: Whether to allow coercion between compatible `AST` / `FST` types on put. For example allow put a
        non-slice `expr` as a slice to something that expects a slice of `expr`s or allowing use of `arg` where
        `arguments` is expected.
    - `elif_`: How to handle lone `If` statements as the only statements in an `If` statement `orelse` field.
        - `False`: Always put as a standalone `If` statement.
        - `True`: If putting a single `If` statement to an `orelse` field of a parent `If` statement then
            put it as an `elif`.
    - `pep8space`: Preceding and trailing empty lines for function and class definitions.
        - `False`: No empty lines.
        - `True`: Two empty lines at module scope and one empty line in other scopes.
        - `1`: One empty line in all scopes.
    - `docstr`: Which docstrings are indentable / dedentable.
        - `False`: None.
        - `True`: All `Expr` string constants (as they serve no other coding purpose).
        - `'strict'`: Only string constants in expected docstring positions (functions, classes and top of module).
    - `pars`: How parentheses are handled, can be `False`, `True` or `'auto'`. This is for individual element
        operations, slice operations ignore this as parentheses usually cannot be removed or may need to be added to
        keep the slices usable. Raw puts generally do not have parentheses added or removed automatically, except
        maybe removed according to this from the destination node if putting to a node instead of a pure location.
        - `False`: Parentheses are not **MODIFIED**, doesn't mean remove all parentheses. Not copied with nodes or
            removed on put from source or destination. Using incorrectly can result in invalid trees.
        - `True`: Parentheses are copied with nodes, added to copies if needed and not present, removed from
            destination on put if not needed there (but not source).
        - `'auto'`: Same as `True` except they are not returned with a copy and possibly removed from source
            on put if not needed (removed from destination first if needed and present on both).
    - `pars_walrus`: Whether to ADD parentheses to top level cut / copied `NamedExpr` nodes or not. If parentheses
        were already copied due to `pars=True` then setting this to `False` will not remove them.
        - `True`: Parenthesize cut / copied `NamedExpr` walrus expressions.
        - `False`: Do not parenthesize cut / copied `NamedExpr` walrus expressions.
        - `None`: Parenthesize according to the `pars` option.
    - `pars_arglike`: Whether to ADD parentheses to argument-like expressions (`*not a`, `*b or c`) when cut /
        copied either as single element or as part of a slice. If parentheses were already present then setting this
        to `False` will not remove them.
        - `True`: Parenthesize cut / copied argument-like expressions.
        - `False`: Do not parenthesize cut / copied argument-like expressions.
        - `None`: Parenthesize according to the `pars` option.
    - `norm`: Default normalize option for puts, gets and self target. Determines how `AST`s which would otherwise
        be invalid because of an operation are handled. Mostly how zero or sometimes one-length elements which
        normally cannot be zero or one length are left / put / returned, e.g. zero-length `Set`. This option can be
        overridden individually for the three cases of `norm_self` (target), `norm_get` (return from a `get()`) and
        `norm_put` (what is being put if it is invalid or an alternate representation).
        - `False`: Allow the `AST` to go to an unsupported length or state and become invalid. A `Set` will result
            in empty curlies which reparse to a `Dict`. A `MatchOr` can go to 1 or zero length. Other `AST` types
            can also go to zero length. Useful for easier editing.
        - `True`: Do not allow the `AST` to go to an unsupported length or state. Can result in an exception being
            thrown no alternative exists or an alternate representation being used or accepted, e.g. A `Set` which
            results in zero length gets converted to `{*()}`.
        - `str`: In some cases an alternate representation can be specified instead of just `True`, e.g. `'call'`
            for `Set` operations.
    - `norm_self`: Override for `norm` which only applies to a target `self` on which an operation is being carried
        out. If this is `None` then `norm` is used.
    - `norm_get`: Override for `norm` which only applies to the return value from a `get()` operation. If this is
        `None` then `norm` is used.
    - `norm_put`: Override for `norm` which only applies to the value to put for a `put()` operation. If this is
        `None` then `norm` is used.
    - `set_norm`: The alternate representation for an empty `Set` normalization by `norm`. This can also be set to
        `False` to disable normalization for all operations on a `Set` (unless one of the `norm` options is set to
        one of these string modes).
        - `'star'`: Starred sequence `{*()}` returned, this or other starred sequences `{*[]}` and `{*{}}` accepted
            to mean empty set on put operations.
        - `'call'`: `set()` call returned and recognized as empty.
        - `'both'`: Both `'star'` and `'call'` recognized on put as empty, `'start'` used for return from get
            operation and normalization of `self`.
        - `False`: No `Set` normalization regardless of `norm` or `norm_*` options, just leave or return an invalid
            `Set` object.
    -`op_side`: When doing slice operations on a `BoolOp` or a `Compare` it may be necessary to specify which side
        operator is to be deleted or inserted before or after. This can take the values of `'left'` or `'right'` and
        specifies which side operator to delete for delete operations. For insert operations this specifies whether
        to insert before an operator `'left'` or operand `'right'`, roughly translating to which side operator is
        treated as part of the operator+operand unit. This option is treated as a hint and may be overridden by
        source code passed to the slice operation or slice position constraints, it will never raise an error if
        set incompatible with what the operation needs. When inserting into a `Compare` a non-global `op` option
        may be necessary to specify extra missing operator to add if a dangling operator is not passed in the source
        to insert.
        - `'left'`: Delete preceding operator on left side of slice or insert before preceding operator.
        - `'right'`: Delete trailing operator on right side of slice or insert after preceding operator.

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
