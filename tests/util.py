import os
import sys
from typing import Any, Literal, NamedTuple

from fst import FST


_PYVER = sys.version_info[1]


def _unfmt_code(code: str | tuple[str, str]) -> str | tuple[str, str]:
    if isinstance(code, str):
        if code.startswith('\n') and code.endswith('\n'):
            return code[1 : -1]

    else:  # tuple[str, str]
        if (src := code[1]).startswith('\n') and src.endswith('\n'):
            return (code[0], src[1 : -1])

    return code


def _fmt_code(code: str | tuple[str, str]) -> tuple[str, bool]:  # -> (src, is_multiline)
    if isinstance(code, tuple):
        src, is_multiline = _fmt_code(code[1])

        if is_multiline:
            return f'({code[0]!r}, {src})', is_multiline
        else:
            return f'({code[0]!r},\n{src})', True

    if code.find(' \n') != -1:
        return repr(code), False
    elif '\n' in code:
        return f"r'''\n{code}\n'''", True
    elif code.endswith("'"):
        return repr(f'\n{code}\n'), False
    else:
        return f"r'''{code}'''", False


def _make_fst(code: str | tuple[str, str], attr: str = '') -> FST:
    mode, src = (None, code) if isinstance(code, str) else code
    root      = FST(src, mode)

    return eval(f'f.{attr}', {'f': root}) if attr else root


class GetPutCase(NamedTuple):
    idx:     int
    attr:    str
    start:   int | Literal['end'] | None
    stop:    int | Literal[False] | None
    field:   str | None
    options: dict[str, Any]
    code:    str | tuple[str, str]
    rest:    list[str | tuple[str, str]]


class GetPutCases(dict):
    def __init__(self, fnm, func):
        self.fnm  = fnm
        self.func = func

        with open(fnm) as f:
            src = f.read()

        globs = {}

        exec(src, globs)

        del globs['__builtins__']

        if len(globs) != 1:
            raise RuntimeError(f'expecting only single data structure in {fnm!r}')

        self.var = next(iter(globs.keys()))

        for key, file_cases in next(iter(globs.values())).items():
            self[key] = self_cases = []

            for j, (_, attr, start, stop, field, options, code, *rest) in enumerate(file_cases):
                code = _unfmt_code(code)

                for i, r in enumerate(rest):
                    rest[i] = _unfmt_code(r)

                self_cases.append(GetPutCase(j, attr, start, stop, field, options, code, rest))

    def write(self):
        out = []

        out.append(f'{self.var} = {{\n')

        for key, cases in self.items():
            out.append(f'{key!r}: [  # ................................................................................\n')

            for idx, attr, start, stop, field, options, code, rest in cases:
                out.append(f'\n({idx}, {attr!r}, {start}, {stop}, {field!r}, {options}')

                for s in [code] + rest:
                    src, is_multiline = _fmt_code(s)
                    c                 = ' ' if is_multiline else '\n'

                    out.append(f',{c}{src}')

                out.append('),\n')

            out.append('],\n\n')

        out.append('}\n')

        with open(self.fnm, 'w') as f:
            f.write(''.join(out))

    def iterate(self, gen=False):
        key = case = None

        try:
            for key, cases in self.items():
                for case in cases:
                    if not (v := case.options.get('_ver')) or v <= _PYVER:
                        yield (key, case, self.exec(case)) if gen else (key, case)

        except Exception:
            print(f'key = {key}, idx = {case and case.idx}, fnm = {self.fnm}')

            raise

    def generate(self):
        for key, case, rest in self.iterate(True):
            self[key][case.idx] = GetPutCase(*case[:-1], rest)

    def exec(self, case) -> list[str | tuple[str, str]]:  # rest
        raise NotImplementedError('this must be implemented in a subclass')


class GetCases(GetPutCases):
    def __init__(self, fnm, func=FST.get):
        super().__init__(fnm, func)

    def exec(self, case) -> list[str | tuple[str, str]]:  # rest
        func = self.func
        rest = None
        h    = None
        g    = None
        f    = _make_fst(case.code, case.attr)
        root = f.root

        try:
            g = func(f, case.start, case.stop, case.field, cut=False, **case.options)
        except Exception as exc:
            rest = [f'**{exc!r}**']

        else:
            try:
                h = func(f, case.start, case.stop, case.field, cut=True, **case.options)
            except Exception as exc:
                rest = [f'**{exc!r}**']

        if rest is None:
            rest = [root.src, root.dump(out=str)]

        if g is not None:
            if (options := case.options).get('_verify', True):
                if options.get('_verify_self', True):
                    root.verify()

                if options.get('_verify_get', True):
                    g.verify()

            g_dump = g.dump(out=str)

            if h is not None:
                if h.src != g.src:
                    raise RuntimeError(f'cut and copied FST src are not identical\n{h.src}\n...\n{g.src}')

                if (h_dump := h.dump(out=str)) != g_dump:
                    raise RuntimeError(f'cut and copied FST dump are not identical\n{h_dump}\n...\n{g_dump}')

            rest.extend([g.src, g_dump])

        return rest


class GetSliceCases(GetCases):
    def __init__(self, fnm):
        super().__init__(fnm, FST.get_slice)


class PutCases(GetPutCases):
    def __init__(self, fnm, func=FST.put):  # func = fst.put or fst.put_slice
        super().__init__(fnm, func)

    def exec(self, case) -> list[str | tuple[str, str]]:  # rest
        raise NotImplementedError


class PutSliceCases(GetCases):
    def __init__(self, fnm):
        super().__init__(fnm, FST.put_slice)


# if __name__ == '__main__':
#     # gpc = GetCases('data/data_get.py', FST.get)
#     gpc = GetSliceCases(os.path.join(os.path.dirname(__file__), 'data/data_get_slice.py'))

#     gpc.generate()
#     gpc.write()
