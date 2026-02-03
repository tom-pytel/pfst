"""Trivia-related `FST` class and standalone methods.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import re
from typing import Literal

from . import fst

from .asttypes import (
    ASTS_LEAF_STMTLIKE,
    ASTS_LEAF_BLOCK,
)

from .common import (
    re_empty_line,
    re_comment_line_start,
    re_empty_line_or_cont,
    re_empty_line_cont_or_comment,
    next_frag,
)

__all__ = [
    'leading_trivia',
    'trailing_trivia',
    'get_trivia_params',
 ]


Trivia = bool | str | int | tuple[bool | str | int, bool | str | int] | tuple[bool | str | int] | tuple[()]  # human interface trivia parameter as passed to functions with None indicating to use global value

_re_stmt_line_comment  = re.compile(r'(\s*;)?(\s*\#(.*)$)?')  # a line comment with optional leading whitespace and maybe a single inert semicolon before, or indicate if there is a trailing semicolon


# ----------------------------------------------------------------------------------------------------------------------

def leading_trivia(
    lines: list[str],
    bound_ln: int,
    bound_col: int,
    ln: int,
    col: int,
    comments: Literal['none', 'all', 'block'] | int,
    space: bool | int,
) -> tuple[tuple[int, int], tuple[int, int] | None, str | None]:
    """Get locations of leading trivia starting at the given bound up to (`ln`, `col`) where the element starts. Can get
    location of a block of comments (no spaces between), all comments after start of bound (with spaces inside) and any
    leading empty lines. Also returns the indentation of the element line if it starts the line.

    Regardless of if no comments or space is requested, this function will always return whether the element starts the
    line or not and the indentation if so.

    **Parameters:**
    - `bound_ln`: Preceding bounding line, other code assumed to end just here.
    - `bound_col`: Preceding bounding column.
    - `ln`: The start line of our element from which we will search back and upwards.
    - `col`: The start column of our element.
    - `comments`: What kind of comments to check for.
        - `'none'`: No comments.
        - `'all'`: A range of not-necessarily contiguous comments between the bound and the start of the element, will
            return location of start of comments.
        - `'block'`: A single contiguous block of comments immediately above the element.
        - `int`: An integer specifies return from this line number if possible. Possible means there are only comments
            and / or empty lined between this line and the start of the element. Any extra empty space to return will be
            searched for from this location, regardless of if there is other empty space below.
    - `space`: How much preceding space to check for, will be returned as a separate location if present.
        - `int`: Integer specifies maximum number of empty lines to return.
        - `False`: Same as `0` which will not check for or return any empty space.
        - `True`: Check all the way up to start of bound and return as much empty space as possible.

    **Returns:**
    - (comment / element text start, space start, indent on element line): Leading trivia info:
        - `[0]`: The start line and column of the first block of comments or the element. The column will be 0 if this
            starts a new line.
        - `[1]`: The start line and column (always 0) of any leading block of empty lines.
        - `[2]`: The indentation of the element line if it starts its own line (and may or may not have preceding
            comments and / or empty space). An empty string indicates the element starts the line at column 0 and `None`
            indicates the element doesn't start the line.

    @private
    """

    assert bound_ln <= ln

    if (bound_ln == ln and bound_col) or not re_empty_line.match(l := lines[ln], 0, col):
        return ((ln, col), None, None)

    indent = l[:col]
    is_lineno = isinstance(comments, int)
    text_pos = (ln, col)  # start of comments or start of element
    top_ln = bound_ln + bool(bound_col)  # topmost possible line to be considered, min return location is (top_ln, 0)
    stop_ln = comments if is_lineno and comments > top_ln else top_ln
    start_ln = ln

    if comments == 'all':
        comments_ln = ln

        while (ln := ln - 1) >= stop_ln:
            if not (m := re_empty_line_cont_or_comment.match(lines[ln])):
                break

            if (g := m.group(1)) and g.startswith('#'):
                comments_ln = ln

        ln += 1
        comments_pos = (comments_ln, 0)

        if comments_ln != start_ln:
            text_pos = comments_pos

        if not space or comments_ln == ln:  # no space requested or we reached top of search or non-comment/empty line right before comment
            return (text_pos, None if comments_pos == text_pos else comments_pos, indent)

        # space requested and there are some empty lines before first comment

        if space is True:
            return (text_pos, (ln, 0), indent)  # infinite space requested so return everything we got

        return (text_pos, (comments_ln - min(space, comments_ln - ln), 0), indent)

    if comments != 'none':
        assert is_lineno or comments == 'block'

        re_pat = re_empty_line_cont_or_comment if is_lineno else re_comment_line_start

        while (ln := ln - 1) >= stop_ln:
            if not (m := re_pat.match(lines[ln])):
                break

        comments_pos = (comments_ln := ln + 1, 0)

        if comments_ln != start_ln:
            text_pos = comments_pos

    else:
        comments_pos = (comments_ln := ln, 0)

    if not space or comments_ln == top_ln:
        return (text_pos, None if comments_pos == text_pos else comments_pos, indent)

    for ln in range(comments_ln - 1, max(top_ln - 1, -1 if space is True else comments_ln - 1 - space), -1):
        if not re_empty_line_or_cont.match(lines[ln]):
            ln += 1

            break

    if ln == comments_ln:
        return (text_pos, None if comments_pos == text_pos else comments_pos, indent)

    return (text_pos, (ln, 0), indent)


def trailing_trivia(
    lines: list[str],
    bound_end_ln: int,
    bound_end_col: int,
    end_ln: int,
    end_col: int,
    comments: Literal['none', 'all', 'block', 'line'] | int,
    space: bool | int,
) -> tuple[tuple[int, int], tuple[int, int] | None, bool]:
    """Get locations of trailing trivia starting at the element up to (`end_ln`, `end_col`) where the given bound ends.
    Can get location of a block of comments (no spaces between), all comments after start of bound (with spaces inside),
    a single comment on the ending line and any trailing empty lines. Also returns whether the element ends the line or
    not.

    Regardless of if no comments or space is requested, this function will always return whether the element ends the
    line or not.

    A trailing line continuation on any line is considered empty space.

    If `bound_end_ln == end_ln` then the element can never end the line, even if the bound is at the end of the line.

    If a line number is passed for `comment` then this is the last line that will be CONSIDERED and the end location CAN
    be on the next line if this line is an allowed comment or empty.

    If the end bound is at the end of a line then that line can be considered and the location returned can be the end
    bound and even if on first line it can be marked as ending the line (even though there may be no next line at EOF).
    This may make some returned locations not start at column 0 even if it is a complete line, especially at the end of
    source without a trailing newline.

    **Parameters:**
    - `bound_end_ln`: Trailing bounding line, other code assumed to start just here.
    - `bound_end_col`: Trailing bounding column.
    - `end_ln`: The end line of our element from which we will search forward and downward.
    - `end_col`: The end column of our element.
    - `comments`: What kind of comments to check for.
        - `'none'`: No comments.
        - `'all'`: A range of not-necessarily contiguous comments between the element and the bound, will return
            location of line just past end of comments.
        - `'block'`: A single contiguous block of comments immediately below the element.
        - `'line'`: Only a possible comment on the element line. If present returns start of next line.
        - `int`: An integer specifies return to this line number if possible. Possible means there are only comments
            and / or empty lined between the end of the element and this line (inclusive). Any extra empty space to
            return will be searched for from this location, regardless of if there is other empty space above.
    - `space`: How much trailing space to check for, will be returned as a separate location if present.
        - `int`: Integer specifies maximum number of empty lines to return.
        - `False`: Same as `0` which will not check for or return any empty space.
        - `True`: Check all the way up to end of bound and return as much empty space as possible.

    **Returns:**
    - (comment / element end, space end, whether the element ends the line or not): Trailing trivia info:
        - `[0]`: The end line and column of the last block of comments or the element. The column will be 0 if this
            ends a line.
        - `[1]`: The end line and column (always 0) of any trailing block of empty lines. If the element does not end
            its then this will be on the same line as the element end and will be the end of the space after the element
            if any, otherwise `None`.
        - `[2]`: Whether the element ends its line or not, NOT whether the last line found ends ITS line. If it ends the
            line then the first location will most likely have a column 0 and the returned line number will be after the
            element `end_ln`. But not always if the end bound was at the end of a line like can happen at the end of
            source if it doesn't have a trailing newline.

    @private
    """

    assert bound_end_ln >= end_ln

    if bound_end_ln == end_ln:
        assert bound_end_col >= end_col

        len_line = len(lines[end_ln])

        if not (frag := next_frag(lines, end_ln, end_col, end_ln, bound_end_col, True)):
            space_col = min(bound_end_col, len_line)
        elif comments == 'none' or not frag.src.startswith('#'):
            space_col = frag.col
        else:
            return ((end_ln, len_line), None, True)

        return ((end_ln, end_col), None if space_col == end_col else (end_ln, space_col), space_col == len_line)

    is_lineno = isinstance(comments, int)

    if frag := next_frag(lines, end_ln, end_col, end_ln + 1, 0, True):
        if not frag.src.startswith('#') or (comments < end_ln if is_lineno else comments == 'none'):
            space_pos = None if (c := frag.col) == end_col else (end_ln, c)

            return ((end_ln, end_col), space_pos, False)

        text_pos = (end_ln + 1, 0)  # comment on line so text pos must be one past

    else:
        text_pos = (end_ln, end_col)  # no comment on line so default text pos is end of element unless other comments found

    past_bound_end_ln = bound_end_ln + 1

    if bound_end_col >= (ll := len(lines[bound_end_ln])):  # special stuff happens if bound is at EOL
        bound_end_pos = (bound_end_ln, ll)  # this is only used if bound is at EOL so doesn't need to be set if not
        bottom_ln = past_bound_end_ln  # two past bottommost line to be considered, max return location is bound_end_pos

    else:
        bottom_ln = bound_end_ln  # one past bottommost line to be considered, max return location is (bottom_ln, 0)

    stop_ln = comments + 1 if is_lineno and comments < bottom_ln else bottom_ln
    start_ln = end_ln + 1

    if comments == 'all':
        comments_ln = start_ln

        while (end_ln := end_ln + 1) < stop_ln:
            if not (m := re_empty_line_cont_or_comment.match(lines[end_ln])):
                break

            if (g := m.group(1)) and g.startswith('#'):
                comments_ln = end_ln + 1

        comments_pos = (comments_ln, 0) if comments_ln < past_bound_end_ln else bound_end_pos

        if comments_ln != start_ln:
            text_pos = comments_pos

        if not space:  # no space requested
            return (text_pos, None if comments_pos == text_pos else comments_pos, True)

        space_pos = (end_ln, 0) if end_ln < past_bound_end_ln else bound_end_pos

        if space_pos == text_pos:  # we reached end of search or non-comment/empty line right after comment
            return (text_pos, None, True)

        # space requested and there are some empty lines after last comment

        if space is True:
            return (text_pos, space_pos, True)  # infinite space requested so return everything we got

        space_ln = comments_ln + min(space, end_ln - comments_ln)
        space_pos = (space_ln, 0) if space_ln < past_bound_end_ln else bound_end_pos

        return (text_pos, space_pos, True)  # return only number of lines limited by finite requested space

    if is_lineno or comments == 'block':
        re_pat = re_empty_line_cont_or_comment if is_lineno else re_comment_line_start

        while (end_ln := end_ln + 1) < stop_ln:
            if not (m := re_pat.match(lines[end_ln])):
                break

        comments_ln = end_ln

    else:
        assert comments in ('none', 'line')

        comments_ln = end_ln + 1

    comments_pos = (comments_ln, 0) if comments_ln < past_bound_end_ln else bound_end_pos

    if comments_ln != start_ln:
        text_pos = comments_pos

    if not space or comments_ln == bottom_ln:
        return (text_pos, None if comments_pos == text_pos else comments_pos, True)

    for end_ln in range(comments_ln, bottom_ln if space is True else min(comments_ln + space, bottom_ln)):
        if not re_empty_line_or_cont.match(lines[end_ln]):
            break

    else:
        end_ln += 1

    space_pos = (end_ln, 0) if end_ln < past_bound_end_ln else bound_end_pos

    return (text_pos, None if space_pos == text_pos else space_pos, True)


def get_trivia_params(
    trivia: Trivia, neg: bool = False
) -> tuple[str | int, bool | int, bool, str | int, bool | int, bool]:
    """Convert options compact human representation to parameters usable for `_leading/trailing_trivia()`.

    This conversion is fairly loose and will accept shorthand '+/-#' for 'block+/-#' / 'line+/-#'.

    **Parameters:**
    - `neg`: Whether to use `'-#'` suffix numbers or not (will still return `_neg` as `True` but `_space` will be 0).

    **Returns:**
    - (`lead_comments`, `lead_space`, `lead_neg`, `trail_comments`, `trail_space`, `trail_neg`): Two sets of parameters
        for the trivia functions along with the `_neg` indicators of whether the `_space` params came from negative
        space specifiers `'-#'` or not.
    """

    if not isinstance(trivia, tuple):
        lead_comments = trivia
        trail_comments = True

    elif (lt := len(trivia)) == 2:
        lead_comments, trail_comments = trivia

    elif not lt:  # () is shorthand for (False, False)
        lead_comments = trail_comments = False

    elif lt == 1:
        lead_comments = True
        trail_comments = trivia[0]

    else:
        raise ValueError('invalid trivia tuple')

    lead_space = lead_neg = False

    if isinstance(lead_comments, bool):
        lead_comments = 'block' if lead_comments else 'none'

    elif isinstance(lead_comments, str):
        if (i := lead_comments.find('+')) != -1:
            lead_space = int(n) if (n := lead_comments[i + 1:]) else True
            lead_comments = lead_comments[:i] or 'block'

        elif (i := lead_comments.find('-')) != -1:
            lead_neg = True
            lead_space = (int(n) if (n := lead_comments[i + 1:]) else True) if neg else 0
            lead_comments = lead_comments[:i] or 'block'

        assert lead_comments != 'line'

    trail_space = trail_neg = False

    if isinstance(trail_comments, bool):
        trail_comments = 'line' if trail_comments else 'none'

    elif isinstance(trail_comments, str):
        if (i := trail_comments.find('+')) != -1:
            trail_space = int(n) if (n := trail_comments[i + 1:]) else True
            trail_comments = trail_comments[:i] or 'line'

        elif (i := trail_comments.find('-')) != -1:
            trail_neg = True
            trail_space = (int(n) if (n := trail_comments[i + 1:]) else True) if neg else 0
            trail_comments = trail_comments[:i] or 'line'

    return lead_comments, lead_space, lead_neg, trail_comments, trail_space, trail_neg


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _getput_line_comment(
    self: fst.FST,
    comment: str | None | Literal[False] = False,
    field: Literal['body', 'orelse', 'finalbody'] | None = None,
    full: bool = False,
) -> str | None:
    """Get and / or put current line comment for this node.

    The line comment is the single comment at the end of the last line of the location of this node, with the exception
    of statement block nodes where the line comment lives on the last line of the header of the node (after the `:`,
    since the comment on the last line of the location belongs to the last child).

    **Parameters:**
    - `comment`: The comment operation to perform after getting the current comment.
        - `str`: Put new comment which may or may not need to have the initial `'#'` according to the `full` parameter.
        - `None`: Delete current comment (if present).
        - `False`: Do not modify current comment, just get it.
    - `field`: If `self` is a block statement then this can specify which field to operate on, only `'body'`, `'orelse'`
        and `'finalbody'` make sense to use and an error will be raised if the field is not present or there is nothing
        in it. `None` means use default `'body'` if block statement.
    - `full`:
        - `False`: The gotten comment text is returned stripped of the `'#'` and any leading and trailing whitespace. On
            put the `comment` text is put to existing comment if is present and otherwise is prepended with `'  #'` and
            a single leading whitespace after that if needed and put after the node.
        - `True`: The entire gotten comment from the end of the node to the end of the line is returned with no
            whitespace stripped, e.g. `'  # comment  '`. On put the `comment` **MUST** start with a `'#'` and possible
            leading whitespace before that and is put verbatim with no stripping, replacing any existing comment from
            the end of the node to the end of the line.

    **Returns:**
    - `str`: The current comment, before any replacement, with or without the leading whitespace and `'#'` as per the
        `full` paramenter.
    - `None`: There was no comment present.
    """

    ast = self.a
    ast_cls = ast.__class__

    # TODO: most expressionlike nodes can have line comments (sliceable ones, and even not if the are separated onto multiple lines and enclosed in parent or grouping pars)

    if ast_cls not in ASTS_LEAF_STMTLIKE:
        raise NotImplementedError('get / put line comment for non-statementlike node')

    if is_block := (ast_cls in ASTS_LEAF_BLOCK):
        if field is None:
            field = 'body'

        _, _, end_ln, end_col = self._loc_block_header_end(field)

    else:
        _, _, end_ln, end_col = self.bloc

    lines = self.root._lines
    last_stmt_line = lines[end_ln]
    m = _re_stmt_line_comment.match(last_stmt_line, end_col)  # will match anything even if empty

    if (old_comment := m.group(2)) and not full:  # if full is False then old_comment will be either None or the full comment group as it should be
        old_comment = m.group(3).strip()  # comment present and full=False, we need just the comment text

    if comment is False:  # if only get operation then we are done
        return old_comment

    # put operation

    if comment is not None:
        if '\n' in comment:
            raise ValueError('line comment cannot have newlines in it')

        if full:
            if not comment.lstrip().startswith('#'):
                raise ValueError("full line comment must start with '#'")

        elif not comment[:1].isspace():
            comment = ' ' + comment

    if old_comment is not None:  # if comment already present then any replacement is trivial
        self._put_src(comment, end_ln, m.start(2 if comment is None or full else 3), end_ln, 0x7fffffffffffffff)
        self._touchall(True, False, False)  # touch parents to clear bloc caches because comment on last child statement is included in parent bloc

        return old_comment

    if comment is None:  # if deleting comment that doesn't exist then this is even more trivial
        return old_comment

    # put comment where there was no comment before, may need to normalize block header or semicoloned statements

    with self._modifying():  # this isn't strictly needed at the time of writing, future-proofing
        before_semi_end_col = end_col

        if has_semi := m.group(1):  # if semicolon present then we start search after it
            end_col = m.end(1)

        if not full:
            comment = '  #' + comment

        if not (l := last_stmt_line[end_col:]) or l.isspace():  # no other statement or line continuation on last statement line so we can just add the comment
            pass  # noop

        elif is_block:
            if self._normalize_block(field):
                _, _, end_ln, end_col = self._loc_block_header_end(field)  # any remaining junk on header tail (maybe line continuation) is harmless to remove

        # we are past any semicolon on this line, its either another statement or a line continuation ... which may lead to another statement or the semicolon which is not on this line, or not

        elif (next_stmt := self.next()) and next_stmt.pfield.name == self.pfield.name:  # if there is a next sibiling and is part of same body then we need to process more, if not then safe to nuke rest of line
            next_ln, next_col, _, _ = next_stmt.bloc

            if ((frag := next_frag(lines, end_ln, end_col, next_ln, next_col + 1, True, None))  # search to 1 past start of next statement to be able to run into it it on logical line
                and frag.src.startswith(';')  # a semicolon?
            ):
                if has_semi:  # if already had one then error
                    raise RuntimeError('should not get here, found two semicolons without a statement between them')  # pragma: no cover

                frag = next_frag(lines, frag.ln, frag.col + 1, next_ln, next_col + 1, True, None)  # search again, it better not be another semicolon!

            if frag and not frag.src.startswith('#'):  # if its not a comment then its the next statement
                assert frag.ln == next_ln and frag.col == next_col

                indent = self._get_block_indent()

                if (parent := self.parent) and parent._normalize_block(self.pfield.name, indent=indent):  # if have parent then normalize the block because could all be on header logical line separated with semicolons
                    _, _, end_ln, before_semi_end_col = self.bloc  # locations have changed
                    next_ln, next_col, _, _ = next_stmt.bloc

                self._put_src([comment, indent], end_ln, before_semi_end_col, next_ln, next_col, False)  # now, FINALLY, we write the comment along with a newline to split up the statements, don't need to touch explicitly because offseting _put_src touches

                return old_comment

        self._put_src(comment, end_ln, end_col, end_ln, 0x7fffffffffffffff)
        self._touchall(True, False, False)

        return old_comment
