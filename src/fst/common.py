"""Low level common data and functions that are not part of or aware of the FST class."""

import re
import sys
from functools import wraps
from math import log10
from typing import Callable, NamedTuple

from .asttypes import AST
from .astutil import constant

try:
    from tokenize import FSTRING_START, FSTRING_END

    try:
        from tokenize import TSTRING_START, TSTRING_END

        FTSTRING_START_TOKENS = (FSTRING_START, TSTRING_START)
        FTSTRING_END_TOKENS = (FSTRING_END, TSTRING_END)

    except ImportError:
        TSTRING_START = TSTRING_END = None
        FTSTRING_START_TOKENS = (FSTRING_START,)
        FTSTRING_END_TOKENS = (FSTRING_END,)

except ImportError:
    FSTRING_START = FSTRING_END = TSTRING_START = TSTRING_END = None
    FTSTRING_START_TOKENS = FTSTRING_END_TOKENS = ()

__all__ = [
    'NodeError',
    'astfield',
    'fstloc',
    'fstlocn',
    'srcwpos',
    'nspace',
    'pyver',
    'shortstr',
    'next_frag',
    'prev_frag',
    'next_find',
    'prev_find',
    'next_find_re',
    'next_delims',
    'prev_delims',
]


PYVER  = sys.version_info[:2]
PYLT11 = PYVER < (3, 11)
PYLT12 = PYVER < (3, 12)
PYLT13 = PYVER < (3, 13)
PYLT14 = PYVER < (3, 14)
PYGE11 = PYVER >= (3, 11)
PYGE12 = PYVER >= (3, 12)
PYGE13 = PYVER >= (3, 13)
PYGE14 = PYVER >= (3, 14)

re_empty_line_start           = re.compile(r'[ \t]*')            # start of completely empty or space-filled line (from start pos, start of line indentation)
re_empty_line                 = re.compile(r'[ \t]*$')           # completely empty or space-filled line (from start pos, start of line indentation)
re_comment_line_start         = re.compile(r'[ \t]*#')           # empty line preceding a comment
re_line_continuation          = re.compile(r'[^#]*\\$')          # line continuation with backslash not following a comment start '#' (from start pos, assumed no asts contained in line)
re_empty_space                = re.compile(r'\s*$')              # completely empty or space-filled line (from start pos, start of line indentation, any space, not just line indenting space)
re_empty_line_or_cont         = re.compile(r'[ \t]*(\\)?$')      # empty line or line continuation
re_empty_line_cont_or_comment = re.compile(r'[ \t]*(\\|#.*)?$')  # empty line or line continuation or a pure comment line
re_line_end_cont_or_comment   = re.compile(r'.*?(\\|#.*)?$')     # line end line continuation or a comment, the first part is mostly meant to skip closing parentheses and separators, not expression stuff

_re_next_frag                     = re.compile(r'\s*([^\s#\\]+)')          # next non-space non-continuation non-comment code text, don't look into strings with this!
_re_next_frag_or_comment          = re.compile(r'\s*([^\s#\\]+|#.*)')      # next non-space non-continuation code or comment text, don't look into strings with this!
_re_next_frag_or_lcont            = re.compile(r'\s*([^\s#\\]+|\\$)')      # next non-space non-comment code including logical line end, don't look into strings with this!
_re_next_frag_or_comment_or_lcont = re.compile(r'\s*([^\s#\\]+|#.*|\\$)')  # next non-space non-continuation code or comment text including logical line end, don't look into strings with this!


class NodeError(Exception):
    """General FST node error."""

    rawable: bool  ; """Whether the operation that caused this error can be retried in raw mode. @private"""

    def __init__(self, *args: object, rawable: bool = False) -> None:
        """@private"""

        super().__init__(*args)

        self.rawable = rawable


