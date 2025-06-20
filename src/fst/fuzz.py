"""Fuzzers, mostly mean for debugging `fst` itself."""

import argparse
import os
import sys
import sysconfig
from ast import *
from collections import defaultdict
from itertools import repeat
from math import log10
from random import choice, randint, random, seed, shuffle
from types import NoneType
from typing import Any, Generator, Iterable, Literal

from .astutil import *
from .astutil import TypeAlias, TemplateStr, Interpolation
from .fst import FST, NodeError

PROGRAM     = 'python -m fst.fuzz'
_PY_VERSION = sys.version_info[:2]
_PYLT12     = _PY_VERSION < (3, 12)
_PYLT14     = _PY_VERSION < (3, 14)


def find_pys(path) -> list[str]:
    if os.path.isfile(path):
        return [path] if path.endswith('.py') else []

    if os.path.isdir(path):
        fnms = []

        for dir, _, fnms_ in os.walk(path):
            fnms.extend(os.path.join(dir, fnm) for fnm in fnms_ if fnm.endswith('.py'))

        return fnms

    raise ValueError(f'unknown thing: {path}')


def ignorable_exc(exc: Exception, putsrc: str | Literal[False] | None = None):
    if isinstance(exc, NotImplementedError):
        return True

    msg = str(exc)

    ignorable = isinstance(exc, (NodeError, ValueError)) and (
        msg.endswith('cannot be Starred') or
        'not implemented' in msg or
        'in this state' in msg or
        'pattern expression' in msg or
        'invalid value for MatchValue.value' in msg or
        'invalid value for MatchMapping.keys' in msg or
        'cannot reparse Starred in slice as Starred' in msg or
        'expecting identifier, got' in msg or
        'not allowed in this alias' in msg
        # (msg.startswith('cannot put ') and (msg.endswith(' to MatchMapping.keys') or msg.endswith(' to MatchValue.value')))
    )

    if not ignorable and isinstance(exc, SyntaxError):
        if (
            # msg.startswith('cannot assign to literal here') or
            # msg.startswith('cannot assign to expression here') or
            # "Maybe you meant '==' instead of '='" in msg or
            # "Maybe you meant '==' or ':=' instead of '='"
            "Maybe you meant '==' " in msg or
            ' for augmented assignment' in msg or
            msg.startswith('positional argument follows keyword argument') or
            msg.startswith('cannot use starred expression here') or
            msg.startswith('illegal target for annotation') or
            # msg.startswith('cannot delete literal') or
            # msg.startswith('cannot delete function call') or
            msg.startswith('cannot delete ') or
            # msg.startswith('cannot assign to literal') or
            # msg.startswith('cannot assign to function call') or
            # msg.startswith('cannot assign to expression') or
            # msg.startswith('cannot assign to None') or
            msg.startswith('cannot assign to ') or
            (msg.startswith('future feature') and 'is not defined' in msg)
        ):
            ignorable = True

        elif putsrc:  # Starred stuff like "*a or b" coming from original code
            try:
                FST._parse_callarg(putsrc)
            except SyntaxError:
                pass
            else:
                ignorable = True

    return ignorable


def astbase(cls: type[AST]) -> type[AST]:  # ast base class just above AST
    while (c := cls.__bases__[0]) is not AST:
        cls = c

    return cls


ASTCat = type[AST]  # mod, stmt, expr, Slice, slice, expr_context, boolop, operator, unaryop, cmpop, comprehension, excepthandler, ExceptHandler, arguments, arg, keyword, alias, withitem, match_case, pattern

def astcat(fst: FST) -> ASTCat:  # ast category (replacement compatibility)
    a = fst.a

    if isinstance(a, ExceptHandler):
        return ExceptHandler if isinstance(fst.parent.a, Try) else excepthandler  # Try vs. TryStar
    if isinstance(a, (Starred, Slice)):
        return a.__class__
    if fst.has_slice():
        return slice  # Tuple containing Slice

    return astbase(a.__class__)


ASTCAT_ALLOWED_REPLACEMENTS = {  # general, not specific cases
    Starred: (Starred, expr),
    Slice:   (Slice, expr),
    slice:   (slice, Slice, expr),
}

def astcat_allowed_replacements(cat: ASTCat) -> ASTCat | tuple[ASTCat]:
    return ASTCAT_ALLOWED_REPLACEMENTS.get(cat, cat)


