import re
import sys
from typing import Any, Generator, Literal, NamedTuple

from fst import FST
from fst.asttypes import _slice
from fst.astutil import copy_ast, compare_asts
from fst.fst_options import _ALL_OPTIONS

from ast import AST

__all__ = ['ParseCases', 'GetCases', 'GetSliceCases', 'PutCases', 'PutSliceCases']


_PYVER = sys.version_info[1]

ParseMode = str | type[AST] | None

_ALL_TEST_OPTIONS = {*_ALL_OPTIONS, 'one', 'cut'}  # we also allow these keywords as options because it is convenient for testing



def _unfmt_code(code: str | tuple[str, str]) -> str | tuple[ParseMode, str]:
    if isinstance(code, str):
        if code.startswith('\n') and code.endswith('\n'):
            return code[1 : -1]

    else:  # tuple[str, str]
        if (src := code[1]).startswith('\n') and src.endswith('\n'):
            return (code[0], src[1 : -1])

    return code


def _fmt_code(code: str | tuple[ParseMode, str]) -> tuple[str, bool]:  # -> (src, is_multiline)
    if isinstance(code, tuple):
        src, is_multiline = _fmt_code(code[1])
        c0 = c0.__name__ if isinstance(c0 := code[0], type) else repr(c0)

        if is_multiline:
            return f'({c0}, {src})', is_multiline
        else:
            return f'({c0},\n{src})', True

    q = '"""' if "'''" in code else "'''"

    if code.find(' \n') != -1:
        return repr(code), False
    elif code.endswith(' '):
        return repr(code) if '\n' in code else f"r{q}{code}{q}", False
    elif '\n' in code:
        return f"r{q}\n{code}\n{q}", True
    elif code.endswith("'"):
        return repr(f'\n{code}\n'), False
    else:
        return f"r{q}{code}{q}", False


def _make_fst(code: str | tuple[str, str], attr: str = '', attr2: str | None = None) -> FST:
    mode, src = (None, code) if isinstance(code, str) else code
    root      = FST(src, mode)

    if attr2 is None:
        return eval(f'f{"." * bool(attr) + attr}', {'f': root})
    else:
        return eval(f'f{"." * bool(attr) + attr}, f{"." * bool(attr2) + attr2}', {'f': root})


def _san_exc(exc: Exception) -> Exception:
    exc.args = exc.args[:1]

    return exc


def _clean_options(options: dict[str, Any]) -> dict[str, Any]:
    """Filter out any options which are not actual `FST` options."""

    return {o: v for o, v in options.items() if o in _ALL_TEST_OPTIONS}


class BaseCase(NamedTuple):
    lineno:  int
    key:     str
    idx:     int
    attr:    str  # the previous are runtime generated, this one and the following are stored
    start:   int | Literal['end'] | None
    stop:    int | Literal[False] | None
    field:   str | None
    options: dict[str, Any]
    code:    str | tuple[str, str]
    rest:    list[str | tuple[str, str]]

    def id(self) -> str:
        return f'lineno = {self.lineno}, key = {self.key!r}, idx = {self.idx}'