class astfield(NamedTuple):
    """Name and optional index indicating a field location in an `AST` (or `FST`) node."""

    name: str                ; """The actual field name, a la "body", "value", "orelse", etc..."""
    idx:  int | None = None  ; """The index if the field is a list, else `None`."""

    def __repr__(self) -> str:
        return f'astfield({self.name!r})' if (idx := self.idx) is None else f'astfield({self.name!r}, {idx})'

    def get(self, parent: AST) -> AST | constant:
        """Get child node at this field in the given `parent`."""

        return getattr(parent, self.name) if self.idx is None else getattr(parent, self.name)[self.idx]

    def get_default(self, parent: AST, default: AST | constant = False) -> AST | constant:
        """Get child node at this field in the given `parent`. Return `default` if not found instead of raising
        `AttributError` or `IndexError`, `False` works well because not normally found in locations where `AST` nodes
        can reside in `AST` trees."""

        return (getattr(parent, self.name, default) if (idx := self.idx) is None else
                default if (body := getattr(parent, self.name, False)) is False or idx >= len(body) else
                body[idx])

    def set(self, parent: AST, child: AST) -> None:
        """Set `child` node at this field in the given `parent`."""

        if self.idx is None:
            setattr(parent, self.name, child)
        else:
            getattr(parent, self.name)[self.idx] = child


class fstloc(NamedTuple):
    """Full location span."""

    ln:      int  ; """Start line number."""
    col:     int  ; """Start column."""
    end_ln:  int  ; """End line number (inclusive)."""
    end_col: int  ; """End column (exclusive)."""

    bln      = property(lambda self: self.ln)       ; """Alias for `ln`."""  # for convenience
    bcol     = property(lambda self: self.col)      ; """Alias for `col`."""
    bend_ln  = property(lambda self: self.end_ln)   ; """Alias for `end_ln`."""
    bend_col = property(lambda self: self.end_col)  ; """Alias for `end_col`."""
    loc      = property(lambda self: self)          ; """To be able to use as `FST.loc`."""
    bloc     = loc                                  ; """Alias for `loc`."""

    is_FST   = False                                ; """@private"""  # for quick checks vs. `FST`

    def __repr__(self) -> str:
        ln, col, end_ln, end_col = self

        return f'fstloc({ln}, {col}, {end_ln}, {end_col})'


class fstlocn(fstloc):
    """Version of `fstloc` with a namespace, used for `pars().n`."""

    def __repr__(self) -> str:
        ln, col, end_ln, end_col = self
        ns = ', '.join(f'{n}={v!r}' for n, v in self.__dict__.items())

        return (f'fstlocn({ln}, {col}, {end_ln}, {end_col}, {ns})' if ns else
                f'fstlocn({ln}, {col}, {end_ln}, {end_col})')

    def __new__(cls, ln: int, col: int, end_ln: int, end_col: int, **kwargs) -> 'fstlocn':
        self = fstloc.__new__(cls, ln, col, end_ln, end_col)

        self.__dict__.update(kwargs)

        return self


class srcwpos(NamedTuple):
    """@private"""

    ln:  int
    col: int
    src: str


class nspace:
    """Simple namespace class used for several things.

    @private
    """

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)


assert sys.version_info[0] == 3, 'pyver() assumes python major version 3'

_pyver_registry = {}  # {'__module__.__qualname__': [(func, (ge, lt) | unbound +ge | unbound -lt]), ...}
_pyver = sys.version_info[1]  # just the minor version