class FSTParts:
    """Build and manipulate index into individual FST node interchangeable type groups."""

    cats: dict   # {FST: ASTCat, ...}
    parts: dict  # {ASTCat: [FST, ...], ...}

    def __init__(self, fst: FST, exclude: type[AST] | tuple[type[AST]] | None = None):
        if isinstance(fst, FSTParts):
            self.cats    = fst.cats.copy()
            self.parts   = {c: fs.copy() for c, fs in fst.parts.items()}
            self.exclude = fst.exclude if exclude is None else exclude

            return

        cats  = {}                 # {FST: ASTCat, ...}
        parts = defaultdict(list)  # {ASTCat: [FST, ...], ...}

        if exclude is None:
            exclude = (expr_context, mod, FormattedValue, Interpolation)

        for a in walk(fst.a):
            if isinstance(a, exclude):
                continue

            f   = a.f
            cat = cats[f] = astcat(f)

            parts[cat].append(f)

        self.cats    = cats
        self.parts   = dict(parts)
        self.exclude = exclude

    def copy(self) -> 'FSTParts':
        return FSTParts(self)

    def remove(self, fst: FST):
        if not isinstance(fst.a, self.exclude):
            if c := (cats := self.cats).get(fst):
                del cats[fst]

                self.parts[c].remove(fst)

    def add(self, fst: FST):  # or put back removed
        if not isinstance(fst.a, self.exclude):
            self.cats[fst] = cat = astcat(fst)

            self.parts[cat].append(fst)

    def remove_all(self, fst: FST):
        exclude = self.exclude
        parts   = self.parts
        cats    = self.cats

        for a in walk(fst.a):
            if not isinstance(a, exclude):
                if c := cats.get(f := a.f):
                    del cats[f]

                    parts[c].remove(f)

    def add_all(self, fst: FST):  # or put back removed
        exclude = self.exclude
        parts   = self.parts
        cats    = self.cats

        for a in walk(fst.a):
            if not isinstance(a, exclude):
                f       = a.f
                cats[f] = cat = astcat(f)

                parts[cat].append(f)

    def getrnd(self, cat: ASTCat | Iterable[ASTCat] | None = None) -> tuple[FST | None, ASTCat | None]:
        if cat is None:
            cat = [c for c, fs in self.parts.items() if fs]
        else:
            cat = [cat] if isinstance(cat, type) else list(cat)

        while cat:
            if p := self.parts.get(c := cat[i := randint(0, len(cat) - 1)]):
                return choice(p), c

            del cat[i]

        return None, None


def test_replace(fst: FST, with_: FST | None) -> bool:
    stmt_ = fst.parent_stmt()
    path  = stmt_.child_path(fst)
    stmt_ = stmt_.copy()

    try:
        stmt_.child_from_path(path).replace(with_.copy() if with_ else with_, raw=False).root.verify()
    except Exception:
        return False

    return True


def can_replace(tgt: FST, repl: FST) -> bool:  # assuming ASTCat has already been checked and only testing allowed category
    repla, repl_parenta = repl.a, repl.parent.a
    tgta , tgt_parenta  = tgt.a,  tgt.parent.a
    tgt_field, _        = tgt.pfield
    repl_field, _       = repl.pfield

    if _PYLT12:
        if any(isinstance(f.a, (JoinedStr, TemplateStr)) for f in tgt.parents()):
            return False

        if isinstance(repl_parenta, (JoinedStr, TemplateStr, FormattedValue, Interpolation)):
            return False

    else:
        if isinstance(tgt_parenta, (JoinedStr, TemplateStr)):
            return False

        if isinstance(tgt_parenta, (FormattedValue, Interpolation)) and tgt_field != 'value':
            return False

    if isinstance(tgta, expr) and any(isinstance(f.a, pattern) for f in tgt.parents()):
        if tgt_field == 'value':
            if not is_valid_MatchValue_value(repla):
                return False

        if tgt_field == 'cls':
            if not isinstance(repla, Name):
                return False

        elif isinstance(tgta, (Name, Attribute)):
            if not isinstance(repla, (Name, Attribute)):
                return False

        elif not is_valid_MatchValue_value(repla):
            return False

    if isinstance(tgta, pattern) and isinstance(repla, MatchStar) and not isinstance(tgt_parenta, MatchSequence):
        return False

    if repl_field == 'vararg' and isinstance(repla.annotation, Starred) and tgt_field != 'vararg':  # because could have Starred annotation headed for a non-vararg field
        return False

    if isinstance(tgta, Slice) and not isinstance(repla, Slice):
        return False

    if isinstance(tgta, alias):
        if isinstance(tgt_parenta, Import):
            if '*' in repla.name:
                return False

        if isinstance(tgt_parenta, ImportFrom):
            if '.' in repla.name:
                return False
            if '*' in repla.name and len(tgt_parenta.names) > 1:
                return False

    if (isinstance(tgta, arguments) and isinstance(tgt_parenta, Lambda) and
        not isinstance(repl_parenta, Lambda)
    ):
        return False

    if (isinstance(tgta, arg) and isinstance(tgt_parenta, arguments) and
        isinstance(tgt.parent.parent.a, Lambda) and repla.annotation
    ):
        return False

    if not isinstance(ctx := getattr(tgta, 'ctx', Load()), Load):
        if isinstance(ctx, Del) or not getattr(repla, 'ctx', None):
            return False

        allowed = None
        f       = tgt

        while f := f.parent:
            if isinstance(a := f.a, (Delete, Assign, For, AsyncFor, comprehension)):
                allowed = (Name, Attribute, Subscript)#, Tuple, List)

                break

            if isinstance(a, (AugAssign, AnnAssign)):
                allowed = (Name, Attribute, Subscript)

                break

            if isinstance(a, (TypeAlias, NamedExpr)):
                allowed = Name

                break

            if not isinstance(a, expr):  # EXPRISH?
                break

        if not allowed or not isinstance(repla, allowed):
            return False

    return True


