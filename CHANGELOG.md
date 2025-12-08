## 0.2.4 - alpha - 2025-12-08

### Fixed

- fix raw reparse of top level `match_case` or `ExceptHandler` when the change is only in the block header which is at column / line 0
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
- option `norm_self` controls whether statementish bodies can be zeroed out or not

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

- fix insert at `body[0]` after block header with comment deleting comment
- fix several semicolon and unicode character position issues
- fix forced grouping parenthesize `Starred` child location
- normalize identifier to put BEFORE checking against keyword *facepalm*
- fix coerce `except*` `AST` slice to `FST`
- fix put star `*` to parenthesized single element non-star `ImportFrom.names`
- fix get slice from start of unparenthesized tuple in f-string expression on py < 3.12
- fix get format_spec escape sequences from `rf'{...:\xFF}'` string
- statement-ish operations at end of source no longer add trailing newline
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

- don't return trailing newline after comment in get statementish
- `dump()` uses color when printing to a terminal and formats a little better
- improve indent infer to check solo block statements, `ExceptHandler`s and `match_case`s
- change `ExceptHandler`s and `match_case`s to use explicit slice type instead of `Module`
- restrict raw node puts to only modify existing, no delete or pure insert
- change `Compare` combined field indexing to not include `.left`, just `.ops` and `.comparators`
- `dump()` indicates trailing whitespace after stmts, including with trailing `;`
- recognize Devanagari and Hebrew for identifiers
- adapt statement-ish operations to use new trivia parameters
- put slice source to `Call.args` and `ClassDef.bases` doesn't need trialing comma
- `get_src()` and `put_src()` clip and validate coordinates
- LOTS of code cleanups, refactor, clean up API


## 0.2.2 - alpha - 2025-09-23

### Fixed

- use Modifying context manager on `get_slice(..., cut=True)`
- recognize multiline parenthesized `ImportFrom.names` and `With.items` as enclosed
- fix get one from field which can contain a value but is currently `None`
- fix raw reparse of compound block header statement which has a line continuation in the header
- fix raw reparse `TryStar` erroneously to `Try`
- fix `par(force=True)` on delimited `Tuple` or `MatchSequence`
- disallow put `Starred` to `Delete` `Tuple` or `List` elements

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

- fix detect tuple `((1)+1),(1)` as not delimited
- set `Starred` location correctly after unparenthesize of its value
- don't parenthesize `Starred.value` multiple times if already has parentheses
- handle multiline import aliases correctly
- fix some negative indexing get / put cases
- never automatically add parentheses to copied Slice
- disallow Starred as a target to Delete
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
- parse expressionish elements don't have to start at beginning of line
- allow put any kind of expression slice to tuple, including Slices
- lots of code cleanups


## 0.2.0 - alpha - 2025-08-07

### Fixed

- statementish cut marks tree as modified
- undelimited sequence operations joining alphanumerics
- disallow merge of `1.` float literal directly to left of alphanumeric
- put to `ImportFrom.module` with dot following directly after 'from'

### Added

- trivia (comments and space) specification
- prescribed slicing for `MatchSequence.patterns`
- prescribed slicing for `MatchMapping.keys:patterns`
- prescribed slicing for `MatchOr.patterns`

### Updated

- redid expressionish slicing to use new trivia
- split out more tests into separate files
- preserve comments on parenthesize tuple
- lots of code cleanups


## 0.1.1 - alpha - 2025-07-07

### Fixed

- disallow parse naked `GeneratorExp`
- disallow put wildcard `'_'` name to `MatchClass.cls`
- docs page filenames for github pages

### Added

- put one `ImportFrom.level`, `comprehension.is_async` and `Constant.kind`
- `pars_walrus` option

### Updated

- lots of code cleanups

## 0.1.0 - alpha - 2025-06-28

### Added

- first public version
