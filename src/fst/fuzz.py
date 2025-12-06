"""Ugly, super-hacky standalone runnable module of fuzzers, mostly meant for debugging `fst` itself."""

import argparse
import gc
import os
import sys
import sysconfig
import tokenize
from ast import *
from collections import defaultdict
from io import BytesIO
from itertools import repeat
from keyword import iskeyword as keyword_iskeyword
from math import log10
from pprint import pp
from random import choice, randint, random, seed, shuffle, sample
from types import NoneType
from typing import Any, Generator, Iterable, Literal, NamedTuple
from unicodedata import normalize

from .asttypes import TypeAlias, TemplateStr, Interpolation, _ExceptHandlers
from .astutil import *
from .astutil import re_alnumdot_alnum
from .common import PYLT11, PYLT12, PYLT14, PYGE12, astfield, next_frag
from .view import fstview
from .parsex import parse, parse_expr_arglike
from .fst import FST
from . import NodeError

try:
    from tokenize import FSTRING_MIDDLE
    try:
        from tokenize import TSTRING_MIDDLE
        ftstr_middles = (FSTRING_MIDDLE, TSTRING_MIDDLE)
    except ImportError:
        ftstr_middles = (FSTRING_MIDDLE,)
except ImportError:
    ftstr_middles = ()


INCLUDE_PYTHON_STDLIB = True

PROGRAM = 'python -m fst.fuzz'

UNICODE = ''.join([
    'ä',
    'µ',          # normalization
    '蟒',
    # 'x󠄀',           # variation selector
    '𝔘𝔫𝔦𝔠𝔬𝔡𝔢',      # normalization
    'абвгд',
    'Źdźbło',
    'العربية',    # Arabic
    '中文',        # Chinese
    'кириллица',  # Cyrillic
    'Ελληνικά',   # Greek
    # 'עִברִית',       # Hebrew
    '日本語',      # Japanese
    '한국어',       # Korean
    'ไทย',        # Thai
    # 'देवनागरी',      # Devanagari
])

ASTS_STMT_NONBLOCK = (
    Return,
    Delete,
    Assign,
    TypeAlias,
    AugAssign,
    AnnAssign,
    Raise,
    Assert,
    Import,
    ImportFrom,
    Global,
    Nonlocal,
    Expr,
    Pass,
    Break,
    Continue,
)