class Fuzzy:
    syspyfnms = None
    name      = 'Fuzzy'
    forever   = False

    def __init__(self, args: dict[str, Any]):
        self.args    = args
        self.batch   = args.get('batch')
        self.debug   = args.get('debug')
        self.loop    = args.get('loop')
        self.seed    = args.get('seed')
        self.shuffle = args.get('shuffle')
        self.verbose = args.get('verbose')
        self.verify  = args.get('verify')

        if paths := args.get('PATH'):
            fnms = sum((find_pys(path) for path in paths), start=[])

        elif Fuzzy.syspyfnms is None:
            fnms = find_pys(sys.prefix)

            if stdlib := sysconfig.get_paths().get('stdlib'):
                fnms.extend(find_pys(stdlib))

        self.fnms = fnms

    def iter_pys(self) -> Generator[tuple[str, FST], None, None]:
        fnms  = self.fnms
        width = int(log10(len(fnms) - 1 or 1)) + 1

        if self.args['shuffle']:
            fnms = fnms[:]

            shuffle(fnms)

        for i, fnm in enumerate(fnms):
            head = f'{i:<{width}}: {fnm}'

            try:
                with open(fnm) as f:
                    fst = FST.fromsrc(f.read())

            except (NodeError, SyntaxError, UnicodeDecodeError) as exc:
                print(f'{head} - read/parse fail: **{exc.__class__.__name__}**')

            else:
                print(head)

                yield fnm, fst

    def fuzz(self) -> bool:
        for fnm, fst in self.iter_pys():
            seed((rnd_seed := randint(0, 2**32-1)) if (rnd_seed := self.seed) is None else rnd_seed)

            try:
                self.fuzz_one(fst, fnm)

            except Exception:
                print('-'*80)
                print('Random seed was:', rnd_seed)

                raise

        return self.forever

    def fuzz_one(self, fst: FST, fnm: str):
        pass


# ----------------------------------------------------------------------------------------------------------------------

class VerifyCopy(Fuzzy):
    name = 'verify_copy'

    def fuzz_one(self, fst, fnm) -> bool:
        for f in fst.walk('all'):
            if not f.is_parsable():  # because .verify() needs to parse
                continue

            g = None

            try:
                g = f.copy()

                g.verify()

            except Exception:
                print('src:', '-'*75)
                print(f.src)
                print('.'*80)
                f.dump('stmt')

                if g:
                    print('cpy:', '-'*75)
                    print(g.src)
                    print('.'*80)
                    g.dump('stmt')

                raise


