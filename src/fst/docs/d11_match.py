r"""
# Match, search and substitute

To be able to execute the examples, import this.

>>> import ast, re
>>> from fst import *
>>> from fst.match import *


## Match

`fst` provides a way to do structural pattern matching against `FST` or `AST` trees. The elements of the pattern are
special `M_Pattern` classes provided by `fst`, or just normal `AST` classes, though type checkers might complain about
that usage.

Apart from that, the other differences between using internal `M` patterns and actual `AST` for the patterns nodes is
that for the `M` patterns you only specify the fields you need whereas for `AST` nodes you may have to explicitly
provide fields you don't need as wildcards. Patterns also allow you to match virtual fields.

Here is an example of a structural match to give you an idea, it will be explained below. This pattern will match any
`logger.info()` call which has a `cid` keyword argument:

>>> pat = MCall(
...    MAttribute('logger', 'info'),
...    keywords=[..., Mkeyword('cid'), ...],
... )

>>> bool(pat.match(FST('logger.info(a, cid=1)')))
True

>>> bool(pat.match(FST('logger.info(a)')))
False

>>> bool(pat.match(FST('not_logger.info(a, cid=1)')))
False

You can also match against pure `AST` trees. The `match()` function only matches against the node you give it and in the
following examples the `ast.parse()` function returns `Module` so we do the `.body[0].value` to get the proper node to
match against.

>>> bool(pat.match(ast.parse('( logger ).info(a, cid=1)').body[0].value))
True

>>> bool(pat.match(ast.parse('logger.not_info(a, cid=1)').body[0].value))
False

The `match()` function can be called on the `M_Pattern` object as shown above, or on the `FST` node.

>>> bool(FST('(logger\n.\ninfo)(a, cid=1)').match(pat))
True

>>> bool(FST('logger.info(a)').match(pat))
False

If matching from the `FST` node then you can use a pure or mixed `AST` pattern (instead of `MAST`).

>>> ast_pat = Call(
...    Attribute('logger', 'info'),
...    ...,
...    [..., keyword('cid', ...), ...],
... )

>>> bool(FST('logger.info(a, cid=1)').match(ast_pat))
True

>>> bool(FST('logger.info(a)').match(ast_pat))
False

You will note the use of the `Ellipsis` in the examples above. The `...` serves as a wildcard in pattern matching. It
matches anything in place of an actual field value and serves as a zero-or-more `*`-style wildcard when used inside a
list field, as shown above in the `keywords` field.


## String and regex patterns

In the example above the `Attribute` node was created with a proper expected string attribute of `'info'` but also with
a string parameter for the `value` field, which should normally be a node. The `fst` matcher allows strings (or regexes)
in place of nodes and in this case it will attempt to match the string against the source code of the node.

In case of an `FST` node this source is gotten directly from the stored source for the tree so a normal `str` has to
match exactly.

>>> bool(MAssign(..., 'a + b').match(FST('v = a + b')))
True

>>> bool(MAssign(..., 'a + b').match(FST('v = a+b')))
False

You can use a regex in this case.

>>> bool(MAssign(..., re.compile(r'a\s*\+\s*b')).match(FST('v = a+b')))
True

>>> bool(MAssign(..., re.compile(r'a\s*\+\s*b')).match(FST('v = (a   + \nb)')))
True

In the case of an `FST` node, the source matched against is the location of the node **WITHOUT** any enclosing grouping
parentheses. You can also match source against `AST` nodes, in which case they are internally unparsed for the check.

>>> bool(MAssign(..., 'a + b').match(ast.parse('v = a+b').body[0]))
True

The `a + b` with the spaces matches the `a+b` in the `AST` because when unparsed it winds up as `a + b`, which is the
standard `AST` spacing.

Strings and regexes can also be used for fields which are normally strings themselves (instead of nodes), in which case
it they are not matched against source but rather against the actual values of the fields.

>>> bool(MImportFrom(module='mod.submod').match(FST('from mod.submod import *')))
True

>>> bool(MImportFrom(module='mod.submod')
...      .match(FST('from mod\\\n.\\\nsubmod import *')))
True

>>> bool(MImportFrom(module=re.compile(r'.*\.submod'))
...      .match(FST('from mod . submod import *')))
True

These are matched by value even in list fields of strings.

>>> bool(FST('global a, b, c, d, e, f').match(Global([..., 'c', ...])))
True


## Primitives

Apart from strings, other primitives are also matched directly.

>>> bool(MImportFrom(level=2).match(FST('from . import *')))
False

>>> bool(MImportFrom(level=2).match(FST('from .. import *')))
True

>>> bool(MImportFrom(level=2).match(FST('from ... import *')))
False

For `Constant` nodes any kind of primitive can be matched.

>>> bool(MConstant(b'a').match(FST('b"a"', Constant)))
True

>>> bool(MConstant(b'a').match(FST('b"b"', Constant)))
False

>>> bool(MConstant(b'a').match(FST('123j', Constant)))
False

Primitive matching matches **EXACT** types, this means `False != 0 != 0.0 != 0j`.

>>> bool(MConstant(0).match(FST('0.0', Constant)))
False

>>> bool(MConstant(False).match(FST('0', Constant)))
False

>>> bool(MConstant(0j).match(FST('0j', Constant)))
True

And finally, when matching a `Constant.value`, the `...` is not considered a wildcard as it is a valid concrete value
which can show up inside of a `Constant`.

>>> bool(MConstant(...).match(FST('...', Constant)))
True

>>> bool(MConstant(...).match(FST('"string"', Constant)))
False

If you wish to use the wildcard to match a `Constant.value` then either use the wildcard one level above if that is
possible, or better just enclose it with the `M()` functional pattern.

>>> bool(MConstant(M(...)).match(FST('"string"', Constant)))
True


## Type match

This is a simple match which takes an `AST` type or the corresponding `MAST` type and if the target node is of this type
then the match is successful.

>>> bool(FST('a + b').match(BinOp))
True

>>> bool(FST('a + b').match(MBinOp))
True

>>> bool(FST('a + b').match(Call))
False

Its not really meant to be used like this but rather deeper in pattern structures.

>>> bool(MList([..., MCall, ...]).match(FST('[a, b, c, d]')))
False

>>> bool(MList([..., MCall, ...]).match(FST('[a, b(), c, d]')))
True


## `M_Match` object and tags

So far we have been showing the return of `match()` as a `bool`, but the actual return value is either `None` for no match
or an `M_Match` object for a successful match. This match object may contain tagged values which we have not show yet,
so here they are

>>> m = MConstant(M(tag=..., static_tag=True)).match(FST('"string"', Constant))

>>> m
<M_Match {'tag': 'string', 'static_tag': True}>

The `tag` tag in this case gets the value of the thing actually matched, and the `static_tag` is just a fixed-value
tag which is added on a successful match, meant to be used for flags.

These tags can be accessed via the `.tags` attribute on the match object.

>>> m.tags
mappingproxy({'tag': 'string', 'static_tag': True})

Or as a convenience directly as attributes, though this should be used with care as the tags may be shadowed by existing
attributes on the `M_Match` node.

>>> m.tag
'string'

>>> m.static_tag
True

One benefit is quick existence checking as nonexistent tags do not raise `AttributeError` but rather return a falsey
object.

>>> bool(m.nonexistent_tag)
False

Otherwise you can just access the `.tags` dictionary directly or call `.get()` on the match object just like you would
on the `.tags` dictionary.

>>> m.tags['tag']
'string'

>>> m.get('nonexistent', 'NOOO!')
'NOOO!'


## `M()` pattern

The `M()` pattern was used above to attach tags to a successful match. This class can tag whatever is matched directly
below it in the eventual `M_Match` object if the given `M` object lives in a successful match path, as well as any
number of static value tags. The target matched may or MAY NOT be added to tags depending on if the match pattern is
specified with a keyword or as an anonymous positional argument.

This will match successfully, but as there is no tag provided for the match the target matched will not be added to
tags.

>>> M(Constant).match(FST('1'))
<M_Match {}>

If you want the tag then you need to specify the pattern with a keyword.

>>> M(tag=Constant).match(FST('1'))
<M_Match {'tag': <Constant ROOT 0,0..0,1>}>

Regardless of tags, the top level match is always available on the match object as the `.matched` attribute.

>>> M(Constant).match(FST('1')).matched
<Constant ROOT 0,0..0,1>

The reason the tags exist however is to be able to match arbitrary nodes below the top level `matched` match.

>>> m = MBinOp(..., ..., M(tag=...)).match(FST('a + b'))

>>> m
<M_Match {'tag': <Name 0,4..0,5>}>

>>> m.matched
<BinOp ROOT 0,0..0,5>

The `M()` pattern can be nested to any level and propagates successful match tags from below.

>>> MBinOp(M(left=...), ..., M(tag1=M(tag2=...))).match(FST('a + b'))
<M_Match {'left': <Name 0,0..0,1>, 'tag2': <Name 0,4..0,5>, 'tag1': <Name 0,4..0,5>}>


## `MNOT()` pattern

This is similar to the `M()` pattern except that it succeeds and adds tags when the child does **NOT** match.

>>> MConstant(M(tag=1, static=True)).match(FST('1'))
<M_Match {'tag': 1, 'static': True}>

>>> print(MConstant(MNOT(tag=1, static=True)).match(FST('1')))
None

>>> MConstant(MNOT(tag=1, static=True)).match(FST('2'))
<M_Match {'tag': 2, 'static': True}>

>>> print(MConstant(M(tag=1, static=True)).match(FST('2')))
None

This tag does not ever propagate any tags from below as it only succeeds when the child patterns fail, and fails if
they succeed. So it can only ever propagate its own tags upwards when there are no tags from children due to failed
match.


## `MOR()` and `MAND()` patterns

These should be self-explanatory. The only thing that needs to be clarified is their tag usage. They both take one or
more patterns and the patterns can be all anonymous, all tagged or a combination.

>>> MOR('a', tag_b='b', tag_c='c').match(FST('a'))
<M_Match {}>

>>> MOR('a', tag_b='b', tag_c='c').match(FST('b'))
<M_Match {'tag_b': <Name ROOT 0,0..0,1>}>

>>> MOR('a', tag_b='b', tag_c='c').match(FST('c'))
<M_Match {'tag_c': <Name ROOT 0,0..0,1>}>

They do not provide static tags as each keyword element is another pattern to match. If you want to add static tags to
a successful or match the either add an `M()` to the whole `MOR`.

>>> M(MOR('a', tag_b='b', tag_c='c'), static=True).match(FST('c'))
<M_Match {'tag_c': <Name ROOT 0,0..0,1>, 'static': True}>

Or to the individual elements.

>>> MOR(M('a', static=False), tag_b='b', tag_c=M('c', static=True)).match(FST('a'))
<M_Match {'static': False}>

>>> MOR(M('a', static=False), tag_b='b', tag_c=M('c', static=True)).match(FST('b'))
<M_Match {'tag_b': <Name ROOT 0,0..0,1>}>

>>> MOR(M('a', static=False), tag_b='b', tag_c=M('c', static=True)).match(FST('c'))
<M_Match {'static': True, 'tag_c': <Name ROOT 0,0..0,1>}>


## `MANY()` pattern

This is essentially a combination of type check with arbitrary fields. It takes an iterable of `AST` and `MAST` types
and an arbitrarly list of keyword-specified fields to match.

The following will match any statement node which can and does have a docstring

>>> pat = MANY(
...     (FunctionDef, AsyncFunctionDef, ClassDef),
...     body=[Expr(Constant(str)), ...],
... )

>>> pat.match(FST('def f(): "docstring"; pass'))
<M_Match {}>

>>> pat.match(FST('def f(): pass; pass'))

>>> pat.match(FST('def f(): pass; "NOTdocstring"'))

>>> pat.match(FST('class cls: "docstring"; pass'))
<M_Match {}>

>>> pat.match(FST('if 1: "NOTdocstring"; pass'))

Multiple fields to match.

>>> pat = MANY(
...     (FunctionDef, AsyncFunctionDef),
...     body=[Expr(Constant(str)), ...],
...     returns='int',
... )

>>> pat.match(FST('def f() -> int: "docstring"; pass'))
<M_Match {}>

>>> pat.match(FST('def f() -> str: "docstring"; pass'))

>>> pat.match(FST('class cls: "docstring"; pass'))

Note that the `returns` field which don't exist on the `ClassDef` node does not cause an error, just a match fail.

Like `MOR` and `MAND`, this pattern doesn't allow static tags. It doesn't even allow match tags as all keywords are used
to specify fields.


## `MRE()` pattern

You can use `re.Pattern` directly but that doesn't allow the use of `re.search()` and loses the `re.Match` object. The
`MRE()` pattern allows all this.

>>> f = FST('some_hidden_gem')

>>> f.match(re.compile(r'.*hidden.*'))
<M_Match {}>

>>> f.match(MRE(m=r'.*hidden.*'))
<M_Match {'m': <re.Match object; span=(0, 15), match='some_hidden_gem'>}>

But even that doesn't give you the position of the hidden gem.

>>> f.match(MRE(m=r'hidden', search=True))
<M_Match {'m': <re.Match object; span=(5, 11), match='hidden'>}>


## `MCB()` pattern

This is a powerful pattern that allows you to inject arbitrary logic at any point of the pattern match. The `CB` stands
for callback and the function you provide is called to determine whether there is a match or not, and can even provide
the return value to add as a tag (if a tag is being added).

>>> pat = MConstant(MCB(lambda x: 2 < x < 8))

>>> pat.match(FST('1'))

>>> pat.match(FST('3'))
<M_Match {}>

>>> pat.match(FST('7'))
<M_Match {}>

>>> pat.match(FST('10'))

Check for only parenthesized tuples.

>>> pat = MCB(FST.is_parenthesized_tuple)

>>> pat.match(FST('x, y, z'))

>>> pat.match(FST('(x, y, z)'))
<M_Match {}>

>>> pat.match(FST('[x, y, z]'))

This node also allows matched target and static tags.

>>> pat = MCB(tgt=FST.is_parenthesized_tuple, static=True)

>>> pat.match(FST('(x, y, z)'))
<M_Match {'tgt': <Tuple ROOT 0,0..0,9>, 'static': True}>

If you pass `tag_call_ret=True` then whatever is returned from the callback function is used for the match tag.

>>> pat = M(node=Name(MCB(upper=str.upper, tag_call_ret=True)))

>>> pat.match(FST('a.b'))

>>> pat.match(FST('some_name'))
<M_Match {'upper': 'SOME_NAME', 'node': <Name ROOT 0,0..0,9>}>

The type of node passed to the callback depends on the type of tree that match is called on.

>>> pat = MCB(lambda n: print(type(n)))

>>> pat.match(FST('name').a)
<class 'ast.Name'>

>>> pat.match(FST('name'))
<class 'fst.fst.FST'>










## `AST` as pattern or target


"""
