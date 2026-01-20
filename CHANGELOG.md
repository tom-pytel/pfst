## 0.2.6 - alpha - ????-??-??

### Fixed

- fixed parse `withitem` of a solo `GeneratorExp`
- allow put `Starred` to `TypeVarTuple.default_value`
- don't try to parse `*starred = value` as `TypeVarTuple` in place of `Assign` on py < 3.13
- don't accept `Starred` node for a `withitem`, `_withitems` normal or `_comprehension_ifs` coerce
- fixed parse of unparenthesized tuple with trailing comma to `_Assign_targets`
- fixed parse location correction of multiline unparenthesized tuple with group parenthesized first and / or last elements
- fixed delimit of whole node at root when degenerate last line has line continuation without trailing newline
- `FST.dump()` will no longer output trailing whitespace on lines when the line is completely empty, better for tests
- fixed `comprehension_ifs` and `_arglikes` coercions where unparenthesized tuple needed to be parenthesized

### Added

- coercion expanded greatly
  - a lot more coercion cases allowed
    - `pattern`, `arguments`, `arg`, `alias`, `withitem`, `TypeVar` and `TypeVarTuple` to `expr`
    - custom slice types `_Assign_targets`, `_decorator_list`, `_arglikes`, `_comprehension_ifs`, `_aliases`, `_withitems` and `_type_params` to `Tuple`, `List` or `Set`
    - all sequence types, custom and standard, to custom slice types
    - all expressions and custom slice types to `pattern`
  - `FST.as_(mode)` for explicit coercion directly to `mode` (which can be an explicit `type[AST]` or a parse mode)
  - `FST(FST, mode)` for constructor default non-destructive coerce copy from other `FST` node, a-la `list(other_list) is not other_list`
  - `FST(AST, mode)` and `FST.fromast(AST, type[AST] or mode)` can use the new coercion to convert `AST`
  - put slice as `one=True` for `_Assign_targets`, `_decorator_list`, `_arglikes`, `_comprehension_ifs`, `_aliases`, `_withitems`, `_type_params` and `_expr_arglikes`

### Updated

- **BREAKING CHANGE** for consistency
  - when putting source instead of an `FST` or `AST` node directly as a slice to an expression, if the source is a delimited sequence then it will always be put as one node and not unpacked
  - previous behavior of `.put_slice('[1, 2, 3]')` being put as a slice of three distinct elements can be selected by passing `one=None`
- parse `withitem` and `_withitems` no longer accept single unparenthesized `Yield`, `NamedExpr` or `Tuple` as a convenience, causes too many problems downstream
- improved put multiline slice aesthetics, specifically better needs-own-line detection and keeping line comment on pre-insert element line instead of moving it
- REMOVED `norm_put` option as was too annoying to maintain everywhere needed for the little good it did, `norm_self` and `norm_get` remain
- allow put `Starred` to `value` field of `Expr`, `Return`, `AnnAssign` and `Yield` even though not compilable, for consistency, our metric is parsability, not compilability
- `parse_withitem('x,')` now parses to singleton `Tuple` `withitem` instead of single `Name` `withitem` with trailing comma, makes more sense
- concretized behavior of put slice with `one=True` for custom special slices, will not put multiple elements now in this mode when one requested
- `FST.dump()` returns `self` when not returning str or lines and those are now specified with `out='str'` or `out='lines'`

## 0.2.5 - alpha - 2026-01-06

### Fixed

