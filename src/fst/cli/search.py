"""STANDALONE CLI MODULE! fst.search command-line structural pattern search utility."""

import argparse
import os
import re
import sys
import traceback
from typing import Callable, Generator

import fst
from .. import FST, M_Pattern
from .. import match
from ..fst_misc import is_terminal_color_enabled


PROGRAM = 'python -m fst.cli.search'

PATTERN_COMPILE_DICT = {
    're': re,
    **{n: v for n, v in fst.__dict__.items() if n in fst.__all__},
    **{n: v for n, v in match.__dict__.items() if n in match.__all__},
}

_SENTINEL = object()


def parse_args(prog: str | None, middle_args: Callable[[argparse.ArgumentParser], None]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=prog)

    parser.add_argument('PATH', nargs='+',
                        help='file(s) to search')
    parser.add_argument('-p', '--pattern', default=None,
                        help='pattern to search for, if not specified will prompt')
    parser.add_argument('-P', '--pattern-file', default=None,
                        help='pattern to search for, if not specified will prompt')

    middle_args(parser)

    parser.add_argument('--ctx', default=False, action=argparse.BooleanOptionalAction,
                        help='match `expr_context` INSTANCES  (default: False)')
    parser.add_argument('--back', default=False, action=argparse.BooleanOptionalAction,
                        help='walk nodes in reverse order  (default: False)')
    parser.add_argument('--color', default=None, action=argparse.BooleanOptionalAction,
                        help='explicitly enable or disable color  (default: auto)')

    args = parser.parse_args()

    if args.color is None:
        args.color = is_terminal_color_enabled()

    if not args.color:
        args.clr_prompt = args.clr_fnm = args.clr_src = args.clr_error = args.clr_reset = ''
    else:
        args.clr_prompt = '\033[1;34m'
        args.clr_fnm = '\033[95m'
        args.clr_src = '\033[90m'
        args.clr_error = '\033[1;31m'
        args.clr_reset = '\033[0m'

    return args


def resolve_pattern(args: argparse.Namespace) -> object:
    if (src := args.pattern) is None and args.pattern_file is None:
        if not os.isatty(sys.stdin.fileno()):
            src = sys.stdin.read()
            pattern = compile_pattern(src, True)

        else:
            print(f'{args.clr_prompt}Enter pattern, Ctrl+D when done, Ctrl+C to exit:{args.clr_reset}')

            while (pattern := compile_pattern(sys.stdin.read(), False)) is _SENTINEL:
                print(f'\n{args.clr_prompt}Try again or Ctrl+C to exit:{args.clr_reset}')

    else:
        if src is None:
            src = read_file(args.pattern_file)
        elif args.pattern_file is not None:
            raise RuntimeError('cannot specify both --pattern and --pattern-file')

        pattern = compile_pattern(src, True)

    if src is not None:
        if src.endswith('\n'):
            src = src[:-1]

        print(f'{args.clr_prompt}Pattern:{args.clr_reset}\n{src}')

    return pattern


def read_file(fnm: str) -> str:
    with open(fnm) as f:
        return f.read()


def compile_pattern(pat: str, allow_raise: bool) -> M_Pattern | object:  # | _SENTINEL
    try:
        return eval(compile(pat, '<pattern>', 'eval'), PATTERN_COMPILE_DICT.copy())

    except Exception:
        if allow_raise:
            raise

        traceback.print_exc()

    return _SENTINEL


def iter_files(args: argparse.Namespace) -> Generator[tuple[str, fst.FST], None, None]:
    for fnm in args.PATH:
        try:
            fp = open(fnm)

            try:
                mod = FST(fp.read(), 'exec')
            finally:
                fp.close()

        except Exception as exc:
            print(f'{args.clr_error}{fnm} - {exc.__class__.__qualname__}: {str(exc)}{args.clr_reset}')

            continue

        yield fnm, mod


def print_lines(args: argparse.Namespace, f: fst.FST) -> None:
    lines = f.lines

    if loc := f.loc:
        _, col, _, end_col = loc

        if args.color:
            lines[-1] = f'{(l := lines[-1])[:end_col]}{args.clr_src}{l[end_col:]}{args.clr_reset}'
            lines[0] = f'{args.clr_src}{(l := lines[0])[:col]}{args.clr_reset}{l[col:]}'

        elif len(lines) == 1:
            if (l := end_col - col) < 2:
                lines.append(f'{" " * col}^')
            else:
                lines.append(f'{" " * col}^{"~" * (l - 2)}^')

        else:
            max_len = max(len(l) for l in lines)

            lines.insert(0, f'{" " * col}v{"~" * (max_len - col - 1)}')  # other arrows '\u25BC, \u25B2, \u25BD, \u25B3, \u2228, \u2227'
            lines.append(f'{"~" * (end_col - 1)}^')

    print('\n'.join(lines))


def print_match(args: argparse.Namespace, f: fst.FST, fnm: str, noloc_parent: bool = False) -> bool:
    if not (loc := f.loc):
        if not noloc_parent:
            return False

        if not (f := f.parent) or not (loc := f.loc):
            return False

    fnmstr = f'{fnm}:' if loc is None else f'{fnm} line {loc.ln + 1}:'

    print(f'{args.clr_fnm}{fnmstr}{args.clr_reset}')

    print_lines(args, f)

    return True


def main() -> None:
    def middle_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--no-nested', default=False, action='store_true',
                            help="don't recurse into nested matches")

    args = parse_args(PROGRAM, middle_args)

    pattern = resolve_pattern(args)

    for fnm, mod in iter_files(args):
        for m in mod.search(pattern, nested=not args.no_nested, ctx=args.ctx, back=args.back):
            print_match(args, m.matched, fnm, noloc_parent=True)


if __name__ == '__main__':
    main()
