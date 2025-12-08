r"""
# Node locations in the source code

To be able to execute the examples, import this.

>>> from fst import *

## `.loc`

Almost all `FST` nodes have a location attribute pointing to where they exist in the source code.

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

These are accessed via the `.loc` attribute (`fst.fst.FST.loc`).

>>> f.loc
fstloc(1, 0, 2, 16)

>>> f.args.loc
fstloc(1, 9, 1, 10)

>>> f.body[0].loc
fstloc(2, 4, 2, 16)

>>> f.body[0].value.op.loc
fstloc(2, 13, 2, 14)

Or the individual location elements can be gotten directly.

>>> f.args.ln
1

>>> f.args.col
9

>>> f.args.end_ln
1

>>> f.args.end_col
10

If you noticed above, nodes which normally don't have locations in `AST` nodes have their locations computed and added
in `FST` nodes, like `arguments` or `operators`.

>>> hasattr(f.a.args, 'lineno')
False

>>> f.args.loc
fstloc(1, 9, 1, 10)

>>> hasattr(f.a.body[0].value.op, 'lineno')
False

>>> f.body[0].value.op.loc
fstloc(2, 13, 2, 14)

The only `AST` nodes which don't get locations like this are:

1. Empty `arguments` nodes since that could allow zero-length locations which are a pain to deal with.
2. `boolop` nodes because a single `AST` may correspond to multiple locations in the expression.
3. `expr_context` nodes which don't have parsable source.

Other nodes that normally don't have locations like `comprehension`, `withitem`, `match_case` and other operators all
have locations computed for them by `FST`.

>>> FST('[i for i in j]').generators[0].loc
fstloc(0, 3, 0, 13)

>>> FST('with a as b: pass').items[0].loc
fstloc(0, 5, 0, 11)

>>> FST('''
... match a:
...     case a as b:
...         pass
... '''.strip()).cases[0].loc
fstloc(1, 4, 2, 12)

>>> FST('a += b').op.loc
fstloc(0, 2, 0, 3)

Yes that last one is an `AugAssign` and the location of the operator is only the `+` and does not include the `=` to
stay consistent with the operators in `BinOp`. For the record, the `=` in a normal `Assign` doesn't get its own operator
anyway so is essentially just a trivia delimiter.

## `.bloc`

There is also a `.bloc` bounding location attribute (`fst.fst.FST.bloc`). This is equal to the `loc` location in all
cases except when there are preceding decorators or a trailing line comment on the last child of a block statement, in
which case those are included in the bounding location. There are corresponding `bln`, `bcol`, `bend_ln` and `bend_col`
attributes.

>>> f = FST('''
... @decorator
... def func(x):
...     return x + 1  # comment
... '''.strip())

>>> print(f.src)
@decorator
def func(x):
    return x + 1  # comment

>>> f.loc
fstloc(1, 0, 2, 16)

>>> f.bloc
fstloc(0, 0, 2, 27)

>>> f.ln, f.col, f.end_ln, f.end_col
(1, 0, 2, 16)

>>> f.bln, f.bcol, f.bend_ln, f.bend_col
(0, 0, 2, 27)

Note that the trailing comment of a non-block statement is not included in the `.bloc`.

>>> FST('i = j  # comment', 'exec').body[0].bloc
fstloc(0, 0, 0, 5)

## Line and column coordinates

`FST` node locations differ from `AST` node locations in that the line numbers start at 0 instead of 1 and the column
offsets are in characters and not encoded bytes.

>>> f = FST('абвгд')

>>> f.loc
fstloc(0, 0, 0, 5)

>>> f.a.lineno, f.a.col_offset, f.a.end_lineno, f.a.end_col_offset
(1, 0, 1, 10)

`FST` nodes also provide the same `lineno` ... `end_col_offset` attributes as `AST` nodes and return the locations in
`AST` coordinates (1 based line, column byte offsets) as a convenience for all nodes, providing these to `AST` nodes
which don't normally have them.

>>> f = FST('[i for i in j]').generators[0]

>>> f.lineno, f.col_offset, f.end_lineno, f.end_col_offset
(1, 3, 1, 13)

>>> hasattr(f.a, 'lineno')
False

You can check if a location comes from an `AST` node or if is computed by `FST`.

>>> f.has_own_loc
False

>>> FST('a = b').has_own_loc
True

The location of the entire source (accessible from any node in the tree), always starts at (0, 0) and ends at the end of
the source code.

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

## Search by location

Lets use this.

>>> f = FST('''
... if a < b:
...     pass
... '''.strip())

>>> f.dump()
If - ROOT 0,0..1,8
  .test Compare - 0,3..0,8
    .left Name 'a' Load - 0,3..0,4
    .ops[1]
     0] Lt - 0,5..0,6
    .comparators[1]
     0] Name 'b' Load - 0,7..0,8
  .body[1]
   0] Pass - 1,4..1,8

You can search for a node by location. This is done by either searching for a node contained **INSIDE** a given location
using `fst.fst.FST.find_in_loc()`.

>>> f.find_in_loc(0, 3, 0, 8)  # "a < b"
<Compare 0,3..0,8>

It doesn't have to be exact, this function returns whole first node found in location.

>>> f.find_in_loc(0, 1, 1, 6)  # "f a < b:\n    pa"
<Compare 0,3..0,8>

Returns only entire nodes in location.

>>> f.find_in_loc(0, 4, 0, 8)  # " < b"
<Lt 0,5..0,6>

Or you can search for a node which **CONTAINS** a location using `fst.fst.FST.find_loc_in()`.

>>> f.find_loc_in(0, 4, 0, 6)  # " <"
<Compare 0,3..0,8>

Will include nodes which match the location **EXACTLY** by default.

>>> f.find_loc_in(0, 3, 0, 8)  # "a < b"
<Compare 0,3..0,8>

But that can be disabled.

>>> f.find_loc_in(0, 3, 0, 8, allow_exact=False)  # "a < b"
<If ROOT 0,0..1,8>

The `fst.fst.FST.find_loc()` method combines the two efficiently to find a node which is either the first one completely
contained in the location, or if no candidate for that then one which contains the location. This is a more general
"find me the node associated with this location" function.

Here it gives the containing node while `find_in_loc()` gives nothing at all.

>>> loc = (0, 4, 0, 5)  # empty space in Compare

>>> print(f'{f.find_loc(*loc) = }\n{f.find_loc_in(*loc) = }\n{f.find_in_loc(*loc) = }')
f.find_loc(*loc) = <Compare 0,3..0,8>
f.find_loc_in(*loc) = <Compare 0,3..0,8>
f.find_in_loc(*loc) = None

And here it gives the contained `Name` same as `find_in_loc()`, which gave nothing above but gives the "closest" node
here.

>>> loc = (0, 3, 0, 5)  # first element of Compare including whitespace after "a "

>>> print(f'{f.find_loc(*loc) = }\n{f.find_loc_in(*loc) = }\n{f.find_in_loc(*loc) = }')
f.find_loc(*loc) = <Name 0,3..0,4>
f.find_loc_in(*loc) = <Compare 0,3..0,8>
f.find_in_loc(*loc) = <Name 0,3..0,4>
"""