class SynOrder(Fuzzy):
    name = 'syn_order'

    def fuzz_one(self, fst, fnm) -> bool:
        bln, bcol = 0, 0

        for f in (gen := fst.walk(True)):
            if _PYLT12 and isinstance(f.a, JoinedStr):  # these have no location info in py <3.12
                gen.send(False)

                continue

            try:
                if not isinstance(f.a, (FormattedValue, Interpolation)):  # preceding '=' debug strings may start after these
                    assert f.bln > bln or (f.bln == bln and f.bcol >= bcol)

                l2   = list(f.walk(True, self_=False, recurse=False))
                l, c = [], None

                while c := f.next_child(c, True):
                    l.append(c)

                try:
                    assert l == l2

                except Exception:
                    print(l)
                    print(l2)

                    raise

                l3   = l2[::-1]
                l, c = [], None

                while c := f.prev_child(c, True):
                    l.append(c)

                try:
                    assert l == l3

                except Exception:
                    print(l)
                    print(l3)

                    raise

                l4 = list(f.walk(True, self_=False, recurse=False, back=True))

                # print('l3:', l3)
                # print('l4:', l4)

                assert l3 == l4

                if isinstance(f.a, (FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp, GeneratorExp)):
                    l5 = list(f.walk(True, self_=False, recurse=False, scope=True))
                    l6 = list(f.walk(True, self_=False, recurse=False, scope=True, back=True))

                    # for g in l5: print(g)
                    # print('...')
                    # for g in l6: print(g)

                    assert l5 == l6[::-1]

            except Exception:
                print(f'... {bln}, {bcol} ... {f.bln}, {f.bcol} ... {f.pfield} ... {f.parent}')

                f.parent.dump()

                while f:
                    print(f)

                    f = f.parent

                raise

            bln, bcol = f.bln, f.bcol


class ReputSrc(Fuzzy):
    name    = 'reput_src'
    forever = True

    def fuzz_one(self, fst, fnm) -> bool:
        lines = fst._lines

        # seed(rnd_seed := randint(0, 2**32-1))

        try:
            for count in range(self.batch or 200):
                copy      = fst.copy()
                ln        = randint(0, len(lines) - 1)
                col       = randint(0, len(lines[ln]))
                end_ln    = randint(ln, len(lines) - 1)
                end_col   = randint(col if end_ln == ln else 0, len(lines[end_ln]))
                put_lines = fst.get_src(ln, col, end_ln, end_col, True)

                if not (count % 10):
                    # s = f'{count, ln, col, end_ln, end_col}'

                    # sys.stdout.write('\x08' * 40 + s.ljust(40))
                    sys.stdout.write('.')
                    sys.stdout.flush()

                try:
                    copy.put_src(put_lines, ln, col, end_ln, end_col)
                    copy.verify()

                    compare_asts(fst.a, copy.a, locs=True, raise_=True)

                    assert copy.src == fst.src

                except:
                    # print('\nRandom seed was:', rnd_seed)
                    print()
                    print(count, ln, col, end_ln, end_col)
                    print('-'*80)
                    print(put_lines)
                    # print('.'*80)
                    # print(copy.src)

                    raise

        finally:
            print()


from fst.fst_one import (
    _PUT_ONE_HANDLERS, _put_one_exprish_optional, _put_one_identifier_optional,
    _put_one_Dict_keys, _put_one_withitem_optional_vars,
    _put_one_ExceptHandler_name, _put_one_keyword_arg, _put_one_NOT_IMPLEMENTED_YET,)

