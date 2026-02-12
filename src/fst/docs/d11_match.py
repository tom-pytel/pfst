r"""
# Match, search and substitute

To be able to execute the examples, import this.

>>> import ast, re
>>> from fst import *
>>> from fst.match import *


# Match

`fst` provides a way to do structural pattern matching against `FST` or `AST` trees. The elements of the pattern are
special `M_Pattern` classes provided by `fst`, or just normal `AST` classes, though type checkers might complain about
that usage.

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
list field, as shown in the `keywords` field.


## String and regex patterns

In the example above the `Attribute` node was created with a proper expected string attribute of `'info'` but also with
a string parameter for the `value` field, which should normally be a node. The `fst` matcher allows strings (or regexes)
in place of nodes and in this case it will attempt to match the string against the source code of the node.

In case of an `FST` node this source is gotten directly from the stored source from the tree. A normal `str` has to
match exactly.

>>> bool(MAssign(..., 'a + b').match(FST('v = a + b')))
True

>>> bool(MAssign(..., 'a + b').match(FST('v = a+b')))
False

You can use a regex for more flexible matching.

>>> bool(MAssign(..., re.compile(r'a\s*\+\s*b')).match(FST('v = a+b')))
True

>>> bool(MAssign(..., re.compile(r'a\s*\+\s*b')).match(FST('v = (a   + \nb)')))
True

In the case of an `FST` node, the source matched against comes from the location of the node **WITHOUT** any enclosing
grouping parentheses. You can also match source against `AST` nodes, in which case they are internally unparsed for the
check.

>>> bool(MAssign(..., 'a + b').match(ast.parse('v = a+b').body[0]))
True

The `a + b` with the spaces matches the `a+b` in the `AST` because when unparsed it winds up as `a + b`, which is the
standard `AST` spacing.

Strings and regexes can also be used for fields which are normally strings themselves (instead of nodes), in which case
it they are not matched against source but rather against the actual values of the field.

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
possible, or just enclose the value field with the `M()` functional pattern.

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


## `FSTMatch` object and tags

So far we have been showing the return of `match()` as a `bool`, but the actual return value is either `None` for no match
or an `FSTMatch` object for a successful match. This match object may contain tagged values which we have not show yet,
so here they are

>>> m = MConstant(M(tag=..., static_tag=True)).match(FST('"string"', Constant))

>>> m
<FSTMatch <Constant ROOT 0,0..0,8> {'tag': 'string', 'static_tag': True}>

The `tag` tag in this case gets the value of the thing actually matched, and the `static_tag` is just a fixed-value
tag which is added on a successful match, meant to be used for flags.

These tags can be accessed via the `.tags` attribute on the match object.

>>> m.tags
mappingproxy({'tag': 'string', 'static_tag': True})

Or as a convenience directly as attributes. You do not have to worry about tags shadowing real `FSTMatch` attributes
as tags which would do that are not allowed and raise an exception if you try to create a pattern with them.

>>> m.tag
'string'

>>> m.static_tag
True

>>> M(tags=...)
Traceback (most recent call last):
...
ValueError: invalid tag 'tags' shadows match class attribute

Attribute tag access allows quick existence checking as nonexistent tags do not raise `AttributeError` but rather return
a falsey object.

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
below it in the eventual `FSTMatch` object if the given `M` object lives in a successful match path, as well as any
number of static value tags. The target matched may or MAY NOT be added to tags depending on if the match pattern is
specified with a keyword or as an anonymous positional argument.

This will match successfully, but as there is no tag provided for the match the target matched will not be added to
tags.

>>> M(Constant).match(FST('1'))
<FSTMatch <Constant ROOT 0,0..0,1>>

If you want the tag then you need to specify the pattern with a keyword.

>>> M(tag=Constant).match(FST('1'))
<FSTMatch <Constant ROOT 0,0..0,1> {'tag': <Constant ROOT 0,0..0,1>}>

Regardless of tags, the top level match is always available on the match object as the `.matched` attribute.

>>> M(Constant).match(FST('1')).matched
<Constant ROOT 0,0..0,1>

The reason the tags exist however is to be able to match arbitrary nodes below the top level `matched` match.

>>> m = MBinOp(..., ..., M(tag=...)).match(FST('a + b'))

>>> m
<FSTMatch <BinOp ROOT 0,0..0,5> {'tag': <Name 0,4..0,5>}>

>>> m.matched
<BinOp ROOT 0,0..0,5>

The `M()` pattern can be nested to any level and propagates successful match tags from below.

>>> MBinOp(M(left=...), ..., M(tag1=M(tag2=...))).match(FST('a + b'))
<FSTMatch <BinOp ROOT 0,0..0,5> {'left': <Name 0,0..0,1>, 'tag2': <Name 0,4..0,5>, 'tag1': <Name 0,4..0,5>}>

This pattern can go almost anywhere and tag nodes, primitives, `None` and even entire list fields.

>>> MAST(names=M(l=[...])).match(FST('global a, b, c'))
<FSTMatch <Global ROOT 0,0..0,14> {'l': <<Global ROOT 0,0..0,14>.names>}>

Here it returned an `FSTView` for the list because the node we used as an `FST`. In case of `AST` it just returns what
is there.

>>> MAST(names=M(l=[...])).match(ast.parse('global a, b, c').body[0])
<FSTMatch Global(names=['a', 'b', 'c']) {'l': ['a', 'b', 'c']}>


## `MNOT()` pattern

This is similar to the `M()` pattern except that it succeeds and adds tags when the child does **NOT** match.

>>> print(MConstant(MNOT(tag=1, static=True)).match(FST('1')))
None

>>> MConstant(MNOT(tag=1, static=True)).match(FST('2'))
<FSTMatch <Constant ROOT 0,0..0,1> {'tag': 2, 'static': True}>

This tag does not propagate any tags from below as it only succeeds when the child pattern fails, and fails if it
succeeds. So it can only ever propagate its own tags upwards when there are no tags from children due to failed match.


## `MOR()` and `MAND()` patterns

These should be self-explanatory. The only thing that needs to be clarified is their tag usage. They both take one or
more patterns and the patterns can be all anonymous, all tagged or a combination.

>>> MOR('a', tag_b='b', tag_c='c').match(FST('a'))
<FSTMatch <Name ROOT 0,0..0,1>>

>>> MOR('a', tag_b='b', tag_c='c').match(FST('b'))
<FSTMatch <Name ROOT 0,0..0,1> {'tag_b': <Name ROOT 0,0..0,1>}>

>>> MOR('a', tag_b='b', tag_c='c').match(FST('c'))
<FSTMatch <Name ROOT 0,0..0,1> {'tag_c': <Name ROOT 0,0..0,1>}>

They do not provide static tags as each keyword element is another pattern to match. If you want to add static tags to
a successful or match the either add an `M()` to the whole `MOR`.

>>> M(MOR('a', tag_b='b', tag_c='c'), static=True).match(FST('c'))
<FSTMatch <Name ROOT 0,0..0,1> {'tag_c': <Name ROOT 0,0..0,1>, 'static': True}>

Or to the individual elements.

>>> MOR(M('a', static=False), tag_b='b', tag_c=M('c', static=True)).match(FST('a'))
<FSTMatch <Name ROOT 0,0..0,1> {'static': False}>

>>> MOR(M('a', static=False), tag_b='b', tag_c=M('c', static=True)).match(FST('b'))
<FSTMatch <Name ROOT 0,0..0,1> {'tag_b': <Name ROOT 0,0..0,1>}>

>>> MOR(M('a', static=False), tag_b='b', tag_c=M('c', static=True)).match(FST('c'))
<FSTMatch <Name ROOT 0,0..0,1> {'static': True, 'tag_c': <Name ROOT 0,0..0,1>}>


## `MANY()` pattern

This is essentially a combination of type check with arbitrary fields. It takes an iterable of `AST` and `MAST` types
and an arbitrarly list of keyword-specified fields to match.

The following will match any statement node which can and does have a docstring

>>> pat = MANY(
...     (FunctionDef, AsyncFunctionDef, ClassDef),
...     body=[Expr(Constant(str)), ...],
... )

>>> pat.match(FST('def f(): "docstring"; pass'))
<FSTMatch <FunctionDef ROOT 0,0..0,26>>

>>> pat.match(FST('def f(): pass; pass'))

>>> pat.match(FST('def f(): pass; "NOTdocstring"'))

>>> pat.match(FST('class cls: "docstring"; pass'))
<FSTMatch <ClassDef ROOT 0,0..0,28>>

>>> pat.match(FST('if 1: "NOTdocstring"; pass'))

Multiple fields to match.

>>> pat = MANY(
...     (FunctionDef, AsyncFunctionDef),
...     body=[Expr(Constant(str)), ...],
...     returns='int',
... )

>>> pat.match(FST('def f() -> int: "docstring"; pass'))
<FSTMatch <FunctionDef ROOT 0,0..0,33>>

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
<FSTMatch <Name ROOT 0,0..0,15>>

>>> f.match(MRE(m=r'.*hidden.*'))
<FSTMatch <Name ROOT 0,0..0,15> {'m': <re.Match object; span=(0, 15), match='some_hidden_gem'>}>

Using `search=True` you can narrow down the location of whatever you are looking for.

>>> f.match(MRE(m=r'hidden', search=True))
<FSTMatch <Name ROOT 0,0..0,15> {'m': <re.Match object; span=(5, 11), match='hidden'>}>


## `MOPT()` pattern

This is a pattern or `None` match. It can be used to optionally match single-element fields which may or may not be
present. That is, both a normal value which matches the pattern and a `None` value are considered a successful match.
A non-`None` value which does NOT match the pattern is considered a failure.

>>> MFunctionDef(returns=MOPT('int')) .match(FST('def f(): pass'))
<FSTMatch <FunctionDef ROOT 0,0..0,13>>

>>> MFunctionDef(returns=MOPT('int')) .match(FST('def f() -> int: pass'))
<FSTMatch <FunctionDef ROOT 0,0..0,20>>

>>> MFunctionDef(returns=MOPT('int')) .match(FST('def f() -> str: pass'))

>>> MDict([MOPT('a')], ['b']) .match(FST('{a: b}'))
<FSTMatch <Dict ROOT 0,0..0,6>>

>>> MDict([MOPT('a')], ['b']) .match(FST('{**b}'))
<FSTMatch <Dict ROOT 0,0..0,5>>

>>> MDict([MOPT('a')], ['b']) .match(FST('{x: b}'))

>>> MMatchMapping(rest=MOPT('a')) .match(FST('{1: x, **a}', 'pattern'))
<FSTMatch <MatchMapping ROOT 0,0..0,11>>

>>> MMatchMapping(rest=MOPT('a')) .match(FST('{1: x, **b}', 'pattern'))

>>> MMatchMapping(rest=MOPT('a')) .match(FST('{1: x}', 'pattern'))
<FSTMatch <MatchMapping ROOT 0,0..0,6>>


## `MCB()` pattern

This is a powerful pattern that allows you to inject arbitrary logic at any point of the pattern match. The `CB` stands
for callback and the function you provide is called to determine whether there is a match or not, and can even provide
the return value to add as a tag (if a tag is being added).

>>> pat = MConstant(MCB(lambda x: 2 < x < 8))

>>> pat.match(FST('1'))

>>> pat.match(FST('3'))
<FSTMatch <Constant ROOT 0,0..0,1>>

>>> pat.match(FST('7'))
<FSTMatch <Constant ROOT 0,0..0,1>>

>>> pat.match(FST('10'))

Check for only parenthesized tuples.

>>> pat = MCB(FST.is_parenthesized_tuple)

>>> pat.match(FST('x, y, z'))

>>> pat.match(FST('(x, y, z)'))
<FSTMatch <Tuple ROOT 0,0..0,9>>

>>> pat.match(FST('[x, y, z]'))

This node also allows matched target and static tags.

>>> pat = MCB(tgt=FST.is_parenthesized_tuple, static=True)

>>> pat.match(FST('(x, y, z)'))
<FSTMatch <Tuple ROOT 0,0..0,9> {'tgt': <Tuple ROOT 0,0..0,9>, 'static': True}>

If you pass `tag_ret=True` then whatever is returned from the callback function is used for the match tag (assuming it
is a truthy value, otherwise the match is assumed to have failed).

>>> pat = M(node=Name(MCB(upper=str.upper, tag_ret=True)))

>>> pat.match(FST('a.b'))

>>> pat.match(FST('some_name'))
<FSTMatch <Name ROOT 0,0..0,9> {'upper': 'SOME_NAME', 'node': <Name ROOT 0,0..0,9>}>

An explicit fail value can be provided in case you want to be able to tag falsey values directly, it is checked by
equality.

>>> MCB(tag=lambda f: False, tag_ret=True, fail_val=None).match(FST('a'))
<FSTMatch <Name ROOT 0,0..0,1> {'tag': False}>

>>> MCB(tag=lambda f: None, tag_ret=True, fail_val=None).match(FST('a'))

The type of node passed to the callback depends on the type of tree that match is called on.

>>> pat = MCB(lambda n: print(type(n)))

>>> pat.match(FST('name').a)
<class 'ast.Name'>

>>> pat.match(FST('name'))
<class 'fst.fst.FST'>


## `MTAG()` pattern

This pattern allows you to match against tags that exist at the point that this pattern is reached. Mostly meant for
matching against already matched nodes, but can also be used to match against arbitrary tag values as well as long as
they are valid patterns.

>>> MBinOp(M(left_='a'), right=MTAG('left_')).match(FST('a + a'))
<FSTMatch <BinOp ROOT 0,0..0,5> {'left_': <Name 0,0..0,1>}>

In the example above we match a `BinOp` which has the same node on the right as the left. It will fail if they are
different.

>>> MBinOp(M(left='a'), right=MTAG('left')).match(FST('a + b'))

The tag must already have been matched, not be in the future.

>>> MBinOp(MTAG('right'), right=M(right='a')).match(FST('a + a'))

As stated, the tag to match does not have to come from an actual previous match, it can be set explicitly.

>>> pat = MBinOp(
...    MOR(M('if_a', then='then_b'), M('if_x', then='then_y')),
...    ...,
...    MTAG('then'))

>>> pat.match(FST('if_a + then_b'))
<FSTMatch <BinOp ROOT 0,0..0,13> {'then': 'then_b'}>

>>> pat.match(FST('if_a + then_y'))

>>> pat.match(FST('if_x + then_y'))
<FSTMatch <BinOp ROOT 0,0..0,13> {'then': 'then_y'}>

Can match previously matched multinode items from `Dict`, `MatchMapping` or `arguments`.

>>> MDict(_all=[M(s=...), ..., MTAG(e='s')]).match(FST('{1:a,1:a}'))
<FSTMatch <Dict ROOT 0,0..0,9> {'s': <<Dict ROOT 0,0..0,9>._all[:1]>, 'e': <<Dict ROOT 0,0..0,9>._all[1:2]>}>

>>> MDict(_all=[M(start=...), ..., MTAG('start')]).match(FST('{**b, 1: a, **b}'))
<FSTMatch <Dict ROOT 0,0..0,16> {'start': <<Dict ROOT 0,0..0,16>._all[:1]>}>


## `MN()` quantifier pattern

This is essentially a counted wildcard for use inside list fields to match a pattern between a minimum and maximum
number of times.

>>> MList([MN('a', 1, 2)]).match(FST('[]'))

>>> MList([MN('a', 1, 2)]).match(FST('[a]'))
<FSTMatch <List ROOT 0,0..0,3>>

>>> MList([MN('a', 1, 2)]).match(FST('[a, a]'))
<FSTMatch <List ROOT 0,0..0,6>>

>>> MList([MN('a', 1, 2)]).match(FST('[a, a, a]'))

The pattern above will only match 1 or 2 instances of `a`. It failed the last check because there were three `a`s and
we did not account for that in the full pattern.

>>> MList([MN('a', 1, 2), ...]).match(FST('[a, a, a]'))
<FSTMatch <List ROOT 0,0..0,9>>

Now we tag it to show that it only "consumed" two of the `a` instances.

>>> MList([MN(t='a', min=1, max=2), ...]).match(FST('[a, a, a]'))
<FSTMatch <List ROOT 0,0..0,9> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

When a quantifier pattern is tagged then it returns a list of `FSTMatch` objects in that tag of all the nodes that were
matched. If used with a tag like this then any tags from the children are made available in their individual match
objects.

>>> MList([MN(t=M(u=MRE('a|b')), min=1, max=2), ...]).match(FST('[a, b, a]'))
<FSTMatch <List ROOT 0,0..0,9> {'t': [<FSTMatch <Name 0,1..0,2> {'u': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'u': <Name 0,4..0,5>}>]}>

If the pattern is untagged however, the tags from all the children are collapsed and the latter matches override
earlier tag values. All the tags are put into the parent match object and the matched nodes do not get their own
individual match objects.

>>> MList([MN(M(u=MRE('a|b')), min=1, max=2), ...]).match(FST('[a, b, a]'))
<FSTMatch <List ROOT 0,0..0,9> {'u': <Name 0,4..0,5>}>

One case to look out for is when using a quantifier with a minimum of 0. This can always match something since it can
match nonexistent elements.

>>> MList([MN(t='a', min=0, max=2), ...]).match(FST('[b, b, b]'))
<FSTMatch <List ROOT 0,0..0,9> {'t': []}>

There was a successful match against 0 elements in this case.


## `MSTAR()`, `MPLUS()`, `MQMARK()`, `MMIN()` and `MMAX()` quantifier patterns

These are just convenience classes subclassed off of `MN` which provide predefined `min` and / or `max` values. `MSTAR`
is match zero or more.

>>> bool(MList([MSTAR('a')]).match(FST('[]')))
True

>>> bool(MList([MSTAR('a')]).match(FST('[a]')))
True

>>> bool(MList([MSTAR('a')]).match(FST('[a, a]')))
True

>>> bool(MList([MSTAR('a')]).match(FST('[a, a, a]')))
True

`MPLUS` is one or more.

>>> bool(MList([MPLUS('a')]).match(FST('[]')))
False

>>> bool(MList([MPLUS('a')]).match(FST('[a]')))
True

>>> bool(MList([MPLUS('a')]).match(FST('[a, a]')))
True

>>> bool(MList([MPLUS('a')]).match(FST('[a, a, a]')))
True

`MQMARK` is zero or one, just like the regex `?` question mark.

>>> bool(MList([MQMARK('a')]) .match(FST('[]')))
True

>>> bool(MList([MQMARK('a')]) .match(FST('[a]')))
True

>>> bool(MList([MQMARK('a')]) .match(FST('[b]')))
False

>>> bool(MList([MQMARK('a')]) .match(FST('[a, a]')))
False

>>> bool(MList([MQMARK('a'), ...]) .match(FST('[a, a]')))
True

`MMIN` is expectedly minimum.

>>> bool(MList([MMIN('a', 2)]).match(FST('[]')))
False

>>> bool(MList([MMIN('a', 2)]).match(FST('[a]')))
False

>>> bool(MList([MMIN('a', 2)]).match(FST('[a, a]')))
True

>>> bool(MList([MMIN('a', 2)]).match(FST('[a, a, a]')))
True

And `MMAX` is maximum.

>>> bool(MList([MMAX('a', 2)]).match(FST('[]')))
True

>>> bool(MList([MMAX('a', 2)]).match(FST('[a]')))
True

>>> bool(MList([MMAX('a', 2)]).match(FST('[a, a]')))
True

>>> bool(MList([MMAX('a', 2)]).match(FST('[a, a, a]')))
False

>>> bool(MList([MMAX('a', 2), ...]).match(FST('[a, a, a]')))
True


## `AST` as pattern or target

`AST` trees can be matched against patterns or they can be used as patterns themselves. In fact, this is the exact
mechanism which is used by the `MTAG()` pattern to compare previously matched parts of the tree.

>>> FST('a = b ; call()').match(ast.parse('a = b ; call()'))
<FSTMatch <Module ROOT 0,0..0,14>>

It is not any less efficient to use `AST` as a pattern vs. using the `MAST` pattern classes. The differences are:

- `AST` nodes may need all required fields to be specified whereas for the pattern classes all fields are optional. The
    way handle this if using `AST` is just to specify those fields as `...` wildcards.

>>> FST('a + b').match(MBinOp(op='+'))
<FSTMatch <BinOp ROOT 0,0..0,5>>

vs.

>>> FST('a + b').match(BinOp(..., '+', ...))
<FSTMatch <BinOp ROOT 0,0..0,5>>

- The `MAST` patterns allow you to match against virtual fields like `_all` or `_args`, `AST` nodes do not.

>>> FST('call(a, **b)').match(MCall(_args=['a', '**b']))
<FSTMatch <Call ROOT 0,0..0,12>>

vs.

>>> FST('call(a, **b)').match(Call(..., args=['a'], keywords=['**b']))
<FSTMatch <Call ROOT 0,0..0,12>>

- And finally, your type checker will complain if you use any patterns, values or wildcards in `AST` fields which are not
    expected to be there.

```
$ mypy -c "from ast import *; Call(..., args=['a'], keywords=['**b'])"
error: Argument 1 to "Call" has incompatible type "EllipsisType"; expected "expr" [arg-type]
error: List item 0 has incompatible type "str"; expected "expr"  [list-item]
error: List item 0 has incompatible type "str"; expected "keyword"  [list-item]
```

## Virtual fields and `FSTView`



# Search

# Substitute





"""
