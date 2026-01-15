# pfst

[![PyPI version](https://img.shields.io/badge/pypi-0.2.5-orange.svg)](https://pypi.org/project/pfst/)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

**High-level Python AST/CST manipulation that preserves formatting**

## Overview

This module exists in order to facilitate quick and easy high level editing of Python source in the form of an `AST` tree while preserving formatting. It is meant to allow you to change Python code functionality while not having to deal with the details of:

- Operator precedence and parentheses
- Indentation and line continuations
- Commas, semicolons, and tuple edge cases
- Comments and docstrings
- Various Python version–specific syntax quirks
- Lots more...

See [Example Recipes](https://tom-pytel.github.io/pfst/fst/docs/d12_examples.html) for more in-depth examples.

```py
>>> import fst  # pip install pfst, import fst

>>> ext_ast = fst.parse('if a: b = c, d  # comment')

>>> ext_ast.f.body[0].body[0].value.elts[1:1] = 'u,\nv  # blah'

>>> print(fst.unparse(ext_ast))
if a: b = (c, u,
          v,  # blah
          d)  # comment
```

The tree is just normal `AST` with metadata.

```py
>>> import ast

>>> print(ast.unparse(ext_ast))
if a:
    b = (c, u, v, d)
```

`fst` works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute (type-safe accessor `castf()` provided) which keep extra structure information, the original source, and provide the interface to format-preserving operations. Each operation through `fst` is a simultaneous edit of the `AST` tree and the source code and those are kept synchronized so that the current source will always parse to the current tree.

Formatting, comments, and layout are preserved unless explicitly modified. Unparsing is lossless by default and performs no implicit normalization or stylistic rewriting.

## Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)

## Install

From PyPI:

    pip install pfst

From GitHub using pip:

    pip install git+https://github.com/tom-pytel/pfst.git

From GitHub, after cloning for development:

    pip install -e .[dev]

## Example

A simple example to give an idea of the API. This function adds a `correlation_id=CID` keyword argument to all
`logger.info()` calls, but only if it's not already there.

```py
>>> import fst

>>> def inject_logging_metadata(src: str) -> str:
...     tree = fst.FST(src)
...
...     for call in tree.walk(fst.Call):
...         if (call.func.is_Attribute
...             and call.func.attr == 'info'
...             and call.func.value.is_Name
...             and call.func.value.id == 'logger'
...             and not any(kw.arg == 'correlation_id' for kw in call.keywords)
...         ):
...             call.append('correlation_id=CID', trivia=(False, False))
...
...     return tree.src
```

```py
>>> src = """
... logger.info('Hello world...')  # ok
... logger.info('Already have id', correlation_id=other_cid)  # ok
... logger.info()  # yes, no logger message, too bad
...
... class cls:
...     def method(self, thing, extra):
...         if not thing:
...             (logger).info(  # just checking
...                 f'not a {thing}',  # this is fine
...                 extra=extra,       # also this
...             )
... """.strip()
```

```py
>>> print(inject_logging_metadata(src))
logger.info('Hello world...', correlation_id=CID)  # ok
logger.info('Already have id', correlation_id=other_cid)  # ok
logger.info(correlation_id=CID)  # yes, no logger message, too bad

class cls:
    def method(self, thing, extra):
        if not thing:
            (logger).info(  # just checking
                f'not a {thing}',  # this is fine
                extra=extra, correlation_id=CID # also this
            )
```

## Robust

Crazy syntax is handled correctly, which is a main goal of this module.

```py
>>> f = FST(r'''
... if True:
...     @decorator1
...
...     # pre-comment
...     \
...  @ \
...   ( decorator2 )(
...         a,
...     ) \
...     # post-comment
...
...     @ \
...     decorator3()
...
...     def func(): weird\
...  ; \
... \
... stuff()
...
...     pass
... '''.strip())
```

```py
>>> deco = f.body[0].get_slice(1, 2, 'decorator_list', cut=True, trivia=('all-', 'all-'))
```

```py
>>> deco.dump('stmt+')
0: # pre-comment
1: \
2: @ \
3: ( decorator2 )(
4:     a,
5: ) \
6: # post-comment
_decorator_list - ROOT 0,0..8,0
  .decorator_list[1]
   0] Call - 4,0..6,1
     .func Name 'decorator2' Load - 4,2..4,12
     .args[1]
      0] Name 'a' Load - 5,4..5,5
```

```py
>>> print(f.src)
if True:
    @decorator1
    @ \
    decorator3()

    def func(): weird\
 ; \
\
stuff()

    pass
```

```py
>>> f.body[0].put_slice(deco, 'decorator_list', trivia=('all-', 'all-'))

>>> f.body[0].body[0] = 'good'
```

```py
>>> print(f.src)
if True:
    # pre-comment
    \
    @ \
    ( decorator2 )(
        a,
    ) \
    # post-comment
    def func():
        good
        stuff()

    pass
```

## Misc

Familiar AST structure and pythonic operations.

```py
>>> f = FST('if a:\n    print(a)')

>>> f.test = 'not a'

>>> f.body.append('return a')

>>> print(f.src)
if not a:
    print(a)
    return a
```

Higher level slice abstraction.

```py
>>> print(FST('a < b < c')._all[:2].copy().src)
a < b

>>> f = FST('case {1: a, 2: b, **c}: pass')  # match_case

>>> print(f.pattern.get_slice(1, 3, '_all').src)
{2: b, **c}

>>> f = FST('call(a, b=c, *d)')

>>> f._args[1:] = '*e, f=g, **h'

>>> print(f.src)
call(a, *e, f=g, **h)
```

Can zero out bodies.

```py
>>> f = FST("""
... def func(self):  # comment
...     pass
... """.strip())

>>> del f.body

>>> print(f.src)
def func(self):  # comment

>>> f.body.append('pass')

>>> print(f.src)
def func(self):  # comment
    pass
```

Including non-statement.

```py
>>> f = FST('[i for i in j]')

>>> del f.generators

>>> print(f.src)
[i]

>>> f.generators.extend('for a in b for i in a')

>>> print(f.src)
[i for a in b for i in a]
```

Use native AST.

```py
>>> f = FST('i = [a, b, c]')

>>> f.targets[0] = Subscript(Name('j'), Slice(Name('x'), Name('y')))

>>> f.value.elts[1:] = Name('d')

>>> print(f.src)
j[x:y] = [a, d]
```

Don't have to care if docstrings are there or not.

```py
>>> f = FST("""
... class cls:
...     \"\"\"docstring\"\"\"
...     a = b
...     c = d
... """.strip())

>>> f._body[0] = 'pass'

>>> print(f.src)
class cls:
    """docstring"""
    pass
    c = d
```

Traversal is in syntactic order.

```py
>>> list(f.src for f in FST('call(a, x=1, *b, y=2, **c)').walk())[1:]
['call', 'a', 'x=1', '1', '*b', 'b', 'y=2', '2', '**c', 'c']

>>> list(f.src for f in FST('def func[T](a=1, b=2) -> int: pass').walk())[1:]
['T', 'a=1, b=2', 'a', '1', 'b', '2', 'int', 'pass']

>>> list(f.src for f in FST('{key1: val1, **val2, key3: val3}').walk())[1:]
['key1', 'val1', 'val2', 'key3', 'val3']
```

Locations are zero based in character units, not bytes. Most nodes have a location, including ones which don't in `AST`
nodes.

```py
>>> FST('蟒=Æ+д').dump()
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name '蟒' Store - 0,0..0,1
  .value BinOp - 0,2..0,5
    .left Name 'Æ' Load - 0,2..0,3
    .op Add - 0,3..0,4
    .right Name 'д' Load - 0,4..0,5
```

For more examples see the documentation in `docs/`, or if you're feeling particularly masochistic have a look at the
tests in the `tests/` directory.

### TODO

This module is not finished but functional enough that it can be useful.

* Put one to:
  * `FormattedValue.conversion`
  * `FormattedValue.format_spec`
  * `Interpolation.str`
  * `Interpolation.conversion`
  * `Interpolation.format_spec`

* Prescribed get / put slice from / to:
  * `arguments._all`
  * `MatchClass.patterns`
  * `MatchClass.patterns+kwd_attrs:kwd_patterns`
  * `JoinedStr.values`
  * `TemplateStr.values`

* Improve comment and whitespace handling, especially allow get / put comments in single element non-statement
operations where it may apply (where comment may belong to expression instead of statement). Allow specify insert line.
Direct comment manipulation functions.

* Indentation of multiline sequences should be better, tree search / match, decide between primitive or node ops on
primitive fields, different source encodings, code cleanups, API additions for real-world use, optimization, testing,
bughunting, etc...

* Finish `reconcile()`. Proper comment handling, locations and deduplication. Make it use all slice operations to
preserve more formatting.


### Trivia

The "F" in FST stands for "Fun".
