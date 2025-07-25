#!/usr/bin/env python3

import importlib
from pathlib import Path

from pdoc import doc
from pdoc import extract
from pdoc import render

PRIVATE = ['fst_parse', 'fst_raw', 'fst_slice_old', 'fst_slice', 'fst_one', 'fst_misc', 'reconcile', 'srcedit_old']


def pdoc(*modules: Path | str, output_directory: Path | None = None) -> str | None:
    all_modules: dict[str, doc.Module] = {}

    for module_name in extract.walk_specs(modules):
        all_modules[module_name] = doc.Module.from_name(module_name)

    for module in all_modules.values():
        out = render.html_module(module, all_modules)
        if not output_directory:
            return out
        else:
            outfile = output_directory / f"{module.fullname.replace('.', '/')}.html"
            outfile.parent.mkdir(parents=True, exist_ok=True)
            outfile.write_bytes(out.encode())

    assert output_directory

    index = render.html_index(all_modules)

    if index:
        (output_directory / "index.html").write_bytes(index.encode())

    search = render.search_index(all_modules)

    if search:
        (output_directory / "search.js").write_bytes(search.encode())

    return None


if __name__ == "__main__":
    import argparse
    # from collections import abc
    from types import FunctionType
    # from typing import ForwardRef, Union, Generator, get_args, get_origin
    import fst
    from fst import FST

    parser = argparse.ArgumentParser(prog='python make_docs.py')

    parser.add_argument('--private', default=False, action='store_true', help='expose private stuff')
    # parser.add_argument('modules', type=str, default=[], metavar='module', nargs='*', help='modules to process')

    args = parser.parse_args()
    # modules = args.modules

    with open('VERSION') as f:
        version = f.read().strip()

    fst.__doc__ = fst.__doc__.replace('{{VERSION}}', version)

    if not args.private:
        all_funcs = set(v for k, v in FST.__dict__.items() if isinstance(v, FunctionType))

    else:
        all_funcs = set()

        for mod in (f'fst.{mod}' for mod in PRIVATE):  # add contents of __all_private__ to __all__
            mod = importlib.import_module(mod)

            if all_private := getattr(mod, '__all_private__', None):
                mod.__all__ = getattr(mod, '__all__', []) + all_private

            all_funcs.update(f for f in mod.__dict__.values() if isinstance(f, FunctionType))

        for n, f in FST.__dict__.items():  # make all FST methods public
            if n.startswith('_') and isinstance(f, FunctionType):
                if f in all_funcs:
                    f.__doc__ = (f.__doc__ or '') + '@public'
                else:
                    all_funcs.add(f)

    # frFST  = ForwardRef('FST')
    # allFST = {'FST', frFST}
    # allT   = {Union, Generator, abc.Generator}

    # def fixTyping(t):
    #     if t in allFST:
    #         return FST

    #     if (o := get_origin(t)) not in allT:
    #         return t

    #     args    = list(get_args(t))
    #     changed = False

    #     for i, a in enumerate(args):
    #         if (b := fixTyping(a)) is not a:
    #             args[i] = b
    #             changed = True

    #     return o[tuple(args)] if changed else t

    # for f in all_funcs:  # change all 'FST' __annotations__ to point to actual FST class
    #     if anns := getattr(f, '__annotations__'):
    #         for a, v in anns.items():
    #             if v in allFST:
    #                 anns[a] = FST
    #             elif (w := fixTyping(v)) is not v:
    #                 anns[a] = w

    render.configure(
        docformat='markdown',
        include_undocumented=True,
        edit_url_map={},
        favicon=None,
        footer_text=None,
        logo=None,
        logo_link=None,
        math=False,
        mermaid=False,
        search=False,  # True,
        show_source=False,
        template_directory=None,
    )

    fst.__all__ = ['docs', 'fst', 'view', 'misc', 'astutil']

    if args.private:
        fst.__all__.extend(PRIVATE)

    pdoc('fst', output_directory=Path('docs'))
