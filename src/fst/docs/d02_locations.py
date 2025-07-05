r"""
# Node locations in the source code

To be able to execute the examples, import this.
```py
>>> from fst import *
```

## `loc` and `bloc`

Almost all `FST` nodes have a location attribute pointing to where they exist in the source code.

```py
>>> f = FST('''
... @decorator
... def func(x):
...     return x + 1
... '''.strip())

>>> f.dump()
FunctionDef - ROOT 1,0..2,16
  .name 'func'
  .args arguments - 1,9..1,10
    .args[1]
    0] arg - 1,9..1,10
      .arg 'x'
  .body[1]
  0] Return - 2,4..2,16
    .value BinOp - 2,11..2,16
      .left Name 'x' Load - 2,11..2,12
      .op Add - 2,13..2,14
      .right Constant 1 - 2,15..2,16
  .decorator_list[1]
  0] Name 'decorator' Load - 0,1..0,10
```

These are accessed via the `.loc` attribute.

```py
>>> f.loc
fstloc(1, 0, 2, 16)

>>> f.args.loc
fstloc(1, 9, 1, 10)

>>> f.body[0].loc
fstloc(2, 4, 2, 16)

>>> f.body[0].value.op.loc
fstloc(2, 13, 2, 14)
```

Or the individual location elements can be gotten directly.

```py
>>> f.args.ln
1

>>> f.args.col
9

>>> f.args.end_ln
1

>>> f.args.end_col
10
```

If you noticed above, nodes which normally don't have locations in `AST` nodes have their locations computed and added
in `FST` nodes, like `arguments` or `operators`.

```py
>>> hasattr(f.a.args, 'lineno')
False

>>> f.args.loc
fstloc(1, 9, 1, 10)

>>> hasattr(f.a.body[0].value.op, 'lineno')
False

>>> f.body[0].value.op.loc
fstloc(2, 13, 2, 14)
```

The only `AST` nodes which don't get locations like this are:

1. Empty `arguments` nodes since that could allow zero-length locations which are a pain to deal with.
2. `boolop` nodes because a single `AST` may correspond to multiple locations in the expression.
3. `expr_context` nodes which don't have parsable source.

Other nodes that normally don't have locations like `comprehension`, `withitem`, `match_case` and other operators all
have locations computed for them by `FST`.

```py
>>> FST('[i for i in j]').generators[0].loc
fstloc(0, 3, 0, 13)

>>> FST('with a as b: pass').items[0].loc
fstloc(0, 5, 0, 11)

>>> FST('''
... match a:
...    case a as b:
...        pass
... '''.strip()).cases[0].loc
fstloc(1, 3, 2, 11)

>>> FST('a += b').op.loc
fstloc(0, 2, 0, 4)
```

There is also a `bloc` location attribute, which is equal to the `loc` location in all cases except when there are
preceding decorators, in which case the location starts at the first decorator. There are corresponding `bln`, `bcol`,
`bend_ln` and `bend_col` attributes, though the last three currently just equal the normal `loc` elements. This may
change in the future (include trailing comments maybe).

```py
>>> f = FST('''
... @decorator
... def func(x):
...     return x + 1
... '''.strip())

>>> print(f.src)
@decorator
def func(x):
    return x + 1

>>> f.loc
fstloc(1, 0, 2, 16)

>>> f.bloc
fstloc(0, 0, 2, 16)

>>> f.ln, f.col, f.end_ln, f.end_col
(1, 0, 2, 16)

>>> f.bln, f.bcol, f.bend_ln, f.bend_col
(0, 0, 2, 16)
```

## Line and column coordinates

`FST` node locations differ from `AST` node locations in that the line numbers start at 0 instead of 1 and the column
offsets are in characters and not encoded bytes.

```py
>>> f = FST('абвгд')
>>> f.loc
fstloc(0, 0, 0, 5)

>>> f.a.lineno, f.a.col_offset, f.a.end_lineno, f.a.end_col_offset
(1, 0, 1, 10)
```

`FST` nodes also provide the same `lineno` ... `end_col_offset` attributes as `AST` nodes and return the locations in
`AST` coordinates (1 based line, column byte offsets) as a convenience for all nodes, providing these to `AST` nodes
which don't normally have them.

```py
>>> f = FST('[i for i in j]').generators[0]
>>> f.lineno, f.col_offset, f.end_lineno, f.end_col_offset
(1, 3, 1, 13)

>>> hasattr(f.a, 'lineno')
False
```

You can check if a location comes from an `AST` node or if is computed by `FST`.

```py
>>> f.has_own_loc
False

>>> FST('a = b').has_own_loc
True
```

The location of the entire source (accessible from any node in the tree), always starts at (0, 0) and ends at the end of
the source code.

```py
>>> f = FST('''
... @decorator
... def func(x):
...     return x + 1
... '''.strip())

>>> f.whole_loc
fstloc(0, 0, 2, 16)

>>> f.body[0].value.op.whole_loc
fstloc(0, 0, 2, 16)

>>> len(f.lines), len(f.lines[-1])
(3, 16)
```

## Search by location

You can search for a node by location. This is done by either searching for a node in a given location.

```py
>>> f = FST('''
... if a < b:
...     print(a)
... '''.strip())

>>> # find node matching or in this location
>>> f.find_in_loc(0, 3, 0, 8).src
'a < b'

>>> # doesn't have to be exact, this function returns whole first node found in location
>>> f.find_in_loc(0, 1, 1, 6).src
'a < b'

>>> # returns only entire nodes in location
>>> f.find_in_loc(0, 4, 0, 6).src
'<'
```

Or searching for a node which contains a location.

```py
>>> # or you can search for a node entirely CONTAINING THE LOCATION
>>> f.find_loc(0, 4, 0, 6).src
'a < b'

>>> # will return nodes matching the location EXACTLY by default
>>> f.find_loc(0, 3, 0, 8).src
'a < b'

>>> # but that can be disabled
>>> f.find_loc(0, 3, 0, 8, exact=False).src
'if a < b:\n    print(a)'
```
"""
