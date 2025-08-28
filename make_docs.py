#!/usr/bin/env python3

from pathlib import Path

from pdoc import doc
from pdoc import extract
from pdoc import render


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
    from types import FunctionType
    import fst
    from fst import FST

    parser = argparse.ArgumentParser(prog='python make_docs.py')

    # parser.add_argument('--private', default=False, action='store_true', help='expose private stuff')

    args = parser.parse_args()

    with open('VERSION') as f:
        version = f.read().strip()

    fst.__doc__ = fst.__doc__.replace('{{VERSION}}', version)
    all_funcs   = set(v for k, v in FST.__dict__.items() if isinstance(v, FunctionType))

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

    fst.__all__ = ['docs', 'fst', 'view', 'misc', 'extparse', 'astutil']

    pdoc('fst', output_directory=Path('docs'))
