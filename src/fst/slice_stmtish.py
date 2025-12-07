"""Low level get and put statement-ish slices (including single which is treated as a slice of one).

TODO: THIS NEEDS A REWRITE!"""

from __future__ import annotations

from typing import Any, Literal, Mapping

from . import fst

from .asttypes import (
    ASTS_BLOCK,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    ClassDef,
    ExceptHandler,
    For,
    FunctionDef,
    If,
    Match,
    Module,
    Try,
    While,
    With,
    TryStar,
    match_case,
    mod,
    _ExceptHandlers,
    _match_cases,
)

from .astutil import copy_ast
from .common import astfield, fstloc, next_find, prev_find
from .code import Code, code_as_stmts, code_as__ExceptHandlers, code_as__match_cases
from .traverse import prev_bound, next_bound_step, prev_bound_step
from .fst_misc import get_trivia_params, get_option_overridable, fixup_slice_indices

# ----------------------------------------------------------------------------------------------------------------------
# srcedit_old.py

from . import fst  # noqa: F811

from .asttypes import ASTS_SCOPE_NAMED, AST, Constant, Expr, If, mod  # noqa: F811
from .astutil import bistr

from .common import (
    fstloc,  # noqa: F811
    re_empty_line_start,
    re_empty_line,
    re_comment_line_start,
    re_empty_space,
    re_empty_line_cont_or_comment,
    next_frag,
    prev_frag,
    next_find,  # noqa: F811
    prev_find,  # noqa: F811
)

__all__ = ['get_slice_stmtish', 'put_slice_stmtish']


