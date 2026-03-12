"""STANDALONE CLI MODULE! fst.search command-line structural pattern substitution utility."""

import argparse
import os
import re
import sys

import fst
from .. import match
from ..parsex import _PARSE_MODE_FUNCS
from .search import read_file, parse_args, resolve_pattern, iter_files, print_lines, print_match


PROGRAM = 'python -m fst.cli.sub'

PATTERN_COMPILE_DICT = {
    're': re,
    **{n: v for n, v in fst.__dict__.items() if n in fst.__all__},
    **{n: v for n, v in match.__dict__.items() if n in match.__all__},
}


def resolve_repl(args: argparse.Namespace) -> str:
    if (repl := args.repl) is None and args.repl_file is None:
        if os.isatty(sys.stdin.fileno()):
            print(f'{args.clr_prompt}Enter replacement template, Ctrl+D when done, Ctrl+C to exit:{args.clr_reset}')

        return sys.stdin.read()

    if repl is None:
        repl = read_file(args.repl_file)
    elif args.repl_file is not None:
        raise RuntimeError('cannot specify both --repl and --repl-file')

    src = repl[:-1] if repl.endswith('\n') else repl

    print(f'{args.clr_prompt}Replacement template:{args.clr_reset}\n{src}')

    return fst.FST(repl, args.mode)


def print_sub(args: argparse.Namespace, f: fst.FST) -> None:
    print(f'{args.clr_sub}...{args.clr_reset}')

    print_lines(args, f)


def main() -> None:
    def middle_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-r', '--repl', default=None,
                            help='replacement template, if not specified will prompt')
        parser.add_argument('-R', '--repl-file', default=None,
                            help='replacement template, if not specified will prompt')
        parser.add_argument('-m', '--mode', default='all',
                            choices=[m for m in _PARSE_MODE_FUNCS if isinstance(m, str)],
                            help='replacement template parse mode  (default: all)')
        parser.add_argument('-d', '--dry', action='store_true',
                            help="dry run, don't write substitutions to files")
        parser.add_argument('--nested', action='store_true',
                            help='recurse into nested matches')
        parser.add_argument('-c', '--count', type=int, default=0,
                            help='number of substitutions will be made  (default: unbounded)')
        parser.add_argument('-l', '--loop', nargs='?', type=int, default=False, const=True,
                            help='loop each sub until no longer match  (default: False)')

    args = parse_args(PROGRAM, middle_args, epilog='''
WARNING! Improper usage of `--nested` or `--loop` can lead to infinite looping so the onus is on the user to make sure
the combination of pattern and replacement template cannot cause this.
    '''.strip())

    if args.pattern is None and args.pattern_file is None and args.repl is None and args.repl_file is None:
        if not os.isatty(sys.stdin.fileno()):
            raise RuntimeError('must pass either pattern or repl if stdin is not a tty')

    if args.repl is not None and args.repl_file is not None:
        raise RuntimeError('cannot specify both --repl and --repl-file')

    if not args.color:
        args.clr_sub = ''
    else:
        args.clr_sub = '\033[35m'

    pattern = resolve_pattern(args)
    repl = resolve_repl(args)

    for fnm, mod in iter_files(args):
        mod.sub(
            pattern,
            repl,
            nested=args.nested,
            callback=lambda f: not print_match(args, f, fnm),  # noqa: B023
            callback_after=lambda f: print_sub(args, f),
            ctx=args.ctx,
            back=args.back,
        )

        if not args.dry:
            with open(fnm, 'w') as fp:
                fp.write(mod.src)


if __name__ == '__main__':
    main()
