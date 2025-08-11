## 0.2.1 - alpha - ????-??-??

### Fixed

- parse functions handle trailing comments without newlines correctly
- unparse tuple with slices removes tuple parentheses

### Added

- verify() invalid AST slices works
- get_mode() gets parse mode for any FST, including invalid AST slices

### Updated

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
