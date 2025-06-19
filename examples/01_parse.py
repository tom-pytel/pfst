#!/usr/bin/env python

import ast
from fst import *


# Drop-in `ast.parse()` replacement gives normal AST.

a = fst.parse('if 1: i = 2  # comment')
print(ast.dump(a, indent=2))

# Module(
#   body=[
#     If(
#       test=Constant(value=1),
#       body=[
#         Assign(
#           targets=[
#             Name(id='i', ctx=Store())],
#           value=Constant(value=2))],
#       orelse=[])],
#   type_ignores=[])


# But it has an `FST` node at `.f`, we can `dump()` it to stdout.

a.f.dump()

# Module - ROOT 0,0..0,11
#   .body[1]
#   0] If - 0,0..0,11
#     .test Constant 1 - 0,3..0,4
#     .body[1]
#     0] Assign - 0,6..0,11
#       .targets[1]
#       0] Name 'i' Store - 0,6..0,7
#       .value Constant 2 - 0,10..0,11


# Every `AST` node in the tree has one.

a.body[0].body[0].f.dump()

# Assign - 0,6..0,11
#   .targets[1]
#   0] Name 'i' Store - 0,6..0,7
#   .value Constant 2 - 0,10..0,11


# Drop-in `ast.unparse()` replacement outputs with formatting.

print(fst.unparse(a))

# if 1: i = 2  # comment


# You can also just access the source.

print(a.f.src)

# if 1: i = 2  # comment


# Simpler way, gives the same thing.

FST('if 1: i = 2', 'exec').dump()

# Module - ROOT 0,0..0,11
#   .body[1]
#   0] If - 0,0..0,11
#     .test Constant 1 - 0,3..0,4
#     .body[1]
#     0] Assign - 0,6..0,11
#       .targets[1]
#       0] Name 'i' Store - 0,6..0,7
#       .value Constant 2 - 0,10..0,11


# Note the 'exec' mode specifier above, it can be one of the other `ast.parse()` mode specifiers.

FST('if 1: i = 2', 'single').dump()

# Interactive - ROOT 0,0..0,11
#   .body[1]
#   0] If - 0,0..0,11
#     .test Constant 1 - 0,3..0,4
#     .body[1]
#     0] Assign - 0,6..0,11
#       .targets[1]
#       0] Name 'i' Store - 0,6..0,7
#       .value Constant 2 - 0,10..0,11


# Or 'eval'.

print(FST('i + j', 'eval'))

# <Expression ROOT 0,0..0,5>


# If you leave it out then FST gives the minimal valid node, a single statement
# in this case.

print(FST('if 1: i = 2'))

# <If ROOT 0,0..0,11>


# Or just an expression.

print(FST('i + j'))

# <BinOp ROOT 0,0..0,5>


# Including things that are not parsable by themselves.

print(FST('except Exception: pass'))

# <ExceptHandler ROOT 0,0..0,22>


# Or a comprehension.

print(FST('for a in b if a'))

# <comprehension ROOT 0,0..0,15>


# You can tell it what you are looking for.

print(FST('a:b', Slice))

# <Slice ROOT 0,0..0,3>


# Because maybe it is normally shadowed by something more common.

print(FST('a:b'))

# <AnnAssign ROOT 0,0..0,3>


# In some cases you must tell it what you want (valid empty arguments).

print(FST('', arguments))

# <arguments ROOT>


# Have you ever dreamed of being able to parse the `+` operator? Well now you
# can!

print(FST('+'))

# <Add ROOT 0,0..0,1>


# There are some special modes, like 'callarg', which allow parsing some things
# which are not normally parsable in their normal context. The below is not
# normally parsable in an expression context as it is special syntax for `Call`
# vararg arguments. For a full list of parse modes see the documentation for
# `fst.shared.Mode`.

print(FST('*a or b', 'callarg'))

# <Starred ROOT 0,0..0,7>


# You can also pass `AST` nodes, which are then unparsed and reparsed (because
# otherwise we couldn't trust the location information in them). When used like
# this, the `AST` nodes are not consumed.

print(FST(Assign(targets=[Name(id='x')], value=Constant(value=1))).src)

# x = 1


# This also allows normally non-parsable nodes.

FST(Slice(lower=Name(id='a'), upper=Name(id='b'), step=Name(id='c'))).dump()

# Slice - ROOT 0,0..0,5
#   .lower Name 'a' Load - 0,0..0,1
#   .upper Name 'b' Load - 0,2..0,3
#   .step Name 'c' Load - 0,4..0,5


# The FST(...) syntax used above is just a shortcut for the functions
# `FST.fromsrc()` and `FST.fromast()`.

FST.fromsrc('i = 1').dump()

# Module - ROOT 0,0..0,5
#   .body[1]
#   0] Assign - 0,0..0,5
#     .targets[1]
#     0] Name 'i' Store - 0,0..0,1
#     .value Constant 1 - 0,4..0,5


# Except that `fromsrc()` defaults to `mode='exec'` instead of minimal node.

FST.fromsrc('i = 1', 'valid').dump()

# Assign - ROOT 0,0..0,5
#   .targets[1]
#   0] Name 'i' Store - 0,0..0,1
#   .value Constant 1 - 0,4..0,5


# `FST.fromast()` works the same as when passing an `AST` to `FST()`.

FST.fromast(Slice(lower=Name(id='a'), upper=Name(id='b'), step=Name(id='c'))).dump()

# Slice - ROOT 0,0..0,5
#   .lower Name 'a' Load - 0,0..0,1
#   .upper Name 'b' Load - 0,2..0,3
#   .step Name 'c' Load - 0,4..0,5