def pyver(
    func: Callable | None = None, *, ge: int | None = None, lt: int | None = None, else_: Callable | None = None
) -> Callable:
    """Decorator to restrict to a range of python versions. If the version of python does not match the parameters
    passed then will return a previously registered function that does match or `None` if no matching function. Does not
    wrap the functions but rather returns the originals to not add unnecessary overhead.

    **Note:** Yes we are only comparing minor version, if python goes to major 4 then this will be the least of your
    incompatibilities.

    **Parameters:**
    - `func`: The function (or class) being decorated.
    - `ge`: Minimum allowed version of python for this function. `None` for unbound below `lt`.
    - `lt`: Minimum NOT allowed version of python for this function (exclusive, LESS THAN THIS). `None` for unbound
        above `ge`. Both `ge` and `lt` cannot be `None` at the same time.
    - `else_`: If the current python version does not match the specified `ge` and `lt` then use this function instead
        of a standin which raises and error.

    @private
    """

    if ge is None and lt is None:
        raise ValueError("parameters 'ge' and 'lt' cannot both be None at the same time")

    if ge is not None and lt is not None and ge >= lt:
        raise ValueError(f"invalid 'ge' / 'lt' values, {ge} is not smaller than {lt}")

    def decorator(func: Callable) -> Callable:
        key = f'{func.__module__}.{func.__qualname__}'
        ret = func

        if ge is None:
            newver = (func, -lt)

            if _pyver >= lt:
                ret = else_

        elif lt is None:
            newver = (func, ge)

            if _pyver < ge:
                ret = else_

        else:
            newver = (func, (ge, lt))

            if not ge <= _pyver < lt:
                ret = else_

        if not (vers := _pyver_registry.get(key)):
            _pyver_registry[key] = vers = [newver]

        else:
            for verfunc, ver in vers:
                if isinstance(ver, tuple):
                    if (ge is None or ge < ver[1]) and (lt is None or lt > ver[0]):
                        raise ValueError(f"overlap with previously registered version range [3.{ver[0]}, 3.{ver[1]})")

                    if ver[0] <= _pyver < ver[1]:
                        ret = verfunc

                elif ver < 0:  # unbound less than minus this version
                    ver = -ver

                    if ge is None or ge < ver:
                        raise ValueError(f"overlap with previously registered version range < 3.{ver})")

                    if _pyver < ver:
                        ret = verfunc

                else:  # unbound greater than this version
                    if lt is None or lt > ver:
                        raise ValueError(f"overlap with previously registered version range >= 3.{ver})")

                    if ver <= _pyver:
                        ret = verfunc

            vers.append(newver)

        if ret is None:
            @wraps(func)
            def ret(*args: object, **kwargs) -> None:
                raise RuntimeError(f'missing version of {key} for this python version 3.{_pyver}')

        return ret

    return decorator if func is None else decorator(func)


def shortstr(s: str, maxlen: int = 64) -> str:
    """Return string of maximum length `maxlen`, shortening if necessary to "start .. [X chars] .. end".

    @private
    """

    if (l := len(s)) <= maxlen:
        return s

    t = maxlen - 16 - (int(log10(l)) + 1)

    return f'{s[:(t+1)//2]} .. [{l} chars] .. {s[-(t//2):]}'


def next_frag(
    lines: list[str], ln: int, col: int, end_ln: int, end_col: int, comment: bool = False, lcont: bool | None = False
) -> srcwpos | None:
    """Get next fragment of source which may or may not include comments or line continuation backslashes. May be
    restricted to bound or further restricted to not exceed logical line. Assuming start pos not inside str or comment.
    The fragment is not necessarily AST stuff, it can be commas, colons, the 'try' keyword, etc... Fragments can include
    multiple AST nodes in return str if there are no spaces between them like 'a+b'.

    **WARNING!** Make sure the search span does not include any AST strings as those can cause false positives for
    comment hash and line continuation backslashes.

    **Parameters:**
    - `comment`: Whether to return comments found, which will be the whole comment.
    - `lcont`: Whether to return line continuations found (backslash at end of line) if `True`, skip over them if
        `False`, or skip over them and restrict search to logical line `None`.

    @private
    """

    re_pat = (
        (_re_next_frag_or_comment_or_lcont if comment else _re_next_frag_or_lcont)
        if lcont else
        (_re_next_frag_or_comment if comment else _re_next_frag)
    )

    if end_ln == ln:
        return srcwpos(ln, m.start(1), m.group(1)) if (m := re_pat.match(lines[ln], col, end_col)) else None

    if lcont is not None:
        for i in range(ln, end_ln):
            if m := re_pat.match(lines[i], col):
                return srcwpos(i, m.start(1), m.group(1))

            col = 0

    else:  # only match to end of logical line, regardless of (end_ln, end_col) bound
        for i in range(ln, end_ln):
            if not (m := _re_next_frag_or_comment_or_lcont.match(lines[i], col)):
                return None

            if (s := m.group(1)).startswith('#'):
                return srcwpos(i, m.start(1), s) if comment else None

            if s != '\\':  # line continuations are always matched alone
                return srcwpos(i, m.start(1), s)

            col = 0

    if m := re_pat.match(lines[end_ln], 0, end_col):
        return srcwpos(end_ln, m.start(1), m.group(1))

    return None