class ReputOne(Fuzzy):
    name = 'reput_one'

    DELETE     = True  #False  #
    VERIFY     = False  #True  #
    VERIFY_DEL = True

    def fuzz_one(self, fst, fnm) -> bool:
        backup = fst.copy()
        count  = 0

        for f in fst.walk(True, self_=False):

            assert f.a is not None

            sig = (f.parent.a.__class__, f.pfield.name)

            if sig not in _PUT_ONE_HANDLERS or sig in ((Constant, 'value'), (MatchSingleton, 'value')):
                continue

            if (handler := _PUT_ONE_HANDLERS.get(sig, [None])[1]) is _put_one_NOT_IMPLEMENTED_YET:
                continue

            try:
                field, idx = f.pfield

                put = None
                g   = None
                g   = f.copy()
                ast = copy_ast(g.a)
                src = g.src
                put = 'ident'

                if not (count := count + 1) % 100:
                    sys.stdout.write('.'); sys.stdout.flush()


                # IDENTIFIERS

                for subfield in ('name', 'module', 'names', 'attr', 'id', 'arg', 'rest', 'kwd_attrs'):  # check identifiers
                    changed = False

                    if (child := getattr(f.a, subfield, False)) is not False:
                        delete  = self.DELETE and _PUT_ONE_HANDLERS.get((f.a.__class__, subfield), [None])[1] in (
                            _put_one_identifier_optional, _put_one_ExceptHandler_name, _put_one_keyword_arg)
                        changed = True
                        subs    = list(enumerate(child)) if isinstance(child, list) else [(None, child)]

                        for i, child in subs:
                            if isinstance(child, (str, NoneType)):
                                if delete:
                                    try:
                                        f.put(None, i, field=subfield, raw=False)

                                    except Exception as e:
                                        if 'in this state' not in str(e):
                                            raise

                                    if self.verify:
                                        fst.verify()

                                f.put(child, i, field=subfield, raw=False)

                if changed:
                    fst.verify()


                # NODES

                delete = self.DELETE and handler in (_put_one_exprish_optional, _put_one_Dict_keys,
                                                        _put_one_withitem_optional_vars)
                if self.debug:
                    print(f'\n... ... {g=}, {idx=}, {field=}, {g.parent=}, {delete=}, {g.src=}')
                    f.parent.dump(True); print(f.parent.src); print()

                if delete:
                    put = 'del'

                    try:
                        f.parent.put(None, idx, field=field, raw=False)
                    except Exception as e:
                        if not str(e).endswith('in this state'): raise

                    if self.verify:
                        fst.verify()

                puts = [
                    ('fst', lambda: f.parent.put(g, idx, field=field, raw=False)),
                    ('ast', lambda: f.parent.put(ast, idx, field=field, raw=False)),
                    ('src', lambda: f.parent.put(src, idx, field=field, raw=False)),
                ]

                shuffle(puts)

                for put, func in puts:
                    if self.debug:
                        print(f'    {put} - {f.parent.src=}')

                    try:
                        func()

                    except Exception as exc:
                        if self.debug:
                            print(f'    {exc=}')

                        raise

                    if self.verify:
                        fst.verify()

            except Exception as exc:
                if not ignorable_exc(exc, put == 'src' and src):
                    print('-'*80)
                    print(sig, put, fst.child_path(f, True), idx, field, f.parent)
                    print(f'{f=}')
                    print(f'{f.src=}')
                    print(f'{g=}')
                    print(f'{g.src=}')
                    print(f'{ast=}')
                    print(f'{src=}')

                    raise


        sys.stdout.write('\n')

        if self.verbose:
            print(fst.src)

        if not self.verify:
            fst.verify()

        for ast in (fst.a, backup.a):
            for a in walk(ast):
                if isinstance(a, Constant) and isinstance(a.value, str) and (p := (f := a.f).parent):
                    if isinstance(pa := p.a, Expr):  # zero out docstrings because indentation may have changed for docstrings which do not respect their own indentation level
                        a.value = ''

                    elif isinstance(pa, (JoinedStr, TemplateStr)):  # also zero out these Constants in JoinedStr if they are debug strings because different source for same effective expression will cause compare to fail
                        # if ((idx := f.pfield.idx + 1) < len(pa.values) and
                        #     isinstance(na := pa.values[idx], (FormattedValue, Interpolation)) and
                        #     (strs := na.f._get_fmtval_interp_strs()) and strs[0]
                        # ):
                        #     a.value = ''
                        a.value = ''  # just don't compare, pain-in-the-ass because of AST JoinedStrs unparsing without needed information

        try:
            compare_asts(fst.a, backup.a,
                         cb_primitive=(lambda p1, p2, n, i: n in ('kind', 'type_comment') or (p1.__class__ is p2.__class__ and p1 == p2)),
                         raise_=True)

        except Exception as exc:
            if self.debug:
                try:
                    fst.dump()
                except Exception:
                    pass

            raise