class BaseCases(dict):
    def __init__(self, fnm, func=None) -> None:
        self.fnm  = fnm
        self.func = func

        with open(fnm) as f:
            src = f.read()

        globs = {}

        exec(src, globs)

        del globs['__builtins__']

        self.var  = list(globs.keys())[-1]
        self.head = src[:re.search(rf'^{self.var}\s*=', src, re.MULTILINE).start()]
        cases     = globs[self.var]

        assert isinstance(cases, dict) and self.var == self.var.upper(), 'last element of cases data file must be the dictionary of cases'

        case_src_idx = 0
        lineno = 1

        def next_case_lineno() -> int:
            nonlocal case_src_idx, lineno

            prev_case_src_idx = case_src_idx
            case_src_idx = src.index("\n\n('", prev_case_src_idx) + 2  # WARNING! this special string may need to be checked better as test case source may eventually contain something that looks like it1
            lineno += src.count('\n', prev_case_src_idx, case_src_idx)

            return lineno

        for key, file_cases in cases.items():
            self[key] = self_cases = []

            for idx, (attr, start, stop, field, options, code, *rest) in enumerate(file_cases):
                code = _unfmt_code(code)

                for i, r in enumerate(rest):
                    rest[i] = _unfmt_code(r)

                self_cases.append(BaseCase(next_case_lineno(), key, idx, attr, start, stop, field, options, code, rest))

    def write(self):
        out = [self.head]

        out.append(f'{self.var} = {{\n')

        for key, cases in self.items():
            out.append(f'{key!r}: [  # ................................................................................\n')

            for _, _, _, attr, start, stop, field, options, code, rest in cases:
                out.append(f'\n({attr!r}, {start!r}, {stop!r}, {field!r}, {options}')

                for s in [code] + rest:
                    src, is_multiline = _fmt_code(s)
                    c                 = ' ' if is_multiline else '\n'

                    out.append(f',{c}{src}')

                out.append('),\n')

            out.append('],\n\n')

        out.append('}\n')

        with open(self.fnm, 'w') as f:
            f.write(''.join(out))

    def iterate(self, gen=False) -> Generator[BaseCase |
                                              tuple[BaseCase, list[str | tuple[str, str]]],
                                              None, None]:
        case = None

        try:
            for cases in self.values():
                for case in cases:
                    if not (v := case.options.get('_ver')) or v <= _PYVER:
                        yield (case, self.exec(case)) if gen else case

        except Exception:
            print(f'{case.id()}, fnm = {self.fnm}')

            raise

    def generate(self):
        for case, rest in self.iterate(True):
            self[case.key][case.idx] = BaseCase(*case[:-1], rest)

    def exec(self, case) -> list[str | tuple[str, str]]:  # rest
        raise NotImplementedError('this must be implemented in a subclass')


class ParseCases(BaseCases):
    def __init__(self, fnm) -> None:
        super().__init__(fnm, None)

    def exec(self, case) -> list[str | tuple[str, str]]:  # rest
        try:
            f = _make_fst(case.code, '')
        except Exception as exc:
            rest = [f'**{_san_exc(exc)!r}**']
        else:
            rest = [f.root.dump(out=str, loc=case.field != 'JoinedStr')]

        if (r0 := rest[0]).startswith('**'):
            s = f'**{case.field}'
        else:
            s = case.field

        assert s == r0[:len(s)], f"expected node type or error doesn't match, {case.field}"

        return rest


class GetCases(BaseCases):
    def __init__(self, fnm, func=FST.get) -> None:
        super().__init__(fnm, func)

    def exec(self, case) -> list[str | tuple[str, str]]:  # rest
        func = self.func
        rest = None
        h    = None
        g    = exec  # sentinel
        f    = _make_fst(case.code, case.attr)
        opts = _clean_options(case.options)

        try:
            g = func(f, case.start, case.stop, case.field, cut=False, **opts)
        except Exception as exc:
            rest = [f'**{_san_exc(exc)!r}**']

        else:
            try:
                h = func(f, case.start, case.stop, case.field, cut=True, **opts)
            except Exception as exc:
                rest = [f'**{_san_exc(exc)!r}**']

        if rest is None:
            rest = [f.root.src, f.root.dump(out=str)]

        if g is exec:  # exec is sentinel
            pass  # noop
        elif g is None:
            rest.append('**None**')

        else:
            g_is_FST = isinstance(g, FST)

            if (options := case.options).get('_verify', True):
                if options.get('_verify_self', True):
                    f.root.verify()  # _verify_self

                if options.get('_verify_get', True) and g_is_FST:
                    g.verify()  # _verify_get

            if not g_is_FST:
                rest.extend([repr(g), f'{type(g)}'])

            else:
                g_dump = g.dump(out=str)

                if h is not None:
                    if h.src != g.src:
                        raise RuntimeError(f'cut and copied FST src are not identical\n{h.src}\n...\n{g.src}')

                    if (h_dump := h.dump(out=str)) != g_dump:
                        raise RuntimeError(f'cut and copied FST dump are not identical\n{h_dump}\n...\n{g_dump}')

                rest.extend([g.src, g_dump])

        return rest


class GetSliceCases(GetCases):
    def __init__(self, fnm) -> None:
        super().__init__(fnm, FST.get_slice)


