r"""
# Match, search and substitute

To be able to execute the examples, import this.

>>> import ast, re
>>> from fst import *
>>> from fst.match import *

This is just a pretty-print function for long `FSTMatch` objects.

>>> from fst.docs import ppmatch


# Match

`fst` provides a way to do structural pattern matching against `FST` or `AST` trees. The elements of the pattern are
special `M_Pattern` classes provided by `fst`, or just normal `AST` classes, though type checkers might complain about
that usage.

The matcher supports wildcards, regex, logic operations, callbacks, backreferences and quantifiers with backtracking and
subsequences. Additionally, you can tag arbitrary matched subparts of the target or even set static tags along the way
at any point during the matching to be returned in a successful `FSTMatch` object.

Here is an example of a structural match to give you an idea, it will be explained below. This pattern will match any
`logger.info()` call which has a `cid` keyword argument:

>>> pat = MCall(
...    MAttribute('logger', 'info'),
...    keywords=[MQSTAR, Mkeyword('cid'), MQSTAR],
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
...    [MQSTAR, keyword('cid', ...), MQSTAR],
... )

>>> bool(FST('logger.info(a, cid=1)').match(ast_pat))
True

>>> bool(FST('logger.info(a)').match(ast_pat))
False

You will note the use of the `Ellipsis` in the examples above. The `...` serves as a wildcard match-any-single-element
in `fst` pattern matching. It matches anything in place of an actual field value and is equivalent to the regex `.` dot
pattern.


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

>>> bool(FST('global a, b, c, d, e, f').match(Global([MQSTAR, 'c', MQSTAR])))
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

>>> bool(MList([MQSTAR, MCall, MQSTAR]).match(FST('[a, b, c, d]')))
False

>>> bool(MList([MQSTAR, MCall, MQSTAR]).match(FST('[a, b(), c, d]')))
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

Or as a convenience directly as attributes.

>>> m.tag
'string'

>>> m.static_tag
True

You do not have to worry about tags shadowing real `FSTMatch` attributes as tags which would do that are not allowed and
raise an exception if you try to create a pattern with them.

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

>>> ppmatch(MBinOp(M(left=...), ..., M(tag1=M(tag2=...))).match(FST('a + b')))
<FSTMatch <BinOp ROOT 0,0..0,5>
  {'left': <Name 0,0..0,1>, 'tag2': <Name 0,4..0,5>, 'tag1': <Name 0,4..0,5>}>

This pattern can go almost anywhere and tag nodes, primitives, `None` and even entire list fields.

>>> MAST(names=M(l=[MQSTAR])).match(FST('global a, b, c'))
<FSTMatch <Global ROOT 0,0..0,14> {'l': <<Global ROOT 0,0..0,14>.names>}>

Here it returned an `FSTView` for the list because the node we used as an `FST`. In case of `AST` it just returns what
is there.

>>> MAST(names=M(l=[MQSTAR])).match(ast.parse('global a, b, c').body[0])
<FSTMatch Global(names=['a', 'b', 'c']) {'l': ['a', 'b', 'c']}>

It can NOT however wrap quantifier patterns inside list fields. Quantifier patterns can only live directly inside list
fields.

>>> MList([M(MQSTAR)]).match(FST('[1, 2, 3]'))
Traceback (most recent call last):
...
fst.match.MatchError: MQSTAR quantifier pattern in invalid location


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


## `MTYPES()` pattern

This is essentially a combination of type check with arbitrary fields. It takes an iterable of `AST` and `MAST` types
and an arbitrarly list of keyword-specified fields to match.

The following will match any statement node which can and does have a docstring

>>> pat = MTYPES(
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

>>> pat = MTYPES(
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

>>> ppmatch(f.match(MRE(m=r'.*hidden.*')))
<FSTMatch <Name ROOT 0,0..0,15>
  {'m': <re.Match object; span=(0, 15), match='some_hidden_gem'>}>

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

Get node along with name in uppercase.

>>> pat = M(node=Name(MCB(upper=str.upper, tag_ret=True)))

>>> pat.match(FST('a.b'))

>>> pat.match(FST('some_name'))
<FSTMatch <Name ROOT 0,0..0,9> {'upper': 'SOME_NAME', 'node': <Name ROOT 0,0..0,9>}>

An explicit fail object can be provided in case you want to be able to tag falsey values directly, it is checked by
identity.

>>> MCB(tag=lambda f: False, tag_ret=True, fail_obj=None) .match(FST('a'))
<FSTMatch <Name ROOT 0,0..0,1> {'tag': False}>

>>> MCB(tag=lambda f: None, tag_ret=True, fail_obj=None) .match(FST('a'))

The type of node passed to the callback depends on the type of tree that `match()` is called on.

>>> pat = MCB(lambda n: print(type(n)))

>>> pat.match(Name('name'))
<class 'ast.Name'>

>>> pat.match(FST('name'))
<class 'fst.fst.FST'>

A tag getter function can be passed to the callback so it can request tags that have been set so far.

>>> m = M(prev=MCB(
...     lambda t, g: (print(f"this: {t}, prev: {g('prev')}"),),
...     pass_tags=True,
... ))

>>> MList([m, m, m]) .match(FST('[a, b, c]'))
this: <Name 0,1..0,2>, prev: <NoTag>
this: <Name 0,4..0,5>, prev: <Name 0,1..0,2>
this: <Name 0,7..0,8>, prev: <Name 0,4..0,5>
<FSTMatch <List ROOT 0,0..0,9> {'prev': <Name 0,7..0,8>}>


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

>>> ppmatch(MDict(_all=[M(s=...), MQSTAR, MTAG(e='s')]).match(FST('{1:a,1:a}')))
<FSTMatch <Dict ROOT 0,0..0,9>
  {'s': <<Dict ROOT 0,0..0,9>._all[:1]>, 'e': <<Dict ROOT 0,0..0,9>._all[1:2]>}>

>>> MDict(_all=[M(start=...), ..., MTAG('start')]).match(FST('{**b, 1: a, **b}'))
<FSTMatch <Dict ROOT 0,0..0,16> {'start': <<Dict ROOT 0,0..0,16>._all[:1]>}>


## `MQ()` quantifier pattern

The quantifiers allow matching a given pattern between zero and an unbounded number of times in a LIST FIELD. To
reiterate, they can only live in and match elements inside a list field, not individual non-list fields like
`BinOp.left` or `FunctionDef.returns`. So only fields like `Module.body`, `List.elts`, `Dict.keys` or even virtual
fields like `Dict._all`.

**Disclaimer:** Before going any further it needs to be noted that these quantifiers can backtrack and combining them in
certain unoptimal ways can cause pathological behavior in the same way as combining quantifiers poorly in Python regexes
can.

`MQ` is the base class for all the other quantifier patterns `MQSTAR`, `MQPLUS`, `MQ01`, `MQMIN`, `MQMAX` and `MQN` and
can do everything that those classes can do. Those classes are provided however for cleaner and quicker pattern
specification.

On a successful match, the matched target elements can be returned in a list if the pattern to match has a tag. In this
case each matched target element of the list field will get its own `FSTMatch` object in the returned tag list.

>>> ppmatch(MList([MQ(tag=..., min=1, max=None)]).match(FST('[a, b]')))
<FSTMatch <List ROOT 0,0..0,6>
  {'tag': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

Or their individual tags will all be merged in order into a single tags dictionary from the whole quantifier pattern.
Notice it is the last element matched whose tags wind up in the final `FSTMatch` object as it overwrites the previous
matched element tags.

>>> ppmatch(MList([MQ(M(tag=...), min=1, max=None)]).match(FST('[a, b]')))
<FSTMatch <List ROOT 0,0..0,6> {'tag': <Name 0,4..0,5>}>

In the example above, the use of `...` for the pattern is a wildcard which means "match any single element". But there
MUST be an element, it cannot match the lack of an element, its not that kind of wildcard. The `min` specifies the
minimum number of elements that can constitute a successful match, any fewer than this and the match fails.

>>> ppmatch(MList([MQ(M(tag=...), min=3, max=None)]).match(FST('[a, b]')))
None

The `max` specifies the maximum number of matches to allow, and if `None` like the example then it indicates unbounded
and will match as many instances of the pattern as possible. If there is an actual maximum value and the maximum is
reached, then the rest of the list must be accounted for somehow or the match will fail.

>>> ppmatch(MList([MQ(tag=..., min=1, max=2)]).match(FST('[a, b, c]')))
None

The above failed because it matched `a` and `b` but there was still a `c` left to match. Below we add an `MQSTAR`
pattern to eat the rest of the list so that the match can succeed.

>>> ppmatch(MList([MQ(tag=..., min=1, max=2), MQSTAR]).match(FST('[a, b, c]')))
<FSTMatch <List ROOT 0,0..0,9>
  {'tag': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

The `MQ` pattern itself is greedy and will match as many times as possible up to its maximum and then start backtracking
as needed in order to attempt to match the rest of the patterns that follow it. If it reaches its `min` count of matches
without being able to match following patterns then the whole match fails.

There is a non-greedy version of the `MQ` pattern (and the other quantifier patterns as well). This lives as a child
class of `MQ` itself as `MQ.NG`. It takes the same parameters except that it matches the minimum number of times allowed
at first and then goes matching more and more as needed in order to try to find a match for all the patterns that
follow.

>>> ppmatch(MList([MQ.NG(tag=..., min=1, max=2), MQSTAR]).match(FST('[a, b, c]')))
<FSTMatch <List ROOT 0,0..0,9> {'tag': [<FSTMatch <Name 0,1..0,2>>]}>

Quantifier classes have one more useful trick. Apart from matching a pattern a variable number of times, the pattern
itself can be a arbitrary-length list of other patterns. In short, instead of just matching a single thing any number of
times, quantifier classes can match a given sequence of things any number of times.

>>> ppmatch(MList([MQ(t=['a', 'b'], min=1, max=2)]).match(FST('[a, b, a, b]')))
<FSTMatch <List ROOT 0,0..0,12>
  't': [
    <FSTMatch [<Name 0,1..0,2>, <Name 0,4..0,5>]>,
    <FSTMatch [<Name 0,7..0,8>, <Name 0,10..0,11>]>,
  ],
}>

You can have other patterns inside the quantifier subsequence, even other quantifiers, but be aware that the
backtracking from those quantifiers doesn't mix with the parent quantifier. Otherwise, all patterns will work as
expected.

>>> pat = MList([MQ(t=[M(u=...), MTAG('u')], min=1, max=None)])

>>> ppmatch(pat.match(FST('[a, b, a, b]')))
None

>>> ppmatch(pat.match(FST('[a, a, b, b]')))
<FSTMatch <List ROOT 0,0..0,12>
  't': [
    <FSTMatch [<Name 0,1..0,2>, <Name 0,4..0,5>] {'u': <Name 0,1..0,2>}>,
    <FSTMatch [<Name 0,7..0,8>, <Name 0,10..0,11>] {'u': <Name 0,7..0,8>}>,
  ],
}>

The following is truly an academic excercise, as this is done much more quickly an easily with code and a walk over the
list, but just to show what can be done with matching...

One of the uses for quantifiers in subsequences can be filtering and grouping. The example below will filter all names
from a list and return a match object with a list of matches where each one has a list that starts with a single `Name`
node.

>>> mqnot_Name = MQSTAR(MNOT(Name))

>>> pat = MList([mqnot_Name, MQSTAR(t=[Name, mqnot_Name])])

>>> ppmatch(pat.match(FST('[0, a, 1, 2, b, c, 3, d, 4, 5]')))
<FSTMatch <List ROOT 0,0..0,30>
  't': [
    <FSTMatch [<Name 0,4..0,5>, <Constant 0,7..0,8>, <Constant 0,10..0,11>]>,
    <FSTMatch [<Name 0,13..0,14>]>,
    <FSTMatch [<Name 0,16..0,17>, <Constant 0,19..0,20>]>,
    <FSTMatch [<Name 0,22..0,23>, <Constant 0,25..0,26>, <Constant 0,28..0,29>]>,
  ],
}>


## `MQSTAR()`, `MQPLUS()`, `MQ01()`, `MQMIN()`, `MQMAX()` and `MQN()` quantifier patterns

These are just convenience classes subclassed off of `MQ` which provide predefined `min` and / or `max` values, so we
won't go into much detail for each. There is one particularly useful thing some of these classes provide. You can use
the `MQSTAR`, `MQPLUS` and `MQ01` classes themselves (and their non-greedy versions) in place of their instances as
actual predefined patterns.

`MQSTAR(pat)` is the same as `MQ(pat, min=0, max=None)`. `MQSTAR` by itself is the same as `MQSTAR(...)` and is the
equivalent of regex `.*`.

`MQSTAR.NG(pat)` is the same as `MQ.NG(pat, min=0, max=None)`. `MQSTAR.NG` by itself is the same as `MQSTAR.NG(...)` and
is the equivalent of regex `.*?`.

`MQPLUS(pat)` is the same as `MQ(pat, min=1, max=None)`. `MQPLUS` by itself is the same as `MQPLUS(...)` and is the
equivalent of regex `.+`.

`MQPLUS.NG(pat)` is the same as `MQ.NG(pat, min=1, max=None)`. `MQPLUS.NG` by itself is the same as `MQPLUS.NG(...)` and
is the equivalent of regex `.+?`.

`MQ01(pat)` is the same as `MQ(pat, min=0, max=1)`. `MQ01` by itself is the same as `MQ01(...)` and is the equivalent of
regex `.?`.

`MQ01.NG(pat)` is the same as `MQ.NG(pat, min=0, max=1)`. `MQ01.NG` by itself is the same as `MQ01.NG(...)` and is the
equivalent of regex `.??`.

The class types below cannot be used as instances by themselves as they have mandatory parameter.

`MQMIN(pat, min)` is the same as `MQ(pat, min=min, max=None)`.

`MQMIN.NG(pat, min)` is the same as `MQ.NG(pat, min=min, max=None)`.

`MQMAX(pat, max)` is the same as `MQ(pat, min=0, max=max)`.

`MQMAX.NG(pat, max)` is the same as `MQ.NG(pat, min=0, max=max)`.

`MQN(pat, n)` is the same as `MQ(pat, min=n, max=n)`.

`MQN.NG(pat, n)` is the same as `MQ.NG(pat, min=n, max=n)`.


## Virtual fields and `FSTView`

**Note:** This discussion about virtual fields applies if you will be matching against `FST`'s own convenience fields
that start with an underscore like `_all` or `_args`. Matching against real fields of nodes that also have virtual
fields proceeds normally and these rules do not apply to those matches.

Virtual fields are algorithmic sequence views over the elements of a node that don't actually exist on their own in the
given `AST` node but make sense to access as a sequence. It also makes sense to be able to match on these views and this
is possible. There are two cases to consider.

There are virtual fields that resolve to individual nodes when dereferenced to a single element. These are
straightforward to match as you just use normal patterns in the virtual field list of the match pattern. For example, if
you access the `_all` virtual field on a `Compare`, you will get a single node from the combined `left` + `comparators`
virtual sequence.

>>> ppmatch(MCompare(_all=[MQSTAR(t=...)]).match(FST('a < 1 < b.c')))
<FSTMatch <Compare ROOT 0,0..0,11>
  't': [
    <FSTMatch <Name 0,0..0,1>>,
    <FSTMatch <Constant 0,4..0,5>>,
    <FSTMatch <Attribute 0,8..0,11>>,
  ],
}>

In the example below the single `_args` virtual field matches against both the `Call.args` and `Call.keywords` fields.

>>> ppmatch(MCall(_args=[MQSTAR(t=...)]).match(FST('call(a, *b, c=d, **e)')))
<FSTMatch <Call ROOT 0,0..0,21>
  't': [
    <FSTMatch <Name 0,5..0,6>>,
    <FSTMatch <Starred 0,8..0,10>>,
    <FSTMatch <keyword 0,12..0,15>>,
    <FSTMatch <keyword 0,17..0,20>>,
  ],
}>

And in the next one the `_body` field is rectricted to exclude the first docstring `Expr` node.

>>> ppmatch(MClassDef(_body=[MQSTAR(t=...)]).match(FST('''
... class cls:
...     \'\'\'docstring\'\'\'
...     if 1:
...         pass
...     call(something)
... '''.strip())))
<FSTMatch <ClassDef ROOT 0,0..4,19>
  {'t': [<FSTMatch <If 2,4..3,12>>, <FSTMatch <Expr 4,4..4,19>>]}>

The second case are virtual fields where the individual elements do not resolve to a single node but to a group of
nodes, and when dereferenced give another view instead of a node, a `Dict` for instance.

>>> FST('{a: b, c: d, **b}')._all[1]
<<Dict ROOT 0,0..0,17>._all[1:2]>

You can match against these as a sequence as well by using the type of node that these resolve to when copied, with a
single element in each of the list fields that need to be matched.

In this example we are just showing matching a length-1 target to show how it works.

>>> pat = MDict(_all=[MDict([...], ['b'])])

>>> ppmatch(pat.match(FST('{a: b}')))
<FSTMatch <Dict ROOT 0,0..0,6>>

>>> ppmatch(pat.match(FST('{c: d}')))
None

>>> ppmatch(pat.match(FST('{**b}')))
<FSTMatch <Dict ROOT 0,0..0,5>>

It will not work if you try with any less or more than a single element in the list fields.

>>> ppmatch(MDict(_all=[MDict([], ['b'])]).match(FST('{a: b}')))
Traceback (most recent call last):
...
fst.match.MatchError: matching a Dict pattern against Dict._all the pattern keys must be ... or a length-1 list

Also, quantifiers are not allowed in these multinode single element patterns, even quantifiers that would resolve to a
single element.

>>> ppmatch(MDict(_all=[MDict([MQN('a', 1)], ['b'])]).match(FST('{a: b}')))
Traceback (most recent call last):
...
fst.match.MatchError: MQN quantifier pattern in invalid location

You can use a wildcard `...` in place of the list field to indicate match any single element. And you can use tagging
patterns and quantifiers (outside of the single element to match) like with any other list field match.

>>> ppmatch(MDict(_all=[M(t=MDict(..., ['b']))]).match(FST('{a: b}')))
<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all[:1]>}>

>>> ppmatch(MDict(_all=[MQSTAR(t=MDict(..., ['b']))]).match(FST('{a: b, **b}')))
<FSTMatch <Dict ROOT 0,0..0,11>
  't': [
    <FSTMatch <<Dict ROOT 0,0..0,11>._all[:1]>>,
    <FSTMatch <<Dict ROOT 0,0..0,11>._all[1:2]>>,
  ],
}>

Notice how in each case the match returned is an `FSTView` of the key:value pairs of nodes matched, as they do not
constitute a single node that can be returned on its own. Since this matching mechanism relies on `FSTView`, it will not
match against pure `AST` trees.

>>> ast_ = FST('{a: b}').copy_ast()

>>> ppmatch(MDict(_all=[M(t=MDict(..., ['b']))]).match(ast_))
None

>>> ppmatch(MDict(_all=[MQSTAR(t=MDict(..., ['b']))]).match(ast_))
None

The same pattern usage applies to multinode virtual field matching as to normal nodes, including backreferences.

>>> pat = MDict(_all=[M(t=Dict), MQSTAR(u=MTAG('t'))])

>>> ppmatch(pat.match(FST('{a: b, a: b, a: b}')))
<FSTMatch <Dict ROOT 0,0..0,18>
  't': <<Dict ROOT 0,0..0,18>._all[:1]>,
  'u': [
    <FSTMatch <<Dict ROOT 0,0..0,18>._all[1:2]>>,
    <FSTMatch <<Dict ROOT 0,0..0,18>._all[2:3]>>,
  ],
}>

>>> ppmatch(pat.match(FST('{a: b, a: c, **b}')))
None

And subsequences.

>>> dict_ = MDict([...], ['b'])

>>> mqnot_dict = MQSTAR(MNOT(dict_))

>>> pat = MDict(_all=[mqnot_dict, MQSTAR(t=[dict_, mqnot_dict])])

>>> ppmatch(pat.match(FST('{1:2, 3:b, 4:5, a:b, **b, 8:9}')))
<FSTMatch <Dict ROOT 0,0..0,30>
  't': [
    <FSTMatch [<<Dict ROOT 0,0..0,30>._all[1:2]>, <<Dict ROOT 0,0..0,30>._all[2:3]>]>,
    <FSTMatch [<<Dict ROOT 0,0..0,30>._all[3:4]>]>,
    <FSTMatch [<<Dict ROOT 0,0..0,30>._all[4:5]>, <<Dict ROOT 0,0..0,30>._all[5:6]>]>,
  ],
}>

All these same mechanisms apply to `MatchMapping._all`, with the small change that `MatchMapping` has a standalone
`rest` element that must be matched on its own. Where it starts to get slightly complicated however is with `arguments`.


## `arguments` virtual field matching

This type is considered multinode because the individual arguments can have defaults, and when indexing an argument the
default has to be included, which is a separate node. This is handled fine by both `FSTView` which just gives you
another arguments `FSTView` when dereferencing and when copying a single "argument" it gets returned as another
single-argument `arguments` node.

Where it gets a little complicated is that there are three types of arguments, `posonlyargs`, `args` and `kwonlyargs`.
The complication is which ones to allow to compare with one another to constitute a match. The rules `fst` currently
uses are a best guess at what would work well and may need some tweaking in the future depending on use.

Just like `Dict`, when matching the `_all` field of arguments the individual elements inside the `_all` list field must
be `arguments` or `Marguments` with a single argument element and / or a single default element (if both present then
they must match, no `kw_defaults` with a `posonlyarg`).

>>> pat_pos = Marguments(_all=[M(t=Marguments(posonlyargs=['a'], defaults=['1']))])

>>> ppmatch(pat_pos.match(FST('a=1, /', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>

>>> ppmatch(pat_pos.match(FST('a=1', 'arguments')))
None

>>> ppmatch(pat_pos.match(FST('*, a=1', 'arguments')))
None

Notice how the positional argument pattern only matched the positional target argument. Likewise the keyword-only
argument pattern only matched the keyword target argument.

>>> pat_kw = Marguments(_all=[M(t=Marguments(kwonlyargs=['a'], kw_defaults=['1']))])

>>> ppmatch(pat_kw.match(FST('a=1, /', 'arguments')))
None

>>> ppmatch(pat_kw.match(FST('a=1', 'arguments')))
None

>>> ppmatch(pat_kw.match(FST('*, a=1', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>

However, by default the normal argument type matches all other types.

>>> pat_arg = Marguments(_all=[M(t=Marguments(args=['a'], defaults=['1']))])

>>> ppmatch(pat_arg.match(FST('a=1, /', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>

>>> ppmatch(pat_arg.match(FST('a=1', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,3> {'t': <<arguments ROOT 0,0..0,3>._all[:1]>}>

>>> ppmatch(pat_arg.match(FST('*, a=1', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>

This is in order to allow ignoring argument type and just matching the argument contents. This can be turned off with
the special `_strict` parameter to the `Marguments` pattern.

>>> pat_arg_strict = Marguments(
...     _all=[M(t=Marguments(args=['a'], defaults=['1'], _strict=True))])

>>> ppmatch(pat_arg_strict.match(FST('a=1, /', 'arguments')))
None

>>> ppmatch(pat_arg_strict.match(FST('a=1', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,3> {'t': <<arguments ROOT 0,0..0,3>._all[:1]>}>

>>> ppmatch(pat_arg_strict.match(FST('*, a=1', 'arguments')))
None

This parameter can also be used to loosen the matching criteria for the other types of arguments, both positional and
keyword-only.

>>> pat_pos_nonstrict = Marguments(
...     _all=[M(t=Marguments(posonlyargs=['a'], defaults=['1'], _strict=False))])

>>> ppmatch(pat_pos_nonstrict.match(FST('a=1, /', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>

>>> ppmatch(pat_pos_nonstrict.match(FST('a=1', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,3> {'t': <<arguments ROOT 0,0..0,3>._all[:1]>}>

>>> ppmatch(pat_pos_nonstrict.match(FST('*, a=1', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>

The `_strict` parameter only applies to argument type, not to the presence of absence of a default value. Which may be
required.

>>> pat_def_required = Marguments(_all=[M(t=Marguments(args=['a'], defaults=['1']))])

>>> ppmatch(pat_def_required.match(FST('a=1', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,3> {'t': <<arguments ROOT 0,0..0,3>._all[:1]>}>

>>> ppmatch(pat_def_required.match(FST('a', 'arguments')))
None

Or may be specifically excluded.

>>> pat_def_excluded = Marguments(_all=[M(t=Marguments(args=['a'], defaults=[]))])

>>> ppmatch(pat_def_excluded.match(FST('a=1', 'arguments')))
None

>>> ppmatch(pat_def_excluded.match(FST('a', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,1> {'t': <<arguments ROOT 0,0..0,1>._all[:1]>}>

Or may be optional.

>>> pat_def_optional = Marguments(_all=[M(t=Marguments(args=['a'], defaults=...))])

>>> ppmatch(pat_def_optional.match(FST('a=1', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,3> {'t': <<arguments ROOT 0,0..0,3>._all[:1]>}>

>>> ppmatch(pat_def_optional.match(FST('a', 'arguments')))
<FSTMatch <arguments ROOT 0,0..0,1> {'t': <<arguments ROOT 0,0..0,1>._all[:1]>}>

Arguments can also be backreferenced, in which case the presence or absence of the default must match and the matching
is done as if `_strict=False`. Meaning a previously matched positional or keyword-only argument will match any other
type of argument.

Yes the following example is an invalid uncompilable arguments field but `fst` only deals with parsability so this is
used here for demonstration purposes in place of a more complicated comparison against an arguments field in another
`FunctionDef`.

>>> pat = Marguments(_all=[M(t=arguments), MQSTAR(u=MTAG('t'))])

>>> ppmatch(pat.match(FST('a=1, /, a=1, *, a=1')))
<FSTMatch <arguments ROOT 0,0..0,19>
  't': <<arguments ROOT 0,0..0,19>._all[:1]>,
  'u': [
    <FSTMatch <<arguments ROOT 0,0..0,19>._all[1:2]>>,
    <FSTMatch <<arguments ROOT 0,0..0,19>._all[2:3]>>,
  ],
}>

Last few notes:

- `vararg` and `kwarg` arguments must match exactly, they can never match with any other type of argument.

- This discussion has been about matching INDIVIDUAL arguments in a virtual `_all` field. If you will be matching a
    whole `.args` field of a `FunctionDef` to another one, it must match exactly.


## `AST` nodes as pattern or target

`AST` trees can be matched against patterns or they can be used as patterns themselves. In fact, this is the exact
mechanism which is used by the `MTAG()` pattern to compare previously matched parts of the tree.

>>> FST('a = b ; call()').match(ast.parse('a = b ; call()'))
<FSTMatch <Module ROOT 0,0..0,14>>

It is not any less efficient to use `AST` as a pattern vs. using the `MAST` pattern classes. The differences are:

- `AST` nodes may need all required fields to be specified whereas for the pattern classes all fields are optional. The
    way handle this if using `AST` is just to pass those fields as `...` wildcards.

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

- And finally, your type checker will complain if you use any patterns, values or wildcards in `AST` fields which are
    not expected to be there.

```
$ mypy -c "from ast import *; Call(..., args=['a'], keywords=['**b'])"
error: Argument 1 to "Call" has incompatible type "EllipsisType"; expected "expr" [arg-type]
error: List item 0 has incompatible type "str"; expected "expr"  [list-item]
error: List item 0 has incompatible type "str"; expected "keyword"  [list-item]
```


# Search

`fst.fst.FST.search(pat)` is essentially just a walk over the nodes of the `FST` node it is called on and an attempted match
against each of those, yielding the `FSTMatch` object if successful. So basically:

```py
def search(self, pat):
    for f in self.walk():
        if m := f.match(pat):
            yield m
```

The real `FST.search()` function does analyze the pattern and restricts the match checking only to types which can
possibly match the pattern. So it will never attempt to match a `MBinOp(..., '+', ...)`  against a `Compare` node for
example. But if the pattern contains nodes at the top level where the matching type cannot be determined at the start of
the search (like the callback `MCB` pattern where an arbitrary user-supplied function determines matching conditions)
then all nodes walked need to attempt a match anyway.

Here is an example of a search for a comparison for a `var.__class__` which `is` or `is not` a specific `ZST` or
`zst.ZST`. Remember that the `search()` function returns a generator so you need to iterate over the results.

>>> pat = Compare(
...     left=MAttribute(attr='__class__'),
...     ops=[MOR(IsNot, Is)],
...     comparators=[MOR(Name('ZST'), Attribute('zst', 'ZST'))],
... )

>>> f = FST('''
... if is_AST := ast_cls is not zst.ZST:
...     ast = code.a
...
... if code_cls is keyword or (
...         code_cls is zst.ZST and code.a.__class__ is keyword):
...     return code_as_keyword(code, options, parse_params, sanitize=sanitize)
...
... if src_or_ast_or_fst.__class__ is ZST:
...     return src_or_ast_or_fst.as_(
...         mode, kwargs.get('copy', True), **filter_options(kwargs))
...
... return 'an ZST' if value.__class__ is not zst.ZST else None
... '''.strip())

>>> for m in f.search(pat):
...     print(m.matched.src)
src_or_ast_or_fst.__class__ is ZST
value.__class__ is not zst.ZST

And if you want just the first match then get the first element of the returned generator.

>>> print(next(f.search(pat)).matched.src)
src_or_ast_or_fst.__class__ is ZST

The `search()` function accepts a few parameters to pass through on to the underlying walk function if you wish to
refine the walk itself, they are: `self_`, `recurse`, `scope`, `back`, `asts`. If you want to know what they do then
have a look at the `fst.fst.FST.walk()` function.

>>> for m in f.search(pat, back=True):
...     print(m.matched.src)
value.__class__ is not zst.ZST
src_or_ast_or_fst.__class__ is ZST

Since the search generator yields the actual `FSTMatch` objects from the `match()` calls, you get all the tags that
result from the match.

>>> from pprint import pp

>>> pat = MOR(M(Name, is_name=True), M(Attribute, is_attr=True))

>>> pp(list(FST('[a, 1, 2, b.c, 3, d, 4]').search(pat)))
[<FSTMatch <Name 0,1..0,2> {'is_name': True}>,
 <FSTMatch <Attribute 0,10..0,13> {'is_attr': True}>,
 <FSTMatch <Name 0,10..0,11> {'is_name': True}>,
 <FSTMatch <Name 0,18..0,19> {'is_name': True}>]

Notice the search recursed into the `Attribute` and found and returned the `Attribute.value` as a `Name`. By default the
`search()` function will recurse into nested matches. If you don't want this behavior then if you are iterating the
search generator yourself you can `send(False)` to it. Or you can just set the `nested` parameter to `False` on the call
to `search()`.

>>> pp(list(FST('[a, 1, 2, b.c, 3, d, 4]').search(pat, nested=False)))
[<FSTMatch <Name 0,1..0,2> {'is_name': True}>,
 <FSTMatch <Attribute 0,10..0,13> {'is_attr': True}>,
 <FSTMatch <Name 0,18..0,19> {'is_name': True}>]


# Substitute





"""
