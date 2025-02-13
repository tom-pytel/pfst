from .fst import parse


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(prog='python -m fst')

    parser.add_argument('infile', nargs='?', default='-',
                        help='the file to parse; defaults to stdin')
    parser.add_argument('-m', '--mode', default='exec',
                        choices=('exec', 'single', 'eval', 'func_type'),
                        help='specify what kind of code must be parsed')
    parser.add_argument('--no-type-comments', default=True, action='store_false',
                        help="don't add information about type comments")
    parser.add_argument('-a', '--include-attributes', action='store_true',
                        help='attributes always included, here for compatibility')
    parser.add_argument('-i', '--indent', type=int, default=2,
                        help='indentation of nodes (number of spaces)')
    parser.add_argument('--no-verify', default=True, action='store_false',
                        help="don't verify parsed AST")
    parser.add_argument('-f', '--full', default=False, action='store_true',
                        help="show full tree including empty nodes")

    args = parser.parse_args()

    if args.infile == '-':
        name = '<stdin>'
        source = sys.stdin.buffer.read()
    else:
        name = args.infile
        with open(args.infile, 'rb') as infile:
            source = infile.read()

    ast = parse(source, name, args.mode, type_comments=args.no_type_comments)

    if args.no_verify:
        ast.f.verify()

    ast.f.dump(full=args.full, indent=args.indent)


if __name__ == '__main__':
    main()