def prev_frag(
    lines: list[str],
    ln: int,
    col: int,
    end_ln: int,
    end_col: int,
    comment: bool = False,
    lcont: bool | None = False,
    *,
    state: list | None = None,
) -> srcwpos | None:
    """Get prev fragment of source which may or may not include comments or line continuation backslashes. May be
    restricted to bound or further restricted to not exceed logical line. Assuming start pos not inside str or comment.
    The fragment is not necessarily AST stuff, it can be commas, colons, the 'try' keyword, etc... Fragments can include
    multiple AST nodes in return str if there are no spaces between them like 'a+b'.

    **WARNING!** Make sure the search span does not include any AST strings as those can cause false positives for
    comment hash and line continuation backslashes.

    **Parameters:**
    - `comment`: Whether to return comments found, which will be the whole comment.
    - `lcont`: Whether to return line continuations found (backslash at end of line) if `True`, skip over them if
        `False`, or skip over them and restrict search to logical line `None`.
    - `state`: Can be used to cache walk but must only be used if the walk is sequentially backwards starting each time
        at the start position of the previously returned match.

    @private
    """

    re_pat = (
        (_re_next_frag_or_comment_or_lcont if comment else _re_next_frag_or_lcont)
        if lcont else
        (_re_next_frag_or_comment if comment else _re_next_frag)
    )

    if state is None:
        state = []

    def last_match(l: str, c: int, ec: int, p: re.Pattern) -> re.Match | None:
        if state:
            return state.pop()

        while m := p.match(l, c, ec):
            s = m.group(1)

            if (not comment and s.startswith('#')) or (lcont is False and s == '\\'):
                break

            c = m.end(1)

            state.append(m)

        return state.pop() if state else None

    if end_ln == ln:
        return srcwpos(ln, m.start(1), m.group(1)) if (m := last_match(lines[ln], col, end_col, re_pat)) else None

    if lcont is not None:
        for i in range(end_ln, ln, -1):
            if m := last_match(lines[i], 0, end_col, re_pat):
                return srcwpos(i, m.start(1), m.group(1))

            end_col = 0x7fffffffffffffff

        if m := last_match(lines[ln], col, end_col, re_pat):
            return srcwpos(ln, m.start(1), m.group(1))

    else:  # only match to start of logical line, regardless of (ln, col) bound
        cont_ln = end_ln

        if not (m := last_match(lines[end_ln], 0, end_col, _re_next_frag_or_comment_or_lcont)):
            end_ln -= 1
            end_col = 0x7fffffffffffffff

        else:
            if not (s := m.group(1)).startswith('#') or comment:
                return srcwpos(end_ln, m.start(1), m.group(1))

            end_col = m.start(1)

        i = end_ln + 1

        while (i := i - 1) >= ln:
            if not (m := last_match(lines[i], 0 if i > ln else col, end_col, _re_next_frag_or_comment_or_lcont)):
                if i < cont_ln:  # early out
                    return None

            elif (s := m.group(1)) == '\\':
                cont_ln = ln
                end_col = m.start(1)  # in case state was exhausted
                i += 1  # to search same line again, possibly from new end_col

                continue

            elif s.startswith('#') or i < cont_ln:  # a comment here started a previous line and thus not a line continuation, or just no line continuation on new previous line
                return None
            else:
                return srcwpos(i, m.start(1), m.group(1))

            end_col = 0x7fffffffffffffff  # will take effect for previous line when state empties

    return None