class PutOneExpr(Fuzzy):
    name    = 'put_one_expr'
    forever = True

    exprs   = [
        'a or b',
        'a\nor\nb',
        'a := b',
        'a\n:=\nb',
        'a | b',
        'a\n|\nb',
        'a ** b',
        'a\n**\nb',
        'not a',
        'not\na',
        '~a',
        '~\na',
        'lambda: None',
        'lambda:\nNone',
        'a if b else c',
        'a\nif\nb\nelse\nc',
        '{a: b}',
        '{a:\nb}',
        '{a}',
        '{a,\nb}',
        '[a for a in b]',
        '[a\nfor\na\nin\nb]',
        '{a for a in b}',
        '{a\nfor\na\nin\nb}',
        '{a: c for a, c in b}',
        '{a: c\nfor\na, c\nin\nb}',
        '(a for a in b)',
        '(a\nfor\na\nin\nb)',
        'await a',
        'await\na',
        'yield',
        'yield a',
        'yield\na',
        'yield from a',
        'yield\nfrom\na',
        'a < b',
        'a\n<\nb',
        'f(a)',
        'f\n(\na\n)',
        "f'{a}'",
        'f"{a}"',
        "f'''{a}'''",
        'f"""{a}"""',
        '...',
        'None',
        'True',
        'False',
        '1',
        '1.0',
        '1j',
        "'a'",
        '"a"',
        "'''a'''",
        '"""a"""',
        "b'a'",
        'b"a"',
        "b'''a'''",
        'b"""a"""',
        'a.b',
        'a\n.\nb',
        'a[b]',
        'a\n[\nb\n]',
        '*a',
        '*\na',
        '[a, b]',
        '[\na\n,\nb\n]',
        '(a, b)',
        '(\na\n,\nb\n)',
        'a,',
        'a\n,',
        'a, b',
        'a\n,\nb',

        '\na\nor\nb\n',
        '\na\n:=\nb\n',
        '\na\n|\nb\n',
        '\na\n**\nb\n',
        '\nnot\na\n',
        '\n~\na\n',
        '\nlambda\n:\nNone\n',
        '\na\nif\nb\nelse\nc\n',
        '\n{\na\n:\nb\n}\n',
        '\n{\na\n,\nb\n}\n',
        '\n[\na\nfor\na\nin\nb\n]\n',
        '\n{\na\nfor\na\nin\nb\n}\n',
        '\n{\na\n:\nc\nfor\na\n,\nc\nin\nb\n}\n',
        '\n(\na\nfor\na\nin\nb\n)\n',
        '\nawait\na\n',
        '\nyield\n',
        '\nyield\na\n',
        '\nyield\nfrom\na\n',
        '\na\n<\nb\n',
        '\nf\n(\na\n)\n',
        "\nf'{a}'\n",
        '\nf"{a}"\n',
        "\nf'''\n{\na\n}\n'''\n",
        '\nf"""\n{\na\n}\n"""\n',
        '\n...\n',
        '\nNone\n',
        '\nTrue\n',
        '\nFalse\n',
        '\n1\n',
        '\n1.0\n',
        '\n1j\n',
        "\n'a'\n",
        '\n"a"\n',
        "\n'''\na\n'''\n",
        '\n"""\na\n"""\n',
        "\nb'a'\n",
        '\nb"a"\n',
        "\nb'''\na\n'''\n",
        '\nb"""\na\n"""\n',
        '\na\n.\nb\n',
        '\na\n[\nb\n]\n',
        '\n*\na\n',
        '\n[\na\n,\nb\n]\n',
        '\n(\na\n,\nb\n)\n',
        '\na\n,\n',
        '\na\n,\nb\n',
    ]

    if not _PYLT14:
        exprs.extend([
            "t'{a}'",
            't"{a}"',
            "t'''{a}'''",
            't"""{a}"""',
        ])

    exprs = [FST(e, 'expr') for e in exprs]

    def fuzz_one(self, fst, fnm) -> bool:
        count       = 0
        dst_exprs   = []
        extra_exprs = []

        for f in fst.walk(True):
            if isinstance(a := f.a, expr):
                if getattr(a, 'ctx', None).__class__ is not Load:
                    continue

                if not f.is_parsable():
                    continue

                dst_exprs.append(f)

                if not f.has_slice():
                    extra_exprs.append(f.copy())

        try:
            for e in reversed(dst_exprs):
                if not ((count := count + 1) % 100):
                    sys.stdout.write('.')
                    sys.stdout.flush()

                org = choice(choice([self.exprs, extra_exprs]))

                match randint(0, 2):
                    case 0:
                        put  = 'fst'
                        code = org.copy()
                    case 1:
                        put  = 'ast'
                        code = copy_ast(org.a)
                    case 2:
                        put  = 'src'
                        code = org.src

                try:
                    e.replace(code, raw=False)

                    if self.verify:
                        fst.verify()

                except Exception as exc:
                    if not ignorable_exc(exc, put == 'src' and code):
                        print('\n-', put, '--- parent', '-'*63)
                        print((p := e.parent_stmtish()).src)
                        print('.'*80)
                        p.dump()
                        print('- target', '-'*71)
                        print(e.src)
                        print('.'*80)
                        print(e.dump())
                        print('- replacement', '-'*66)
                        print(org.src)
                        print('.'*80)
                        org.dump()

                        raise

            fst.verify()

        finally:
            sys.stdout.write('\n')

        if self.verbose:
            print(fst.src)


