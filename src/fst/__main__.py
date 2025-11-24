from .fst import parse
from .parsex import _PARSE_MODE_FUNCS


def main() -> None:
    import sys
    import argparse

    parser = argparse.ArgumentParser(prog='python -m fst')

    parser.add_argument('infile', nargs='?', default='-',
                        help='the file to parse; defaults to stdin')
    parser.add_argument('-m', '--mode', default='all',
                        choices=[m for m in _PARSE_MODE_FUNCS if isinstance(m, str)],
                        help='specify what kind of code must be parsed')
    parser.add_argument('-f', '--full', default=False, action='store_true',
                        help="show full tree including empty nodes")
    parser.add_argument('-e', '--expand', default=False, action='store_true',
                        help="expanded view")
    parser.add_argument('-s', '--stmt', default=False, action='store_true',
                        help="show statmenent source lines")
    parser.add_argument('-n', '--node', default=False, action='store_true',
                        help="show all node source lines")
    parser.add_argument('-+', dest='src_plus', default=False, action='store_true',
                        help="show all non-coding source lines")
    parser.add_argument('--type-comments', default=False, action='store_true',
                        help="add information about type comments")
    parser.add_argument('-i', '--indent', type=int, default=2,
                        help='indentation of nodes (number of spaces)')
    parser.add_argument('-l', '--list-indent', default=1, action='store_true',
                        help="indent list elements")
    parser.add_argument('--no-verify', default=False, action='store_true',
                        help="don't verify parsed AST")

    args = parser.parse_args()

    if args.infile == '-':
        name = '<stdin>'
        source = sys.stdin.buffer.read()

    else:
        name = args.infile

        with open(args.infile, 'rb') as infile:
            source = infile.read()

    ast = parse(source.decode(), name, args.mode, type_comments=args.type_comments)

    if not args.no_verify:# and args.mode in ('exec', 'eval', 'single', 'stmt', 'expr'):
        ast.f.verify(raise_=True)

    if src := ('node' if args.node else 'stmt' if args.stmt else None):
        if args.src_plus:
            src += '+'

    ast.f.dump(src=src, full=args.full, expand=args.expand, indent=args.indent, list_indent=args.list_indent)


if __name__ == '__main__':
    main()