class PutCases(BaseCases):  # TODO: maybe automatically test 'raw' here?
    def __init__(self, fnm, func=FST.put) -> None:  # func = fst.put or fst.put_slice
        super().__init__(fnm, func)

    def exec(self, case) -> list[str | tuple[str, str]]:  # rest
        _, _, _, attr, start, stop, field, options, code, case_rest = case

        func     = self.func
        is_raw   = options.get('raw', False)
        cmp_asts = options.get('_cmp_asts', True)
        rest0    = case_rest[0]
        rest     = [rest0]
        tail     = None
        src      = None if rest0 is None or rest0 == '**DEL**' else rest0 if isinstance(rest0, str) else None if ((rest01 := rest0[1]) == '**DEL**') else rest01
        opts     = _clean_options(case.options)

        if (to_attr := opts.get('to')) is None:
            f = _make_fst(code, attr)
        else:
            f, to = _make_fst(code, attr, to_attr)
            opts = {**opts, 'to': to}

        if not src or options.get('_src', True):  # HACK to allow not putting as source text and only FST and AST, useful for testing things that only apply to AST/FST puts like coerce
            src_code = src
        else:
            src_code = _make_fst(rest0)

        try:
            g = func(f, src_code, start, stop, field, **opts)
        except Exception as exc:
            rest.append(f'**{_san_exc(exc)!r}**')

        else:
            if is_raw:
                f = g
            elif g is not f:
                raise RuntimeError('FST returned from func src put not identical to passed in')

            if options.get('_verify', True) and options.get('_verify_self', True):
                f.root.verify()

            rest.append(f.root.src)

            f_dump = f.root.dump(out=str)
            tail   = [f_dump]

            if src is not None and not is_raw:
                try:
                    h = _make_fst(rest0)
                except Exception as exc:
                    rest.append(f'**{_san_exc(exc)!r}**')

                else:
                    # is_special_slice = isinstance(h.a, _slice)

                    a = copy_ast(h.a)
                    k = _make_fst(code, attr)

                    try:
                        g = func(k, h, start, stop, field, **opts)
                    except Exception as exc:
                        rest.append(f'**{_san_exc(exc)!r}**')

                    else:
                        if is_raw:
                            k = g
                        elif g is not k:
                            raise RuntimeError('FST returned from func FST put not identical to passed in')

                        if k.root.src != f.root.src:
                            exc = RuntimeError(f'FST put and src put src are not identical\n{k.root.src}\n...\n{f.root.src}')

                            if is_raw:
                                rest.append(f'**{_san_exc(exc)!r}**')
                            else:
                                raise exc

                        if (k_dump := k.root.dump(out=str)) != f_dump:
                            exc = RuntimeError(f'FST put and src put dump are not identical\n{k_dump}\n...\n{f_dump}')

                            if is_raw:
                                rest.append(f'**{_san_exc(exc)!r}**')
                            else:
                                raise exc

                        if options.get('_ast', True):  # and not is_special_slice:
                            l = _make_fst(code, attr)

                            try:
                                g = func(l, a, start, stop, field, **opts)
                            except Exception as exc:
                                rest.append(f'**{_san_exc(exc)!r}**')

                            else:
                                if is_raw:
                                    l = g
                                elif g is not l:
                                    raise RuntimeError('FST returned from func AST put not identical to passed in')

                                if cmp_asts and not compare_asts(l.root.a, f.root.a):
                                    exc = RuntimeError(f'AST put and src put AST are not identical\n{l.root.dump(out=str)}\n...\n{f.root.dump(out=str)}')  # XXX this repr(AST) for earlier py "<ast.Module object at 0x7f70c295bd30>"

                                    if is_raw:
                                        rest.append(f'**{_san_exc(exc)!r}**')
                                    else:
                                        raise exc

                                if l.root.src != f.root.src:
                                    rest.append(l.root.src)

        return rest + tail if tail else rest


class PutSliceCases(PutCases):
    def __init__(self, fnm) -> None:
        super().__init__(fnm, FST.put_slice)


# if __name__ == '__main__':
#     # gpc = GetCases(os.path.join(os.path.dirname(__file__), 'data/data_get.py'))
#     # gpc = GetSliceCases(os.path.join(os.path.dirname(__file__), 'data/data_get_slice.py'))
#     gpc = PutCases(os.path.join(os.path.dirname(__file__), 'data/data_test.py'))

#     gpc.generate()
#     gpc.write()
