# Overview

This module exists in order to facilitate quick and easy editing of Python source while preserving formatting. It deals automatically with all the silly nonsense like indentation, parentheses, commas, comments, docstrings, semicolons, line continuations, precedence, decorator @ signs, else vs. elif and lots and lots of niche special cases. It is meant to be a high level way of modifying some code while maintaining the rest of the file unchanged.

`pfst` provides its own comprehensive format-preserving operations for AST trees, but also allows the AST tree to be changed by anything else outside of its control and can then automatically reconcile the changes with what it knows to preserve formatting where possible.

It works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provides the interface to the source-preserving operations.  The fact that it just extends existing `AST` nodes means that the AST tree can be used as normal anywhere that AST is used, and later `unparsed()` with formatting preserved where it can be. The degree to which formatting is preserved depends on how many operations are executed natively through FST mechanisms and how well FST reconcile works for operations which are not.

`pfst` does not do any parsing of its own but rather relies on the builtin Python parser and unparser so it stays 100% compliant. This means you get perfect parsing but also that it is limited to the syntax of the running Python version, but many options exist for running any specific verion of Python.

`pfst` does basic validation but will not prevent you from burning yourself if you really want to.

# Examples

```py
```






## TODO=

* Reconcile.

* Put one to `FormattedValue` / `Interpolation` `conversion` and `format_spec`, `JoinedStr` / `TemplateStr` `values`.

* Prescribed (non-raw) get / put slice from / to:
  * `FunctionDef.decorator_list`
  * `AsyncFunctionDef.decorator_list`
  * `ClassDef.decorator_list`
  * `ClassDef.bases`
  * `Delete.targets`
  * `Assign.targets`
  * `BoolOp.values`
  * `Call.args`
  * `comprehension.ifs`
  * `ListComp.generators`
  * `SetComp.generators`
  * `DictComp.generators`
  * `GeneratorExp.generators`
  * `ClassDef.keywords`
  * `Call.keywords`
  * `Import.names`
  * `ImportFrom.names`
  * `With.items`
  * `AsyncWith.items`
  * `MatchSequence.patterns`
  * `MatchMapping.patterns`
  * `MatchClass.patterns`
  * `MatchOr.patterns`
  * `FunctionDef.type_params`
  * `AsyncFunctionDef.type_params`
  * `ClassDef.type_params`
  * `TypeAlias.type_params`
  * `Global.names`
  * `Nonlocal.names`
  * `JoinedStr.values`
  * `TemplateStr.values`

* Redo comment handling, where to `put()` wrt comments, interface for modifying just those.


## Trivia

The "F" in FST stands for "Fun".
