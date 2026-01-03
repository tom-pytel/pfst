# Overview

This module exists in order to facilitate quick and easy high level editing of Python source in the form of an `AST` tree while preserving formatting. It is meant to allow you to change Python code functionality while not having to deal with the minutiae of:

- Operator precedence and parentheses
- Indentation and line continuations
- Commas, semicolons, and tuple edge cases
- Comments and docstrings
- Various Python version–specific syntax quirks
- Lots more...

See [Example Recipes](https://tom-pytel.github.io/pfst/fst/docs/d12_examples.html) for more in-depth examples.

```py
>>> import fst

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

# Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)

# Install

From PyPI:

    pip install pfst

From GitHub using pip:

    pip install git+https://github.com/tom-pytel/pfst.git

From GitHub, after cloning for development:

    pip install -e .[dev]

# Example

```py
>>> from fst import *

>>> def type_annotations_to_type_comments(src: str) -> str:
...     fst_ = FST(src, 'exec')  # same as "fst.parse(src).f"
...
...     # walk the whole tree but only yield AnnAssign nodes
...     for f in fst_.walk(AnnAssign):
...         # if just an annotation then skip it, alternatively could
...         # clean and store for later addition to __init__() assign in class
...         if not f.value:
...             continue
...
...         # own_src() gives us the original source exactly as written but dedented
...         target = f.target.own_src()
...         value = f.value.own_src()
...
...         # we use ast_src() for the annotation to get a clean type string
...         annotation = f.annotation.ast_src()
...
...         # preserve any existing end-of-line comment
...         comment = ' # ' + comment if (comment := f.get_line_comment()) else ''
...
...         # reconstruct the line using the PEP 484 type comment style
...         new_src = f'{target} = {value}  # type: {annotation}{comment}'
...
...         # replace the node, trivia=False preserves any leading comments
...         f.replace(new_src, trivia=False)
...
...     return fst_.src  # same as fst.unparse(fst_.a)
```

```py
>>> src = """
... def func():
...     normal = assign
...
...     x: int = 1
...
...     # y is such and such
...     y: float = 2.0  # more about y
...     # y was a good variable...
...
...     structure: tuple[
...         tuple[int, int],  # extraneous comment
...         dict[str, Any],   # could break stuff
...     ] | None = None# blah
...
...     call(  # invalid but just for demonstration purposes
...         some_arg,          # non-extraneous comment
...         some_kw=kw_value,  # will not break stuff
...     )[start : stop].attr: SomeClass = getthis()
... """.strip()
```

```py
>>> print(src)
def func():
    normal = assign

    x: int = 1

    # y is such and such
    y: float = 2.0  # more about y
    # y was a good variable...

    structure: tuple[
        tuple[int, int],  # extraneous comment
        dict[str, Any],   # could break stuff
    ] | None = None# blah

    call(  # invalid but just for demonstration purposes
        some_arg,          # non-extraneous comment
        some_kw=kw_value,  # will not break stuff
    )[start : stop].attr: SomeClass = getthis()
```

```py
>>> print(type_annotations_to_type_comments(src))
def func():
    normal = assign

    x = 1  # type: int

    # y is such and such
    y = 2.0  # type: float # more about y
    # y was a good variable...

    structure = None  # type: tuple[tuple[int, int], dict[str, Any]] | None # blah

    call(  # invalid but just for demonstration purposes
        some_arg,          # non-extraneous comment
        some_kw=kw_value,  # will not break stuff
    )[start : stop].attr = getthis()  # type: SomeClass
```

# Robust

Crazy syntax is handled correctly (which is a main goal of this module).

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

# Misc

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
<<FunctionDef ROOT 0,0..1,8>.body [<Pass 1,4..1,8>]>

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

Higher level slice abstraction.

```py
>>> print(FST('a < b < c')._all[:2].copy().src)
a < b

>>> f = FST('case {1: a, 2: b, **c}: pass', 'match_case')

>>> print(f.pattern.get_slice(1, 3, '_all').src)
{2: b, **c}
```

For more examples see the documentation in `docs/`, or if you're feeling particularly masochistic have a look at the
tests in the `tests/` directory.

## TODO

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

* More and better coercion, tree search, indentation of multiline sequences should be better, decide between primitive
or node ops on primitive fields, different source encodings, code cleanups, API additions for real-world use,
optimization, testing, bughunting, etc...

* Finish `reconcile()`. Proper comment handling, locations and deduplication. Make it use all slice operations to
preserve more formatting.


## Trivia

The "F" in FST stands for "Fun".