def next_find(
    lines: list[str],
    ln: int,
    col: int,
    end_ln: int,
    end_col: int,
    src: str,
    first: bool = False,
    *,
    comment: bool = False,
    lcont: bool | None = False,
) -> tuple[int, int] | None:
    """Find location of a string in the bound walking forward from the start. Returns `None` if string not found.

    **WARNING!** Make sure the search span does not include any AST strings as those can cause false positives for
    comment hash and line continuation backslashes.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        end of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `next_frag()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `next_frag()`. Can stop search on line continuation if `first` is `True`.

    **Returns:**
    - `fstpos | None`: Location of start of found `src` or `None` if not found with the given parameters.

    @private
    """

    if first:
        if frag := next_frag(lines, ln, col, end_ln, end_col, comment, lcont):
            cln, ccol, csrc = frag

            if csrc.startswith(src):
                return cln, ccol

    else:
        while frag := next_frag(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = frag

            if (idx := csrc.find(src)) != -1:
                return ln, col + idx

            col += len(csrc)

    return None


def prev_find(
    lines: list[str],
    ln: int,
    col: int,
    end_ln: int,
    end_col: int,
    src: str,
    first: bool = False,
    *,
    comment: bool = False,
    lcont: bool | None = False,
    state: list | None = None,
) -> tuple[int, int] | None:
    """Find location of a string in the bound walking backwards from the end. Returns `None` if string not found. If
    `comment` is `True` then `src` must match the START of the src comment found, not the tail like for non-comment
     strings found in order to be considered successful.

    **WARNING!** Make sure the search span does not include any AST strings as those can cause false positives for
    comment hash and line continuation backslashes.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        start of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `prev_frag()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `prev_frag()`. Can stop search on line continuation if `first` is `True`.
    - `state`: The `state` parameter to `prev_frag()`. Be careful using this here and keep in mind its line caching
        functionality if changing search parameters.

    **Returns:**
    - `fstpos | None`: Location of start of found `src` or `None` if not found with the given parameters.

    @private
    """

    if first:
        if frag := prev_frag(lines, ln, col, end_ln, end_col, comment, lcont, state=state):
            ln, col, csrc = frag

            if comment and csrc.startswith('#'):
                if csrc.startswith(src):
                    return ln, col

            elif csrc.endswith(src):
                return ln, col + len(csrc) - len(src)

    else:
        if state is None:
            state = []

        while frag := prev_frag(lines, ln, col, end_ln, end_col, comment, lcont, state=state):
            end_ln, end_col, csrc = frag

            if comment and csrc.startswith('#'):
                if csrc.startswith(src):
                    return end_ln, end_col

            elif (idx := csrc.rfind(src)) != -1:
                return end_ln, end_col + idx

    return None


def next_find_re(
    lines: list[str],
    ln: int,
    col: int,
    end_ln: int,
    end_col: int,
    pat: re.Pattern,
    first: bool = False,
    *,
    comment: bool = False,
    lcont: bool | None = False,
) -> srcwpos | None:
    """Find location of a regex pattern in the bound walking forward from the start. Returns `None` if string not found.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        end of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `next_frag()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `next_frag()`. Can stop search on line continuation if `first` is `True`.

    **Returns:**
    - `srcwpos | None`: Location of start of `pat` and the string matching the pattern or `None` if not found with the
        given parameters.

    @private
    """

    if first:
        if frag := next_frag(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = frag

            if m := pat.match(csrc):
                return srcwpos(ln, col, m.group())

    else:
        while frag := next_frag(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = frag

            if m := pat.search(csrc):
                return srcwpos(ln, col + m.start(), m.group())

            col += len(csrc)

    return None


def next_delims(
    lines: list[str], end_ln: int, end_col: int, bound_end_ln: int, bound_end_col: int, delim: str = ')'
) -> list[tuple[int, int]]:
    """Return a list of the locations of closing parentheses (or any specified delimiter or character) starting at
    (`end_ln`, `end_col`) until the end of the bound. The locations of the delimiters will be AFTER the delimiter.
    The list includes (`end_ln`, `end_col`) as the first element. The list ends if a non `delim` character is
    encountered while searching forward.

    **Returns:**
    - `[(end_ln, end_col), (ln_end_par1, col_end_par1), (ln_end_par2, col_end_par2), ...]`

    @private
    """

    delims = [(end_ln, end_col)]

    while frag := next_frag(lines, end_ln, end_col, bound_end_ln, bound_end_col):
        ln, col, src = frag

        for c in src:
            if c != delim:
                break

            end_ln = ln
            end_col = col = col + 1

            delims.append((end_ln, end_col))

        else:
            continue

        break

    return delims


def prev_delims(
    lines: list[str], bound_ln: int, bound_col: int, ln: int, col: int, delim: str = '('
) -> list[tuple[int, int]]:
    """Return a list of the locations of opening parentheses (or any specified delimiter or character) starting at
    (`ln`, `col`) going backwards until the start of the bound. The list includes (`ln`, `col`) as the first
    element. The list ends if a non `par` character is encountered while searching backward.

    **Returns:**
    - `[(ln, col), (ln_par1, col_par1), (ln_par2, col_par2), ...]`

    @private
    """

    delims = [(ln, col)]
    state = []

    while frag := prev_frag(lines, bound_ln, bound_col, ln, col, state=state):
        ln, col, src = frag
        col += len(src)

        for c in src[::-1]:
            if c != delim:
                break

            ln = ln
            col -= 1

            delims.append((ln, col))

        else:
            continue

        break

    return delims
