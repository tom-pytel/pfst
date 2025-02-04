from .fst import parse


def main():
    import argparse

    parser = argparse.ArgumentParser(prog='python -m fst')

    parser.add_argument('infile', type=argparse.FileType(mode='rb'), nargs='?',
                        default='-',
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
                        help="don't verify parse AST")

    args = parser.parse_args()

    with args.infile as infile:
        source = infile.read()

    ast = parse(source, args.infile.name, args.mode, type_comments=args.no_type_comments)

    if args.no_verify:
        ast.f.verify()

    ast.f.dump(indent=args.indent)


if __name__ == '__main__':
    main()
