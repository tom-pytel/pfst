# Overview

This module exists in order to facilitate quick and easy editing of Python AST trees while preserving formatting. It deals with all the nonsense like indentation, line spacing, comments, docstrings, parentheses, commas, semicolons, line continuations, decorator @ signs, else vs. elif, deletions leaving an empty set changing to "set()", generator expression as the only parameter to a function sharing its enclosing parentheses with the function arguments, etc...

It works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provide the interface for source-preserving operations. The fact that it just extends existing `AST` nodes means that the `AST` tree (yes "`AST` tree" is redundand) can be used as normal and later `unparsed()` with formatting preserved where it can be. The degree to which formatting is preserved depends on how many operations are executed natively through `FST` mechanisms and how well `reconcile()` works for those which are not.












## Todo

* `put()` individual non-slice nodes.
* Reconcile AST nodes modified not using FST machinery.
* Implement individual sequence slice non-raw paths.
* Redo sequence slices for same comment behavior as statements.
* Clean up comment handling, where to insert wrt comments, interface for modifying just those.

Note: The "F" in FST stands for "Fun" syntax tree.
