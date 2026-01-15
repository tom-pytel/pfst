r'''
# Example recipes

These are a few snippets which do some real-world-ish things. The comment handling blemishes are left in place and your
actual mileage with comments at the edges of modifications will vary. It depends very much of correct usage of the
`trivia` option both on `get()` and `put()`, and comment handling in general needs a bit more work (a lot more work),
but they are preserved mostly.

The examples are deliberately not the most efficient but are rather meant to show off `fst` usage and features. Some of
them are somewhat formatter-y, which is not the intended use of this module, but fine for demonstration purposes. If you
want to see an example of an intended use case then see [Instrument expressions](#instrument-expressions).

You will see a lot of `.replace()` of nodes while `.walk()`ing them, this is allowed as `walk()` is really a
`transform()` function, see `fst.fst.FST.walk()` for more details.

To be able to execute the examples, import this.

>>> from fst import *

This is just a print helper function for this documentation, you can ignore it.

>>> def pprint(src):  # helper
...     print(src.replace('\n\n', '\n\xa0\n'))  # replace() to avoid '<BLANKLINE>'


## Type annotations to type comments

This doesn't do full validation and there could be extra functionality added for class attributes and updates if they
are set in a constructor, but should be enough to show how something more complete would be done.

```py
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
...         # '.own_src()' gives us the original source exactly as written dedented
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

Original.

```py
>>> pprint(src)
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

Processed:

```py
>>> pprint(type_annotations_to_type_comments(src))
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


## Inject logging metadata

You want to add a `correlation_id=CID` keyword argument to all `logger.info()` calls, but only if its not already there.

```py
>>> def inject_logging_metadata(src: str) -> str:
...     fst = FST(src, 'exec')
...
...     for f in fst.walk(Call):
...         if (f.func.is_Attribute
...             and f.func.attr == 'info'
...             and f.func.value.is_Name
...             and f.func.value.id == 'logger'
...             and not any(kw.arg == 'correlation_id' for kw in f.keywords)
...         ):
...             f.append('correlation_id=CID', trivia=(False, False))
...
...     return fst.src
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

Original.

```py
>>> pprint(src)
logger.info('Hello world...')  # ok
logger.info('Already have id', correlation_id=other_cid)  # ok
logger.info()  # yes, no logger message, too bad
 
class cls:
    def method(self, thing, extra):
        if not thing:
            (logger).info(  # just checking
                f'not a {thing}',  # this is fine
                extra=extra,       # also this
            )
```

Processed:

```py
>>> pprint(inject_logging_metadata(src))
logger.info('Hello world...', correlation_id=CID)  # ok
logger.info('Already have id', correlation_id=other_cid)  # ok
logger.info(correlation_id=CID)  # yes, no logger message, too bad
 
class cls:
    def method(self, thing, extra):
        if not thing:
            (logger).info(  # just checking
                f'not a {thing}',  # this is fine
                extra=extra,       # also this
                correlation_id=CID
            )
```


## `else if` chain to `elif`

`fst` has `elif` <-> `else if` code built in as its needed for statement insertions and deletions from conditional
bodies so its fairly easy to leverage to change these kinds of chains. The inverse of this operation can be done just
by changing the `f.is_elif()` check to `is True` and the `elif_` parameter to `elif_=False` in the `replace()`, though
you may need to tweak the `trivia` parameters for best results.

Yes the comments on the replaced `else` headers disappear. Could preserve them explicitly by using `get_line_comment()`
and then inserting them above the `if` manually using `put_src()`. Eventually should make this automatic.

```py
>>> def else_if_chain_to_elifs(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk(If):  # we will only get the `ast.If` nodes
...         if (len(f.orelse) == 1
...             and f.orelse[0].is_elif() is False  # False means normal `if`
...         ):
...             f.orelse[0].replace(  # can replace while walking
...                 f.orelse[0].copy(trivia=('block', 'all')),
...                 trivia=(False, 'all'),  # trivia specifies how to handle comments
...                 elif_=True,  # elif_=True is default, here to show usage
...             )
...
...     return fst.src
```

```py
>>> src = r"""
... def func():
...     # pre-if-a
...     if a:  # if-a
...         # pre-i
...         i = 1  # i
...         # post-i
...
...     else:  # else-a
...         # pre-if-b
...         if b:  # if-b
...             # pre-j
...             j = 2  # j
...             # post-j
...
...         else:  # else-b
...             # pre-if-c
...             if c:  # if-c
...                 # pre-k
...                 k = 3  # k
...                 # post-k
...
...             else:  # else-c
...                 # pre-l
...                 l = 4  # l
...                 # post-l
...
...             # post-else-c
...
...         # post-else-b
...
...     # post-else-a
... """.strip()
```

Original:

```py
>>> pprint(src)
def func():
    # pre-if-a
    if a:  # if-a
        # pre-i
        i = 1  # i
        # post-i
 
    else:  # else-a
        # pre-if-b
        if b:  # if-b
            # pre-j
            j = 2  # j
            # post-j
 
        else:  # else-b
            # pre-if-c
            if c:  # if-c
                # pre-k
                k = 3  # k
                # post-k
 
            else:  # else-c
                # pre-l
                l = 4  # l
                # post-l
 
            # post-else-c
 
        # post-else-b
 
    # post-else-a
```

Processed:

```py
>>> pprint(else_if_chain_to_elifs(src))
def func():
    # pre-if-a
    if a:  # if-a
        # pre-i
        i = 1  # i
        # post-i
 
    # pre-if-b
    elif b:  # if-b
        # pre-j
        j = 2  # j
        # post-j
 
    # pre-if-c
    elif c:  # if-c
        # pre-k
        k = 3  # k
        # post-k
 
    else:  # else-c
        # pre-l
        l = 4  # l
        # post-l
 
    # post-else-c
 
    # post-else-b
 
    # post-else-a
```


## Pull out nested functions

This is a bit trickier than it sounds because of possible nonlocal accesses by the inner functions. This is solved by
checking for those accesses and not pulling those functions out. Names are also changed to avoid collision at the global
scope.

The nonlocal variable check is not complete as a full check would check if the "free" symbols aren't actually global or
builtins, in which case they can be ignored and the function can be moved. We also don't check possible `type_params`
or function `returns` fields for possible nonlocal references but just assume they are all global for this example. We
also don't check for name override in children when replacing function name, but that is another detail not needed for
demonstration purposes.

```py
>>> def pull_out_inner_funcs_safely(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk({FunctionDef, AsyncFunctionDef}):
...         if (parent_scope := f.parent_named_scope()).is_funcdef:  # func in a func
...             func_name = f.name
...             syms = f.scope_symbols(full=True)
...
...             # ignore any reference of function to itself
...             if func_name in syms['free']:
...                 del syms['free'][func_name]
...
...             # check if the inner function uses explicit or implicit nonlocals
...             if syms['nonlocal'] or syms['free']:
...                 continue
...
...             # check if any function args defaults use variables
...             if next(f.args.walk(Name), False):
...                 continue
...
...             # build global name from enclosing scopes
...             global_name = f'{parent_scope.name}_{func_name}'
...             top_scope = parent_scope
...
...             while up_scope := top_scope.parent_named_scope(mod=False):
...                 top_scope = up_scope
...                 global_name = f'{top_scope.name}_{global_name}'
...
...             # replace all occurrences of original inner name with new global one
...             # we do this first so that it includes the function being moved
...             for g in parent_scope.walk(Name):
...                 if g.id == func_name:
...                     g.replace(global_name)
...
...             f = f.cut()
...             f.name = global_name
...
...             # insert just before our top-level scope
...             fst.body.insert(f, top_scope.pfield.idx, pep8space=1)
...
...     return fst.src
```

```py
>>> src = r"""
... def get_lookup(val):
...     if not val:
...         return
...
...     def closure():  # can't pull out because of closure
...         return val[0]
...
...     def default_arg(val=val):  # can't pull out because of default arg
...         return val[0]
...
...     def safe(val):  # safe to pull out
...         return val[0]
...
...     return closure, default_arg, safe
...
... class cls:
...     def method1(self, a, b):
...         def fib(n):  # recursive for fun
...             if n <= 1:
...                 return n
...
...             return fib(n - 1) + fib(n - 2)
...
...         return fib(n)
... """.strip()
```

Original:

```py
>>> pprint(src)
def get_lookup(val):
    if not val:
        return
 
    def closure():  # can't pull out because of closure
        return val[0]
 
    def default_arg(val=val):  # can't pull out because of default arg
        return val[0]
 
    def safe(val):  # safe to pull out
        return val[0]
 
    return closure, default_arg, safe
 
class cls:
    def method1(self, a, b):
        def fib(n):  # recursive for fun
            if n <= 1:
                return n
 
            return fib(n - 1) + fib(n - 2)
 
        return fib(n)
```

Processed:

```py
>>> pprint(pull_out_inner_funcs_safely(src))
def get_lookup_safe(val):  # safe to pull out
    return val[0]
 
def get_lookup(val):
    if not val:
        return
 
    def closure():  # can't pull out because of closure
        return val[0]
 
    def default_arg(val=val):  # can't pull out because of default arg
        return val[0]
 
    return closure, default_arg, get_lookup_safe
 
def cls_method1_fib(n):  # recursive for fun
    if n <= 1:
        return n
 
    return cls_method1_fib(n - 1) + cls_method1_fib(n - 2)
 
class cls:
    def method1(self, a, b):
        return cls_method1_fib(n)
```


## `lambda` to `def`

Maybe you have too many lambdas and want proper function defs for debugging or logging or other tools. Note the defs are
left in the same scope in case of nonlocals.

```py
>>> def lambdas_to_defs(src):
...     fst = FST(src, 'exec')
...     indent = fst.indent  # to show its there, inferred from src, single level str
...
...     for f in fst.walk(Assign):
...         if (f.value.is_Lambda
...             and f.targets[0].is_Name
...             and len(f.targets) == 1   # for demo purposes just deal with this case
...         ):
...             flmb = f.value
...             fdef = FST(f"""
... def {f.targets[0].id}({flmb.args.src}):
... {indent}return _
...                 """.strip())  # template
...             fdef.body[0].value = flmb.body.copy()
...
...             # explicitly preserve lambda line comment
...             fdef.put_line_comment(f.get_line_comment(full=True), full=True)
...
...             f.replace(
...                 fdef,
...                 trivia=(False, 'line'),  # eat line comment but not leading
...                 pep8space=1,  # don't doublespace inserted func def (at mod scope)
...             )
...
...     return fst.src
```

```py
>>> src = r"""
... # lambda comment
... mymin = lambda a, b: a if a < b else b  # inline lambda comment
...
... # class comment
... class cls:
...         name = lambda self: str(self)
...
...         def method(self, a, b):
...                 add = lambda a, b: a + b
...
...                 return add(a, b)
... """.strip()
```

Original:

```py
>>> pprint(src)
# lambda comment
mymin = lambda a, b: a if a < b else b  # inline lambda comment
 
# class comment
class cls:
        name = lambda self: str(self)
 
        def method(self, a, b):
                add = lambda a, b: a + b
 
                return add(a, b)
```

Processed:

```py
>>> pprint(src := lambdas_to_defs(src))
# lambda comment
def mymin(a, b):  # inline lambda comment
        return a if a < b else b
 
# class comment
class cls:
        def name(self):
                return str(self)
 
        def method(self, a, b):
                def add(a, b):
                        return a + b
 
                return add(a, b)
```

Now lets also pull out the nested function.

```py
>>> pprint(pull_out_inner_funcs_safely(src))
# lambda comment
def mymin(a, b):  # inline lambda comment
        return a if a < b else b
 
def cls_method_add(a, b):
        return a + b
 
# class comment
class cls:
        def name(self):
                return str(self)
 
        def method(self, a, b):
                return cls_method_add(a, b)
```


## `isinstance()` to `__class__ is` / `in`

Maybe you realize that all your `isinstance()` checks are incurring a 1.3% performance penalty and you don't like that
so you want to replace them all in your codebase with direct class identity checks. This can be done for non-base
classes (like most `AST` types are).

```py
>>> NAMES = {
... 'Add', 'And', 'AnnAssign', 'Assert', 'Assign', 'AsyncFor', 'AsyncFunctionDef',
... 'AsyncWith', 'Attribute', 'AugAssign', 'Await', 'BinOp', 'BitAnd', 'BitOr',
... 'BitXor', 'BoolOp', 'Break', 'Call', 'ClassDef', 'Compare', 'Constant',
... 'Continue', 'Del', 'Delete', 'Dict', 'DictComp', 'Div', 'Eq', 'ExceptHandler',
... 'Expr', 'Expression', 'FloorDiv', 'For', 'FormattedValue', 'FunctionDef',
... 'FunctionType', 'GeneratorExp', 'Global', 'Gt', 'GtE', 'If', 'IfExp', 'Import',
... 'ImportFrom', 'In', 'Interactive', 'Interpolation', 'Invert', 'Is', 'IsNot',
... 'JoinedStr', 'LShift', 'Lambda', 'List', 'ListComp', 'Load', 'Lt', 'LtE',
... 'MatMult', 'Match', 'MatchAs', 'MatchClass', 'MatchMapping', 'MatchOr',
... 'MatchSequence', 'MatchSingleton', 'MatchStar', 'MatchValue', 'Mod', 'Module',
... 'Mult', 'Name', 'NamedExpr', 'Nonlocal', 'Not', 'NotEq', 'NotIn', 'Or',
... 'ParamSpec', 'Pass', 'Pow', 'RShift', 'Raise', 'Return', 'Set', 'SetComp',
... 'Slice', 'Starred', 'Store', 'Sub', 'Subscript', 'TemplateStr', 'Try', 'TryStar',
... 'Tuple', 'TypeAlias', 'TypeIgnore', 'TypeVar', 'TypeVarTuple', 'UAdd', 'USub',
... 'UnaryOp', 'While', 'With', 'Yield', 'YieldFrom', 'alias', 'arg', 'arguments',
... 'comprehension', 'keyword', 'match_case', 'withitem',
... }

>>> def isinstance_to_class_check(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk(Call):
...         if (f.func.is_Name
...             and f.func.id == 'isinstance'  # isinstance()
...         ):
...             ftest, ftype = f.args  # assume there are two for isinstance()
...             fparent = f.parent
...
...             # isinstance(..., one of NAMES)
...             if ftype.is_Name and ftype.id in NAMES:
...                 op, notop = 'is', 'is not'
...             # isinstance(..., (one of NAMES, ...))
...             elif (
...                 ftype.is_Tuple
...                 and all(g.is_Name and g.id in NAMES for g in f.args[1].elts)
...             ):
...                 op, notop = 'in', 'not in'
...             else:
...                 continue
...
...             # 'not isinstance()' -> '__class__ is not' / 'not in'
...             if fparent.is_UnaryOp and fparent.op.is_Not:
...                 f = fparent
...                 fparent = f.parent
...                 op = notop
...
...             fnew = FST(f'_.__class__ {op} _')
...
...             fnew.left.value.replace(ftest.copy())
...             fnew.comparators[0].replace(ftype.copy())
...
...             if fparent.is_NamedExpr:  # be nice and parenthesize ourselves here
...                 fnew.par()  # we know we are the .value
...
...             f.replace(fnew, pars=True)  # preserve our own pars if present
...
...     return fst.src
```

```py
>>> src = """
... def is_valid_target(asts: AST | list[AST]) -> bool:
...     \"\"\"Check if `asts` is a valid target for `Assign` or `For`
...     operations. Must be `Name`, `Attribute`, `Subscript`
...     and / or possibly nested `Starred`, `Tuple` and `List`.\"\"\"
...
...     stack = [asts] if isinstance(asts, AST) else list(asts)
...
...     while stack:
...         if isinstance(a := stack.pop(), (Tuple, List)):
...             stack.extend(a.elts)
...         elif isinstance(a, Starred):
...             stack.append(a.value)
...         elif not isinstance(a, (Name, Attribute, Subscript)):
...             return False
...
...     return True
... """.strip()
```

Original:

```py
>>> pprint(src)
def is_valid_target(asts: AST | list[AST]) -> bool:
    """Check if `asts` is a valid target for `Assign` or `For`
    operations. Must be `Name`, `Attribute`, `Subscript`
    and / or possibly nested `Starred`, `Tuple` and `List`."""
 
    stack = [asts] if isinstance(asts, AST) else list(asts)
 
    while stack:
        if isinstance(a := stack.pop(), (Tuple, List)):
            stack.extend(a.elts)
        elif isinstance(a, Starred):
            stack.append(a.value)
        elif not isinstance(a, (Name, Attribute, Subscript)):
            return False
 
    return True
```

Processed:

```py
def is_valid_target(asts: AST | list[AST]) -> bool:
    """Check if `asts` is a valid target for `Assign` or `For`
    operations. Must be `Name`, `Attribute`, `Subscript`
    and / or possibly nested `Starred`, `Tuple` and `List`."""
 
    stack = [asts] if isinstance(asts, AST) else list(asts)
 
    while stack:
        if (a := stack.pop()).__class__ in (Tuple, List):
            stack.extend(a.elts)
        elif a.__class__ is Starred:
            stack.append(a.value)
        elif a.__class__ not in (Name, Attribute, Subscript):
            return False
 
    return True
```


## Squash nested `with`s

Slice operations make this easy enough. We only do synchronous `with` here as you can't mix sync with async anyway. Yes
the alignment is ugly, it will eventually be done properly, first priority was functional correctness. The comment on
the `with ctx():` could be preserved explicitly but not doing it here, eventually will be automatic option.

```py
>>> def squash_nested_withs(src: str) -> str:
...     fst = FST(src, 'exec')
...
...     for f in fst.walk(With):  # we only get With nodes
...         while f.body[0].is_With:  # first child is another With
...             # append child items to ours
...             f.items.extend(f.body[0].items.copy(), trivia=(False, False))
...
...             f.put_slice(  # copy child body into our own
...                 f.body[0].get_slice(trivia=('all+', 'block'), cut=True),
...                 trivia=(False, False),
...             )
...
...     return fst.src
```

```py
>>> src = r"""
... # with comment
... with open(a) as f:
...     with (
...         lock1,  # first lock
...         func() as lock2,  # this gets preserved
...     ):
...         with ctx():  # this does not belong to ctx()
...             # body comment
...             pass
...             # end body comment
...
... # post-with comment
... """.strip()
```

Original:

```py
>>> pprint(src)
# with comment
with open(a) as f:
    with (
        lock1,  # first lock
        func() as lock2,  # this gets preserved
    ):
        with ctx():  # this does not belong to ctx()
            # body comment
            pass
            # end body comment
 
# post-with comment
```

Processed:

```py
>>> pprint(squash_nested_withs(src))
# with comment
with (open(a) as f,
     lock1,  # first lock
     func() as lock2,  # this gets preserved
     ctx()
     ):
    # body comment
    pass
    # end body comment
 
# post-with comment
```


## Add decorator to class methods

This one is very simple, we just want to add our own decorator to all class methods, not normal functions, with the
constraint that it be as close to the function as possible but not after a `@contextmanager`.

```py
>>> def insert_decorator_to_class_methods(src: str) -> str:
...     fst = FST(src, 'exec')
...
...     for f in fst.walk({FunctionDef, AsyncFunctionDef}):
...         if f.parent.is_ClassDef:
...             if any((deco := d).is_Name and d.id == 'contextmanager'
...                    for d in f.decorator_list):
...                 idx = deco.pfield.idx
...             else:
...                 idx = 'end'
...
...             f.decorator_list.insert('@our_decorator', idx, trivia=False)
...
...     return fst.src
```

```py
>>> src = r"""
... def normal_function():
...     ...
...
... class SomeClass:
...     @staticmethod
...     def get_options() -> dict[str, Any]:
...         ...
...
...     # class comment
...     @classmethod
...     def get_cls_option(option: str, options: Mapping[str, Any] = {}) -> object:
...         ...
...
...     # another class comment
...     async def set_async_inst_options(**options) -> dict[str, Any]:
...         ...
...
...     @ \
... staticmethod
...     # intentionally screwy
...     @ (
...         contextmanager
...     )
...     def options(**options) -> Iterator[dict[str, Any]]:
...         ...
... """.strip()
```

Original:

```py
>>> pprint(src)
def normal_function():
    ...
 
class SomeClass:
    @staticmethod
    def get_options() -> dict[str, Any]:
        ...
 
    # class comment
    @classmethod
    def get_cls_option(option: str, options: Mapping[str, Any] = {}) -> object:
        ...
 
    # another class comment
    async def set_async_inst_options(**options) -> dict[str, Any]:
        ...
 
    @ \
staticmethod
    # intentionally screwy
    @ (
        contextmanager
    )
    def options(**options) -> Iterator[dict[str, Any]]:
        ...
```

Processed:

```py
>>> pprint(insert_decorator_to_class_methods(src))
def normal_function():
    ...
 
class SomeClass:
    @staticmethod
    @our_decorator
    def get_options() -> dict[str, Any]:
        ...
 
    # class comment
    @classmethod
    @our_decorator
    def get_cls_option(option: str, options: Mapping[str, Any] = {}) -> object:
        ...
 
    # another class comment
    @our_decorator
    async def set_async_inst_options(**options) -> dict[str, Any]:
        ...
 
    @ \
staticmethod
    # intentionally screwy
    @our_decorator
    @ (
        contextmanager
    )
    def options(**options) -> Iterator[dict[str, Any]]:
        ...
```


## Comprehension to loop

We build up a body and replace the original comprehension `Assign` statement with the new statements.

```py
>>> def list_comprehensions_to_loops(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if (f.is_Assign  # to show we can check here instead of passing to walk()
...             and f.value.is_ListComp
...             and f.targets[0].is_Name
...             and len(f.targets) == 1
...         ):
...             var = f.targets[0].id
...             fcomp = f.value
...             fcur = ftop = FST(f'{var} = []\n_', 'exec')
...             # the `_` will become first `for`
...
...             for fgen in fcomp.generators:
...                 ffor = FST('for _ in _:\n    _')  # for loop, just copy the source
...                 ffor.target = fgen.target.copy()
...                 ffor.iter = fgen.iter.copy()
...
...                 fcur = fcur.body[-1].replace(ffor)
...                 fifs = fgen.ifs
...                 nifs = len(fifs)
...
...                 if nifs:  # if no ifs then no test
...                     if nifs == 1:  # if single test then just use that
...                         ftest = fifs[0].copy()
...
...                     else:  # if multiple then join with `and`
...                         ftest = FST(' and '.join('_' * nifs))
...
...                         for i, fif in enumerate(fifs):
...                             ftest.values[i] = fif.copy()
...
...                     fifstmt = FST('if _:\n    _')
...                     fifstmt.test = ftest
...
...                     fcur = fcur.body[-1].replace(fifstmt)
...
...             # the ffor is the last one processed above (the innermost)
...             fcur.body[-1].replace(f'{var}.append({fcomp.elt.own_src()})')
...
...             f.replace(
...                 ftop,
...                 one=False,  # this allows to replace a single element with multiple
...                 trivia=(False, False)
...             )
...
...     return fst.src
```

```py
>>> src = r"""
... def f(k):
...     # safe comment
...     clean = [i for i in k]
...
...     # happy comment
...     messy = [
...         ( i )  # weird pars
...         for (
...             j
...         ) in k  # outer loop
...         if
...         j  # misc comment
...         and not validate(j)
...         for i in j  # inner loop
...         if i
...         if validate(i)
...     ]
...     # silly comment
...
...     return clean + messy
... """.strip()
```

Original:

```py
>>> pprint(src)
def f(k):
    # safe comment
    clean = [i for i in k]
 
    # happy comment
    messy = [
        ( i )  # weird pars
        for (
            j
        ) in k  # outer loop
        if
        j  # misc comment
        and not validate(j)
        for i in j  # inner loop
        if i
        if validate(i)
    ]
    # silly comment
 
    return clean + messy
```

Processed:

```py
>>> pprint(list_comprehensions_to_loops(src))
def f(k):
    # safe comment
    clean = []
    for i in k:
        clean.append(i)
 
    # happy comment
    messy = []
    for j in k:
        if (j  # misc comment
            and not validate(j)):
            for i in j:
                if i and validate(i):
                    messy.append(i)
    # silly comment
 
    return clean + messy
```


## Align equals

This is just here to show pure source modification without messing with the actual structure. It just walks everything
and stores all `Assign` nodes and any block of two or more nodes which start on consequtive lines and at the same column
get aligned. All the source put function does is offset `AST` node locations for source change. Same column is used as
proxy for verifying same parent.

```py
>>> def align_equals(fst):
...     flast = None
...     blocks = []  # [[feq1, feq2, ...], [feq1, ...], ...]
...
...     # first we build up list of contiguous Assign nodes
...     for f in fst.walk(Assign):
...         if not flast or f.col != flast.col or f.ln != flast.ln + 1:
...             blocks.append([])
...
...         blocks[-1].append(flast := f)
...
...     for block in blocks:
...         if len(block) > 1:
...             eq_col = max(f.targets[-1].pars().end_col for f in block)
...
...             for f in block:
...                 # we know this is all on one line by how we constructed it
...                 ln, _, _, end_col = f.targets[-1].pars()
...                 eq_str = f'{" " * (eq_col - end_col)} = '
...
...                 f.put_src(eq_str, ln, end_col, ln, f.value.pars().col, 'offset')
```

```py
>>> src = r"""
... a = 1
... this = that
... whatever[f].a   = "YAY!"
...
... on_multiple_lines = (
...     1, 2)
... we_dont_align = None
...
... ASTS_LEAF_FUNCDEF = {FunctionDef, AsyncFunctionDef}
... ASTS_LEAF_DEF = ASTS_LEAF_FUNCDEF | {ClassDef}
... ASTS_LEAF_DEF_OR_MOD = ASTS_LEAF_DEF | ASTS_LEAF_MOD
... ASTS_LEAF_FOR = {For, AsyncFor}
... ASTS_LEAF_WITH = {With, AsyncWith}
... ASTS_LEAF_TRY = {Try, TryStar}
... ASTS_LEAF_IMPORT = {Import, ImportFrom}
... """.strip()
```

Original:

```py
>>> pprint(src)
a = 1
this = that
whatever[f].a   = "YAY!"
 
on_multiple_lines = (
    1, 2)
we_dont_align = None
 
ASTS_LEAF_FUNCDEF = {FunctionDef, AsyncFunctionDef}
ASTS_LEAF_DEF = ASTS_LEAF_FUNCDEF | {ClassDef}
ASTS_LEAF_DEF_OR_MOD = ASTS_LEAF_DEF | ASTS_LEAF_MOD
ASTS_LEAF_FOR = {For, AsyncFor}
ASTS_LEAF_WITH = {With, AsyncWith}
ASTS_LEAF_TRY = {Try, TryStar}
ASTS_LEAF_IMPORT = {Import, ImportFrom}
```

Processed:

```py
>>> fst = FST(src, 'exec')
>>> align_equals(fst)  # we pass as an FST so we can `.dump()` below
>>> pprint(fst.src)
a             = 1
this          = that
whatever[f].a = "YAY!"
 
on_multiple_lines = (
    1, 2)
we_dont_align = None
 
ASTS_LEAF_FUNCDEF    = {FunctionDef, AsyncFunctionDef}
ASTS_LEAF_DEF        = ASTS_LEAF_FUNCDEF | {ClassDef}
ASTS_LEAF_DEF_OR_MOD = ASTS_LEAF_DEF | ASTS_LEAF_MOD
ASTS_LEAF_FOR        = {For, AsyncFor}
ASTS_LEAF_WITH       = {With, AsyncWith}
ASTS_LEAF_TRY        = {Try, TryStar}
ASTS_LEAF_IMPORT     = {Import, ImportFrom}
```

Here we do a quick dump of the first three statements to show that all the locations of the nodes were offset properly.

```py
>>> _ = fst.body[:3].copy().dump('stmt')
Module - ROOT 0,0..2,22
  .body[3]
0: a             = 1
   0] Assign - 0,0..0,17
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Constant 1 - 0,16..0,17
1: this          = that
   1] Assign - 1,0..1,20
     .targets[1]
      0] Name 'this' Store - 1,0..1,4
     .value Name 'that' Load - 1,16..1,20
2: whatever[f].a = "YAY!"
   2] Assign - 2,0..2,22
     .targets[1]
      0] Attribute - 2,0..2,13
        .value Subscript - 2,0..2,11
          .value Name 'whatever' Load - 2,0..2,8
          .slice Name 'f' Load - 2,9..2,10
          .ctx Load
        .attr 'a'
        .ctx Store
     .value Constant 'YAY!' - 2,16..2,22
```


## Make all f-strings self-documenting

**Note:** This example in particular is Python 3.12+ because of the comment in the multiline f-string. The function
itself will work mostly on lower version Pythons.

Suppose you just want to improve the debug logs by adding self-documenting debug strings to all f-strings, e.g.
`f"{var}"` into `f"{var=}"`. The example below shows how, though there is just one caveat to look out for if you want to
continue working with the `AST` tree:

The source is updated and all the node locations are fine, but the `put_src(..., action='offset')` only offsets node
locations and does not create the `AST` nodes for any new `Constant` strings due to the newly self-documenting
`FormattedValue` nodes. If you only care about source for output (like this example) then this is a non-issue. If you
need those nodes to continue working with an `AST` tree then you can do a `root.reparse()` after making all the changes,
or individual `reparse()` on each modified statement, or use `put_src(..., action='reparse')` for each individual
change, but that would be slower.

```py
>>> def self_document_fstring_expressions(src: str) -> str:
...     fst = FST(src, 'exec')
...
...     for f in fst.walk(FormattedValue):  # could add Interpolation to do both
...         _, _, end_ln, end_col = f.value.pars()  # value end after parentheses
...
...         # hacky but valid way to check if '=' already there and not in comment
...         # between the end of the expression and end of FormattedValue
...         lines = f.get_src(end_ln, end_col, f.end_ln, f.end_col - 1, as_lines=True)
...
...         if not any(l.lstrip().startswith('=') for l in lines):
...             # insert the equals just after the expression
...             f.put_src('=', end_ln, end_col, end_ln, end_col, 'offset')
...
...     return fst.src
```

```py
>>> src = """
... f'added here {a}, and here { ( b ) }'
...
... f'not added here {c=}'
...
... f\"\"\"{(  # =========================
...     d,  # commented out =, so added
... )}, {e
...     =} <- not commented out so not added\"\"\"
... """.strip()
```

Original:

```py
>>> pprint(src)
f'added here {a}, and here { ( b ) }'
 
f'not added here {c=}'
 
f"""{(  # =========================
    d,  # commented out =, so added
)}, {e
    =} <- not commented out so not added"""
```

Processed:

```py
f'added here {a=}, and here { ( b )= }'
 
f'not added here {c=}'
 
f"""{(  # =========================
    d,  # commented out =, so added
)=}, {e
    =} <- not commented out so not added"""
```


## Normalize docstrings

`get_docstr()` gives you a normal string and `put_docstr()` puts it with appropriate formatting for a docstring. In this
case we also pass `reput=True` because we specifically want it to remove and then put the docstring expression again so
that it precedes any comments. Otherwise it just replaces the docstring in the location where it currently is.

```py
>>> def normalize_docstrings(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if f.has_docstr:
...             f.put_docstr(f.get_docstr(), reput=True)
...
...     return fst.src
```

```py
>>> src = """
... class cls:
...     # docstr should be before this
...     "Some\\nunformatted\\ndocstr."  # what is this?!?
...
...     def method(self):
...
...         \"\"\"I'm not
...     even properly
... aligned!!! \\U0001F92a
...         Or am I\\x3f\"\"\"
...         # comment
...
...         pass
... """.strip()
```

Original:

```py
>>> pprint(src)
class cls:
    # docstr should be before this
    "Some\nunformatted\ndocstr."  # what is this?!?
 
    def method(self):
 
        """I'm not
    even properly
aligned!!! \U0001F92a
        Or am I\x3f"""
        # comment
 
        pass
```

Processed:

```py
class cls:
    """Some
    unformatted
    docstr."""
 
    # docstr should be before this
    # what is this?!?
 
    def method(self):
        """I'm not
        even properly
        aligned!!! 🤪
        Or am I?"""
 
        # comment
 
        pass
```


## Reparenthesize expressions

Parentheses are handled completely automatically normally and you can use this mechanism to clean up unnecessary
or ugly parenthesization. Yes we realize some unnecessary parenthesization may be dictated by the currently enforced
aesthetic paradigm of any given project. This is just to show proper functional parenthesization by `fst`.

```py
>>> def reparenthesize_simple(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if f.is_parenthesizable():
...             f.replace(f.copy())
...
...     return fst.src
```

```py
>>> src = r"""
... (x * y) * (a + b)  # "x * y" doesn't need pars, 'a + b' does
...
... (x * y) * z  # "x * y" is unpard because doesn't change tree structure
...
... x * (y * z)  # not unpard because would change structure (order of operations)
...
... a + ( (  (y) * (z)))  # nested pars cleaned up
...
... x * ( (  (y) * (z)))  # original pars normally left if needed, unless unpar() used
...
... if (
...     (a <= b)
... ):  # not needed
...     return (a  # hello
...             < b)  # needed for parsability
...
... match ("a"  # implicit string pars needed
...        "b"):
...     case ((1) | (a)):  # unnecessary pars
...         pass
...     case (a, b):  # MatchSequence node intrinsic pars are not removed
...         pass
...     case ( ( (a, b) ) ):  # but the unnecessary ones are
...         pass
... """.strip()
```

Original:

```py
>>> pprint(src)
(x * y) * (a + b)  # "x * y" doesn't need pars, 'a + b' does
 
(x * y) * z  # "x * y" is unpard because doesn't change tree structure
 
x * (y * z)  # not unpard because would change structure (order of operations)
 
a + ( (  (y) * (z)))  # nested pars cleaned up
 
x * ( (  (y) * (z)))  # original pars normally left if needed, unless unpar() used
 
if (
    (a <= b)
):  # not needed
    return (a  # hello
            < b)  # needed for parsability
 
match ("a"  # implicit string pars needed
       "b"):
    case ((1) | (a)):  # unnecessary pars
        pass
    case (a, b):  # MatchSequence node intrinsic pars are not removed
        pass
    case ( ( (a, b) ) ):  # but the unnecessary ones are
        pass
```

Processed:

```py
>>> pprint(reparenthesize_simple(src))
x * y * (a + b)  # "x * y" doesn't need pars, 'a + b' does
 
x * y * z  # "x * y" is unpard because doesn't change tree structure
 
x * (y * z)  # not unpard because would change structure (order of operations)
 
a + y * z  # nested pars cleaned up
 
x * ( (  y * z))  # original pars normally left if needed, unless unpar() used
 
if a <= b:  # not needed
    return (a  # hello
            < b)  # needed for parsability
 
match ("a"  # implicit string pars needed
       "b"):
    case 1 | a:  # unnecessary pars
        pass
    case (a, b):  # MatchSequence node intrinsic pars are not removed
        pass
    case (a, b):  # but the unnecessary ones are
        pass
```

A slight tweak to the function to unparenthesize first will force reparenthesize of parentheses which are needed but may
not have been in normal locations to begin with.

```py
>>> def reparenthesize_full(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if f.is_parenthesizable():
...             f.unpar().replace(f.copy())
...
...     return fst.src
```

```py
>>> pprint(reparenthesize_full(r"""
... a + ( (  (y) * (z)))  # nested pars cleaned up
...
... x * ( (  (y) * (z)))  # original pars normally left if needed, unless unpar() used
... """.strip()))
a + y * z  # nested pars cleaned up
 
x * (y * z)  # original pars normally left if needed, unless unpar() used
```


## Instrument expressions

Suppose there is an external library that overloaded some operators and there are problems and you want to log all the
operations (or do something else with them). This is the type of problem that `fst` was conceived to solve easily. The
instrumentation is ugly but is meant to show that all these nested manipulations maintain the correct working source.

Note that this instrumentation counts on the fact that the syntactic order of the children of these particular node
types is actually the order they will be evaluated in. This is not always the case, e.g. with the `IfExp` node the
middle gets evaluated first `THEN_THIS if FIRST_THIS else OR_THEN_THIS`.

```py
>>> def instrument_operations(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if getattr(f, '_dirty', False):  # did we generate this?
...             continue
...
...         if f.is_BinOp:
...             fargs = [f.left, f.right]
...         elif f.is_UnaryOp:
...             fargs = [f.operand]
...         elif f.is_Compare:
...             fargs = [f.left, *f.comparators]
...         else:
...             continue
...
...         for g in f.parents():  # make sure we don't overwrite vars in use by parent
...             if (base := getattr(g, '_base_idx', None)) is not None:
...                 break
...         else:
...             base = 0
...
...         nargs = len(fargs)
...         ftmps = ', '.join(f'_{i + base}' for i in range(nargs))
...         fsettmps = ', '.join(f'_{i + base} := _' for i in range(nargs))
...
...         fnew = FST(f'({fsettmps}, log({f.src!r}, {ftmps}), _)[{nargs + 1}]')
...         felts = fnew.value.elts
...
...         for i in range(nargs):
...             felts[i].value.replace(fargs[i].copy())
...             fargs[i].replace(f'_{i + base}')
...
...         fold = felts[-1].replace(f.copy())  # put operation using temp vars
...         fnew = f.replace(fnew)
...
...         fold._dirty = True  # must set after the replace because FST may change
...         fnew._base_idx = base + nargs - 1  # safe start idx for children to use
...
...     return fst.src
```

```py
>>> src = r"""
... def shape_score(a, b, c, d):
...     x = (a * b) - -(c + d)
...     y = ~(a - c) + (b ^ d)
...     z = (x // (abs(y) or 1))
...
...     return (z < 0) * -z + (z >= 0) * +z
... """.strip()
```

Original:

```py
>>> pprint(src)
def shape_score(a, b, c, d):
    x = (a * b) - -(c + d)
    y = ~(a - c) + (b ^ d)
    z = (x // (abs(y) or 1))
 
    return (z < 0) * -z + (z >= 0) * +z
```

Processed:

```py
>>> pprint(inst := instrument_operations(src))
def shape_score(a, b, c, d):
    x = (_0 := (_1 := a, _2 := b, log('a * b', _1, _2), _1 * _2)[3], _1 := (_1 := (_1 := c, _2 := d, log('c + d', _1, _2), _1 + _2)[3], log('-(c + d)', _1), -_1)[2], log('(a * b) - -(c + d)', _0, _1), _0 - _1)[3]
    y = (_0 := (_1 := (_1 := a, _2 := c, log('a - c', _1, _2), _1 - _2)[3], log('~(a - c)', _1), ~_1)[2], _1 := (_1 := b, _2 := d, log('b ^ d', _1, _2), _1 ^ _2)[3], log('~(a - c) + (b ^ d)', _0, _1), _0 + _1)[3]
    z = (_0 := x, _1 := abs(y) or 1, log('x // (abs(y) or 1)', _0, _1), _0 // _1)[3]
 
    return (_0 := (_1 := (_2 := z, _3 := 0, log('z < 0', _2, _3), _2 < _3)[3], _2 := (_2 := z, log('-z', _2), -_2)[2], log('(z < 0) * -z', _1, _2), _1 * _2)[3], _1 := (_1 := (_2 := z, _3 := 0, log('z >= 0', _2, _3), _2 >= _3)[3], _2 := (_2 := z, log('+z', _2), +_2)[2], log('(z >= 0) * +z', _1, _2), _1 * _2)[3], log('(z < 0) * -z + (z >= 0) * +z', _0, _1), _0 + _1)[3]
```

Now lets compile and execute these functions to make sure everything still works.

```py
>>> def log(s, *args):  # log function for the instrumented code
...    print(f'src: {s!r}, args: {args}')

>>> exec(src, original_ns := {})
>>> exec(inst, inst_ns := {'log': log})

>>> original_shape_score = original_ns['shape_score']
>>> inst_shape_score = inst_ns['shape_score']
```

Here we execute them the with the same sets of values to make sure everything comes out the same. In addition, the
instrumented code will log the source being executed and the arguments to those expressions (or do whatever else you
want the log function to do).

```py
>>> print(original_shape_score(1, 2, 3, 4))
1

>>> print(inst_shape_score(1, 2, 3, 4))
src: 'a * b', args: (1, 2)
src: 'c + d', args: (3, 4)
src: '-(c + d)', args: (7,)
src: '(a * b) - -(c + d)', args: (2, -7)
src: 'a - c', args: (1, 3)
src: '~(a - c)', args: (-2,)
src: 'b ^ d', args: (2, 4)
src: '~(a - c) + (b ^ d)', args: (1, 6)
src: 'x // (abs(y) or 1)', args: (9, 7)
src: 'z < 0', args: (1, 0)
src: '-z', args: (1,)
src: '(z < 0) * -z', args: (False, -1)
src: 'z >= 0', args: (1, 0)
src: '+z', args: (1,)
src: '(z >= 0) * +z', args: (True, 1)
src: '(z < 0) * -z + (z >= 0) * +z', args: (0, 1)
1
```

```py
>>> print(original_shape_score(3, 2, 3, 4))
2

>>> print(inst_shape_score(3, 2, 3, 4))
src: 'a * b', args: (3, 2)
src: 'c + d', args: (3, 4)
src: '-(c + d)', args: (7,)
src: '(a * b) - -(c + d)', args: (6, -7)
src: 'a - c', args: (3, 3)
src: '~(a - c)', args: (0,)
src: 'b ^ d', args: (2, 4)
src: '~(a - c) + (b ^ d)', args: (-1, 6)
src: 'x // (abs(y) or 1)', args: (13, 5)
src: 'z < 0', args: (2, 0)
src: '-z', args: (2,)
src: '(z < 0) * -z', args: (False, -2)
src: 'z >= 0', args: (2, 0)
src: '+z', args: (2,)
src: '(z >= 0) * +z', args: (True, 2)
src: '(z < 0) * -z + (z >= 0) * +z', args: (0, 2)
2
```

```py
>>> print(original_shape_score(3, -1, 9, 4))
10

>>> print(inst_shape_score(3, -1, 9, 4))
src: 'a * b', args: (3, -1)
src: 'c + d', args: (9, 4)
src: '-(c + d)', args: (13,)
src: '(a * b) - -(c + d)', args: (-3, -13)
src: 'a - c', args: (3, 9)
src: '~(a - c)', args: (-6,)
src: 'b ^ d', args: (-1, 4)
src: '~(a - c) + (b ^ d)', args: (5, -5)
src: 'x // (abs(y) or 1)', args: (10, 1)
src: 'z < 0', args: (10, 0)
src: '-z', args: (10,)
src: '(z < 0) * -z', args: (False, -10)
src: 'z >= 0', args: (10, 0)
src: '+z', args: (10,)
src: '(z >= 0) * +z', args: (True, 10)
src: '(z < 0) * -z + (z >= 0) * +z', args: (0, 10)
10
```
'''