class SrcEdit:
    """This class controls most source editing behavior."""

    def pre_comments(
        self,
        lines: list[bistr],
        bound_ln: int,
        bound_col: int,
        bound_end_ln: int,
        bound_end_col: int,
        precomms: bool | str | None = None,
    ) -> tuple[int, int] | None:
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
            precomms = fst.FST.get_option('precomms')
        if not precomms:
            return None

        if (bound_ln == bound_end_ln
            or (
                bound_end_col
                and not re_empty_line.match(lines[bound_end_ln], 0, bound_end_col)
        )):
            return None

        allpre = precomms == 'all'
        pre_ln = None
        re_pat = re_empty_line_cont_or_comment if allpre else re_comment_line_start

        for ln in range(bound_end_ln - 1, bound_ln - (not bound_col), -1):  # only consider whole lines
            if not (m := re_pat.match(lines[ln])):
                break

            if not allpre or (g := m.group(1)) and g.startswith('#'):
                pre_ln = ln
                pre_col = 0

        return None if pre_ln is None else (pre_ln, pre_col)

    def post_comments(
        self,
        lines: list[bistr],
        bound_ln: int,
        bound_col: int,
        bound_end_ln: int,
        bound_end_col: int,
        postcomms: bool | str | None = None,
    ) -> tuple[int, int] | None:
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
            postcomms = fst.FST.get_option('postcomms')
        if not postcomms:
            return None

        blkpost = True if (allpost := postcomms == 'all') else postcomms == 'block'

        if single_ln := bound_end_ln == bound_ln:
            frag = next_frag(lines, bound_ln, bound_col, bound_ln, bound_end_col, True)
        else:
            frag = next_frag(lines, bound_ln, bound_col, bound_ln, 0x7fffffffffffffff, True)

        if frag:
            if not frag.src.startswith('#'):
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

    def get_slice_stmt(
        self,
        get_fst: fst.FST,
        field: str,
        cut: bool,
        block_loc: fstloc,  # TODO: clean this up
        ffirst: fst.FST,
        flast: fst.FST,
        fpre: fst.FST | None,
        fpost: fst.FST | None,
        *,
        del_else_and_fin: bool = True,
        **options,
    ) -> tuple[fstloc, fstloc | None, list[str] | None]:  # (copy_loc, del/put_loc, put_lines)
        """Copy or cut from block of statements. If cutting all elements from a deletable field like 'orelse' or
        'finalbody' then the corresponding 'else:' or 'finally:' will also be removed from the source (though not
        copied), and the formatting flags will apply to deleting any preceding comments and/or space. If you wish to
        apply different format flags to the copy and delete then copy what you want first then cut with different flags.

        **Parameters:**
        - `get_fst`: The source `FST` container that is being gotten from. No text has been changed at this point but the
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

        bound_ln, bound_col = fpre.bloc[2:] if fpre else block_loc[:2]
        bound_end_ln, bound_end_col = fpost.bloc[:2] if fpost else block_loc[2:]

        lines = get_fst.root._lines
        put_lines = None
        pre_comms = self.pre_comments(lines, bound_ln, bound_col, ffirst.bln, ffirst.bcol,
                                      options.get('precomms'))
        post_comms = self.post_comments(lines, flast.bend_ln, flast.bend_col, bound_end_ln, bound_end_col,
                                        options.get('postcomms'))
        pre_semi = not pre_comms and prev_find(lines, bound_ln, bound_col, ffirst.ln, ffirst.col, ';',
                                               True, comment=True, lcont=None)
        post_semi = not post_comms and next_find(lines, flast.end_ln, flast.end_col, bound_end_ln, bound_end_col, ';',
                                                 True, comment=True, lcont=None)

        copy_start = pre_comms or ffirst.bloc[:2]

        if not post_comms:
            copy_loc = fstloc(*copy_start, *flast.bloc[2:])
        elif post_comms[1]:  # comment does not end with newline
            copy_loc = fstloc(*copy_start, *post_comms)
        else:  # comment ends with newline but we don't want the copy to include it
            copy_loc = fstloc(*copy_start, post_comms[0] - 1, len(lines[post_comms[0] - 1]))

        if fpre:  # set block start to just past prev statement or block open (colon)
            block_ln, block_col = fpre.bloc[2:]

        elif frag := prev_frag(lines, bound_ln, bound_col, copy_loc.ln, copy_loc.col, False, False):
            block_ln, block_col, src = frag
            block_col += len(src)

        else:
            block_ln = bound_ln
            block_col = bound_col

        # get copy and delete locations according to possible combinations of preceding and trailing comments, semicolons and line continuation backslashes

        def fix_post_semi_with_tail(end_ln: int, end_col: int, starts_line: bool) -> tuple[fstloc, list[str]] | None:
            if frag := next_frag(lines, end_ln, end_col, end_ln,
                                 bound_end_col if end_ln == bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                put_lines = None
                ln, col = copy_loc[:2]

                if frag.src.startswith('#'):
                    del_loc = fstloc(ln, col, end_ln, frag.col)

                    if starts_line and fpost:
                        put_lines = [re_empty_line_start.match(lines[copy_loc.ln]).group(0)]  # can use copy_loc.ln because if got this line there are never any preceding comments

                else:  # HACK FIX! TODO: do this properly, only here because '\\\n stmt' does not work at module level even though it works inside indented blocks, otherwise `del_loc` above would be sufficient unconditionally
                    del_loc = fstloc(ln, 0, bound_end_ln, bound_end_col)

                    if fpost:
                        put_lines = [ffirst._get_indent()]  # SHOULDN'T DO THIS HERE!!!

                return del_loc, put_lines

            return None

        def fix_post_semi(post_semi: tuple[int, int]) -> tuple[fstloc, list[str] | None]:
            end_ln, end_col = post_semi
            end_col += 1

            if t := fix_post_semi_with_tail(end_ln, end_col, False):
                del_loc, put_lines = t

            else:
                ln, col = copy_loc[:2]
                del_col = 0 if ln != block_ln else block_col

                if end_ln == bound_end_ln:
                    del_loc = fstloc(ln, col if fpost else del_col, bound_end_ln, bound_end_col)
                    put_lines = None

                else:
                    del_loc = fstloc(ln, del_col, end_ln + 1, 0)
                    put_lines = ['', ''] if del_col else None

            return del_loc, put_lines

        if pre_comms:
            if post_comms:
                del_loc = fstloc(*pre_comms, *post_comms)

            else:
                if not post_semi:
                    end_ln, end_col = copy_loc[2:]

                else:
                    end_ln, end_col = post_semi
                    end_col += 1

                if t := fix_post_semi_with_tail(end_ln, end_col, True):  # we know it starts a line because pre_comms exists
                    del_loc, put_lines = t

                elif end_ln != bound_end_ln:
                    del_loc = fstloc(*pre_comms, end_ln + 1, 0)

                else:
                    del_loc = fstloc(*pre_comms, bound_end_ln, bound_end_col)

                    if fpost:  # ends at next statement, otherwise if fpost doesn't exist then was empty line after a useless trailing ';'
                        put_lines = [re_empty_line_start.match(lines[ffirst.bln]).group(0)]  # we know it starts a line because pre_comms exists, not copy_loc.ln because that is comment

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

                if next_frag(lines, end_ln, end_col, end_ln,
                             bound_end_col if at_bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                    del_loc = fstloc(*fpre.bloc[2:], end_ln, end_col)
                else:
                    del_loc = fstloc(*fpre.bloc[2:], end_ln, len(lines[end_ln]))

        elif post_semi:
            del_loc, put_lines = fix_post_semi(post_semi)

        else:
            ln, col, end_ln, end_col = copy_loc
            at_bound_end_ln = end_ln == bound_end_ln

            if frag := next_frag(lines, end_ln, end_col, end_ln,
                                 bound_end_col if at_bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                del_loc = fstloc(ln, col, end_ln, frag.col)

            else:
                del_col = 0 if ln != block_ln else block_col

                if not at_bound_end_ln:
                    del_loc = fstloc(ln, del_col, end_ln + 1, 0)
                else:
                    del_loc = fstloc(ln, del_col, bound_end_ln, bound_end_col)

        # special case of deleting everything from a block

        if not fpre and not fpost:
            if (del_else_and_fin
                and (
                    (is_finally := field == 'finalbody')  # remove 'else:' or 'finally:' (but not 'elif ...:' as that lives in first cut statement)
                    or (field == 'orelse' and not lines[ffirst.bln].startswith('elif', ffirst.bcol))
            )):
                del_ln, del_col, del_end_ln, del_end_col = del_loc

                del_ln, del_col = prev_find(lines, bound_ln, bound_col, del_ln, del_col,
                                            'finally' if is_finally else 'else', False, comment=False, lcont=False)  # `first=False` because have to skip over ':'

                if put_lines:
                    put_lines[0] = lines[del_ln][:del_col] + put_lines[0]  # prepend block start indentation to existing indentation, silly but whatever

                if pre_pre_comms := self.pre_comments(lines, bound_ln, bound_col, del_ln, 0, options.get('precomms')):
                    del_ln, _ = pre_pre_comms

                del_loc = fstloc(del_ln, 0, del_end_ln, del_end_col)

            elif get_fst.parent and not del_loc.end_col and del_loc.ln == block_ln:  # avoid deleting trailing newline of only statement just past block open
                del_ln, del_col, del_end_ln, del_end_col = del_loc

                del_loc = fstloc(del_ln, del_col, (ln := del_end_ln - 1), len(lines[ln]))

        # delete preceding and trailing empty lines according to 'pep8' and 'space' format flags

        prespace = o_prespace = (float('inf') if (o := fst.FST.get_option('prespace', options)) is True else int(o))
        postspace = o_postspace = (float('inf') if (o := fst.FST.get_option('postspace', options)) is True else int(o))
        pep8space = fst.FST.get_option('pep8space', options)

        if pep8space:
            if not 0 <= pep8space <= 1:
                raise ValueError(f"'pep8space' must be True, False or 1, not {pep8space}")

            pep8space = 2 if pep8space is True and (p := get_fst.parent_scope(True)) and isinstance(p.a, mod) else 1

            if (fpre
                and isinstance(ffirst.a, ASTS_SCOPE_NAMED)
                and (
                    fpre.pfield.idx
                    or not isinstance(a := fpre.a, Expr)
                    or not isinstance(v := a.value, Constant)
                    or not isinstance(v.value, str)
                )
            ):
                prespace = max(prespace, pep8space)

            elif fpost and isinstance(flast.a, ASTS_SCOPE_NAMED):
                postspace = max(postspace, pep8space)

        del_ln, del_col, del_end_ln, del_end_col = del_loc

        if prespace:
            new_del_ln = max(bound_ln + bool(bound_col), del_ln - prespace)  # first possible full empty line to delete to

            if del_ln > new_del_ln and (not del_col or re_empty_line.match(lines[del_ln], 0, del_col)):
                if frag := prev_frag(lines, new_del_ln, 0, del_ln, 0, True, False):
                    new_del_ln = frag.ln + 1

                if new_del_ln < del_ln:
                    indent = lines[del_ln][:del_col]
                    put_lines = [indent + put_lines[0], *put_lines[1:]] if put_lines else [indent]
                    del_ln = new_del_ln
                    del_col = 0

        if postspace:
            if not del_end_col:
                new_del_end_ln = min(bound_end_ln, del_end_ln + postspace)  # last possible end line to delete to
                del_end_ln = (frag.ln
                              if (frag := next_frag(lines, del_end_ln, 0, new_del_end_ln, 0, True, True)) else
                              new_del_end_ln)

            elif del_end_col == len(lines[del_end_ln]):
                new_del_end_ln = min(bound_end_ln, del_end_ln + postspace + 1)  # account for not ending on newline
                del_end_ln = (frag.ln - 1
                              if (frag := next_frag(lines, del_end_ln, del_end_col, new_del_end_ln, 0, True, True)) else
                              new_del_end_ln - 1)
                del_end_col = len(lines[del_end_ln])

        del_pre_post_space = (min(o_prespace, del_loc.ln - del_ln),
                              min(o_postspace, del_end_ln - del_loc.end_ln))  # how many deleted empty leading and trailing lines (minimized to original requested value because may have been increased to pep8space)
        del_loc = fstloc(del_ln, del_col, del_end_ln, del_end_col)

        # remove possible line continuation preceding delete start position because could link to invalid following block statement, but only if there is not a post_semi which is not being deleted

        del_ln, del_col, del_end_ln, del_end_col = del_loc

        if (del_ln > bound_ln
            and (not del_col or re_empty_line.match(lines[del_ln], 0, del_col))
            and lines[del_ln - 1].endswith('\\')  # the endswith() is not definitive because a comment may end with it
            and (not post_semi or (post_semi < (del_end_ln, del_end_col)))  # very special case of leaving trailing semicolon on next line, which absolutely needs the line continuation above
        ):
            new_del_ln = del_ln - 1
            new_del_col = 0 if new_del_ln != bound_ln else bound_col

            if frag := prev_frag(lines, new_del_ln, new_del_col, new_del_ln, 0x7fffffffffffffff, True, False):  # skip over lcont but not comment if is there because that invalidates quick '\\' check above
                new_del_col = None if (src := frag.src).startswith('#') else frag.col + len(src)

            if new_del_col is not None:
                del_loc = fstloc(new_del_ln, new_del_col, del_end_ln, del_end_col)
                indent = lines[del_ln][:del_col]
                put_lines = ['', indent + put_lines[0], *put_lines[1:]] if put_lines else ['', indent]

        # finally done

        return copy_loc, del_loc, put_lines, del_pre_post_space, (pre_semi, post_semi)

    def _format_space(
        self,
        tgt_fst: fst.FST,
        put_fst: fst.FST,
        put_body: list[AST],
        block_loc: fstloc,
        put_loc: fstloc,
        fpre: fst.FST | None,
        fpost: fst.FST | None,
        del_lines: list[str] | None,
        is_ins: bool,
        **options,
    ) -> None:
        """Add preceding and trailing newlines as needed. We always insert statements (or blocks of them) as their own
        lines but may also add newlines according to PEP8."""

        lines = tgt_fst.root._lines
        put_lines = put_fst._lines
        put_col = put_loc.col
        pep8space = fst.FST.get_option('pep8space', options)

        if not 0 <= pep8space <= 1:
            raise ValueError(f"'pep8space' must be True, False or 1, not {pep8space}")

        if is_pep8 := bool(put_body) and pep8space:  # no pep8 checks if only text being put (no AST body)
            pep8space = 2 if pep8space is True and (p := tgt_fst.parent_scope(True)) and isinstance(p.a, mod) else 1

        prepend = 2 if put_col else 0  # don't put initial empty line if putting on a first AST line at root

        if (is_pep8
            and fpre
            and ((put_ns := isinstance(put_body[0], ASTS_SCOPE_NAMED)) or isinstance(fpre.a, ASTS_SCOPE_NAMED))
        ):  # preceding space
            if (pep8space == 1
                or (
                    not fpre.pfield.idx
                    and isinstance(a := fpre.a, Expr)  # docstring
                    and isinstance(v := a.value, Constant)
                    and isinstance(v.value, str)
            )):
                want = 1
            else:
                want = pep8space

            if need := (
                want
                if not re_empty_line.match(put_lines[0])
                else 1
                if (want == 2 and (len(put_lines) < 2 or not re_empty_line.match(put_lines[1])))
                else 0
            ):  # how many empty lines at start of put_fst?
                bound_ln = block_loc.ln
                ln = put_loc.ln

                if not put_col:
                    need += 2

                if ln > bound_ln and re_empty_line.match(lines[ln], 0, put_col):  # reduce need by leading empty lines present in destination
                    if need := need - 1:
                        if (ln := ln - 1) > bound_ln and re_empty_line.match(lines[ln]):
                            need = 0

                if (need
                    and not is_ins
                    and put_ns
                    and ln > bound_ln
                    and re_comment_line_start.match(lines[ln])
                    and not fst.FST.get_option('precomms', options)
                    and not fst.FST.get_option('prespace', options)
                ):  # super-duper special case, replacing a named scope (at start) with another named scope, if not removing comments and/or space then don't insert space between preceding comment and put fst (because there was none before the previous named scope)
                    need = 0

                prepend += need

        if not (
            is_pep8 and fpost and (isinstance(put_body[-1], ASTS_SCOPE_NAMED) or isinstance(fpost.a, ASTS_SCOPE_NAMED))
        ):  # if don't need pep8space then maybe just need trailing newline
            if put_loc.end_col == len(lines[-1]) and put_loc.end_ln == len(lines) - 1:  # if putting to very end of source then don't add newlines
                postpend = 0
            else:  # otherwise if last line of put contains something then append a newline
                postpend = bool((l := put_lines[-1]) and not re_empty_line.match(l))

        else:
            postpend = pep8space + 1
            ln = len(put_lines) - 1

            while postpend:  # how many empty lines at end of put_fst?
                if (l := put_lines[ln]) and not re_empty_line.match(l):
                    break

                postpend -= 1

                if (ln := ln - 1) < 0:
                    break

            if postpend:  # reduce needed postpend by trailing empty lines present in destination
                _, _, end_ln, end_col = put_loc
                len_lines = len(lines)

                while postpend and re_empty_line.match(lines[end_ln], end_col):
                    postpend -= 1
                    end_col = 0

                    if (end_ln := end_ln + 1) >= len_lines:
                        break

                postpend += not postpend

        if prepend:
            put_fst._put_src([''] * prepend, 0, 0, 0, 0, False)

        if postpend:
            if put_lines[-1].isspace():  # if last line is a pure indent then insert new lines before it
                put_lines[-1:-1] = [bistr('')] * postpend
            else:
                put_lines.extend([bistr('')] * postpend)

        if del_lines:
            put_lines[-1] = bistr(put_lines[-1] + del_lines[0])

            put_lines.extend(bistr(s) for s in del_lines[1:])

        put_fst._touch()

    def put_slice_stmt(
        self,
        tgt_fst: fst.FST,
        put_fst: fst.FST,
        put_body: list[AST],
        field: str,
        block_loc: fstloc,
        opener_indent: str,
        block_indent: str,
        ffirst: fst.FST,
        flast: fst.FST,
        fpre: fst.FST | None,
        fpost: fst.FST | None,
        *,
        docstr_strict_exclude: AST | None = None,
        **options,
    ) -> fstloc:  # put_loc
        """Put to block of statements(ish). Calculates put location and modifies `put_fst` as necessary to create proper
        frag. The "ish" in statemnents means this can be used to put `ExceptHandler`s to a 'handlers' field or
        `match_case`s to a 'cases' field.

        If `ffirst` and `flast` are `None` it means that it is a pure insertion and no elements are being removed. In
        this case use `fpre` and `fpost` to determine locations, one of which could be missing if the insertion is at
        the beginning or end of the sequence. If all of these are `None` then this indicates a put to empty block, in
        which case use `tgt_fst`, `field` and/or `block_loc` for location.

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
        - `tgt_fst`: The destination `FST` container that is being put to.
        - `put_fst`: The block which is being put. Must be a `Module` with a `body` of one or multiple statmentish
            nodes or a SPECIAL SLICE `_ExceptHandlers` or `_match_cases`. Not indented, indent and mutate this object to
            set what will be put at `put_loc`.
        - `put_body`: The list of `AST` nodes of `put_fst`.
        - `field`: The name of the field being gotten from, e.g. `'body'`, `'orelse'`, etc...
        - `cut`: If `False` the operation is a copy, `True` means cut.
        - `opener_indent`: The indent string of the block header being put to (`if`, `with`, `class`, etc...), not the
            statements in the block.
        - `block_indent`: The indent string to be applied to `put_fst` statements in the block, which is the total
            indentation (including `opener_indent`) of the statements in the block.
        - `block_loc`: A rough location encompassing the block part being edited outside of ASTS, used mostly if `fpre`
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
        - `fstloc`: location where the potentially modified `put_fst` source should be put, replacing whatever is at the
            location currently.
        """

        opt_elif = fst.FST.get_option('elif_', options)
        docstr = fst.FST.get_option('docstr', options)
        lines = tgt_fst.root._lines
        put_lines = put_fst._lines
        is_handler = field == 'handlers'
        is_orelse = field == 'orelse'

        if not ffirst:  # pure insertion
            is_elif = (not fpre and not fpost and is_orelse and opt_elif and len(b := put_body) == 1 and
                       isinstance(b[0], If) and isinstance(tgt_fst.a, If))

            put_fst._indent_lns(opener_indent if is_handler or is_elif else block_indent, skip=0, docstr=docstr,
                                docstr_strict_exclude=docstr_strict_exclude)

            if fpre:  # with preceding statement, maybe trailing statement
                ln, col, end_ln, end_col = block_loc

                while ln < end_ln:
                    if not (frag := next_frag(lines, ln, col, ln, 0x7fffffffffffffff, True, True)):
                        put_loc = fstloc(ln, col, ln + 1, 0)

                        break

                    cln, ccol, csrc = frag

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

                        ln += 1
                        col = 0

                else:
                    if fpost:  # next statement on semicolon separated line continuation
                        indent = bistr(block_indent)
                        put_loc = block_loc

                    else:
                        indent = bistr('')
                        put_loc = fstloc(end_ln, re_empty_space.search(lines[end_ln], col).start(), end_ln, end_col)

                    if (l := put_lines[-1]) and not re_empty_line.match(l):
                        put_lines.append(indent)
                    else:
                        put_lines[-1] = indent

                    put_fst._touch()

            elif fpost:  # no preceding statement, only trailing
                if is_handler or tgt_fst.is_root:
                    if not is_handler and isinstance(tgt_fst.a, ASTS_BLOCK):  # in this case start will be before block header colon
                        ln, col = next_find(lines, *block_loc, ':')
                        col += 1

                    else:  # special case, start will be after last statement or just after 'try:' colon or if is mod then there is no colon
                        ln, col = block_loc[:2]

                else:  # start is after block header open colon, search back to it
                    ln, col = prev_find(lines, *block_loc, ':', True)
                    col += 1

                if frag := next_frag(lines, ln, col, *block_loc[2:], True, None):
                    ln, col, src = frag
                    col += len(src)

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

                while frag := next_frag(lines, ln, col, ln, end_col if single_ln else 0x7fffffffffffffff, True, False):
                    _, ccol, csrc = frag

                    if frag.src.startswith('#'):
                        col = ccol + len(csrc)  # we want to put after any post-comments

                        break

                    assert csrc.startswith(';')  # not expecting anything else after colon in empty block, '\\' is ignored in search

                    col = ccol + 1

                if single_ln:
                    put_loc = fstloc(ln, col, ln, end_col)
                else:
                    put_loc = fstloc(ln, col, ln + 1, 0)

            self._format_space(tgt_fst, put_fst, put_body, block_loc, put_loc, fpre, fpost, None, True, **options)

            return put_loc

        # replacement

        del_else_and_fin = False
        indent = opener_indent if is_handler else block_indent

        if not fpre and not fpost and is_orelse and isinstance(tgt_fst.a, If):  # possible else <-> elif changes
            orelse = tgt_fst.a.orelse
            opt_elif = fst.FST.get_option('elif_', options)
            is_old_elif = orelse[0].f.is_elif()
            is_new_elif = opt_elif and len(put_body) == 1 and isinstance(put_body[0], If)

            if is_new_elif:
                ln, col, end_ln, end_col = put_body[0].f.bloc
                del_else_and_fin = True
                indent = opener_indent

                put_fst._put_src(['elif'], ln, col, ln, col + 2, False)  # replace 'if' with 'elif'

            elif is_old_elif:
                indent = None

                put_fst._indent_lns(block_indent, skip=0, docstr=docstr, docstr_strict_exclude=docstr_strict_exclude)
                put_fst._put_src([opener_indent + 'else:', ''], 0, 0, 0, 0, False)

        if indent is not None:
            put_fst._indent_lns(indent, skip=0, docstr=docstr, docstr_strict_exclude=docstr_strict_exclude)

        _, put_loc, del_lines, _, (pre_semi, post_semi) = (
            self.get_slice_stmt(tgt_fst, field, True, block_loc, ffirst, flast, fpre, fpost,
                                del_else_and_fin=del_else_and_fin, **options))

        put_ln, put_col, put_end_ln, put_end_col = put_loc

        if pre_semi and post_semi:
            if fpost:  # sandwiched between two semicoloned statements
                put_ln = fpre.bend_ln
                put_col = fpre.bend_col
                put_end_ln = fpost.bln
                put_end_col = fpost.bcol
                del_lines = [block_indent]

            else:  # eat whitespace after trailing useless semicolon
                put_col = re_empty_space.search(lines[put_ln], 0, put_col).start()

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

        self._format_space(tgt_fst, put_fst, put_body, block_loc, put_loc, fpre, fpost, del_lines, False, **options)

        return put_loc


_src_edit = SrcEdit()

# ----------------------------------------------------------------------------------------------------------------------

def _set_end_pos_w_maybe_trailing_semicolon(self: fst.FST, end_ln: int, end_col: int) -> None:
    """Set end position of last child `self` and parents after checking for trailing semicolon after given position."""

    lines = self.root._lines

    if (frag := next_frag(lines, end_ln, end_col, len(lines) - 1, 0x7fffffffffffffff)) and frag.src.startswith(';'):
        end_ln, end_col, _ = frag
        end_col += 1  # just past the semicolon

    self._set_end_pos(end_ln + 1, lines[end_ln].c2b(end_col))


def _set_end_pos_after_del(self: fst.FST, bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int) -> None:
    """Fix end location of a block statement after its last child (position-wise, not last existing child) has been
    cut or deleted. Will set end position of `self` and any parents who `self` is the last child of to the new last
    position if it is past the block-open colon, otherwise set end at just past the block-open colon.

    **Parameters:**
    - `(bound_ln, bound_col)`: Position before block colon but after and pre-colon `AST` node.
    - `(bound_end_ln, bound_end_col)`: Position after block colon, probably start of deleted region, only used if
        new last child is before colon.
    """

    if ((last_child := self.last_child())  # easy enough when we have a new last child
        and last_child.pfield.name in ('body', 'orelse', 'finalbody', 'handlers', 'cases')  # but make sure its past the block open colon
    ):
        _, _, end_ln, end_col = last_child.loc

    elif end := prev_find(self.root._lines, bound_ln, bound_col, bound_end_ln, bound_end_col, ':'):  # find first preceding block colon, its there unless first opened block in module
        end_ln, end_col = end
        end_col += 1  # just past the colon

    else:
        end_ln = bound_ln
        end_col = bound_col

    _set_end_pos_w_maybe_trailing_semicolon(self, end_ln, end_col)


def _elif_to_else_if(self: fst.FST, docstr: bool | Literal['strict'] = True) -> None:
    """Convert an 'elif something:\\n  ...' to 'else:\\n  if something:\\n    ...'. Make sure to only call on an
    actual `elif`, meaning the lone `If` statement in the parent's `orelse` block which is an actual `elif` and not
    an `if`."""

    indent = self._get_indent()

    self._indent_lns(skip=0, docstr=docstr)

    if not self.next():  # last child?
        self.parent._set_end_pos((a := self.a).end_lineno, a.end_col_offset)  # we're an elif, there is definitely a parent

    ln, col, _, _ = self.loc

    self._put_src(['if'], ln, col, ln, col + 4, False)
    self._put_src([indent + 'else:', indent + self.root.indent], ln, 0, ln, col, False)


def _normalize_block(self: fst.FST, field: str = 'body', *, indent: str | None = None) -> None:
    """Move statements on the same logical line as a block open to their own line, e.g:
    ```
    if a: call()
    ```
    Becomes:
    ```
    if a:
        call()
    ```

    **Parameters:**
    - `field`: Which block to normalize (`'body'`, `'orelse'`, `'handlers'`, `'finalbody'`).
    - `indent`: The indentation to use for the relocated line if already known, saves a call to `_get_indent()`.
    """

    if isinstance(self.a, mod) or not (block := getattr(self.a, field)) or not isinstance(block, list):
        return

    b0 = block[0].f
    b0_ln, b0_col, _, _ = b0.bloc
    root = self.root

    if not (colon := prev_find(root._lines, *prev_bound(b0), b0_ln, b0_col, ':', True, comment=True, lcont=None)):  # must be there
        return

    if indent is None:
        indent = b0._get_indent()

    ln, col = colon

    self._put_src(['', indent], ln, col + 1, b0_ln, b0_col, False)


def _can_del_all(self: fst.FST, field: str, options: Mapping[str, Any]) -> bool:
    """Whether can delete all elements of af a body list of children according to options or not."""

    if field == 'orelse' or not get_option_overridable('norm', 'norm_self', options):
        return True

    if field == 'body':
        return isinstance(self.a, Module)

    if field == 'cases':
        return isinstance(self.a, _match_cases)

    if field == 'finalbody':
        return bool(self.a.handlers)

    return isinstance(a := self.a, _ExceptHandlers) or bool(a.finalbody)  # field == 'handlers'


# ......................................................................................................................

def _get_slice_stmtish_old(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    one: bool,
    options: Mapping[str, Any],
    ld_neg: bool,
    tr_neg: bool,
) -> fst.FST:
    ast = self.a
    body = getattr(ast, field)
    start, stop = fixup_slice_indices(len(body), start, stop)

    if start == stop:
        if field == 'handlers':
            return fst.FST(_ExceptHandlers([], 1, 0, 1, 0), [''], None, from_=self)
        elif field == 'cases':
            return fst.FST(_match_cases([], 1, 0, 1, 0), [''], None, from_=self)

        return fst.FST(Module(body=[], type_ignores=[]), [''], None, from_=self)

    if cut and not start and stop == len(body) and not _can_del_all(self, field, options):
        raise ValueError(f'cannot cut all elements from {ast.__class__.__name__}.{field} without norm_self=False')

    ffirst = body[start].f
    flast = body[stop - 1].f
    fpre = body[start - 1].f if start else None
    fpost = body[stop].f if stop < len(body) else None
    indent = ffirst._get_indent()

    block_loc = fstloc(*(fpre.bloc[2:] if fpre else prev_bound_step(ffirst)),
                       *(fpost.bloc[:2] if fpost else next_bound_step(flast)))

    copy_loc, put_loc, put_lines, (del_prespace, del_postspace), _ = (
        _src_edit.get_slice_stmt(self, field, cut, block_loc, ffirst, flast, fpre, fpost, **options))

    if not cut:
        asts = [copy_ast(body[i]) for i in range(start, stop)]
        put_loc = None

    else:
        is_last_child = not fpost and not flast.next()
        asts = body[start : stop]

        del body[start : stop]

        for i in range(start, len(body)):
            body[i].f.pfield = astfield(field, i)

    if not one:
        if field == 'handlers':
            lines = self.root._lines
            copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

            get_ast = _ExceptHandlers(handlers=asts, lineno=copy_ln + 1, col_offset=lines[copy_ln].c2b(copy_col),
                                      end_lineno=copy_end_ln + 1, end_col_offset=lines[copy_end_ln].c2b(copy_end_col))

        elif field == 'cases':
            lines = self.root._lines
            copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

            get_ast = _match_cases(cases=asts, lineno=copy_ln + 1, col_offset=lines[copy_ln].c2b(copy_col),
                                   end_lineno=copy_end_ln + 1, end_col_offset=lines[copy_end_ln].c2b(copy_end_col))

        else:
            get_ast = Module(body=asts, type_ignores=[])

    elif len(asts) == 1:
        get_ast = asts[0]
    else:
        raise ValueError('cannot specify `one=True` if getting multiple statements')

    prefix = [''] * (del_prespace + 1) if del_prespace and not ld_neg else None  # if maybe requested leading space returned (ld_neg=False) and there was leading space deleted then add this many leading empty lines, this is a HACK because old stmtish slicing did not support this, need to redo
    suffix = [''] * (del_postspace + 1) if del_postspace and not tr_neg else None  # same for trailing space

    fst_, _ = self._make_fst_and_dedent(indent, get_ast, copy_loc, prefix, suffix, put_loc, put_lines,
                                        docstr=fst.FST.get_option('docstr', options),
                                        docstr_strict_exclude=asts[0] if asts and start else None)  # if slice gotten doesn't start at 0 then first element cannot be a 'strict' docstr even though it is first in the new slice

    if cut and is_last_child:  # correct for removed last child nodes or last nodes past the block open colon
        _set_end_pos_after_del(self, block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)

    if len(asts) == 1 and isinstance(a := asts[0], If):
        a.f._maybe_fix_elif()

    return fst_


def _put_slice_stmtish_old(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> bool:
    ast = self.a
    root = self.root
    body = getattr(ast, field)
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if code is None:
        put_fst = None
        put_fst_end_nl = False

    else:
        if is_handlers := (field == 'handlers'):
            if len_slice == len_body and not isinstance(code, AST):  # if replacing all handlers then can change Try <-> TryStar according to what is being put (if we know, we don't know if code is AST)
                is_trystar = None
            elif isinstance(ast, Try):
                is_trystar = False
            elif isinstance(ast, TryStar):
                is_trystar = True
            else:  # isinstance(ast, _ExceptHandlers)
                is_trystar = body[0].f._is_except_star() if body else None

            put_fst = code_as__ExceptHandlers(code, root.parse_params, is_trystar=is_trystar)
            put_body = put_fst.a.handlers

        elif field == 'cases':
            put_fst = code_as__match_cases(code, root.parse_params)
            put_body = put_fst.a.cases

        else:  # 'body', 'orelse', 'finalbody'
            put_fst = code_as_stmts(code, root.parse_params)
            put_body = put_fst.a.body

        # NOTE: we do not convert an empty put_body to put_fst=None because we may be putting just comments and/or empty space

        put_fst_lines = put_fst._lines
        put_fst_end_nl = not put_fst_lines[-1]

        if one and len(put_body) != 1:
            raise ValueError('expecting a single element')

    if not len_slice and (not put_fst or (not put_body and len(put_fst_lines) == 1 and not put_fst_lines[0])):  # deleting empty slice or assigning empty fst to empty slice, noop
        return True

    if (not put_fst or not put_body) and len_slice == len_body and not _can_del_all(self, field, options):
        raise ValueError(f'cannot delete all elements from {ast.__class__.__name__}.{field} without norm_self=False')

    lines = root._lines
    fpre = body[start - 1].f if start else None
    fpost = body[stop].f if stop < len_body else None

    if put_fst:
        opener_indent = self._get_indent()

        if not body:
            block_indent = (opener_indent
                            if isinstance(self.a, (mod, _ExceptHandlers, _match_cases)) else
                            opener_indent + root.indent)

        elif not (b0 := body[0]).f.is_elif():
            block_indent = b0.f._get_indent()
        elif (bb := b0.body) or (bb := b0.orelse):
            block_indent = bb[0].f._get_indent()
        else:
            block_indent = opener_indent + root.indent

        if fpre or fpost:
            _normalize_block(self, field, indent=block_indent)  # don't want to bother figuring out if valid to insert to statements on single block logical line

    if len_slice:  # replacement
        ffirst = body[start].f
        flast = body[stop - 1].f

        block_loc = fstloc(*(fpre.bloc[2:] if fpre else prev_bound_step(ffirst)),
                           *(fpost.bloc[:2] if fpost else next_bound_step(flast)))

        is_last_child = not fpost and not flast.next()

    else:  # insertion
        ffirst = flast = None

        if field == 'orelse' and len_body == 1 and (f := body[0].f).is_elif():
            _elif_to_else_if(f, fst.FST.get_option('docstr', options))

        if fpre:
            block_loc = fstloc(*fpre.bloc[2:], *(fpost.bloc[:2] if fpost else next_bound_step(fpre)))
            is_last_child = not fpost and not fpre.next()

        elif fpost:
            if isinstance(ast, (mod, _ExceptHandlers, _match_cases)):  # put after all header stuff in module
                ln, col, _, _ = fpost.bloc
                block_loc = fstloc(ln, col, ln, col)

            elif field != 'handlers' or ast.body:
                block_loc = fstloc(*prev_bound_step(fpost), *fpost.bloc[:2])

            else:  # special case because 'try:' doesn't have ASTs inside it and each 'except:' lives at the 'try:' indentation level
                end_ln, end_col = fpost.bloc[:2]
                ln, col = prev_find(lines, *prev_bound_step(fpost), end_ln, end_col, ':')
                block_loc = fstloc(ln, col + 1, end_ln, end_col)

            is_last_child = False

        else:  # insertion into empty block (or nonexistent 'else' or 'finally' block)
            if not put_body and field in ('orelse', 'finalbody'):
                raise ValueError(f"cannot insert empty statement into empty '{field}' field")

            if isinstance(ast, (FunctionDef, AsyncFunctionDef, ClassDef, With, AsyncWith, Match, ExceptHandler,
                                match_case)):  # only one block possible, 'body' or 'cases'
                block_loc = fstloc(*self.bloc[2:], *next_bound_step(self))  # end of bloc will be just past ':'
                is_last_child = True

            elif isinstance(ast, (mod, _ExceptHandlers, _match_cases)):  # put after all header stuff in module or top level ExceptHandler or match_case slice
                _, _, end_ln, end_col = self.bloc

                block_loc = fstloc(end_ln, end_col, end_ln, end_col)
                is_last_child = True

            elif isinstance(ast, (For, AsyncFor, While, If)):  # 'body' or 'orelse'
                if field == 'orelse':
                    is_last_child = True

                    if not (body_ := ast.body):
                        block_loc = fstloc(*self.bloc[2:], *next_bound_step(self))
                    else:
                        block_loc = fstloc(*body_[-1].f.bloc[2:], *next_bound_step(self))

                else:  # field == 'body':
                    if orelse := ast.orelse:
                        ln, col = next_find(lines, *(f := orelse[0].f).prev().bloc[2:], *f.bloc[:2], ':')  # we know its there
                        block_loc = fstloc(ln, col + 1, *orelse[0].f.bloc[:2])
                        is_last_child = False

                    else:
                        block_loc = fstloc(*self.bloc[2:], *next_bound_step(self))
                        is_last_child = True

            else:  # isinstance(ast, (Try, TryStar))
                assert isinstance(ast, (Try, TryStar))

                if field == 'finalbody':
                    is_last_child = True

                    if not (block := ast.orelse) and not (block := ast.handlers) and not (block := ast.body):
                        block_loc = fstloc(*self.bloc[2:], *next_bound_step(self))
                    else:
                        block_loc = fstloc(*block[-1].f.bloc[2:], *next_bound_step(self))

                elif field == 'orelse':
                    if finalbody := ast.finalbody:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')  # we can use bloc[:2] even if there are ASTs between that and here because 'finally' must be on its own line
                        is_last_child = False

                    else:
                        end_ln, end_col = next_bound_step(self)
                        is_last_child = True

                    if not (block := ast.handlers) and not (block := ast.body):
                        ln, col = prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                        block_loc = fstloc(ln, col + 1, end_ln, end_col)

                    else:
                        block_loc = fstloc(*block[-1].f.bloc[2:], end_ln, end_col)

                elif field == 'handlers':
                    if orelse := ast.orelse:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *orelse[0].f.bloc[:2], 'else')
                        is_last_child = False

                    elif finalbody := ast.finalbody:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')
                        is_last_child = False

                    else:
                        end_ln, end_col = next_bound_step(self)
                        is_last_child = True

                    if not (body_ := ast.body):
                        ln, col = prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                        block_loc = fstloc(ln, col + 1, end_ln, end_col)

                    else:
                        block_loc = fstloc(*body_[-1].f.bloc[2:], end_ln, end_col)

                else:  # field == 'body'
                    if handlers := ast.handlers:
                        end_ln, end_col = handlers[0].f.bloc[:2]
                        is_last_child = False

                    elif orelse := ast.orelse:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *orelse[0].f.bloc[:2], 'else')
                        is_last_child = False

                    elif finalbody := ast.finalbody:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')
                        is_last_child = False

                    else:
                        end_ln, end_col = next_bound_step(self)
                        is_last_child = True

                    ln, col = prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                    block_loc = fstloc(ln, col + 1, end_ln, end_col)

    if not put_fst:
        _, put_loc, put_lines, _, _ = (
            _src_edit.get_slice_stmt(self, field, True, block_loc, ffirst, flast, fpre, fpost, **options))

        if put_loc:
            self._put_src(put_lines, *put_loc, True)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        put_len = 0

    else:
        put_loc = _src_edit.put_slice_stmt(self, put_fst, put_body, field, block_loc, opener_indent, block_indent,
                                           ffirst, flast, fpre, fpost,
                                           docstr_strict_exclude = put_body[0] if put_body and start else None,
                                           **options)

        put_fst._offset(0, 0, put_loc.ln, 0 if put_fst.bln or put_fst.bcol else lines[put_loc.ln].c2b(put_loc.col))
        self._put_src(put_fst_lines, *put_loc, False)
        self._unmake_fst_tree(body[start : stop])
        put_fst._unmake_fst_parents(True)

        body[start : stop] = put_body

        put_len = len(put_body)
        FST = fst.FST
        stack = [FST(body[i], self, astfield(field, i)) for i in range(start, start + put_len)]

        self._make_fst_tree(stack)

        if is_handlers and is_trystar is None and not isinstance(ast, _ExceptHandlers):  # we may have to change Try <-> TryStar if put ExceptHandlers and all handlers replaced
            is_except_star = body[0].f._is_except_star()

            if is_except_star != isinstance(ast, TryStar):  # need to swap?
                new_type = TryStar if is_except_star else Try
                new_ast = new_type(body=ast.body, handlers=body, orelse=ast.orelse, finalbody=ast.finalbody,
                                   lineno=ast.lineno, col_offset=ast.col_offset,
                                   end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)
                new_ast.f = self  # FST remains same
                self.a = new_ast  # point to new AST
                ast.f = None  # clean up old AST

                if pfield := self.pfield:  # if there is a parent then set new AST as the child replacing current child
                    pfield.set(self.parent.a, new_ast)

    for i in range(start + put_len, len(body)):
        body[i].f.pfield = astfield(field, i)

    if is_last_child:  # correct parent for modified / removed last child nodes
        if not put_fst or not put_body:  # could be a slice put with no statements
            _set_end_pos_after_del(self, block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)

        else:
            _, _, end_ln, end_col = put_body[-1].f.loc

            _set_end_pos_w_maybe_trailing_semicolon(self, end_ln, end_col)

    return put_fst_end_nl


# ----------------------------------------------------------------------------------------------------------------------
# HACK adapt new trivia params to old and fix for introduced trailing newline on put or cut

# Old trivia parameters for code above:
# - `precomms`: Preceding comments.  - DEPRECATED, STILL USED FOR STMTS, REPLACED WITH `trivia`!
#     - `False`: No preceding comments.
#     - `True`: Single contiguous comment block immediately preceding position.
#     - `'all'`: Comment blocks (possibly separated by empty lines) preceding position.
# - `postcomms`: Trailing comments.  - DEPRECATED, STILL USED FOR STMTS, REPLACED WITH `trivia`!
#     - `False`: No trailing comments.
#     - `True`: Only comment trailing on line of position, nothing past that on its own lines.
#     - `'block'`: Single contiguous comment block following position.
#     - `'all'`: Comment blocks (possibly separated by empty lines) following position.
# - `prespace`: Preceding empty lines (max of this and `pep8space` used).  - DEPRECATED, STILL USED FOR STMTS, REPLACED
#     WITH `trivia`!
#     - `False`: No empty lines.
#     - `True`: All empty lines.
#     - `int`: A maximum number of empty lines.
# - `postspace`: Same as `prespace` except for trailing empty lines.  - DEPRECATED, STILL USED FOR STMTS, REPLACED
#     WITH `trivia`!

_trivia2precomms  = {False: False, 'none': False, 'block': True, 'all': 'all', True: True}
_trivia2postcomms = {False: False, 'none': False, 'line': True, 'block': 'block', 'all': 'all', True: True}


def _maybe_del_trailing_newline(self: fst.FST, old_last_line: str, put_fst_end_nl: bool) -> None:
    """Cut or del or put operation may leave a trailing newline at end of source. If that happens and there was not a
    traling newline before then remove it. Also update end location of `_ExceptHandlesr` or `_match_cases` SPECIAL SLICE
    since those always need to end at end of source."""

    root = self.root
    roota = root.a
    is_special = isinstance(roota, (_ExceptHandlers, _match_cases))
    lines = root._lines

    if (not put_fst_end_nl
        and old_last_line
        and not (new_last_line := lines[-1])
        and new_last_line is not old_last_line
    ):  # if self last line changed and was previously not a trailing newline and code put did not end in trailing newline then make sure it is not so now
        child_root = root

        if (is_special or isinstance(roota, mod)) and not (child_root := root.last_child()):
            if len(lines) > 1:
                del lines[-1]  # we specifically delete just one trailing newline because there may be multiple and we want to preserve the rest

                root._touch()

        elif child_root.end_ln < len(lines) - 1:  # make sure position doesn't include last line (possibly body cut down to zero elements)
            del lines[-1]

            child_root._touchall(True, True, False)

    if is_special:  # if a special _ExceptHandler or _match_cases slice then end needs to be set to end of source
        roota.end_lineno = len(lines)
        roota.end_col_offset = lines[-1].lenbytes

        root._touch()


def get_slice_stmtish(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
    *,
    one: bool = False,
) -> fst.FST:
    old_last_line = self.root._lines[-1]
    ld_comms, ld_space, ld_neg, tr_comms, tr_space, tr_neg = get_trivia_params(options.get('trivia'), True)

    options = dict(options,
        precomms = _trivia2precomms[ld_comms],
        postcomms = _trivia2postcomms[tr_comms],
        prespace = ld_space,
        postspace = tr_space,
    )

    fst_ = _get_slice_stmtish_old(self, start, stop, field, cut, one, options, ld_neg, tr_neg)

    _maybe_del_trailing_newline(self, old_last_line, not cut)

    return fst_


def put_slice_stmtish(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    old_last_line = self.root._lines[-1]
    ld_comms, ld_space, ld_neg, tr_comms, tr_space, tr_neg = get_trivia_params(options.get('trivia'), True)

    options = dict(options,
        precomms=_trivia2precomms[ld_comms],
        postcomms=_trivia2postcomms[tr_comms],
        prespace=ld_space,
        postspace=tr_space,
    )

    put_fst_end_nl = _put_slice_stmtish_old(self, code, start, stop, field, one, options)

    _maybe_del_trailing_newline(self, old_last_line, put_fst_end_nl)
