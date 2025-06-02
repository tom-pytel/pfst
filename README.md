# Overview

This module exists in order to facilitate quick and easy editing of Python AST trees while preserving formatting (yes, "`AST` tree" is redundant). It deals with all the silly nonsense like indentation, parentheses, commas, comments, docstrings, semicolons, line continuations, precedence, decorator @ signs, else vs. elif, nodes without locations, PEP8 function spacing, Dict '\*\*d' keys `AST`s being `None`, line continuation backslashes at start of line being a noop, lone starred expression in a slice being a tuple without commas, deletions from a set leaving invalid empty curlies "{}" (change to "{\*()}"), generator expression as the only argument to a function call sharing its enclosing parentheses with the call arguments, lone parenthesized tuple in unparenthesized `With.items` left after delete of optional_vars needing grouping parentheses added in order to avoid converting tuple elements to new `withitem`s, and lots more!

`pfst` works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provides the interface for source-preserving operations. The fact that it just extends existing `AST` nodes means that the `AST` tree can be used as normal and later `unparsed()` with formatting preserved where it can be. The degree to which formatting is preserved depends on how many operations are executed natively through `FST` mechanisms and how well `reconcile()` works for operations which are not.

`pfst` does not do any parsing of its own but rather relies on the builtin Python parser and unparser so it stays 100% compliant. This also means it is limited to the syntax of the running Python version.


















## Todo

* Reconcile AST nodes modified not using FST machinery.
* Individual sequence slice non-raw paths.
* Redo comment handling, where to put wrt comments, interface for modifying just those.
* Redo sequence slices for same comment behavior as statements.
* Support put/get/parse JoinedStr/FormattedValue and TemplateStr/Interpolation.

Trivia: The "F" in FST stands for "Fun".
