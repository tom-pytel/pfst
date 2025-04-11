# Overview

This module exists in order to facilitate quick and easy editing of Python AST trees while preserving formatting. It deals with all the nonsense like indentation, line spacing, comments, docstrings, parentheses, commas, semicolons, line continuations, decorator @ signs, else vs. elif, deletions leaving an empty set changing to "set()", generator expression as the only parameter to a function sharing its enclosing parentheses with the function arguments, etc...

It works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provide the interface for source-preserving operations. The fact that it just extends an `AST` tree means it can be used wherever `AST` is used, though the degree to which formatting is preserved depends on how many operations are executed natively through `FST` mechanisms.
















Note: The "F" in FST stands for "Fun" syntax tree.