- fixed parenthesize copied multiline walrus not being parenthesized for parsability if `pars_walrus=False`
- update parent nodes' end locations correctly when a raw put to an elif completely removes it without replacing with anything
- insert extra line at end when force-parenthesizing an expression at root that has a last line as a comment
- diallow parenthesization of immediate string `Constant` children of f/t-strings
- fixed delimit whole root node error when last line was a comment
- fixed `MatchMapping` single-element operation indexing of `rest` if present
- fixed parse single-element undelimited `MatchSequence` to include trailing comma
- disallowed putting already parenthesized elements to top level of `Import/ImportFrom.names` and `With/AsyncWith.items`
- gave `AsyncWith` put one the correct handler, was missing cases because was doing normal expression put
- `put_src(action='offset')` exactly on `FormattedValue` or `Interpolation` debug expression will update the preceding debug string `Constant` correctly
- fixed `replace()` end of sequence with empty slice while using `one=False` returns `None` instead of raising
- fixed minor type_params non-existent brackets location bug due to use of `loc` instead of `bloc`
- fixed syntax order bug in `walk()` for multiple mixed `Starred` and `keywords`, `*a, b=c, *d, e=f, etc...`
- fixed some `walk(scope=True)` incorrectly included / excluded nodes from function defs

### Added

- `reparse()` to force reparse of `AST` tree from source
- prescribed slicing for `Call.args+keywords` and `_args` virtual field
- prescribed slicing for `ClassDef.bases+keywords` and `_bases` virtual field
- prescribed slicing for `Call.keywords`
- prescribed slicing for `ClassDef.keywords`
- `insert()`, `append()`, `extend()`, `prepend()`, `prextend()` convenience functions to `FST` class, work same as `fstview` versions
- `__getitem__()` and friends to `FST` class to access default field.
- `own_src()` and `own_lines()` to efficiently get dedented code without having to `copy().src`
- `ast_src()` to quickly get unparsed source with formatting stripped
- `get_line_comment()` and `put_line_comment()` for easy get and set statement line comments
- `_body` virtual field for accessing block statement bodies leaving any possibly present docstr unchanged
- dummy view for nonexistent list fields from higher python versions on lower ones
- new coercions on put: `arg` to `arguments`, `withitem` to `expr`
- basic options checking in all functions which take them, make sure all passed are actual options
- `FST` slice views validate and truncate indices as needed for modifications elsewhere
- added `set_docstr()` which formats and indents string to put
- pre-generate `AST` type check predicates instead of on import, faster execution
- pre-generate `AST` field accessors instead of on import, faster execution
- `FST.is_alive` to check if node has been removed or replaced
- `FST.scope_symbols()` to get the names used in a scope

### Updated

- `par(force='unsafe')` parenthesizes anything, `par(force=True)` only what is syntactically valid
- recognize line comment after a trailining statement semicolon as belonging to the statement
- `copy()` can strip non-node source from root node copy using parameter `whole=False` (which can handle trivia ops at root)
- can control optional parenthesization of cut / put `Tuple` slices via `pars` option
- implemented trivia specification by absolute line numbers for statementlikes so can enable for all
- implemented `coerce` option for `MatchOr` and `MatchSequence`
- removed `matchor_norm` option, didn't make sense
- pass through more specific `SyntaxError` information from our extended parsing
- filled out test coverage for all modules
- simplified `reconcile()` usage, user doesn't need to preserve explicit "marked" copy
- add negative and `'end'` index options to `get_src()` and `put_src()`
- change get/put index specification to use 0 to `'end'` instead of archaic `None` and `False` for the slice endpoints
- `FST.type_params` on py < 3.12 and `.default_value` on py < 3.13 give dummy values
- `fstview` can represent unbounded field list, can grow as well as shrink with modifications outside the view
- changed `.docstr` to `get_docstr()` which now dedents returned string
- made some more useful predicate functions public
- optimized some internal offset and syntax ordering functions
- `walk()` allows parent nodes to be modified
- all traversal functions can take container of `AST` types to filter traversal
- cleaned up and optimized traversal functions
- optimized lots of `isinstance()` and `issubclass()` to check directly by class


## 0.2.4 - alpha - 2025-12-08

### Fixed

