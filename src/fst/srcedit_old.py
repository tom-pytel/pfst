"""Old source location editing stuff, needs to be moved into fst_slice."""

from __future__ import annotations

from ast import *

from .astutil import bistr
from .misc import (
    fstloc,
    NAMED_SCOPE,
    re_empty_line_start, re_empty_line, re_comment_line_start, re_line_trailing_space,
    re_empty_line_cont_or_comment,
    _next_src, _prev_src, _next_find, _prev_find, _next_pars, _prev_pars,
)


class SrcEdit:
    """This class controls most source editing behavior."""

    def _fixup_expr_seq_bound(self, lines: list[str], seq_loc: fstloc,
                              fpre: FST | fstloc | None, fpost: FST | fstloc | None,
                              flast: FST | fstloc | None,
                              ) -> tuple[fstloc, FST | fstloc | None, FST | fstloc | None] | None:
        """Depending on existence preceding or following expressions and a full sequence location, return a bound
        `fstloc` that represents a search space in the source for commas and parenteses and the like. Will exclude any
        closing parentheses belonging to `fpre` and any opening parenthese belonging to `fpost` from the bound."""

        if not fpre:
            if not fpost:
                return None

            start_ln  = seq_loc.ln
            start_col = seq_loc.col

        else:
            start_ln, start_col = (pars :=
                _next_pars(lines, fpre.end_ln, fpre.end_col, seq_loc.end_ln, seq_loc.end_col))[-1]

            if len(pars) > 1:
                fpre = fstloc(fpre.ln, fpre.col, start_ln, start_col)

        if not fpost:
            stop_ln  = seq_loc.end_ln
            stop_col = seq_loc.end_col

        else:
            if flast:  # make sure there are no ASTs where we will be searching because their strings can screw up _prev_src()
                from_ln  = flast.end_ln
                from_col = flast.end_col

            elif fpre:
                from_ln  = start_ln
                from_col = start_col

            else:
                from_ln  = seq_loc.ln
                from_col = seq_loc.col

            stop_ln, stop_col = (pars := _prev_pars(lines, from_ln, from_col, fpost.ln, fpost.col))[-1]

            if len(pars) > 1:
                fpost = fstloc(stop_ln, stop_col, fpost.end_ln, fpost.end_col)

        return fstloc(start_ln, start_col, stop_ln, stop_col), fpre, fpost

    def _expr_src_edit_locs(self, lines: list[bistr], loc: fstloc, bound: fstloc, at_end: bool = False,
                            ) -> tuple[fstloc, fstloc, list[str]]:
        """Get expression copy and delete locations. There can be commas in the bound in which case the expression is
        treated as part of a comma delimited sequence. In this case, if there is a trailing comma within bounding span then
        it is included in the delete location. Any enclosing grouping parentheses within the bounding span are included. Any
        closing parentheses after the start of or opening parentheses before the end of `bound` are also handled correctly.

        **Parameters:**
        - `lines`: The lines corresponding to the expression and its `bound` location.
        - `loc`: The location of the expression, can be multiple or no expressions, just the location matters.
        - `bound`: The bounding location not to go outside of. Must entirely contain `loc` (can be same as). Must not
            contain any part of other `AST` nodes like other members of a sequence. Can contain any number of open and close
            parentheses for the expression itself and closing and opening parentheses belonging to expressions from outside
            the bound.
        - `at_end`: Whether `loc` is at the end of a sequence, used to remove trailing whitespace from preceding comma.

        **Returns:**
        - `(copy_loc, del_loc)`: `copy_loc` is the location of source that should be used if copying the expression.
            `del_loc` is the location which should be deleted used if removing the expression. Both are used
            for a cut operation.
        """

        copy_ln,  copy_col,  copy_end_ln,  copy_end_col  = loc
        bound_ln, bound_col, bound_end_ln, bound_end_col = bound

        precomma_end_ln = None
        state           = []

        while True:
            if not (code := _prev_src(lines, bound_ln, bound_col, copy_ln, copy_col, state=state)):
                if bound_ln != copy_ln:
                    copy_col = 0

                break

            ln, col, src  = code
            col          += len(src)

            for c in src[::-1]:
                if c == ',':
                    precomma_end_ln  = ln
                    precomma_end_col = col

                    if ln != copy_ln:
                        copy_col = 0

                    break

                elif c != '(':  # we don't actually count and check these because there may be other parens inside the `loc` which we cannot see here
                    raise ValueError(f"expecting leading comma or open parenthesis, got '{c}'")

                col      -= 1
                copy_ln   = ln
                copy_col  = col

            if precomma_end_ln is not None:
                break

        loc_end_ln     = copy_end_ln
        loc_end_col    = copy_end_col
        postcomma_have = None

        while True:
            if not (code := _next_src(lines, copy_end_ln, copy_end_col, bound_end_ln, bound_end_col)):
                if bound_end_ln != copy_end_ln:
                    copy_end_ln  = bound_end_ln
                    copy_end_col = 0

                break

            ln, col, src = code

            for c in src:
                if c == '(':  # may not have been excluded from bounds as is not part of expressions, if so then adjust end bound and done
                    bound_end_ln  = ln
                    bound_end_col = col

                    break

                col += 1

                if c == ',':
                    if postcomma_have:
                        raise ValueError('multiple trailing commas found')

                    postcomma_have = True

                elif c != ')':
                    raise ValueError(f"not expecting code, got '{src}'"
                                    if postcomma_have else
                                    f"expecting close parenthesis or trailing comma, got '{src}'")

                else:  # c == ')'
                    if postcomma_have:
                        raise ValueError('found close parenthesis after trailing comma')

                    loc_end_ln  = ln  # we update loc because end parens are definitive end of loc, and may not have been checked before calling this function
                    loc_end_col = col

                copy_end_ln  = ln
                copy_end_col = col

            else:
                continue

            break  # this happens if we found an open parenthesis

        # special sauce, can probably be simplified

        del_end_ln = copy_end_ln

        if not copy_end_col and precomma_end_ln is not None:  # ends on newline and there is something before
            del_end_col = 0

        else:
            del_end_col = bound_end_col

            if postcomma_have and copy_end_ln == loc_end_ln:  # end comma on same line as end of expr, don't copy it
                copy_end_col = loc_end_col

        del_ln  = copy_ln
        del_col = copy_col

        if not copy_col and copy_ln != bound_ln:  # starts on newline
            copy_ln  = copy_ln - 1
            copy_col = len(lines[copy_ln])

        elif copy_ln == precomma_end_ln:  # copy start on same line as preceding comma
            if postcomma_have:  # other items follow or explicit trailing comma at end of sequence, delete up to end (including postcomma)
                del_end_col = bound_end_col

                if at_end:  # definitively at end, delete whitespace at end of precomma
                    del_col = precomma_end_col

            elif precomma_end_ln == bound_ln:  # no items following, previous item, delete up to end of item past precomma
                del_col = bound_col
            else:  # previous comma not on same line as previous item, preserve its unique and special formatting as a trailing comma at end of sequence
                del_col = precomma_end_col

        if not del_col and del_end_col and (col := re_empty_line_start.match(lines[del_ln]).end()):  # delete from start of line to middle of line, maybe there is indentation to leave in place
            del_col = col

        # end of special sauce

        return fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col), fstloc(del_ln, del_col, del_end_ln, del_end_col)

    def pre_comments(self, lines: list[bistr], bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                     precomms: bool | str | None = None) -> tuple[int, int] | None:
        """Return the position of the start of any preceding comments to the element which is assumed to live just past
        (`bound_ln`, `bound_col`). Returns `None` if no preceding comment. If preceding entire line comments exist then
        the returned position column should be 0 (the start of the line) to indicate that it is a full line comment.
        Only preceding entire line comments start comment should be returned. This particular implementation will return
        any full line comments directly preceding the element if it starts its own line. An empty line ends the
        preceding comments even if there are more comments before it, unless precomms is `'all'`.

        **Parameters:**
        - `precomms`: Preceding comments to get. See `FST` source editing `options`.

        **Returns:**
        - `(ln, col) | None`: If not getting comments or comments not found will return `None`, otherwise position of
            start of preceding comments.
        """

        if precomms is None:
            precomms = FST.get_option('precomms')
        if not precomms:
            return None

        if bound_ln == bound_end_ln or (bound_end_col and
                                        not re_empty_line.match(lines[bound_end_ln], 0, bound_end_col)):
            return None

        allpre = precomms == 'all'
        pre_ln = None
        re_pat = re_empty_line_cont_or_comment if allpre else re_comment_line_start

        for ln in range(bound_end_ln - 1, bound_ln - (not bound_col), -1):  # only consider whole lines
            if not (m := re_pat.match(lines[ln])):
                break

            if not allpre or (g := m.group(1)) and g.startswith('#'):
                pre_ln  = ln
                pre_col = 0

        return None if pre_ln is None else (pre_ln, pre_col)

    def post_comments(self, lines: list[bistr], bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                      postcomms: bool | str | None = None) -> tuple[int, int] | None:
        """Return the position of the end of any trailing comments to the element which is assumed to live just before
        (`bound_end_ln`, `bound_end_col`). Returns `None` if no trailing comment. Should return the location at the
        start of the next line if comment present because a comment should never be on the last line, but if a comment
        ends the bound should return the end of the bound. This particular implementation will return any comment which
        lives on the same line as `bound_ln`, no other comments past it on following lines.

        **Parameters:**
        - `postcomms`: Trailing comments to get. See `FST` source editing `options`.

        **Returns:**
        - `(end_ln, end_col) | None`: If not getting comments or comments not found will return `None`, otherwise
            position of end of trailing comments (past trailing comment newline if possible).
        """

        if postcomms is None:
            postcomms = FST.get_option('postcomms')
        if not postcomms:
            return None

        blkpost = True if (allpost := postcomms == 'all') else postcomms == 'block'

        if single_ln := bound_end_ln == bound_ln:
            code = _next_src(lines, bound_ln, bound_col, bound_ln, bound_end_col, True)
        else:
            code = _next_src(lines, bound_ln, bound_col, bound_ln, 0x7fffffffffffffff, True)

        if code:
            if not code.src.startswith('#'):
                return None

            if not blkpost:
                return (bound_ln, bound_end_col) if single_ln else (bound_ln + 1, 0)

        elif not blkpost or single_ln:
            return None

        for ln in range(bound_ln + 1, bound_end_ln + 1):
            if not (m := re_empty_line_cont_or_comment.match(lines[ln])):
                break

            if g := m.group(1):
                if g.startswith('#'):
                    bound_ln = ln

            elif not allpost:
                break

        return (bound_ln, bound_end_col) if bound_ln == bound_end_ln else (bound_ln + 1, 0)

    def get_slice_seq(self, fst: FST, cut: bool, seq_loc: fstloc,
                      ffirst: FST | fstloc, flast: FST | fstloc,
                      fpre: FST | fstloc | None, fpost: FST | fstloc | None,
    ) -> tuple[fstloc, fstloc | None, list[str] | None]:  # (copy_loc, del/put_loc, put_lines)
        """Copy or cut from comma delimited sequence.

        The `ffirst`, `flast`, `fpre` and `fpost` parameters are only meant to pass location information so you should
        only count on their respective `.ln`, `.col`, `.end_ln` and `.end_col` being correct (within `fst`).

        **Parameters:**
        - `fst`: The source `FST` container that is being gotten from. No text has been changed at this point but the
            respective `AST` nodes may have been removed in case of `cut`.
        - `cut`: If `False` the operation is a copy, `True` means cut.
        - `seq_loc`: The full location of the sequence in `fst`, excluding parentheses / brackets / curlies.
        - `ffirst`: The first `FST` or `fstloc` being gotten.
        - `flast`: The last `FST` or `fstloc` being gotten.
        - `fpre`: The preceding-first `FST` or `fstloc`, not being gotten, may not exist if `ffirst` is first of seq.
        - `fpost`: The after-last `FST` or `fstloc` not being gotten, may not exist if `flast` is last of seq.

        **Returns:**
        - If `cut=False` then only the first element of the return tuple is used for the copy and the other two are
            ignored so they don't need to be calculated. If `cut=True` then should return the copy location, a delete
            location and optionally lines to replace the deleted portion (which can only be non-coding source).
        """

        lines = fst.root._lines

        if not (bound_pre_post := self._fixup_expr_seq_bound(lines, seq_loc, fpre, fpost, flast)):
            return seq_loc, seq_loc, None

        bound, _, _       = bound_pre_post
        copy_loc, del_loc = self._expr_src_edit_locs(
            lines, fstloc(ffirst.ln, ffirst.col, flast.end_ln, flast.end_col), bound)

        if not fpost:
            del_ln, del_col, del_end_ln, del_end_col = del_loc

            if (new_del_col := re_line_trailing_space.match(lines[del_ln],
                                                            bound.col if del_ln == bound.ln else 0,
                                                            del_col := del_col).start(1)) < del_col:  # move del start to beginning of any trailing whitespace from del location before end of sequence
                del_loc = fstloc(del_ln, new_del_col, del_end_ln, del_end_col)

        return copy_loc, del_loc, None

    def put_slice_seq(self, fst: FST, put_fst: FST | None, indent: str, seq_loc: fstloc,
                      ffirst: FST | fstloc | None, flast: FST | fstloc | None,
                      fpre: FST | fstloc | None, fpost: FST | fstloc | None,
                      pfirst: FST | fstloc | None, plast: FST | fstloc | None,
    ) -> fstloc:  # del_loc
        """Put to comma delimited sequence.

        The `ffirst`, `flast`, `fpre` and `fpost` parameters are only meant to pass location information so you should
        only count on their respective `.ln`, `.col`, `.end_ln` and `.end_col` being correct (within `src`).

        If `ffirst` and `flast` are `None` it means that it is a pure insertion and no elements are being removed. In
        this case use `fpre` and `fpost` to determine locations, one of which could be missing if the insertion is at
        the beginning or end of the sequence, both of which missing indicates put to empty sequence (in which case use
        `seq_loc` for location).

        The first line of `put_fst` is unindented and should remain so as it is concatenated with the target line at the
        point of insertion. The last line of `put_fst` is likewise prefixed to the line following the deleted location.

        There is always an operation if this is called, insertion, deletion, or replacement. It is never an empty
        assignment to an empty slice.

        **Parameters:**
        - `fst`: The destination `FST` container that is being put to.
        - `put_fst`: The sequence which is being put, may be `None` in case of deletion. Already indented, mutate this
            object to change what will be put (both source and `AST` nodes, node locations must be offset if source is
            changed).
        - `indent`: The indent string which was applied to `put_fst`.
        - `seq_loc`: The full location of the sequence in `fst`, excluding parentheses / brackets / curlies.
        - `ffirst`: The first destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `flast`: The last destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `fpre`: The preceding-first destination `FST` or `fstloc`, not being replaced, may not exist if `ffirst` is
            first of seq.
        - `fpost`: The after-last destination `FST` or `fstloc` not being replaced, may not exist if `flast` is last of
            seq.
        - `pfirst`: The first source `FST`, else `None` if is assignment from empty sequence or deletion.
        - `plast`: The last source `FST`, else `None` if is assignment from empty sequence or deletion.

        **Returns:**
        - `fstloc`: location where the potentially modified `fst` source should be put, replacing whatever is at the
            location currently.
        """

        lines = fst.root._lines

        if not (bound_pre_post := self._fixup_expr_seq_bound(lines, seq_loc, fpre, fpost, flast)):  # if operating on whole sequence then just use the whole sequence location, if this doesn't return then one of `fpre` or `fpost` exists
            return seq_loc

        bound, fpre, fpost = bound_pre_post

        if not put_fst or not pfirst:  # `pfirst` may be None and `put_fst` not if assigning empty sequence, regardless, pure delete (or assign empty sequence, ALMOST exactly same thing), fflrst/last guaranteed to exist
            return self._expr_src_edit_locs(fst.root._lines,
                                            fstloc(ffirst.ln, ffirst.col, flast.end_ln, flast.end_col),
                                            bound, not fpost)[1]

        if ffirst:  # flast also exists, replacement
            put_ln      = ffirst.ln
            put_col     = ffirst.col
            put_end_ln  = flast.end_ln
            put_end_col = flast.end_col

        elif fpost:  # insertion
            put_end_ln  = put_ln  = fpost.ln
            put_end_col = put_col = fpost.col

        else:  # fpre guaranteed to exist, insertion
            put_end_ln  = put_ln  = fpre.end_ln
            put_end_col = put_col = fpre.end_col

        put_lines = put_fst._lines
        del_loc   = self._expr_src_edit_locs(fst.root._lines,
                                             fstloc(put_ln, put_col, put_end_ln, put_end_col), bound)[1]

        if not put_lines[0]:
            if re_empty_line.match(l := lines[put_ln], 0, put_col):  # strip leading newline from `put_fst` if location being put already has one - NOTE: could also check re_empty_line.match(put_lines[0]) instead of just put_lines[0]
                put_fst._put_src(None, 0, 0, 1, re_empty_line_start.match(put_lines[1]).end(), False)

            elif (new_del_col := re_line_trailing_space.match(l,
                                                              bound.col if put_ln == bound.ln else 0,
                                                              del_col := del_loc.col).start(1)) < del_col:  # move del start to beginning of any trailing whitespace from put location before newline
                del_loc = fstloc(del_loc.ln, new_del_col, del_loc.end_ln, del_loc.end_col)

        if not put_lines[-1] and not re_empty_line.match(lines[(end_ln := del_loc.end_ln)], del_loc.end_col,  # add indentation to trailing newline in `put_fst` if there is stuff on the starting line of `put_loc` past the start point
            seq_loc.end_col if seq_loc.end_ln == end_ln else 0x7fffffffffffffff
        ):
            put_fst._put_src([re_empty_line_start.match(lines[put_ln]).group()], ln := put_fst.end_ln, 0, ln, 0,
                               True, put_fst)

        if fpre:
            if (not (code := _next_src(lines, fpre.end_ln, fpre.end_col, del_loc.ln, del_loc.col)) or
                not code.src.startswith(',')
            ):
                put_fst._put_src([', ' if put_lines[0] else ','], 0, 0, 0, 0, False)

        if fpost:
            if not put_fst._maybe_add_comma(plast.end_ln, plast.end_col, False, True):
                if put_lines[-1].endswith(',', -1):  # slice being put ends on comma without a space, add one
                    put_fst._put_src([' '], ln := put_fst.end_ln, col := put_fst.end_col, ln, col, True, put_fst)

        return del_loc

    def get_slice_stmt(self, fst: FST, field: str, cut: bool, block_loc: fstloc,  # TODO: clean this up
                       ffirst: FST, flast: FST, fpre: FST | None, fpost: FST | None, *,
                       del_else_and_fin: bool = True, ret_all: bool = False, **options,
    ) -> tuple[fstloc, fstloc | None, list[str] | None]:  # (copy_loc, del/put_loc, put_lines)
        """Copy or cut from block of statements. If cutting all elements from a deletable field like 'orelse' or
        'finalbody' then the corresponding 'else:' or 'finally:' will also be removed from the source (though not
        copied), and the formatting flags will apply to deleting any preceding comments and/or space. If you wish to
        apply different format flags to the copy and delete then copy what you want first then cut with different flags.

        **Parameters:**
        - `fst`: The source `FST` container that is being gotten from. No text has been changed at this point but the
            respective `AST` nodes may have been removed in case of `cut`.
        - `field`: The name of the field being gotten from, e.g. `'body'`, `'orelse'`, etc...
        - `cut`: If `False` the operation is a copy, `True` means cut.
        - `block_loc`: A rough location suitable for checking comments outside of ASTS if `fpre` / `fpost` not
            available. Should include trailing newline after `flast` if one is present, but NO PARTS OF ASTS.
        - `ffirst`: The first `FST` being gotten.
        - `flast`: The last `FST` being gotten.
        - `fpre`: The preceding-first `FST`, not being gotten, may not exist if `ffirst` is first of seq.
        - `fpost`: The after-last `FST` not being gotten, may not exist if `flast` is last of seq.
        - `options`: See `FST` source editing `options`. Options used here `precomms`, `postcomms`, `prespace`,
            `postspace` and `pep8space`. `space` options determine how many empty lines to remove on a cut.

        **Returns:**
        - If `cut=False` then only the first element of the return tuple is used for the copy and the other two are
            ignored so they don't need to be calculated. If `cut=True` then should return the copy location, a delete
            location and optionally lines to replace the deleted portion (which can only be non-coding source).
        """

        bound_ln, bound_col         = fpre.bloc[2:] if fpre else block_loc[:2]
        bound_end_ln, bound_end_col = fpost.bloc[:2] if fpost else block_loc[2:]

        lines      = fst.root._lines
        put_lines  = None
        pre_comms  = self.pre_comments(lines, bound_ln, bound_col, ffirst.bln, ffirst.bcol,
                                       options.get('precomms'))
        post_comms = self.post_comments(lines, flast.bend_ln, flast.bend_col, bound_end_ln, bound_end_col,
                                        options.get('postcomms'))
        pre_semi   = not pre_comms and _prev_find(lines, bound_ln, bound_col, ffirst.ln, ffirst.col, ';',
                                                  True, comment=True, lcont=None)
        post_semi  = not post_comms and _next_find(lines, flast.end_ln, flast.end_col, bound_end_ln, bound_end_col, ';',
                                                   True, comment=True, lcont=None)
        copy_loc   = fstloc(*(pre_comms or ffirst.bloc[:2]), *(post_comms or flast.bloc[2:]))

        if fpre:  # set block start to just past prev statement or block open (colon)
            block_ln, block_col = fpre.bloc[2:]

        elif code := _prev_src(lines, bound_ln, bound_col, copy_loc.ln, copy_loc.col, False, False):
            block_ln, block_col, src  = code
            block_col                += len(src)

        else:
            block_ln  = bound_ln
            block_col = bound_col

        # get copy and delete locations according to possible combinations of preceding and trailing comments, semicolons and line continuation backslashes

        def fix_post_semi_with_tail(end_ln, end_col, starts_line):
            if code := _next_src(lines, end_ln, end_col, end_ln,
                                 bound_end_col if end_ln == bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                put_lines = None
                ln, col   = copy_loc[:2]

                if code.src.startswith('#'):
                    del_loc = fstloc(ln, col, end_ln, code.col)

                    if starts_line and fpost:
                        put_lines = [re_empty_line_start.match(lines[copy_loc.ln]).group(0)]

                else:  # HACK FIX! TODO: do this properly, only here because '\\\n stmt' does not work at module level even though it works inside indented blocks, otherwise `del_loc` above would be sufficient unconditionally
                    del_loc = fstloc(ln, 0, bound_end_ln, bound_end_col)

                    if fpost:
                        put_lines = [ffirst.get_indent()]  # SHOULDN'T DO THIS HERE!!!

                return del_loc, put_lines

            return None

        def fix_post_semi(post_semi):
            end_ln, end_col  = post_semi
            end_col         += 1

            if t := fix_post_semi_with_tail(end_ln, end_col, False):
                del_loc, put_lines = t

            else:
                ln, col = copy_loc[:2]
                del_col = 0 if ln != block_ln else block_col

                if end_ln == bound_end_ln:
                    del_loc   = fstloc(ln, col if fpost else del_col, bound_end_ln, bound_end_col)
                    put_lines = None

                else:
                    del_loc   = fstloc(ln, del_col, end_ln + 1, 0)
                    put_lines = ['', ''] if del_col else None

            return del_loc, put_lines

        if pre_comms:
            if post_comms:
                del_loc = copy_loc

            else:
                if not post_semi:
                    end_ln, end_col = copy_loc[2:]

                else:
                    end_ln, end_col  = post_semi
                    end_col         += 1

                if t := fix_post_semi_with_tail(end_ln, end_col, True):  # we know it starts a line because pre_comms exists
                    del_loc, put_lines = t

                elif end_ln != bound_end_ln:
                    del_loc = fstloc(*pre_comms, end_ln + 1, 0)

                else:
                    del_loc = fstloc(*pre_comms, bound_end_ln, bound_end_col)

                    if fpost:  # ends at next statement, otherwise if fpost doesn't exist then was empty line after a useless trailing ';'
                        put_lines = [re_empty_line_start.match(lines[copy_loc.ln]).group(0)]  # we know it starts a line because pre_comms exists

        elif post_comms:
            if pre_semi:
                ln, col = post_comms
                del_loc = fstloc(*fpre.bloc[2:], ln := ln - (not col), len(lines[ln]))  # we know fpre exists because of pre_semi, leave trailing newline

            else:
                ln, col = copy_loc[:2]
                del_col = 0 if ln != block_ln else block_col
                del_loc = fstloc(ln, del_col, *post_comms)

        elif pre_semi:
            if post_semi:
                if fpost:
                    del_loc = fstloc(*pre_semi, *post_semi)
                else:
                    del_loc, put_lines = fix_post_semi(post_semi)

            else:
                end_ln, end_col = copy_loc[2:]
                at_bound_end_ln = end_ln == bound_end_ln

                if _next_src(lines, end_ln, end_col, end_ln,
                             bound_end_col if at_bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                    del_loc = fstloc(*fpre.bloc[2:], end_ln, end_col)
                else:
                    del_loc = fstloc(*fpre.bloc[2:], end_ln, len(lines[end_ln]))

        elif post_semi:
            del_loc, put_lines = fix_post_semi(post_semi)

        else:
            ln, col, end_ln, end_col = copy_loc
            at_bound_end_ln          = end_ln == bound_end_ln

            if code := _next_src(lines, end_ln, end_col, end_ln,
                                 bound_end_col if at_bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                del_loc = fstloc(ln, col, end_ln, code.col)

            else:
                del_col = 0 if ln != block_ln else block_col

                if not at_bound_end_ln:
                    del_loc = fstloc(ln, del_col, end_ln + 1, 0)
                else:
                    del_loc = fstloc(ln, del_col, bound_end_ln, bound_end_col)

        # special case of deleting everything from a block

        if not fpre and not fpost:
            if del_else_and_fin and ((is_finally := field == 'finalbody') or  # remove 'else:' or 'finally:' (but not 'elif ...:' as that lives in first cut statement)
                (field == 'orelse' and not lines[ffirst.bln].startswith('elif', ffirst.bcol))
            ):
                del_ln, del_col, del_end_ln, del_end_col = del_loc

                del_ln, del_col = _prev_find(lines, bound_ln, bound_col, del_ln, del_col,
                                             'finally' if is_finally else 'else', False, comment=False, lcont=False)  # `first=False` because have to skip over ':'

                if put_lines:
                    put_lines[0] = lines[del_ln][:del_col] + put_lines[0]  # prepend block start indentation to existing indentation, silly but whatever

                if pre_pre_comms := self.pre_comments(lines, bound_ln, bound_col, del_ln, 0, options.get('precomms')):
                    del_ln, _ = pre_pre_comms

                del_loc = fstloc(del_ln, 0, del_end_ln, del_end_col)

            elif fst.parent and not del_loc.end_col and del_loc.ln == block_ln:  # avoid deleting trailing newline of only statement just past block open
                del_ln, del_col, del_end_ln, del_end_col = del_loc

                del_loc = fstloc(del_ln, del_col, (ln := del_end_ln - 1), len(lines[ln]))

        # delete preceding and trailing empty lines according to 'pep8' and 'space' format flags

        prespace  = (float('inf') if (o := FST.get_option('prespace', options)) is True else int(o))
        postspace = (float('inf') if (o := FST.get_option('postspace', options)) is True else int(o))
        pep8space = FST.get_option('pep8space', options)

        if pep8space:
            if not 0 <= pep8space <= 1:
                raise ValueError(f"'pep8space' must be True, False or 1, not {pep8space}")

            pep8space = 2 if pep8space is True and (p := fst.parent_scope(True)) and isinstance(p.a, mod) else 1

            if fpre and isinstance(ffirst.a, NAMED_SCOPE) and (fpre.pfield.idx or
                                                               not isinstance(a := fpre.a, Expr) or
                                                               not isinstance(v := a.value, Constant) or
                                                               not isinstance(v.value, str)):
                prespace = max(prespace, pep8space)

            elif fpost and isinstance(flast.a, NAMED_SCOPE):
                postspace = max(postspace, pep8space)

        del_ln, del_col, del_end_ln, del_end_col = del_loc

        if prespace:
            new_del_ln = max(bound_ln + bool(bound_col), del_ln - prespace)  # first possible full empty line to delete to

            if del_ln > new_del_ln and (not del_col or re_empty_line.match(lines[del_ln], 0, del_col)):
                if code := _prev_src(lines, new_del_ln, 0, del_ln, 0, True, False):
                    new_del_ln = code.ln + 1

                if new_del_ln < del_ln:
                    indent    = lines[del_ln][:del_col]
                    put_lines = [indent + put_lines[0], *put_lines[1:]] if put_lines else [indent]
                    del_ln    = new_del_ln
                    del_col   = 0

        if postspace:
            if not del_end_col:
                new_del_end_ln = min(bound_end_ln, del_end_ln + postspace)  # last possible end line to delete to
                del_end_ln     = (code.ln
                                  if (code := _next_src(lines, del_end_ln, 0, new_del_end_ln, 0, True, True)) else
                                  new_del_end_ln)

            elif del_end_col == len(lines[del_end_ln]):
                new_del_end_ln = min(bound_end_ln, del_end_ln + postspace + 1)  # account for not ending on newline
                del_end_ln     = (code.ln - 1
                                  if (code := _next_src(lines, del_end_ln, del_end_col, new_del_end_ln, 0, True, True)) else
                                  new_del_end_ln - 1)
                del_end_col    = len(lines[del_end_ln])

        del_loc = fstloc(del_ln, del_col, del_end_ln, del_end_col)

        # remove possible line continuation preceding delete start position because could link to invalid following block statement

        del_ln, del_col, del_end_ln, del_end_col = del_loc

        if (del_ln > bound_ln and (not del_col or re_empty_line.match(lines[del_ln], 0, del_col)) and
            lines[del_ln - 1].endswith('\\')  # the endswith() is not definitive because of comments
        ):
            new_del_ln  = del_ln - 1
            new_del_col = 0 if new_del_ln != bound_ln else bound_col

            if code := _prev_src(lines, new_del_ln, new_del_col, new_del_ln, 0x7fffffffffffffff, True, False):  # skip over lcont but not comment if is there because that invalidates quick '\\' check above
                new_del_col = None if (src := code.src).startswith('#') else code.col + len(src)

            if new_del_col is not None:
                del_loc   = fstloc(new_del_ln, new_del_col, del_end_ln, del_end_col)
                indent    = lines[del_ln][:del_col]
                put_lines = ['', indent + put_lines[0], *put_lines[1:]] if put_lines else ['', indent]

        # finally done

        if ret_all:
            return (copy_loc, del_loc, put_lines, fstloc(bound_ln, bound_col, bound_end_ln, bound_end_col),
                    pre_comms, post_comms, pre_semi, post_semi, (block_ln, block_col))

        return copy_loc, del_loc, put_lines

    def _format_space(self, fst: FST, put_fst: FST,
                      block_loc: fstloc, put_loc: fstloc, fpre: FST | None, fpost: FST | None,
                      del_lines: list[str] | None, is_ins: bool, **options):
        """Add preceding and trailing newlines as needed. We always insert statements (or blocks of them) as their own
        lines but may also add newlines according to PEP8."""

        lines     = fst.root._lines
        put_lines = put_fst._lines
        put_body  = put_fst.a.body
        put_col   = put_loc.col
        pep8space = FST.get_option('pep8space', options)

        if not 0 <= pep8space <= 1:
            raise ValueError(f"'pep8space' must be True, False or 1, not {pep8space}")

        if is_pep8 := bool(put_body) and pep8space:  # no pep8 checks if only text being put (no AST body)
            pep8space = 2 if pep8space is True and (p := fst.parent_scope(True)) and isinstance(p.a, mod) else 1

        prepend = 2 if put_col else 0  # don't put initial empty line if putting on a first AST line at root

        if is_pep8 and fpre and ((put_ns := isinstance(put_body[0], NAMED_SCOPE)) or isinstance(fpre.a, NAMED_SCOPE)):  # preceding space
            if pep8space == 1 or (not fpre.pfield.idx and isinstance(a := fpre.a, Expr) and   # docstring
                                  isinstance(v := a.value, Constant) and isinstance(v.value, str)):
                want = 1
            else:
                want = pep8space

            if need := (want if not re_empty_line.match(put_lines[0]) else 1 if want == 2 and (  # how many empty lines at start of put_fst?
                        len(put_lines) < 2 or not re_empty_line.match(put_lines[1])) else 0):
                bound_ln = block_loc.ln
                ln       = put_loc.ln

                if not put_col:
                    need += 2

                if ln > bound_ln and re_empty_line.match(lines[ln], 0, put_col):  # reduce need by leading empty lines present in destination
                    if need := need - 1:
                        if (ln := ln - 1) > bound_ln and re_empty_line.match(lines[ln]):
                            need = 0

                if (need and not is_ins and put_ns and ln > bound_ln and re_comment_line_start.match(lines[ln]) and
                    not FST.get_option('precomms', options) and not FST.get_option('prespace', options)
                ):  # super-duper special case, replacing a named scope (at start) with another named scope, if not removing comments and/or space then don't insert space between preceding comment and put fst (because there was none before the previous named scope)
                    need = 0

                prepend += need

        if not (is_pep8 and fpost and (isinstance(put_body[-1], NAMED_SCOPE) or isinstance(fpost.a, NAMED_SCOPE))):  # trailing space
            postpend = bool((l := put_lines[-1]) and not re_empty_line.match(l))

        else:
            postpend = pep8space + 1
            ln       = len(put_lines) - 1

            while postpend:  # how many empty lines at end of put_fst?
                if (l := put_lines[ln]) and  not re_empty_line.match(l):
                    break

                postpend -= 1

                if (ln := ln - 1) < 0:
                    break

            if postpend:  # reduce needed postpend by trailing empty lines present in destination
                _, _, end_ln, end_col = put_loc
                len_lines             = len(lines)

                while postpend and re_empty_line.match(lines[end_ln], end_col):
                    postpend -= 1
                    end_col   = 0

                    if (end_ln := end_ln + 1) >= len_lines:
                        break

                postpend += not postpend

        if prepend:
            put_fst._put_src([''] * prepend, 0, 0, 0, 0, False)

        if postpend:
            put_lines.extend([bistr('')] * postpend)

        if del_lines:
            put_lines[-1] = bistr(put_lines[-1] + del_lines[0])

            put_lines.extend(bistr(s) for s in del_lines[1:])

        put_fst._touch()

    def put_slice_stmt(self, fst: FST, put_fst: FST, field: str,
                       block_loc: fstloc, opener_indent: str, block_indent: str,
                       ffirst: FST, flast: FST, fpre: FST | None, fpost: FST | None, **options,
    ) -> fstloc:  # put_loc
        """Put to block of statements(ish). Calculates put location and modifies `put_fst` as necessary to create proper
        code. The "ish" in statemnents means this can be used to put `ExceptHandler`s to a 'handlers' field or
        `match_case`s to a 'cases' field.

        If `ffirst` and `flast` are `None` it means that it is a pure insertion and no elements are being removed. In
        this case use `fpre` and `fpost` to determine locations, one of which could be missing if the insertion is at
        the beginning or end of the sequence. If all of these are `None` then this indicates a put to empty block, in
        which case use `fst`, `field` and/or `block_loc` for location.

        The first line of `put_fst` is unindented and should remain so as it is concatenated with the target line at the
        point of insertion. The last line of `put_fst` is likewise prefixed to the line following the deleted location.

        There is always an insertion or replacement operation if this is called, it is never just a delete or an empty
        assignment to an empty slice.

        If assigning to non-existent `orelse` or `finalbody` fields then the appropriate `else:` or `finally:` is
        prepended to `put_fst` for the final put. If replacing whole body of 'orelse' or 'finalbody' then the original
        'else:' or 'finally:' is not deleted (along with any preceding comments or spaces).

        Block being inserted into assumed to be normalized (no statement or multiple statements on block header logical
        line).

        **Parameters:**
        - `fst`: The destination `FST` container that is being put to.
        - `put_fst`: The block which is being put. Must be a `Module` with a `body` of one or multiple statmentish
            nodes. Not indented, indent and mutate this object to set what will be put at `put_loc`.
        - `field`: The name of the field being gotten from, e.g. `'body'`, `'orelse'`, etc...
        - `cut`: If `False` the operation is a copy, `True` means cut.
        - `opener_indent`: The indent string of the block header being put to (`if`, `with`, `class`, etc...), not the
            statements in the block.
        - `block_indent`: The indent string to be applied to `put_fst` statements in the block, which is the total
            indentation (including `opener_indent`) of the statements in the block.
        - `block_loc`: A rough location ancompassing the block part being edited outside of ASTS, used mostly if `fpre`
            / `fpost` not available. Always after `fpre` if present and before `fpost` if present. May include comments,
            line continuation backslashes and non-AST coding source like 'else:', but NO PARTS OF ASTS. May start before
            start or just past the block open colon.
        - `ffirst`: The first destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `flast`: The last destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `fpre`: The preceding-first destination `FST` or `fstloc`, not being replaced, may not exist if `ffirst` is
            first of seq.
        - `fpost`: The after-last destination `FST` or `fstloc` not being replaced, may not exist if `flast` is last of
            seq.
        - `options`: See `FST` source editing `options`. Options used here `precomms`, `postcomms`, `prespace`,
            `postspace`, `pep8space` and `elif_`. `space` options determine how many empty lines to remove in
            destination on replace. `pep8space` also applies on insert.

        **Returns:**
        - `fstloc`: location where the potentially modified `fst` source should be put, replacing whatever is at the
            location currently.
        """

        lines      = fst.root._lines
        put_lines  = put_fst._lines
        put_body   = put_fst.a.body
        is_handler = field == 'handlers'
        is_orelse  = field == 'orelse'
        docstr     = options.get('docstr')
        opt_elif   = FST.get_option('elif_', options)

        if not ffirst:  # pure insertion
            is_elif = (not fpre and not fpost and is_orelse and opt_elif and len(b := put_body) == 1 and
                       isinstance(b[0], If) and isinstance(fst.a, If))

            put_fst._indent_lns(opener_indent if is_handler or is_elif else block_indent, skip=0, docstr=docstr)

            if fpre:  # with preceding statement, maybe trailing statement
                ln, col, end_ln, end_col = block_loc

                while ln < end_ln:
                    if not (code := _next_src(lines, ln, col, ln, 0x7fffffffffffffff, True, True)):
                        put_loc = fstloc(ln, col, ln + 1, 0)

                        break

                    cln, ccol, csrc = code

                    if csrc.startswith('#'):
                        if cln < end_ln:
                            put_loc = fstloc(cln, ccol + len(csrc), cln + 1, 0)
                        else:
                            put_loc = fstloc(cln, ccol + len(csrc), cln, end_col)

                        break

                    if csrc == ';':
                        col = ccol + 1

                    else:
                        assert csrc == '\\'

                        ln  += 1
                        col  = 0

                else:
                    if fpost:  # next statement on semicolon separated line continuation
                        indent  = bistr(block_indent)
                        put_loc = block_loc

                    else:
                        indent  = bistr('')
                        put_loc = fstloc(end_ln, re_line_trailing_space.match(lines[end_ln], col).start(1),
                                         end_ln, end_col)

                    if (l := put_lines[-1]) and not re_empty_line.match(l):
                        put_lines.append(indent)
                    else:
                        put_lines[-1] = indent

                    put_fst._touch()

            elif fpost:  # no preceding statement, only trailing
                if is_handler or fst.is_root:  # special case, start will be after last statement or just after 'try:' colon or if is mod then there is no colon
                    ln, col = block_loc[:2]

                else:
                    ln, col  = _prev_find(lines, *block_loc, ':', True)
                    col     += 1

                if code := _next_src(lines, ln, col, *block_loc[2:], True, None):
                    ln, col, src  = code
                    col          += len(src)

                    assert ln < block_loc.end_ln

                if block_loc.end_ln > ln:
                    put_loc = fstloc(ln, col, ln + 1, 0)
                else:
                    put_loc = fstloc(ln, col, ln, block_loc.end_col)

                if (l := put_lines[-1]) and not re_empty_line.match(l):
                    put_lines.append(bistr(''))
                else:
                    put_lines[-1] = bistr('')

                put_fst._touch()

            else:  # insertion into empty block
                if is_elif:
                    ln, col, end_ln, end_col = put_body[0].f.bloc

                    put_fst._put_src(['elif'], ln, col, ln, col + 2, False)  # replace 'if' with 'elif'

                elif is_orelse:  # need to create these because they not there if body empty
                    put_fst._put_src([opener_indent + 'else:', ''], 0, 0, 0, 0, False)
                elif field == 'finalbody':
                    put_fst._put_src([opener_indent + 'finally:', ''], 0, 0, 0, 0, False)

                ln, col, end_ln, end_col = block_loc

                single_ln = ln == end_ln

                while code := _next_src(lines, ln, col, ln, end_col if single_ln else 0x7fffffffffffffff, True, False):
                    _, ccol, csrc = code

                    if code.src.startswith('#'):
                        col = ccol + len(csrc)  # we want to put after any post-comments

                        break

                    assert csrc.startswith(';')  # not expecting anything else after colon in empty block, '\\' is ignored in search

                    col = ccol + 1

                if single_ln:
                    put_loc = fstloc(ln, col, ln, end_col)
                else:
                    put_loc = fstloc(ln, col, ln + 1, 0)

            self._format_space(fst, put_fst, block_loc, put_loc, fpre, fpost, None, True, **options)

            return put_loc

        # replacement

        del_else_and_fin = False
        indent           = opener_indent if is_handler else block_indent

        if not fpre and not fpost and is_orelse and isinstance(fst.a, If):  # possible else <-> elif changes
            put_body    = put_fst.a.body
            orelse      = fst.a.orelse
            opt_elif    = FST.get_option('elif_', options)
            is_old_elif = orelse[0].f.is_elif()
            is_new_elif = opt_elif and len(put_body) == 1 and isinstance(put_body[0], If)

            if is_new_elif:
                ln, col, end_ln, end_col = put_body[0].f.bloc
                del_else_and_fin         = True
                indent                   = opener_indent

                put_fst._put_src(['elif'], ln, col, ln, col + 2, False)  # replace 'if' with 'elif'

            elif is_old_elif:
                indent = None

                put_fst._indent_lns(block_indent, skip=0, docstr=docstr)
                put_fst._put_src([opener_indent + 'else:', ''], 0, 0, 0, 0, False)

        if indent is not None:
            put_fst._indent_lns(indent, skip=0, docstr=docstr)

        copy_loc, put_loc, del_lines, bound, pre_comms, post_comms, pre_semi, post_semi, block_start = (
            self.get_slice_stmt(fst, field, True, block_loc, ffirst, flast, fpre, fpost,
                                del_else_and_fin=del_else_and_fin, ret_all=True, **options))

        put_ln, put_col, put_end_ln, put_end_col = put_loc

        if pre_semi and post_semi:
            if fpost:  # sandwiched between two semicoloned statements
                put_ln      = fpre.bend_ln
                put_col     = fpre.bend_col
                put_end_ln  = fpost.bln
                put_end_col = fpost.bcol
                del_lines   = [block_indent]

            else:  # eat whitespace after trailing useless semicolon
                put_col = re_line_trailing_space.match(lines[put_ln], 0, put_col).start(1)

        if put_loc.col:
            if re_empty_line.match(l := lines[put_ln][:put_col]):
                put_col = 0

                if del_lines:
                    del_lines[-1] = del_lines[-1] + l
                else:
                    del_lines = [l]

            elif del_lines and not del_lines[0]:
                del del_lines[0]

        put_loc = fstloc(put_ln, put_col, put_end_ln, put_end_col)

        self._format_space(fst, put_fst, block_loc, put_loc, fpre, fpost, del_lines, False, **options)

        return put_loc


# ----------------------------------------------------------------------------------------------------------------------
_src_edit = SrcEdit()

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