EXPRS = [
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

if not PYLT14:
    EXPRS.extend([
        "t'{a}'",
        't"{a}"',
        "t'''{a}'''",
        't"""{a}"""',
    ])

EXPRS = [FST(e, 'expr') for e in EXPRS]

PATS = [
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

PATS = [FST(e, 'pattern') for e in PATS]


old_FST_put = FST.put
old_FST_put_slice = FST.put_slice

def debug_put(self, code, idx = None, stop = False, field = None, *, one = True, **options):
    print(f'put({self=}, {idx=}, {stop=}, {field=}, {one=}, {options=})')
    print(f'  {code=!r}')

    if isinstance(code, AST):
        print(' ', dump(code))

    elif isinstance(code, FST):
        for l in lines if len(lines := code.lines) <= 11 else lines[:5] + ['...'] + lines[-5:]:
            print(' ', repr(l))

    pre_lines = self.lines

    ret = old_FST_put(self, code, idx, stop, field, one=one, **options)

    verify = bool(self.root.verify(raise_=False))

    print(f'  {verify=}')
    print()

    if not verify:
        print('=== before put self lines ' + '='*80)
        print('\n'.join(pre_lines))
        print()
        print('--- after put self lines ' + '-'*80)
        print('\n'.join(self.lines))
        # print('--- after put whole ' + '-'*80)
        # print(self.root.src)

        raise SystemExit(-1)

    return ret

def debug_put_slice(self, code, start = None, stop = None, field = None, *, one = False, **options):
    print(f'put_slice({self=}, {stop=}, {stop=}, {field=}, {one=}, {options=})')
    print(f'  {code=!r}')

    if isinstance(code, AST):
        print(' ', dump(code))

    elif isinstance(code, FST):
        for l in lines if len(lines := code.lines) <= 11 else lines[:5] + ['... ... ...'] + lines[-5:]:
            print(' ', repr(l))

    pre_lines = self.lines

    ret = old_FST_put_slice(self, code, start, stop, field, one=one, **options)

    verify = bool(self.root.verify(raise_=False))

    print(f'  {verify=}')
    print()

    if not verify:
        print('=== before put self ' + '='*80)
        print('\n'.join(pre_lines))
        print()
        print('--- after put self lines ' + '-'*80)
        print('\n'.join(self.lines))
        # print('--- after put whole ' + '-'*80)
        # print(self.root.src)

        raise SystemExit(-1)

    return ret


def minify_src(source_code):
    tokens = tokenize.tokenize(BytesIO(source_code.encode()).readline)
    result = []
    prev_end = (1, 0)
    prev_str = ''

    for token in tokens:
        tok_type = token.type
        tok_str = token.string
        start, end = token.start, token.end

        if tok_type == tokenize.ENCODING:
            continue
        if tok_type == tokenize.ENDMARKER:
            break

        if tok_type in ftstr_middles:  # handle '{{' and '}}' in f/t-strings
            if tok_str.endswith('{'):
                tok_str = tok_str + '{'
            elif tok_str.endswith('}'):
                tok_str = tok_str + '}'

        if start > prev_end:
            if start[0] > prev_end[0]:
                result.append(' ' * start[1])
            elif re_alnumdot_alnum.match(tok_str[:1] + prev_str[-1:]):
                result.append(' ')

        result.append(tok_str)

        prev_end = end
        prev_str = tok_str

    return ''.join(result)


def add_lineconts(fst: FST) -> None:
    lines = fst._lines
    g = None

    for f in (gen := fst.walk('all')):
        if f.is_stmtish or f.is_mod:
            continue

        if (isinstance(a := f.a, (JoinedStr, TemplateStr))
            or (isinstance(a, Constant)
                and isinstance(a.value, (str, bytes)
        ))):
            gen.send(False)

            g = None  # we don't want to accidentally pick a span which includes this

            continue

        if g is not None and f.parent is g.parent and (ln := g.end_ln) == f.ln:
            # print('...', g, f)
            col = randint(g.end_col, f.col)

            if (l := lines[ln])[col].isspace() or (col and l[col - 1].isspace()):
                fst._put_src('\\\n', ln, col, ln, col, False)

                # if not fst.verify(raise_=False):
                #     print('   ', col)
                #     print(f.parent.lines)
                #     raise RuntimeError

        g = f


def add_semicolons(fst: FST) -> None:
    lines = fst._lines

    for f in fst.walk(True, back=True):
        if not isinstance(f.a, ASTS_STMT_NONBLOCK):
            continue

        if (r := randint(0, 3)) >= 2:
            continue

        if (r
            and (pfield := f.pfield)
            and pfield.idx
            and isinstance((g := f.prev()).a, ASTS_STMT_NONBLOCK)
            and (
                not (fr := next_frag(lines, g.end_ln, g.end_col, g.end_ln, 0x7fffffffffffffff))
                or fr.src.startswith('#')
        )):
            f.parent.put_src(choice((';', ' ;', '; ', ' ; ')), g.end_ln, g.end_col, f.ln, f.col, 'offset')

        elif not (fr := next_frag(lines, f.end_ln, f.end_col, f.end_ln, 0x7fffffffffffffff)) or fr.src.startswith('#'):
            f.parent.put_src(choice((';', ' ;')), f.end_ln, f.end_col, f.end_ln, f.end_col, 'offset')


def add_whitespace(src: str) -> str:
    new_lines = []

    for line in src.split('\n'):
        if randint(0, 1):
            line += '    \t \t \t\t  \t\t\t\t'[(i := randint(0, 15)) : randint(i, 16)]

        new_lines.append(line)

    return '\n'.join(new_lines)


def add_unicode(fst: FST) -> None:
    def ident() -> str:
        while keyword_iskeyword(normalize('NFKC', i := ''.join(sample(UNICODE, randint(1, 12))))):
            pass

        return i

    for f in (gen := fst.walk(True)):
        a = f.a

        if PYLT12 and isinstance(a, JoinedStr):
            gen.send(False)

            continue

        if randint(0, 1):
            continue

        if isinstance(a, Name):
            f.id = ident()
        elif isinstance(a, Attribute):
            f.attr = ident()


def find_pys(path) -> list[str]:
    if os.path.isfile(path):
        return [path] if path.endswith('.py') else []

    if os.path.isdir(path):
        fnms = []

        for dir, _, fnms_ in os.walk(path):
            fnms.extend(os.path.join(dir, fnm) for fnm in fnms_ if fnm.endswith('.py'))

        return fnms

    raise ValueError(f'unknown thing: {path}')


def is_parsable(self) -> bool:
    r"""Whether the source for this node is parsable by `FST` or not (if properly dedented for top level). This is
    different from `astutil.is_parsable` because that one indicates what is parsable by the python `ast` module,
    while `FST` can parse more things. For example, an unparenthesized `NamedExpr` is considered parsable even
    though it would not parse directly using `ast.parse()`.

    **Returns:**
    - `bool`: Whether is parsable by `FST` from a string or not.

    **Examples:**

    >>> from fst import astutil

    >>> FST('i').is_parsable()
    True

    >>> FST('a[b]').slice.is_parsable()
    True

    >>> FST('a[b:c]').slice.is_parsable()
    True

    >>> astutil.is_parsable(FST('a[b:c]').slice.a)
    False

    >>> FST('f"{a!r:<8}"').values[0].is_parsable()
    False

    >>> FST('f"{a!r:<8}"').values[0].value.is_parsable()
    True

    >>> FST('f"{a!r:<8}"').values[0].format_spec.is_parsable()
    False

    >>> FST('try: pass\nexcept: pass').body[0].is_parsable()
    True

    >>> FST('try: pass\nexcept: pass').handlers[0].is_parsable()
    True

    >>> astutil.is_parsable(FST('try: pass\nexcept: pass').handlers[0].a)
    False

    >>> FST('try: pass\nexcept: pass').handlers[0].body[0].is_parsable()
    True

    >>> FST('match a:\n  case 1: pass').cases[0].is_parsable()
    True

    >>> astutil.is_parsable(FST('match a:\n  case 1: pass').cases[0].a)
    False
    """

    if not self.loc:
        return False

    ast = self.a

    if isinstance(ast, (expr_context, type_ignore, FormattedValue, Interpolation)):
        return False

    if parent := self.parent:
        if isinstance(ast, JoinedStr):  # TemplateStr doesn't go into a .format_spec, '.1f' type strings without quote delimiters
            if self.pfield.name == 'format_spec':  # isinstance(parent.a, (FormattedValue, Interpolation)):
                return False

        elif isinstance(ast, Constant):  # string parts of f-string without quote delimiters (probably, unless parts of implicit strings)
            if self.pfield.name == 'values' and isinstance(parent.a, (JoinedStr, TemplateStr)):  # isinstance(ast.value, str)
                return False

    return True


def ignorable_exc(exc: Exception, putsrc: str | Literal[False] | None = None):
    if isinstance(exc, NotImplementedError):
        return True

    msg = str(exc)

    ignorable = isinstance(exc, (NodeError, ValueError)) and (
        msg.endswith('cannot be Starred') or
        'not implemented' in msg or
        'in this state' in msg or
        'at this location' in msg or
        'pattern expression' in msg or
        'invalid value for MatchValue.value' in msg or
        'invalid value for MatchMapping.keys' in msg or
        'cannot reparse Starred in slice as Starred' in msg or
        'expecting identifier, got' in msg or
        'not allowed in this alias' in msg or
        msg == 'cannot put star alias to ImportFrom.names containing multiple aliases' or
        msg == 'cannot have unparenthesized tuple containing Starred in slice'
        # (msg.startswith('cannot put ') and (msg.endswith(' to MatchMapping.keys') or msg.endswith(' to MatchValue.value')))
    )

    if not ignorable and isinstance(exc, SyntaxError):
        if (
            # msg.startswith('cannot assign to literal here') or
            # msg.startswith('cannot assign to expression here') or
            # "Maybe you meant '==' instead of '='" in msg or
            # "Maybe you meant '==' or ':=' instead of '='"
            "Maybe you meant '==' " in msg
            or ' for augmented assignment' in msg
            or msg.startswith('positional argument follows keyword argument')
            or msg.startswith('cannot use starred expression here')
            or msg.startswith('illegal target for annotation')
            or msg.startswith('cannot delete ')
            # msg.startswith('cannot delete literal') or
            # msg.startswith('cannot delete function call') or

            or msg.startswith('cannot assign to ')
            # msg.startswith('cannot assign to literal') or
            # msg.startswith('cannot assign to function call') or
            # msg.startswith('cannot assign to expression') or
            # msg.startswith('cannot assign to None') or
            or (msg.startswith('future feature') and 'is not defined' in msg)
        ):
            ignorable = True

        elif putsrc:  # Starred stuff like "*a or b" coming from original code
            try:
                parse_expr_arglike(putsrc)
            except SyntaxError:
                pass
            else:
                ignorable = True

    return ignorable


def astbase(kls: type[AST]) -> type[AST]:  # ast base class just above AST
    while (c := kls.__bases__[0]) is not AST:
        kls = c

    return kls


ASTCat = type[AST]  # mod, stmt, expr, Slice, slice, expr_context, boolop, operator, unaryop, cmpop, comprehension, excepthandler, ExceptHandler, arguments, arg, keyword, alias, withitem, match_case, pattern

def astcat(ast: AST, parent: AST) -> ASTCat:  # ast category (replacement compatibility)
    if isinstance(ast, ExceptHandler):
        return ExceptHandler if isinstance(parent, Try) else excepthandler  # Try vs. TryStar
    if isinstance(ast, (Starred, Slice)):
        return ast.__class__
    if isinstance(ast, Slice) or (isinstance(ast, Tuple) and any(isinstance(e, Slice) for e in ast.elts)):
        return slice  # Tuple containing Slice

    return astbase(ast.__class__)

def fstcat(fst: FST) -> ASTCat:  # ast category (replacement compatibility)
    a = fst.a

    if isinstance(a, ExceptHandler):
        return ExceptHandler if isinstance(fst.parent.a, Try) else excepthandler  # Try vs. TryStar
    if isinstance(a, (Starred, Slice)):
        return a.__class__
    if fst._has_Slice():
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

    def __init__(self, fst: FST, exclude: type[AST] | tuple[type[AST]] | None = None) -> None:
        if isinstance(fst, FSTParts):
            self.cats = fst.cats.copy()
            self.parts = {c: fs.copy() for c, fs in fst.parts.items()}
            self.exclude = fst.exclude if exclude is None else exclude

            return

        cats = {}                  # {FST: ASTCat, ...}
        parts = defaultdict(list)  # {ASTCat: [FST, ...], ...}

        if exclude is None:
            exclude = (expr_context, mod, FormattedValue, Interpolation)

        for a in walk(fst.a):
            if isinstance(a, exclude):
                continue

            f = a.f
            cat = cats[f] = fstcat(f)

            parts[cat].append(f)

        self.cats = cats
        self.parts = dict(parts)
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
            self.cats[fst] = cat = fstcat(fst)

            if not (fs := self.parts.get(cat)):
                fs = self.parts[cat] = []

            fs.append(fst)

    def remove_all(self, fst: FST):
        exclude = self.exclude
        parts = self.parts
        cats = self.cats

        for a in walk(fst.a):
            if not isinstance(a, exclude) and (f := getattr(a, 'f', None)):
                if (c := cats.get(f)) and f in cats:
                    del cats[f]

                    parts[c].remove(f)

    def add_all(self, fst: FST):  # or put back removed
        exclude = self.exclude
        parts = self.parts
        cats = self.cats

        for a in walk(fst.a):
            if not isinstance(a, exclude):
                f = a.f
                cats[f] = cat = fstcat(f)

                if not (fs := parts.get(cat)):
                    fs = parts[cat] = []

                fs.append(f)

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
    path = stmt_.child_path(fst)
    stmt_ = stmt_.copy()

    try:
        stmt_.child_from_path(path).replace(with_.copy() if with_ else with_, raw=False).root.verify()
    except Exception:
        return False

    return True


def can_replace(tgt: FST, repl: FST) -> bool:  # assuming ASTCat has already been checked and only testing allowed category
    try:
        repla, repl_parenta = repl.a, repl.parent.a
        tgta, tgt_parenta = tgt.a, tgt.parent.a
        tgt_field, _ = tgt.pfield
        repl_field, _ = repl.pfield

        if PYLT12:
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
                if not isinstance(repla, Name) or repla.id == '_':
                    return False

            elif isinstance(tgta, (Name, Attribute)):
                if not isinstance(repla, (Name, Attribute)):
                    return False

            elif not is_valid_MatchValue_value(repla):
                return False

        if isinstance(tgta, pattern) and isinstance(repla, MatchStar) and not isinstance(tgt_parenta, MatchSequence):
            return False

        if tgt.parent_pattern():
            if tgt_field in ('left', 'right', 'operand', 'op'):  # just don't bother
                return False

            if tgt_field == 'keys' and isinstance(repla, Name):
                return False

        if repl_field == 'vararg' and isinstance(repla.annotation, Starred) and tgt_field != 'vararg':  # because could have Starred annotation headed for a non-vararg field
            return False

        if PYLT11:
            if isinstance(tgt_parenta, Tuple) and isinstance(repla, Starred) and tgt.parent.pfield == ('slice', None):
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

        if isinstance(tgta, arguments) and isinstance(tgt_parenta, Lambda) and not isinstance(repl_parenta, Lambda):
            return False

        if (isinstance(tgta, arg)
            and isinstance(tgt_parenta, arguments)
            and isinstance(tgt.parent.parent.a, Lambda)
            and repla.annotation
        ):
            return False

        if not isinstance(ctx := getattr(tgta, 'ctx', Load()), Load):
            if isinstance(ctx, Del) or not getattr(repla, 'ctx', None):
                return False

            allowed = None
            f = tgt

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

                if not isinstance(a, expr):  # ASTS_EXPRISH?
                    break

            if not allowed or not isinstance(repla, allowed):
                return False

        # if isinstance(tgta, operator) and isinstance(repla, operator) and tgt._is_augop() ^ repl._is_augop():
        #     return False

    except Exception:
        return False

    return True


def can_replace_ast(
    tgta: AST, tgt_parenta: AST, tgt_field: str, repla: AST, repl_parenta: AST, repl_field: str
) -> bool:  # the best we can do for pure AST
    try:
        if PYLT12:
            # if any(isinstance(f.a, (JoinedStr, TemplateStr)) for f in tgt.parents()):
            #     return False

            if isinstance(repl_parenta, (JoinedStr, TemplateStr, FormattedValue, Interpolation)):
                return False

        else:
            if isinstance(tgt_parenta, (JoinedStr, TemplateStr)):
                return False

            if isinstance(tgt_parenta, (FormattedValue, Interpolation)) and tgt_field != 'value':
                return False

        # if isinstance(tgta, expr) and any(isinstance(f.a, pattern) for f in tgt.parents()):
        #     if tgt_field == 'value':
        #         if not is_valid_MatchValue_value(repla):
        #             return False

        #     if tgt_field == 'cls':
        #         if not isinstance(repla, Name):
        #             return False

        #     elif isinstance(tgta, (Name, Attribute)):
        #         if not isinstance(repla, (Name, Attribute)):
        #             return False

        #     elif not is_valid_MatchValue_value(repla):
        #         return False

        if isinstance(tgta, pattern) and isinstance(repla, MatchStar) and not isinstance(tgt_parenta, MatchSequence):
            return False

        # if tgt.parent_pattern():
        #     if tgt_field in ('left', 'right', 'operand', 'op'):  # just don't bother
        #         return False

        #     if tgt_field == 'keys' and isinstance(repla, Name):
        #         return False

        if repl_field == 'vararg' and isinstance(repla.annotation, Starred) and tgt_field != 'vararg':  # because could have Starred annotation headed for a non-vararg field
            return False

        # if PYLT11:
        #     if isinstance(tgt_parenta, Tuple) and isinstance(repla, Starred) and tgt.parent.pfield == ('slice', None):
        #         return False

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

        if isinstance(tgta, arguments) and isinstance(tgt_parenta, Lambda) and not isinstance(repl_parenta, Lambda):
            return False

        # if (isinstance(tgta, arg) and isinstance(tgt_parenta, arguments) and
        #     isinstance(tgt.parent.parent.a, Lambda) and repla.annotation
        # ):
        #     return False

        # if not isinstance(ctx := getattr(tgta, 'ctx', Load()), Load):
        #     if isinstance(ctx, Del) or not getattr(repla, 'ctx', None):
        #         return False

        #     allowed = None
        #     f       = tgt

        #     while f := f.parent:
        #         if isinstance(a := f.a, (Delete, Assign, For, AsyncFor, comprehension)):
        #             allowed = (Name, Attribute, Subscript)#, Tuple, List)

        #             break

        #         if isinstance(a, (AugAssign, AnnAssign)):
        #             allowed = (Name, Attribute, Subscript)

        #             break

        #         if isinstance(a, (TypeAlias, NamedExpr)):
        #             allowed = Name

        #             break

        #         if not isinstance(a, expr):  # ASTS_EXPRISH?
        #             break

        #     if not allowed or not isinstance(repla, allowed):
        #         return False

    except Exception:
        return False

    return True


class Fuzzy:
    syspyfnms = None
    name = 'Fuzzy'
    forever = False

    def __init__(self, args: dict[str, Any]) -> None:
        self.args = args
        self.batch = args.get('batch')
        self.debug = args.get('debug')
        self.loop = args.get('loop')
        self.linecont = args.get('linecont')
        self.linecont_rnd = args.get('linecont_rnd')
        self.minify = args.get('minify')
        self.minify_rnd = args.get('minify_rnd')
        self.semicolon = args.get('semicolon')
        self.semicolon_rnd = args.get('semicolon_rnd')
        self.whitespace = args.get('whitespace')
        self.whitespace_rnd = args.get('whitespace_rnd')
        self.unicode = args.get('unicode')
        self.unicode_rnd = args.get('unicode_rnd')
        self.seed = args.get('seed')
        self.reseed = args.get('reseed')
        self.shuffle = args.get('shuffle')
        self.verbose = args.get('verbose')
        self.verify = args.get('verify')

        if paths := args.get('PATH'):
            fnms = sum((find_pys(path) for path in paths), start=[])

        elif Fuzzy.syspyfnms is None:
            fnms = find_pys(sys.prefix)

            if INCLUDE_PYTHON_STDLIB:
                if stdlib := sysconfig.get_paths().get('stdlib'):
                    fnms.extend(find_pys(stdlib))

        self.fnms = fnms

    def iter_pys(self) -> Generator[tuple[str, FST], None, None]:
        fnms = self.fnms
        width = int(log10(len(fnms) - 1 or 1)) + 1

        if self.args['shuffle']:
            fnms = fnms[:]

            shuffle(fnms)

        for i, fnm in enumerate(fnms):
            self.rnd_seed = randint(0, 2**32-1) if self.seed is None else self.seed
            self.rnd_reseed = None

            seed(self.rnd_seed)

            self.minified = (randint(0, 1) and self.args['minify_rnd']) or self.args['minify']  # randint() MUST be executed regardless to preserve deterministic randomness
            self.whitespaced = (randint(0, 1) and self.args['whitespace_rnd']) or self.args['whitespace']
            self.unicoded = (randint(0, 1) and self.args['unicode_rnd']) or self.args['unicode']
            self.semicoloned = (randint(0, 1) and self.args['semicolon_rnd']) or self.args['semicolon']
            self.lineconted = (randint(0, 1) and self.args['linecont_rnd']) or self.args['linecont']

            head = f'{i:<{width}}: {fnm}'

            try:
                with open(fnm) as f:
                    src = f.read()

                if self.minified:
                    src = minify_src(src)

                if self.whitespaced:
                    src = add_whitespace(src)

                fst = FST.fromsrc(src)

                if self.unicoded:
                    add_unicode(fst)

                if self.semicoloned:
                    add_semicolons(fst)

                if self.lineconted:
                    add_lineconts(fst)

            except (NodeError, SyntaxError, UnicodeDecodeError) as exc:
                print(f'{head} - read/parse fail: **{exc.__class__.__name__}**')

            else:
                print(head)

                yield fnm, fst

    def do_reseed(self):
        self.rnd_reseed = randint(0, 2**32-1) if self.reseed is None else self.reseed

        seed(self.rnd_reseed)

    def fuzz(self) -> bool:
        fnm = None

        try:
            for fnm, fst in self.iter_pys():
                seed(self.rnd_seed)

                gc.collect()

                self.fuzz_one(fst, fnm)

        except:  # Exception:
            print('-'*80)
            print('Command line:', ' '.join(sys.argv))
            print('File:', fnm)
            print(f'Preprocessing: {"" if self.minified else "NOT "}minified (-mM), {"" if self.whitespaced else "NOT "}whitespaced (-wW), {"" if self.unicoded else "NOT "}unicoded (-nN), {"" if self.semicoloned else "NOT "}semicoloned (-eE), {"" if self.lineconted else "NOT "}lineconted (-cC)')
            print(f'Random seed: {self.rnd_seed}, reseed: {self.rnd_reseed}')

            raise

        return self.forever

    def fuzz_one(self, fst: FST, fnm: str):
        pass

    def check_abort(self) -> bool:
        """Check memory usage and return abort true if too large. Because random edits can explode file sizes."""

        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        if (l := len(s := line.split()[1])) > 6 or (l == 6 and s > '500000'):
                            print('\nMemory!')

                            return True

                        break

        except Exception:
            pass

        return False


# ----------------------------------------------------------------------------------------------------------------------

class Dump(Fuzzy):
    name = 'dump'
    forever = False

    def fuzz_one(self, fst, fnm) -> bool:
        print(fst.src)


class VerifyCopy(Fuzzy):
    name = 'verify_copy'
    forever = False

    def fuzz_one(self, fst, fnm) -> bool:
        for f in fst.walk('all'):
            if not is_parsable(f):  # because .verify() needs to parse
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
    forever = False

    def fuzz_one(self, fst, fnm) -> bool:
        bln, bcol = 0, 0

        for f in (gen := fst.walk(True)):
            if PYLT12 and isinstance(f.a, JoinedStr):  # these have no location info in py <3.12
                gen.send(False)

                continue

            try:
                if not isinstance(f.a, (FormattedValue, Interpolation)):  # preceding '=' debug strings may start after these
                    assert f.bln > bln or (f.bln == bln and f.bcol >= bcol)

                l2 = list(f.walk(True, self_=False, recurse=False))
                l, c = [], None

                while c := f.next_child(c, True):
                    l.append(c)

                try:
                    assert l == l2

                except Exception:
                    print(l)
                    print(l2)

                    raise

                l3 = l2[::-1]
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

                if isinstance(f.a, (FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp,
                                    GeneratorExp)):
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


class Reparse(Fuzzy):
    name = 'reparse'
    forever = False

    def fuzz_one(self, fst, fnm) -> bool:
        for f in (gen := fst.walk()):
            ast = f.a

            if isinstance(ast, expr_context):
                continue

            if isinstance(ast, (JoinedStr, TemplateStr)):
                gen.send(False)

            f = f.copy()
            a = parse(f.src, f.a.__class__)

            compare_asts(a, f.a, locs=True, ctx=True, raise_=True)


class ReputSrc(Fuzzy):
    name = 'reput_src'
    forever = True

    def fuzz_one(self, fst, fnm) -> bool:
        lines = fst._lines

        # seed(rnd_seed := randint(0, 2**32-1))

        try:
            for count in range(self.batch or 200):
                copy = fst.copy()
                ln = randint(0, len(lines) - 1)
                col = randint(0, len(lines[ln]))
                end_ln = randint(ln, len(lines) - 1)
                end_col = randint(col if end_ln == ln else 0, len(lines[end_ln]))
                put_lines = fst._get_src(ln, col, end_ln, end_col, True)

                if not (count % 10):
                    # s = f'{count, ln, col, end_ln, end_col}'

                    # sys.stdout.write('\x08' * 40 + s.ljust(40))
                    sys.stdout.write('.')
                    sys.stdout.flush()

                try:
                    if self.debug:
                        ls = copy._lines
                        old_lines = ls[max(0, ln - 5) : min(len(ls), end_ln + 6)]

                    copy.put_src(put_lines, ln, col, end_ln, end_col)
                    copy.verify()

                    compare_asts(fst.a, copy.a, locs=True, raise_=True)

                    assert copy.src == fst.src

                except Exception:
                    # print('\nRandom seed was:', rnd_seed)
                    print()
                    print(f'{count=}, loc={(ln, col, end_ln, end_col)}')
                    print('...', 'put_lines', '.'*80)
                    pp(put_lines)

                    if self.debug:
                        print()
                        print('...', 'old_lines', '.'*80)
                        pp(old_lines)

                    if self.verbose:
                        print()
                        print('...', 'full_lines', '.'*80)
                        pp(copy._lines)

                    # print('.'*80)
                    # print(copy.src)

                    raise

        finally:
            print()


class ReputOne(Fuzzy):
    from fst.fst_put_one import (
        _PUT_ONE_HANDLERS,
        _put_one_exprish_optional,
        _put_one_identifier_optional,
        _put_one_Dict_keys,
        _put_one_withitem_optional_vars,
        _put_one_ExceptHandler_name,
        _put_one_keyword_arg,
        _put_one_NOT_IMPLEMENTED_YET,
    )

    name = 'reput_one'
    forever = False

    DELETE = True  #False  #
    VERIFY = False  #True  #
    VERIFY_DEL = True

    def fuzz_one(self, fst, fnm) -> bool:
        backup = fst.copy()
        count = 0

        for f in fst.walk(True, self_=False):

            assert f.a is not None

            sig = (f.parent.a.__class__, f.pfield.name)

            if sig not in ReputOne._PUT_ONE_HANDLERS or sig in ((Constant, 'value'), (MatchSingleton, 'value')):
                continue

            if (handler := ReputOne._PUT_ONE_HANDLERS.get(sig, [None])[1]) is ReputOne._put_one_NOT_IMPLEMENTED_YET:
                continue

            try:
                field, idx = f.pfield

                put = None
                g = None
                g = f.copy()
                ast = copy_ast(g.a)
                src = g.src
                put = 'ident'

                if not (count := count + 1) % 100:
                    sys.stdout.write('.'); sys.stdout.flush()


                # IDENTIFIERS

                for subfield in ('name', 'module', 'names', 'attr', 'id', 'arg', 'rest', 'kwd_attrs'):  # check identifiers
                    changed = False

                    if (child := getattr(f.a, subfield, False)) is not False:
                        delete = self.DELETE and ReputOne._PUT_ONE_HANDLERS.get(
                            (f.a.__class__, subfield), [None])[1] in (ReputOne._put_one_identifier_optional,
                                                                      ReputOne._put_one_ExceptHandler_name,
                                                                      ReputOne._put_one_keyword_arg)
                        changed = True
                        subs = list(enumerate(child)) if isinstance(child, list) else [(None, child)]

                        for i, child in subs:
                            if isinstance(child, (str, NoneType)):
                                if delete:
                                    try:
                                        f.put(None, i, field=subfield, raw=False)

                                    except Exception as e:
                                        if 'in this state' not in str(e) and 'at this location' not in str(e):
                                            raise

                                    if self.verify:
                                        fst.verify()

                                f.put(child, i, field=subfield, raw=False)

                if changed:
                    fst.verify()


                # NODES

                delete = self.DELETE and handler in (ReputOne._put_one_exprish_optional, ReputOne._put_one_Dict_keys,
                                                     ReputOne._put_one_withitem_optional_vars)
                if self.debug:
                    print(f'\n... ... {g=}, {idx=}, {field=}, {g.parent=}, {delete=}, {g.src=}')
                    f.parent.dump(True); print(f.parent.src); print()

                if delete:
                    put = 'del'

                    try:
                        f.parent.put(None, idx, field=field, raw=False)
                    except Exception as e:
                        if 'in this state' not in (s := str(e)) and 'at this location' not in s: raise

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
                         cb_primitive=(lambda p1, p2, n, i: n in ('kind', 'type_comment', 'str') or (p1.__class__ is p2.__class__ and p1 == p2)),
                         raise_=True)

        except Exception:
            if self.debug:
                try:
                    fst.dump()
                except Exception:
                    pass

            raise


class PutOne(Fuzzy):
    """Test as much _put_one() as possible, deletions, identifiers, etc..."""

    name = 'put_one'
    forever = True

    def fuzz_one(self, fst, fnm) -> bool:
        count = 0
        parts = FSTParts(fst.copy())
        dst_nodes = []

        for expr in EXPRS:
            parts.add_all(expr.copy())

        for pat in PATS:
            parts.add_all(pat.copy())

        for f in fst.walk():
            if isinstance(f.a, (expr_context, mod)):#, FormattedValue, Interpolation)):
                continue

            dst_nodes.append(f)

        try:
            for f in reversed(dst_nodes):
                if not ((count := count + 1) % 100):
                    sys.stdout.write('.')
                    sys.stdout.flush()

                # IDENTIFIER CHILDREN

                for subfield in ('name', 'module', 'names', 'attr', 'id', 'arg', 'rest', 'kwd_attrs'):  # check identifiers
                    changed = False

                    if (child := getattr(f.a, subfield, False)) is not False:
                        changed = True
                        subs = list(enumerate(child)) if isinstance(child, list) else [(None, child)]

                        if self.debug:
                            print(f'{subs = }')

                        for i, child in subs:
                            if isinstance(child, (str, NoneType)):
                                try:
                                    f.put('_' if isinstance(f.a, (Global, Nonlocal)) else None, i, field=subfield, raw=False)

                                except Exception as e:
                                    msg = str(e)

                                    if (not msg.startswith('cannot delete')
                                        and not msg.startswith('cannot put slice to')
                                        and msg != "cannot change MatchAs with pattern into wildcard '_'"
                                        and 'not implemented' not in msg
                                    ):  # 'in this state' not in str(e):
                                        raise

                                else:
                                    if self.verify:
                                        fst.verify()

                            try:
                                f.put(child, i, field=subfield, raw=False)

                            except Exception as e:
                                msg = str(e)

                                if 'not implemented' not in msg:
                                    raise

                if changed and self.debug:
                    fst.verify()

                # NODE

                cat = fstcat(f)
                allowed_cats = astcat_allowed_replacements(cat)
                repl, _ = parts.getrnd(allowed_cats)
                parent = f.parent
                field, idx = f.pfield

                if idx is not None and randint(0, 1):  # randomly change index to negative (referring to same location)
                    idx -= len(getattr(parent.a, field))

                if not can_replace(f, repl):
                    continue

                if self.debug:
                    debuglines = [str(f)] + f.lines

                if random() < 0.5 and not ReputOne._PUT_ONE_HANDLERS.get((parent.a.__class__, field), [True])[0]:
                    try:
                        parent.put(None, idx, False, field, raw=False)

                    except Exception as e:
                        msg = str(e)

                        if not msg.startswith('cannot delete') and 'not implemented' not in msg:# and not msg.startswith('cannot put slice to'):
                            raise

                match put := choice(('fst', 'ast', 'src')):
                    case 'fst':
                        code = repl.copy()
                    case 'ast':
                        code = copy_ast(repl.a)
                    case 'src':
                        code = repl.copy().src  # dedent, fix 'elif'

                try:
                    if self.debug:
                        print(f'... {put=}, {idx=}, {field=}')
                        print('\n'.join(debuglines))
                        print(f'{code=}')
                        print(f'{repl=}')
                        print(f'{repl.src=}')

                    parent.put(code, idx, False, field, raw=False)

                    if self.verify:
                        fst.verify()

                except Exception as exc:
                    # if not ignorable_exc(exc) and not (put == 'src' and isinstance(exc, SyntaxError)):
                    if not ignorable_exc(exc, put == 'src' and code):
                        if self.verbose:
                            print(fst.src)

                        raise

            fst.verify()

        finally:
            sys.stdout.write('\n')

        if self.verbose:
            print(fst.src)


class ReconcileRnd(Fuzzy):
    """This changes as many things as possible, so really testing reconcile."""

    name = 'reconcile_rnd'
    forever = True
    # forever = False  # DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG!

    LEVEL_CHANCE = [1/4, 1/3, 1/2]

    def walk_ast(self, ast: AST, level: int = 0, parents: list[AST] = []):
        """Walk pure AST and replace random nodes."""

        next_level = level + 1
        level_chance = self.LEVEL_CHANCE[min(len(self.LEVEL_CHANCE) - 1, level)]
        exclude = self.master_parts.exclude
        parents = parents + [ast]

        for field, child in iter_fields(ast):
            if isinstance(child, AST):
                child = [(None, child)]
            elif isinstance(child, list):
                child = list(enumerate(child))
            else:
                continue

            for idx, a in child:
                if isinstance(a, exclude) or not isinstance(a, AST):
                    continue

                if random() < level_chance:
                    cat = astcat(a, ast)
                    allowed_cats = astcat_allowed_replacements(cat)
                    repltype = choice(('fstin', 'fstout', 'ast'))

                    if repltype == 'fstout':
                        repl, _ = self.master_parts.getrnd(allowed_cats)

                        if repl and can_replace_ast(a, ast, field, repl.a, repl.parent.a, repl.pfield.name):
                            astfield(field, idx).set(ast, a := copy_ast(a))

                            continue

                    # if repltype == 'ast':
                    elif repltype == 'ast':
                        repl, _ = self.master_parts.getrnd(allowed_cats)

                        if repl and can_replace_ast(a, ast, field, repl.a, repl.parent.a, repl.pfield.name):
                            astfield(field, idx).set(ast, a := copy_ast(a))

                    # # if repltype == 'fstin':
                    # elif repltype == 'fstin':
                    #     repl, _ = self.parts.getrnd(allowed_cats)

                    #     if (repl and can_replace_ast(a, ast, field, repl.a, repl.parent.a, repl.pfield.name) and
                    #         # not last_fst.root.child_path(last_fst, as_str=True).startswith(repl.root.child_path(repl, as_str=True))
                    #         repl.a not in parents
                    #     ):
                    #         self.parts.remove_all(repl)
                    #         astfield(field, idx).set(ast, repl.a)

                    #         # print('...', repl.root.child_path(repl, True))

                    #         repl.DO_NOT_ENTER = True

                    #         self.walk_fst(repl, next_level, parents)

                    #         continue

                self.walk_ast(a, next_level, parents)

    def walk_fst(self, fst: FST, level: int = 0, parents: list[AST] = []):
        """Walk in-tree FST and replace random nodes."""

        next_level = level + 1
        level_chance = self.LEVEL_CHANCE[min(len(self.LEVEL_CHANCE) - 1, level)]
        exclude = self.master_parts.exclude
        ast = fst.a
        parents = parents + [ast]

        for f in fst.walk(self_=False, recurse=False):
            if isinstance(f.a, exclude):
                continue

            if random() < level_chance:
                cat = fstcat(f)
                allowed_cats = astcat_allowed_replacements(cat)
                repltype = choice(('fstin', 'fstout', 'ast'))

                if repltype == 'fstout':
                    repl, _ = self.master_parts.getrnd(allowed_cats)

                    if repl and can_replace(f, repl):
                        f.pfield.set(ast, repl.copy().a)

                        continue

                # if repltype == 'ast':
                elif repltype == 'ast':
                    repl, _ = self.master_parts.getrnd(allowed_cats)

                    # if isinstance(repl.a, Is):  # DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG!
                    #     print('\n...', f.parent.src)  # DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG!
                    #     print('\n...', repl.parent.src)  # DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG!

                    if repl and can_replace(f, repl):
                        f.pfield.set(ast, copy_ast(repl.a))

                        # if self.debug:
                        #     self.walk_ast(a, next_level, parents)

                        continue

                # if repltype == 'fstin':
                elif repltype == 'fstin':
                    repl, _ = self.parts.getrnd(allowed_cats)

                    if (repl
                        and can_replace(f, repl)
                        and repl.a not in parents
                        #    not f.root.child_path(f, as_str=True).startswith(repl.root.child_path(repl, as_str=True))
                    ):
                        self.parts.remove_all(repl)
                        f.pfield.set(ast, repl.a)

            if not getattr(f, 'DO_NOT_ENTER', False):
                self.walk_fst(f, next_level, parents)

    # def walk_fst(self, fst: FST, level: int = 0):
    #     """Walk in-tree FST and replace random nodes."""

    #     next_level   = level + 1
    #     level_chance = self.LEVEL_CHANCE[min(len(self.LEVEL_CHANCE) - 1, level)]
    #     exclude      = self.master_parts.exclude
    #     ast          = fst.a

    #     for f in fst.walk(True, self_=False, recurse=False):
    #         if isinstance(f.a, exclude):
    #             continue

    #         if random() < level_chance:
    #             cat          = fstcat(f)
    #             allowed_cats = astcat_allowed_replacements(cat)
    #             repltype     = choice(('fstin', 'fstout', 'ast'))

    #             if repltype == 'fstout':
    #                 repl, _ = self.master_parts.getrnd(allowed_cats)

    #                 if repl and can_replace(f, repl):
    #                     f.pfield.set(ast, repl.copy().a)

    #                     continue

    #             elif repltype == 'ast':
    #                 repl, _ = self.master_parts.getrnd(allowed_cats)

    #                 if repl and can_replace(f, repl):
    #                     f.pfield.set(ast, a := copy_ast(repl.a))

    #                     # self.walk_ast(a, next_level)

    #                     continue

    #             # if repltype == 'fstin':
    #             elif repltype == 'fstin':
    #                 repl, _ = self.parts.getrnd(allowed_cats)

    #                 if (repl and can_replace(f, repl) and
    #                     not f.root.child_path(f, as_str=True).startswith(repl.root.child_path(repl, as_str=True))
    #                 ):
    #                     f.pfield.set(ast, repl.a)

    #         self.walk_fst(f, next_level)

    def fuzz_one(self, fst, fnm) -> bool:
        # self.master_parts = FSTParts(fst)
        # master            = fst.copy()

        real_master = fst.copy()

        if self.debug:
            FST.put = debug_put
            FST.put_slice = debug_put_slice

        try:
            # print(fst.src)
            # print('-'*120)
            for count in range(self.batch or 100):
                if self.check_abort():
                    break

                self.master_parts = FSTParts(real_master)
                master = real_master.copy()

                # if count:
                #     self.do_reseed()  # allow first one to be with specified seed, otherwise reseed to have seed to this round to be able to get back to it quicker
                self.do_reseed()  # always start with new seed so that can return to it immediately

                try:
                    if not (count % 5):
                        sys.stdout.write('.'); sys.stdout.flush()

                    self.parts = self.master_parts.copy()

                    fst = master.copy()
                    # self.parts = FSTParts(fst)
                    mark = fst.mark()

                    self.walk_fst(fst)

                    with FST.options(docstr=False):
                        fst = fst.reconcile(mark)

                    try:
                        fst.verify()

                    except SyntaxError:
                        # if not self.debug:
                        #     raise
                        raise

                except BaseException as exc:  # Exception as exc:
                    if not ignorable_exc(exc):
                        print()

                        if self.verbose:
                            print(fst.src)

                        raise

                # break  # DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG!

        finally:
            print()

            FST.put = old_FST_put
            FST.put_slice = old_FST_put_slice

        if self.verbose:
            print(fst.src)


class ReconcileSame(Fuzzy):
    """Alternates nodes as AST and in-tree FST, sometimes ends with out-of-tree FST."""

    name = 'reconcile_same'
    forever = False

    def walk_ast(self, ast: AST, fst: FST):
        for f in fst.walk(self_=False, recurse=False):  # will have same nodes as ast
            if isinstance(a := f.a, (expr_context, mod)):#, FormattedValue, Interpolation)):
                continue

            if random() < 0.1:
                f.pfield.set(ast, copy_ast(a))

            else:
                f.pfield.set(ast, a)

                if 1:#not isinstance(a, (JoinedStr, TemplateStr)):
                    self.walk_fst(f)

    def walk_fst(self, fst: FST):
        ast = fst.a

        for f in fst.walk(self_=False, recurse=False):
            if isinstance(a := f.a, (expr_context, mod)):#, FormattedValue, Interpolation)):
                continue

            if random() < 0.1:
                f.pfield.set(ast, copy_ast(a))

            else:
                f.pfield.set(ast, a := copy_ast(a))

                if 1:#not isinstance(a, (JoinedStr, TemplateStr)):
                    self.walk_ast(a, f)

    def fuzz_one(self, fst, fnm) -> bool:
        try:
            mark = fst.mark()

            self.walk_fst(fst)

            with FST.options(docstr=False):
                fst = fst.reconcile(mark)

            fst.verify()

        finally:
            if self.verbose:
                print(fst.src)


class SliceStmtish(Fuzzy):
    """Test moving around stmtishs, empty bodies, fstview, stmtish FST identity stability and unmarking deleted FSTs."""

    name = 'slice_stmtish'
    forever = True

    @staticmethod
    def do_move(stmtish: FST, stmtish_container: fstview, dst_container: fstview):
        if random() < 0.5:  # single element stmtish to container
            s = stmtish.cut()

            if len(dst_container):
                r = choice(dst_container).replace(s)
            else:
                r = dst_container.append(s)[0]

            assert s is stmtish
            assert r is stmtish

        else:  # slice stmtish to dst_container
            len_stmtish = len(stmtish_container)
            len_dst = len(dst_container)

            if random() < 0.5 or not dst_container:
                to_start = to_stop = randint(0, len_dst)
            else:
                to_start = randint(0, len_dst - 1)
                to_stop = randint(to_start + 1, len_dst)

            from_start = randint(0, len_stmtish - 1)
            from_stop = randint(from_start + 1, len_stmtish)
            from_start_ = from_start if from_start >= len_stmtish or randint(0, 1) else from_start - len_stmtish  # randomly change index to negative (referring to same location)
            from_stop_ = from_stop if from_stop >= len_stmtish or randint(0, 1) else from_stop - len_stmtish

            fs = stmtish_container[from_start_ : from_stop_]

            org_fsts = list(fs)
            cut = fs.cut()
            cut_body = cut.body if isinstance(cut.a, Module) else cut.handlers if isinstance(cut.a, _ExceptHandlers) else cut.cases

            assert all(f is g for f, g in zip(cut_body, org_fsts))

            to_start_ = to_start if to_start >= len_dst or randint(0, 1) else to_start - len_dst  # randomly change index to negative (referring to same location)
            to_stop_ = to_stop if to_stop >= len_dst or randint(0, 1) else to_stop - len_dst

            dst_container[to_start_ : to_stop_] = cut

            assert all(f is g for f, g in zip(dst_container[to_start : to_start + (from_stop - from_start)], org_fsts))

    def fuzz_one(self, fst, fnm) -> bool:
        with FST.options(norm_self=False):  # so we can cut bodies down to empty
            containers = {
                stmt:          FST.new().body,
                ExceptHandler: FST('try: pass\nfinally: pass').handlers,
                match_case:    FST('match _:\n  case _: pass').cases,
            }

            del containers[match_case][0]

            if not PYLT11:
                containers[excepthandler] = c = FST('try: pass\nexcept* Exception: pass').handlers

                del c[0]

            # containers = {
            #     stmt:          FST('i', 'exec').body,
            #     ExceptHandler: FST('try: pass\nexcept Exception: pass\nfinally: pass').handlers,
            #     match_case:    FST('match _:\n  case _: pass').cases,
            # }

            # if not PYLT11:
            #     containers[excepthandler] = c = FST('try: pass\nexcept* Exception: pass').handlers

            stmtishs = []

            for f in fst.walk(True):
                if fstcat(f) in containers:
                    stmtishs.append(f)

            if not stmtishs:
                return

            if self.debug:
                FST.put = debug_put
                FST.put_slice = debug_put_slice

            try:
                for count in range(self.batch or 1000):
                    if self.check_abort():
                        break

                    try:
                        if not (count % 20):
                            sys.stdout.write('.'); sys.stdout.flush()

                        for _ in range(10):
                            while stmtishs:
                                if (stmtish := stmtishs[i := randint(0, len(stmtishs) - 1)]).a is None:  # if removed completely then forget about it
                                    del stmtishs[i]
                                else:
                                    break

                            else:
                                raise RuntimeError('this should not happen')

                            container = containers[cat := fstcat(stmtish)]
                            container = containers[cat] = getattr(container.base, container.field)  # remake the container because its size can be wrong

                            if any(p is container.base for p in stmtish.parents()):
                                continue

                            break

                        else:
                            continue

                        stmtish_container = getattr(stmtish.parent, stmtish.pfield.name)

                        # from source to temporary container

                        self.do_move(stmtish, stmtish_container, container)

                        # refresh containers because of node operations

                        stmtish_container = getattr(stmtish_container.base, stmtish_container.field)
                        container = getattr(container.base, container.field)

                        # from temporary container to source

                        self.do_move(choice(container), container, stmtish_container)

                        if self.verify:
                            fst.verify()

                    except Exception:
                        print()

                        if self.verbose:
                            print(fst.src)

                        raise

                fst.verify()

            finally:
                print()

                FST.put = old_FST_put
                FST.put_slice = old_FST_put_slice

                if self.verbose:
                    print(fst.src)


class SliceExprish(Fuzzy):
    """Test moving around exprish slices, empty bodies, exprish FST identity stability and unmarking deleted FSTs."""

    name = 'slice_exprish'
    forever = True

    class Bucket(NamedTuple):
        field:       str | None  # None means Dict or MatchMapping
        slice_field: str | None  # None means same as field
        min_script:  int
        min_tmp:     int
        one:         bool
        fst:         FST

    @staticmethod
    def rnd_trivia():
        return (
            choice(('none', 'block', 'all')) + choice(('', '', '', '', '-', '+', '-', '+', '-1', '-2', '-3', '+1', '+2', '+3')),
            choice(('none', 'block', 'all', 'line')) + choice(('', '', '', '', '-', '+', '-', '+', '-1', '-2', '-3', '+1', '+2', '+3')),
        )

    def transfer(
        self,
        dir: str,
        cat: str,
        field: str | None,
        slice_field: str | None,
        src: FST,
        dst: FST,
        min_src: int,
        min_dst: int,
        one: bool,
    ):
        if slice_field is None:
            slice_field = field

        if is_compare := isinstance(src.a, Compare):
            src_len = len(src_body := getattr(src.a, 'comparators')) + 1
            dst_len = len(dst_body := getattr(dst.a, 'comparators')) + 1
        else:
            src_len = len(src_body := getattr(src.a, field or 'keys'))
            dst_len = len(dst_body := getattr(dst.a, field or 'keys'))

        src_start = randint(0, src_len)
        src_stop = randint(src_start, src_len)
        dst_start = randint(0, dst_len)
        dst_stop = randint(dst_start, dst_len)
        src_trivia = SliceExprish.rnd_trivia()
        dst_trivia = SliceExprish.rnd_trivia()

        while dst_len - (dst_stop - dst_start) + (src_stop - src_start) < min_dst:  # make sure to respect min_dst (we assume src has enough elements to reach min_dst if necessary)
            if dst_stop != dst_start:  # first reduce size being overwritten if possible
                dst_start += (i := randint(0, 1))
                dst_stop -= i ^ 1

            else:  # can't reduce any more
                if src_start and (randint(0, 1) or src_stop == src_len):
                    src_start -= 1
                elif src_stop < src_len:
                    src_stop += 1
                else:
                    break  # can actually get here because of initially lower length containers than we allow

        if is_compare:  # can't get empty slice from or insert into Compare
            if src_stop == src_start:
                src_stop += not src_start
                src_start -= bool(src_start)

            if dst_stop == dst_start:
                dst_stop += not dst_start
                dst_start -= bool(dst_start)

        len_src_slice = src_stop - src_start
        cut = False if src_len - len_src_slice < min_src else bool(randint(0, 1))

        if one:
            if src_stop - src_start == 0 and isinstance(src.a, Set):
                one = False
            else:
                one = False if dst_len - (dst_stop - dst_start) + 1 < min_dst or len_src_slice < min_src else bool(randint(0, 1))  # len_src_slice < min_src because of potentially invalid slice ASTs

        if self.debug:  # isinstance(src.a, Set) or isinstance(dst.a, Set):
            print(f'\x08... {dir} {cat = }, {cut = }, {one = }')
            print(f'    {src_start = }, {src_stop = }, {src_len = }, {min_src = }, {src_trivia = }')
            print(f'    {dst_start = }, {dst_stop = }, {dst_len = }, {min_dst = }, {dst_trivia = }')
            print('   PRE SRC: ', src, src.src)
            print('   PRE DST: ', dst, dst.src)
            # if src.parent: print('   PRE SRC PARENT: ', src.parent, src.parent.src)
            # if dst.parent: print('   PRE DST PARENT: ', dst.parent, dst.parent.src)
            # src.dump()

        if not is_compare:
            src_elts = src_body[src_start : src_stop]

            if not field:  # Dict or MatchMapping
                src_elts.extend(getattr(src.a, 'values' if isinstance(src.a, Dict) else 'patterns')[src_start : src_stop])

        src_rest = bool(getattr(src.a, 'rest', False))  # because MatchSequence includes rest in virtual field but we don't deal with it
        src_start_ = src_start if src_start >= src_len or randint(0, 1) else src_start - src_len - src_rest  # randomly change index to negative (referring to same location)
        src_stop_ = src_stop if src_stop >= src_len or randint(0, 1) else src_stop - src_len - src_rest

        slice = src.get_slice(src_start_, src_stop_, field=field, cut=cut, trivia=src_trivia)

        if not is_compare:
            slice_elts = getattr(slice.a, slice_field or 'keys')[:]

            if not slice_field:  # Dict or MatchMapping
                slice_elts.extend(getattr(slice.a, 'values' if isinstance(src.a, Dict) else 'patterns'))

            if cut and not isinstance(src.a, (Global, Nonlocal)):
                assert all(a is b for a, b in zip(src_elts, slice_elts))  # identity check

        if self.debug:  # isinstance(src.a, Set) or isinstance(dst.a, Set):
            print('   SLICE:   ', slice, slice.src)

        dst_rest = bool(getattr(dst.a, 'rest', False))  # because MatchSequence includes rest in virtual field but we don't deal with it
        dst_start_ = dst_start if dst_start >= dst_len or randint(0, 1) else dst_start - dst_len - dst_rest  # randomly change index to negative (referring to same location)
        dst_stop_ = dst_stop if dst_stop >= dst_len or randint(0, 1) else dst_stop - dst_len - dst_rest

        dst.put_slice(slice, dst_start_, dst_stop_, field=field, one=one, trivia=dst_trivia)

        if not is_compare:
            if not one:
                dst_elts = dst_body[dst_start : dst_start + (src_stop - src_start)]

                if not field:  # Dict or MatchMapping
                    dst_elts.extend(getattr(dst.a, 'values' if isinstance(dst.a, Dict) else 'patterns')[dst_start : dst_start + (src_stop - src_start)])

                if not isinstance(src.a, (Global, Nonlocal)):
                    assert all(a is b for a, b in zip(dst_elts, slice_elts))  # identity check

        if self.debug:  # isinstance(src.a, Set) or isinstance(dst.a, Set):
            print('   POST SRC:', src, src.src)
            print('   POST DST:', dst, dst.src)
            # if src.parent: print('   POST SRC PARENT: ', src.parent, src.parent.src)
            # if dst.parent: print('   POST DST PARENT: ', dst.parent, dst.parent.src)
            # dst.dump()
            print()

    @staticmethod
    def cat(fst: FST) -> tuple[str | type[AST], ...]:
        ast = fst.a

        if isinstance(getattr(ast, 'ctx', None), (Store, Del)):
            return ('target',) if isinstance(ast, (Tuple, List)) else ()
        if isinstance(ast, Tuple):
            return ('slice' if fst._has_Slice() else 'seq'),
        if isinstance(ast, (List, Set)):
            return ('seq',)

        if isinstance(ast, (Delete, Assign, Import, Global, Nonlocal,
                            Dict, MatchSequence, MatchMapping, MatchOr,
                            With, AsyncWith,
                            )):
            return (ast.__class__,)

        if isinstance(ast, TypeAlias):
            return ('type_params',)

        if isinstance(ast, (FunctionDef, AsyncFunctionDef)):
            return ('type_params', 'decorator_list')

        if isinstance(ast, ClassDef):
            if not ast.keywords:
                return ('type_params', 'decorator_list', 'ClassDef_bases')
            else:
                return ('type_params', 'decorator_list')

        if isinstance(ast, Compare):
            return (Compare,)

        if isinstance(ast, BoolOp):
            return ('and' if isinstance(ast.op, And) else 'or',)

        if isinstance(ast, (ListComp, SetComp, DictComp, GeneratorExp)):
            return ('generators',)

        if isinstance(ast, Call):
            if ((ast.keywords or len(ast.args) != 1 or not isinstance(ast.args[0], GeneratorExp))  # safe `GeneratorExp`, two possible slices - `args` and `keywords`?
                and not ast.keywords
            ):
                return ('Call_args',)
            else:
                return ()

        if isinstance(ast, ImportFrom):
            return (ImportFrom,) if ast.module != '__future__' and ast.names[0].name != '*' else ()

        if isinstance(ast, comprehension):
            return (comprehension,)

        return ()

    def fuzz_one(self, fst, fnm) -> bool:
        buckets = {
            'slice':          self.Bucket('elts', None, 1, 1, False, FST('tmp[1,]').slice,),  # 1 because of "a[b, c]", must always leave at least 1 element so it doesn't get parentheses
            'target':         self.Bucket('elts', None, 0, 0, True, FST('()')),
            'seq':            self.Bucket('elts', None, 1, 0, True, FST('()')),  # 1 because of Set
            Dict:             self.Bucket(None, None, 0, 0, False, FST('{}')),
            Delete:           self.Bucket('targets', 'elts', 1, 0, True, FST('del a')),
            Assign:           self.Bucket('targets', None, 1, 0, False, FST('', '_Assign_targets')),
            'decorator_list': self.Bucket('decorator_list', None, 0, 0, False, FST('', '_decorator_list')),
            With:             (wbucket := self.Bucket('items', None, 1, 0, False, FST('', '_withitems'))),
            AsyncWith:        wbucket,
            Import:           self.Bucket('names', None, 1, 0, False, FST('', '_aliases')),
            ImportFrom:       self.Bucket('names', None, 1, 0, False, FST('', '_aliases')),
            Global:           (glbucket := self.Bucket('names', 'elts', 1, 1, False, FST('global z'))),
            Nonlocal:         glbucket,
            'ClassDef_bases': self.Bucket('bases', 'elts', 0, 0, True, FST('class tmp(): pass')),
            'and':            self.Bucket('values', None, 2, 2, True, FST('a and b', BoolOp)),  # one=True in this can cause very large expressions and slow performance if testing just this, lower batch size to 100-200
            'or':             self.Bucket('values', None, 2, 2, True, FST('a or b', BoolOp)),  # one=True in this can cause very large expressions and slow performance if testing just this, lower batch size to 100-200
            Compare:          self.Bucket(None, None, 2, 2, True, FST('a < b', Compare)),  # one=True in this can cause very large expressions and slow performance if testing just this, lower batch size to 100-200
            'Call_args':      self.Bucket('args', 'elts', 0, 0, True, FST('call()')),
            'generators':     self.Bucket('generators', None, 1, 0, False, FST('', '_comprehensions')),
            comprehension:    self.Bucket('ifs', None, 0, 0, False, FST('', '_comprehension_ifs')),
            MatchSequence:    self.Bucket('patterns', None, 0, 0, True, FST('[]', pattern)),
            MatchMapping:     self.Bucket(None, None, 0, 0, False, FST('{}', pattern)),
            MatchOr:          self.Bucket('patterns', None, 2, 2, True, FST('(a | b)', pattern)),
        }

        if PYGE12:
            buckets.update({
                'type_params': self.Bucket('type_params', None, 0, 0, False, FST('', '_type_params')),
            })

        exprishs = []  # [('cat', FST), ...]

        for f in (gen := fst.walk(True)):
            if PYLT12 and isinstance(f.a, JoinedStr):
                gen.send(False)

                continue

            if cat := self.cat(f):
                for c in cat:
                    if c in buckets:
                        exprishs.append((c, f))

        if not exprishs:
            return

        try:
            for count in range(self.batch or 1000):
                if self.check_abort():
                    break

                try:
                    if not (count % 20):
                        sys.stdout.write('.'); sys.stdout.flush()

                    for _ in range(10):
                        while exprishs:
                            cat, exprish = exprishs[i := randint(0, len(exprishs) - 1)]

                            if exprish.a is None:  # if removed completely then forget about it
                                del exprishs[i]
                            else:
                                break

                        else:
                            raise RuntimeError('should not get here')

                        bucket = buckets[cat]

                        # if exprish.root is bucket.fst:
                        if exprish.root is not fst:
                            continue

                        break

                    else:
                        continue

                    with FST.options(norm=False):
                        self.transfer('src > bkt:', cat, bucket.field, bucket.slice_field, exprish, bucket.fst, bucket.min_script, bucket.min_tmp, bucket.one)

                        if self.verify:
                            fst.verify()

                        self.transfer('src < bkt:', cat, bucket.field, bucket.slice_field, bucket.fst, exprish, bucket.min_tmp, bucket.min_script, bucket.one)

                        if self.verify:
                            fst.verify()

                    # input('Waiting...')

                except Exception:
                    print()

                    if self.verbose:
                        print(fst.src)

                    raise

            print()

            if self.verbose:
                print(fst.src)

            fst.verify()

        finally:
            pass


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
    parser.add_argument('-R', '--fuzz-rnd', action='store_true', default=False,
                        help='select all randomized fuzzies to run')
    parser.add_argument('-D', '--fuzz-det', action='store_true', default=False,
                        help='select all deterministic fuzzies to run')
    parser.add_argument('-b', '--batch', type=int, default=None,
                        help='batch size override')
    parser.add_argument('-g', '--debug', default=False, action='store_true',
                        help='debug mode, print info, do more debug stuff')
    parser.add_argument('-l', '--loop', type=int, default=None,
                        help='number of times to loop, default forever')
    parser.add_argument('-c', '--linecont', default=False, action='store_true',
                        help='add line continuations to source')
    parser.add_argument('-C', '--linecont-rnd', default=False, action='store_true',
                        help='randomly add line continuations to source')
    parser.add_argument('-e', '--semicolon', default=False, action='store_true',
                        help='add semicolons to source')
    parser.add_argument('-E', '--semicolon-rnd', default=False, action='store_true',
                        help='randomly add semicolons to source')
    parser.add_argument('-m', '--minify', default=False, action='store_true',
                        help='minify all source')
    parser.add_argument('-M', '--minify-rnd', default=False, action='store_true',
                        help='randomly minify source')
    parser.add_argument('-w', '--whitespace', default=False, action='store_true',
                        help='add trailing whitespace to source')
    parser.add_argument('-W', '--whitespace-rnd', default=False, action='store_true',
                        help='randomly add trailing whitespace to source')
    parser.add_argument('-n', '--unicode', default=False, action='store_true',
                        help='add unicode to source')
    parser.add_argument('-N', '--unicode-rnd', default=False, action='store_true',
                        help='randomly add unicode to source')
    parser.add_argument('-s', '--seed', type=int, default=None,
                        help='random seed (set once per file)')
    parser.add_argument('-S', '--reseed', type=int, default=None,
                        help='random reseed (may be set multiple times per file)')
    parser.add_argument('-u', '--shuffle', default=False, action='store_true',
                        help='shuffle files on each loop')
    parser.add_argument('-U', '--shuffle-fuzz', default=False, action='store_true',
                        help='shuffle fuzzies to run')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='verbose output, where applicable')
    parser.add_argument('-y', '--verify', default=False, action='store_true',
                        help='do more verifies, usually after each step (slower)')

    args = parser.parse_args()

    print(f'{args = }')

    fuzz = dict.fromkeys(sum((f.replace(',', ' ').split() for f in args.fuzz), start=[])
                         if args.fuzz or args.fuzz_rnd or args.fuzz_det else
                         (f for f in FUZZIES if f != 'dump'))

    if args.fuzz_rnd:
        for n, f in FUZZIES.items():
            if f.forever:
                fuzz[n] = f

    if args.fuzz_det:
        for n, f in FUZZIES.items():
            if not f.forever and f is not Dump:
                fuzz[n] = f

    print(f'fuzz = {", ".join(fuzz)}')

    if any((fuzzy := f) not in FUZZIES for f in fuzz):
        raise ValueError(f'invalid fuzzy: {fuzzy}')

    fuzzies = []
    args = vars(args)

    for f in fuzz:
        fuzzies.append(FUZZIES[f](args))

    for _ in range(l) if (l := args['loop']) else repeat(None):
        if args['shuffle_fuzz']:
            shuffle(fuzzies)

        for f in fuzzies[:]:
            print(f'Running: {f.name}')

            try:
                if not f.fuzz():
                    print(f'{f.name} has finished and will not be run again.')

                    fuzzies.remove(f)

            except Exception:
                print(f'Was running: {f.name}')

                raise

            finally:
                sys.stdout.flush()

        if not fuzzies:
            print('Done...')

            break


if __name__ == '__main__':
    main()
