## 0.2.3 - alpha - ????-??-??

### Fixed

- statement-ish operations at end of source no longer add trailing newline
- multiline implicit strings with line continuations no longer considered unenclosed
- get one from `Compare` returns copied node instead of original
- never consider `bytes` as docstrings
- multiline f/t-strings joined by line continuations indented correctly
- put string `Expr` as `'strict'` docstr don't in/dedent if not first element

### Added

- `FST.is_expr_arglike` to determine if expression only valid in `Call.args` or `ClassDef.bases`
- `put_src()` "offset" and "no AST change" modes
- `find_loc()` simple find location in or containing given location
- `fst.parse()` handles `bytes` and `AST` as source
- `dump()` specifiable list indentation
- global options made thread-safe (thread local)

### Updated

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