- fixed raw reparse of top level `match_case` or `ExceptHandler` when the change is only in the block header which is at column / line 0
- put slice to last element of undelimited sequence as value of `FormattedValue` or `Interpolation` with format string immediately following will offset that format string location correctly
- correct `.bloc` location if decorator `@` is on a different line with line continuations
- leave leading `\` above statement being deleted if trailing semicolon is left in place on stmt line
- account for degenerate case of first decorator following line continuation in `.bloc`

### Added

- `FST.copy_ast()` to copy just the `AST` tree without any `FST` stuff
- allow `FST.replace()` as a slice operation if applicable (`.replace()` one statement with multiple)
- moved some other predicates from private to public code, e.g. `is_elif()`, etc...
- predicates for checking `AST` type in `FST`, e.g. `is_Name`, `is_Call`, `is_FunctionDef`, etc...
- `FST._all` virtual field slice view attribute access for `Dict`, `MatchMapping` and `Compare`
- `FST.docstr` property
- automatic coercion of nodes put as `AST` or `FST` to compatible types
- replacing all handlers in a `Try` or `TryStar` with the other kind will change the try `AST` to the other kind
- prescribed slicing for `Compare` (`left` + `comparators` as a single body)
- prescribed slicing for `BoolOp.values`
- prescribed slicing for `FunctionDef.decorator_list`
- prescribed slicing for `AsyncFunctionDef.decorator_list`
- prescribed slicing for `ClassDef.decorator_list`
- prescribed slicing for `comprehension.ifs`
- prescribed slicing for `ListComp.generators`
- prescribed slicing for `SetComp.generators`
- prescribed slicing for `DictComp.generators`
- prescribed slicing for `GeneratorExp.generators`
- option `norm_self` controls whether statementlike bodies can be zeroed out or not

### Updated

- lots of documentation updates
- allow put `Slice` to top level parenthesized `Tuple`
- `MatchMapping` slicing includes the `rest` element, more intuitive
- removed artificial distinction between `augop` and `binop`, now is just `operator`
- `.bloc` block statement last child line trailing comment
- change `pars_walrus` and `pars_arglike` to pure overrides
- default disable dump() color on win32
- code cleanups


## 0.2.3 - alpha - 2025-11-01

### Fixed

- fixed insert at `body[0]` after block header with comment deleting comment
- fixed several semicolon and unicode character position issues
- fixed forced grouping parenthesize `Starred` child location
- normalize identifier to put BEFORE checking against keyword *facepalm*
- fixed coerce `except*` `AST` slice to `FST`
- fixed put star `*` to parenthesized single-element non-star `ImportFrom.names`
- fixed get slice from start of unparenthesized tuple in f-string expression on py < 3.12
- fixed get format_spec escape sequences from `rf'{...:\xFF}'` string
- statementlike operations at end of source no longer add trailing newline
- multiline implicit strings with line continuations no longer considered unenclosed
- get one from `Compare` returns copied node instead of original
- never consider `bytes` as docstrings
- multiline f/t-strings joined by line continuations indented correctly
- put string `Expr` as `'strict'` docstr don't in/dedent if not first element

### Added

- put raw slice comma separated sequence to comma separated sequence handles trailing commas
- put raw one to empty `Lambda.args` inserts space between `lambda` keyword and `args`
- parse `Mode` includes names of all `AST` classes as well as the classes themselves
- `FST.is_expr_arglike` to determine if expression only valid in `Call.args` or `ClassDef.bases`
- `put_src()` "offset" and "no AST change" modes
- `find_loc()` simple find location in or containing given location
- `fst.parse()` handles `bytes` and `AST` as source
- `dump()` specifiable list indentation
- global options made thread-safe (thread local)

### Updated

- don't return trailing newline after comment in get statementlike
- `dump()` uses color when printing to a terminal and formats a little better
- improve indent infer to check solo block statements, `ExceptHandler`s and `match_case`s
- change `ExceptHandler`s and `match_case`s to use explicit slice type instead of `Module`
- restrict raw node puts to only modify existing, no delete or pure insert
- change `Compare` combined field indexing to not include `.left`, just `.ops` and `.comparators`
- `dump()` indicates trailing whitespace after stmts, including with trailing `;`
- recognize Devanagari and Hebrew for identifiers
- adapt statementlike operations to use new trivia parameters
- put slice source to `Call.args` and `ClassDef.bases` doesn't need trialing comma
- `get_src()` and `put_src()` clip and validate coordinates
- LOTS of code cleanups, refactor, clean up API


## 0.2.2 - alpha - 2025-09-23

### Fixed

- use Modifying context manager on `get_slice(..., cut=True)`
- recognize multiline parenthesized `ImportFrom.names` and `With.items` as enclosed
- fixed get one from field which can contain a value but is currently `None`
- fixed raw reparse of compound block header statement which has a line continuation in the header
- fixed raw reparse `TryStar` erroneously to `Try`
- fixed `par(force=True)` on delimited `Tuple` or `MatchSequence`
- disallowed put `Starred` to `Delete` `Tuple` or `List` elements

### Added

- prescribed slicing for `ClassDef.bases`
- prescribed slicing for `Call.args`
- prescribed slicing for `With.items`
- prescribed slicing for `AsyncWith.items`
- prescribed slicing for `Import.names`
- prescribed slicing for `ImportFrom.names`
- prescribed slicing for `Global.names`
- prescribed slicing for `Nonlocal.names`

### Updated

- reworked non-AST compatible slices to use custom `_slice` base `AST`
- generalized get / put one and slice test framework and added auto `AST` / `FST` put tests


## 0.2.1 - alpha - 2025-09-01

### Fixed

- fixed detect tuple `((1)+1),(1)` as not delimited
- set `Starred` location correctly after unparenthesize of its value
- don't parenthesize `Starred.value` multiple times if already has parentheses
- handle multiline import aliases correctly
- fixed some negative indexing get / put cases
- never automatically add parentheses to copied Slice
- disallowed Starred as a target to Delete
- allow put to except and case slices
- parse functions handle trailing comments without newlines correctly
- unparse tuple with slices removes tuple parentheses

### Added

- prescribed slicing for `Assign.targets`
- prescribed slicing for `Delete.targets`
- prescribed slicing for `FunctionDef.type_params`
- prescribed slicing for `AsyncFunctionDef.type_params`
- prescribed slicing for `ClassDef.type_params`
- prescribed slicing for `TypeAlias.type_params`
- if can't parenthesize to make parse-safe then will add line continuation backslashes
- slices put element indentation matches elements of target container
- verify() invalid-AST slices works
- get_mode() gets parse mode for any FST, including invalid-AST slices

### Updated

- reduced precedence of `NamedExpr.value` from ATOM to TEST (don't add unnecessary parentheses)
- added ParseError and cleaned up exception usage
- optimized _parse_all() which recognizes and parses any type of node source
- parse expressionlike elements don't have to start at beginning of line
- allow put any kind of expression slice to tuple, including Slices
- lots of code cleanups


## 0.2.0 - alpha - 2025-08-07

### Fixed

- statementlike cut marks tree as modified
- undelimited sequence operations joining alphanumerics
- disallowed merge of `1.` float literal directly to left of alphanumeric
- put to `ImportFrom.module` with dot following directly after 'from'

### Added

- trivia (comments and space) specification
- prescribed slicing for `MatchSequence.patterns`
- prescribed slicing for `MatchMapping.keys:patterns`
- prescribed slicing for `MatchOr.patterns`

### Updated

- redid expressionlike slicing to use new trivia
- split out more tests into separate files
- preserve comments on parenthesize tuple
- lots of code cleanups


## 0.1.1 - alpha - 2025-07-07

### Fixed

- disallowed parse naked `GeneratorExp`
- disallowed put wildcard `'_'` name to `MatchClass.cls`
- docs page filenames for github pages

### Added

- put one `ImportFrom.level`, `comprehension.is_async` and `Constant.kind`
- `pars_walrus` option

### Updated

- lots of code cleanups

## 0.1.0 - alpha - 2025-06-28

### Added

- first public version
