# Overview

This module exists in order to facilitate quick and easy editing of Python AST trees while preserving formatting. It deals with all the nonsense like indentation, line spacing, comments, docstrings, parentheses, commas, line continuations, semicolons, decorator @ signs, else vs. elif, generator expression as the only parameter to function sharing its parentheses with the function arguments, etc... It works by adding `FST` nodes to existing `AST` nodes which keep extra structure information and the original source, which is modified as operations are preformed. The fact that it just extends an `AST` tree means it can be used wherever `AST` is used.

The degree to which formatting is preserved depends on how many operations are executed natively through `FST` mechanisms.
















For the record, "FST" doesn't stand for "Full Syntax Tree" or "Formatted Syntax Tree", it stands for "Fun Syntax Tree".