class PutOnePat(Fuzzy):
    name    = 'put_one_pat'
    forever = True

    pats = [
        '42',
        'None',
        '[a, *b]',
        '[\na\n,\n*\nb\n]',
        'a, *b',
        '\na\n,\n*\nb\n',
        '{"key": _}',
        '{\n"key"\n:\n_\n}',
        'SomeClass(attr=val)',
        'SomeClass\n(\nattr\n=\nval\n)',
        'as_var',
        '1 as as_var',
        '1\nas\nas_var',
        '1 | 2',
        '1\n|\n2',

        '\n42\n',
        '\nNone\n',
        '\n[\na\n,\n*\nb\n]\n',
        '\n\na\n,\n*\nb\n\n',
        '\n{\n"key"\n:\n_\n}\n',
        '\nSomeClass\n(\nattr\n=\nval\n)\n',
        '\nas_var\n',
        '\n1\nas\nas_var\n',
        '\n1\n|\n2\n',
    ]

    pats = [FST(e, 'pattern') for e in pats]

    def fuzz_one(self, fst, fnm) -> bool:
        count = 0
        pats  = []

        for f in fst.walk(True):
            if isinstance(f.a, pattern):
                pats.append(f)

        try:
            for e in reversed(pats):
                if not ((count := count + 1) % 100):
                    sys.stdout.write('.')
                    sys.stdout.flush()

                org  = choice(self.pats)
                code = org.copy()

                match randint(0, 2):
                    case 0:
                        put  = 'fst'
                    case 1:
                        put  = 'ast'
                        code = code.a
                    case 2:
                        put  = 'src'
                        code = code.src

                try:
                    e.replace(code, raw=False)

                    if self.verify:
                        fst.verify()

                except Exception:
                    print('\n-', put, '-'*74)
                    print((p := e.parent_stmtish()).src)
                    print('.'*80)
                    p.dump()
                    print('-'*80)
                    print(e.src)
                    print('.'*80)
                    print(e.dump())
                    print('-'*80)
                    org.dump()
                    print('.'*80)
                    print(org.src)

                    raise

            fst.verify()

        finally:
            sys.stdout.write('\n')


class Reconcile1(Fuzzy):
    """This is mostly testing put and syntax, not so much the reconcile."""

    name    = 'reconcile1'
    forever = True

    def fuzz_one(self, fst, fnm) -> bool:
        master = fst.copy()

        try:
            for count in range(self.batch or 200):
                repltype = None

                try:
                    if not (count % 10):
                        sys.stdout.write('.'); sys.stdout.flush()

                    fst   = master.copy()
                    mark  = fst.mark()
                    parts = FSTParts(fst, exclude=(expr_context, mod, FormattedValue, Interpolation))

                    tgt, cat = parts.getrnd()

                    if not tgt:
                        break

                    if isinstance((tgt_parent := tgt.parent).a,
                                  (FormattedValue, Interpolation, JoinedStr, TemplateStr)):  # not supported yet
                        continue

                    repl, _ = parts.getrnd(astcat_allowed_replacements(cat))

                    if not repl:
                        continue

                    if not can_replace(tgt, repl):
                        continue

                    if (repltype := choice(('fstin', 'fstout', 'ast'))) == 'ast':
                        a = copy_ast(repl.a)
                    elif repltype == 'fstout':
                        a = repl.copy().a

                    else:  # repltype == 'fstin'
                        f = tgt

                        while f := f.parent:  # make sure parent is not put into child in this mode
                            if f is repl:
                                break

                        if f:
                            continue

                        a = repl.a

                    if self.debug:
                        tgt_path    = tgt.root.child_path(tgt, True)
                        repl_path   = repl.root.child_path(repl, True)
                        tgt_parent  = tgt.parent.copy()
                        repl_parent = repl.parent.copy()

                    tgt.pfield.set(tgt.parent.a, a)

                    fst = fst.reconcile(mark)

                    fst.verify()

                except Exception as exc:
                    if not ignorable_exc(exc):
                        print()

                        if self.verbose:
                            print(fst.src)

                        print(f'{repltype = }')
                        print(f'{tgt.src = }')
                        print(f'{repl.src = }')
                        print(f'{type(tgt.a) = }')
                        print(f'{type(repl.a) = }')

                        if self.debug:
                            print(f'{tgt_path = }')
                            print(f'{repl_path = }')
                            print(f'{type(tgt_parent.a) = }')
                            print(f'{type(repl_parent.a) = }')
                            print(f'{tgt_parent.src = }')
                            print(f'{repl_parent.src = }')

                        raise

                    # fst = master.copy()  # because not sure about state

        finally:
            print()

        if self.verbose:
            print(fst.src)


