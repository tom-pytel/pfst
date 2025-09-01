## 0.2.1 - alpha - ????-??-??

### Fixed

- fix detect tuple `((1)+1),(1)` as not delimited
- set `Starred` location correctly after unparenthesize of its value
- don't parenthesize `Starred.value` multiple times if already has parentheses
- handle multiline import aliases correctly
- fix some negative indexing get / put cases
- never automatically add parentheses to copied Slice
- disallow Starred as a target to Delete
- allow put to except and case slices
- allow put any kind of expression slice to tuple, including Slices
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
- lots of code cleanups


## 0.2.0 - alpha - 2025-08-07

### Fixed

- statementish cut marks tree as modified
- undelimited sequence operations joining alphanumerics
- disallow merge of `1.` float literal directly to left of alphanumeric
- put to `ImportFrom.module` with dot following directly after 'from'

### Added
s
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
