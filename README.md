# Overview

This module exists in order to facilitate quick and easy editing of Python AST trees while preserving formatting (yes, "`AST` tree" is redundant). It deals automatically with all the silly nonsense like indentation, parentheses, commas, comments, docstrings, semicolons, line continuations, precedence, decorator @ signs, else vs. elif and lots and lots of niche special cases.

`pfst` works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provides the interface for source-preserving operations. The fact that it just extends existing `AST` nodes means that the `AST` tree can be used as normal and later `unparsed()` with formatting preserved where it can be. The degree to which formatting is preserved depends on how many operations are executed natively through `FST` mechanisms and how well `reconcile()` works for operations which are not.

`pfst` does not do any parsing of its own but rather relies on the builtin Python parser and unparser so it stays 100% compliant. This also means it is limited to the syntax of the running Python version.


[API Documentation](test.html)

















## Todo

* Reconcile AST nodes modified not using FST machinery.
* Individual sequence slice non-raw paths.
* Redo comment handling, where to put wrt comments, interface for modifying just those.
* Redo sequence slices for same comment behavior as statements.
* Support prescribed put/parse JoinedStr/FormattedValue and TemplateStr/Interpolation.

Trivia: The "F" in FST stands for "Fun".