class Reconcile(Fuzzy):
    """This changes as many things as possible, so really testing reconcile."""

    name    = 'reconcile'
    forever = True
    # forever = False  # DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG!

    LEVEL_CHANCE = [1/4, 1/3, 1/2]

    def walk_fst(self, fst: FST, level: int = 0):
        """Walk in-tree FST and replace random nodes."""

        next_level   = level + 1
        level_chance = self.LEVEL_CHANCE[min(len(self.LEVEL_CHANCE) - 1, level)]
        exclude      = self.master_parts.exclude
        ast          = fst.a

        for f in fst.walk(True, self_=False, recurse=False):
            if isinstance(f.a, exclude):
                continue

            if random() < level_chance:
                cat          = astcat(f)
                allowed_cats = astcat_allowed_replacements(cat)
                repltype     = choice(('fstin', 'fstout', 'ast'))

                # if repltype == 'fstout':
                #     repl, _ = self.master_parts.getrnd(allowed_cats)

                #     if repl and can_replace(f, repl):
                #         f.pfield.set(ast, repl.copy().a)

                #         continue

                # elif repltype == 'ast':
                #     repl, _ = self.master_parts.getrnd(allowed_cats)

                #     if repl and can_replace(f, repl):
                #         f.pfield.set(ast, a := copy_ast(repl.a))

                #         # self.walk_ast(a, next_level)

                #         continue

                # elif repltype == 'fstin':
                if repltype == 'fstin':
                    repl, _ = self.parts.getrnd(allowed_cats)

                    if (repl and can_replace(f, repl) and
                        not f.root.child_path(f, as_str=True).startswith(repl.root.child_path(repl, as_str=True))
                    ):
                        f.pfield.set(ast, repl.a)

            self.walk_fst(f, next_level)







    def fuzz_one(self, fst, fnm) -> bool:
        self.master_parts = FSTParts(fst)

        master = fst.copy()

        try:
            for count in range(self.batch or 100):
                try:
                    if not (count % 5):
                        sys.stdout.write('.'); sys.stdout.flush()

                    self.parts = self.master_parts.copy()

                    fst  = master.copy()
                    mark = fst.mark()

                    self.walk_fst(fst)

                    with fst.options(docstr=False):
                        fst = fst.reconcile(mark)

                    fst.verify()

                except Exception as exc:
                    if not ignorable_exc(exc):
                        print()

                        if self.verbose:
                            print(fst.src)

                        raise

                # break  # DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG!

        finally:
            print()

        if self.verbose:
            print(fst.src)


# ----------------------------------------------------------------------------------------------------------------------

FUZZIES = {o.name: o for o in globals().values() if isinstance(o, type) and o is not Fuzzy and issubclass(o, Fuzzy)}


def main():
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=f'Available fuzzies: {", ".join(FUZZIES)}'
    )

    parser.add_argument('PATH', nargs='*',
                        help='path of file or directory of files to use')
    parser.add_argument('-f', '--fuzz', action='append', default=[],
                        help='which fuzzies to run')
    parser.add_argument('-b', '--batch', type=int, default=None,
                        help='batch size override')
    parser.add_argument('-g', '--debug', default=False, action='store_true',
                        help='debug mode, print info, do more debug stuff')
    parser.add_argument('-l', '--loop', type=int, default=None,
                        help='number of times to loop, default forever')
    parser.add_argument('-s', '--seed', type=int, default=None,
                        help='random seed (set per file)')
    parser.add_argument('-u', '--shuffle', default=False, action='store_true',
                        help='shuffle files on each loop')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='verbose output, where applicable')
    parser.add_argument('-y', '--verify', default=False, action='store_true',
                        help='do more verifies, usually after everything (slower)')

    args = parser.parse_args()
    fuzz = dict.fromkeys(sum((f.replace(',', ' ').split() for f in args.fuzz), start=[]) if args.fuzz else FUZZIES)

    print(args)

    if any((fuzzy := f) not in FUZZIES for f in fuzz):
        raise ValueError(f'invalid fuzzy: {fuzzy}')

    fuzzies = []
    args    = vars(args)

    for f in fuzz:
        fuzzies.append(FUZZIES[f](args))

    for _ in range(l) if (l := args['loop']) else repeat(None):
        for f in fuzzies[:]:
            print(f'Running: {f.name}')

            try:
                if not f.fuzz():
                    print(f'{f.name} has finished and will not be run again.')

                    fuzzies.remove(f)

            except Exception:
                print(f'Was running: {f.name}')

                raise

        if not fuzzies:
            print('Done...')

            break


if __name__ == '__main__':
    print('...', sys.argv)
    main()
