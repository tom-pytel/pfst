# Overview

This module exists in order to facilitate quick and easy editing of Python AST trees while preserving formatting. It deals with all the silly nonsense when editing python source like indentation, parentheses, commas, comments, docstrings, semicolons, line continuations, line spacing, precedence, decorator @ signs, else vs. elif, Dict '**d' keys being None, nodes without locations, deletions from a set leaving invalid empty curlies "{}" (change to "{*()}"), generator expression as the only argument to a function call sharing its enclosing parentheses with the call arguments, etc...

It works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provides the interface for source-preserving operations. The fact that it just extends existing `AST` nodes means that the `AST` tree (yes "`AST` tree" is redundand) can be used as normal and later `unparsed()` with formatting preserved where it can be. The degree to which formatting is preserved depends on how many operations are executed natively through `FST` mechanisms and how well `reconcile()` works for operations which are not.















## Todo

* Reconcile AST nodes modified not using FST machinery.
* Non-raw `put()` individual non-slice nodes.
* Make sure precedence is correct everywhere.
* Raw `get()` and `get_slice()`.
* Redo sequence slices for same comment behavior as statements.
  * Implement individual sequence slice non-raw paths.
* Clean up comment handling, where to put wrt comments, interface for modifying just those.

Trivia: The "F" in FST stands for "Fun".
