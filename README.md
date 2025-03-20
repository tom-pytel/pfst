# Overview

This module exists in order to facilitate quick and easy editing of Python AST trees while preserving formatting. It deals with all the nonsense like indentation, parentheses, commas, line continuations, semicolons, comments, decorator @ signs, else vs. elif, etc... It works by adding an `FST` node to existing `AST` nodes which keep extra structure information and the original source, which is modified as operations are preformed. This means that it can be used wherever AST is used. The degree to which formatting is preserved depends on how many operations are executed natively through `FST` mechanisms vs. how many `AST` nodes without original source are added (which will have source `unparse()`d for them and added to the tree).
















For the record, "FST" doesn't stand for "Full Syntax Tree" or "Formatted Syntax Tree", it stands for "Fun Syntax Tree".
