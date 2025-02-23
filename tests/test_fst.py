#!/usr/bin/env python

import os
import sys
import unittest
import ast as ast_

from fst import *
from fst import fst

PYFNMS = sum((
    [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
    for top in ('src', 'tests')),
    start=[]
)

CUT_DATA = [
("""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', None, None, """
()
""", """
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  2] Constant 3 .. 3,4 -> 3,5
  .ctx
    Load
"""),

("""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 0, 2, """
(       # hello
    3,  # third line
)
""", """
(
    1,  # last line
    2,  # second line
)
""", """
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      Tuple .. 0,0 -> 2,1
        .elts[1]
        0] Constant 3 .. 1,4 -> 1,5
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 3,1
  .elts[2]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  .ctx
    Load
"""),

("""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 1, 2, """
(       # hello
    1,  # last line
    3,  # third line
)
""", """
(
    2,  # second line
)
""", """
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      Tuple .. 0,0 -> 3,1
        .elts[2]
        0] Constant 1 .. 1,4 -> 1,5
        1] Constant 3 .. 2,4 -> 2,5
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 1,4 -> 1,5
  .ctx
    Load
"""),

("""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 2, None, """
(       # hello
    1,  # last line
    2,  # second line
)
""", """
(
    3,  # third line
)
""", """
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      Tuple .. 0,0 -> 3,1
        .elts[2]
        0] Constant 1 .. 1,4 -> 1,5
        1] Constant 2 .. 2,4 -> 2,5
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 3 .. 1,4 -> 1,5
  .ctx
    Load
"""),

("""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', None, None, """
()
""", """
(           # hello
    1, 2, 3 # last line
)
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 2,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 1,7 -> 1,8
  2] Constant 3 .. 1,10 -> 1,11
  .ctx
    Load
"""),

("""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 0, 2, """
(           # hello
3, # last line
)
""", """
(
    1, 2)
""", """
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      Tuple .. 0,0 -> 2,1
        .elts[1]
        0] Constant 3 .. 1,0 -> 1,1
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 1,9
  .elts[2]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 1,7 -> 1,8
  .ctx
    Load
"""),

("""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 1, 2, """
(           # hello
    1, 3 # last line
)
""", """
(2,)
""", """
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      Tuple .. 0,0 -> 2,1
        .elts[2]
        0] Constant 1 .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx
    Load
"""),

("""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 2, None, """
(           # hello
    1, 2)
""", """
(3, # last line
)
""", """
Module .. ROOT 0,0 -> 1,9
  .body[1]
  0] Expr .. 0,0 -> 1,9
    .value
      Tuple .. 0,0 -> 1,9
        .elts[2]
        0] Constant 1 .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 1,1
  .elts[1]
  0] Constant 3 .. 0,1 -> 0,2
  .ctx
    Load
"""),

("""
1, 2, 3, 4
""", 'body[0].value', 1, 3, """
1, 4
""", """
(2, 3)
""", """
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value
      Tuple .. 0,0 -> 0,4
        .elts[2]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 4 .. 0,3 -> 0,4
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant 2 .. 0,1 -> 0,2
  1] Constant 3 .. 0,4 -> 0,5
  .ctx
    Load
"""),

("""
1, 2, 3, 4
""", 'body[0].value', -1, None, """
1, 2, 3
""", """
(4,)
""", """
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value
      Tuple .. 0,0 -> 0,7
        .elts[3]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant 4 .. 0,1 -> 0,2
  .ctx
    Load
"""),

("""
1, 2, 3, 4
""", 'body[0].value', None, None, """
()
""", """
(1, 2, 3, 4)
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 0,12
  .elts[4]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
  2] Constant 3 .. 0,7 -> 0,8
  3] Constant 4 .. 0,10 -> 0,11
  .ctx
    Load
"""),

("""
1, 2, 3, 4
""", 'body[0].value', 1, 1, """
1, 2, 3, 4
""", """
()
""", """
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] Expr .. 0,0 -> 0,10
    .value
      Tuple .. 0,0 -> 0,10
        .elts[4]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        3] Constant 4 .. 0,9 -> 0,10
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 0,2
  .ctx
    Load
"""),

("""
1, 2, 3, 4
""", 'body[0].value', 1, None, """
1,
""", """
(2, 3, 4)
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Constant 1 .. 0,0 -> 0,1
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 0,9
  .elts[3]
  0] Constant 2 .. 0,1 -> 0,2
  1] Constant 3 .. 0,4 -> 0,5
  2] Constant 4 .. 0,7 -> 0,8
  .ctx
    Load
"""),

("""
1, 2, 3, 4
""", 'body[0].value', 0, 3, """
4,
""", """
(1, 2, 3)
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Constant 4 .. 0,0 -> 0,1
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 0,9
  .elts[3]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
  2] Constant 3 .. 0,7 -> 0,8
  .ctx
    Load
"""),

("""
(1, 2
  ,  # comment
3, 4)
""", 'body[0].value', 1, 2, """
(1, 3, 4)
""", """
(2
  ,  # comment
)
""", """
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
        .elts[3]
        0] Constant 1 .. 0,1 -> 0,2
        1] Constant 3 .. 0,4 -> 0,5
        2] Constant 4 .. 0,7 -> 0,8
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx
    Load
"""),

("""
(1, 2
  ,
3, 4)
""", 'body[0].value', 1, 2, """
(1,
3, 4)
""", """
(2
  ,)
""", """
Module .. ROOT 0,0 -> 1,5
  .body[1]
  0] Expr .. 0,0 -> 1,5
    .value
      Tuple .. 0,0 -> 1,5
        .elts[3]
        0] Constant 1 .. 0,1 -> 0,2
        1] Constant 3 .. 1,0 -> 1,1
        2] Constant 4 .. 1,3 -> 1,4
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 1,4
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx
    Load
"""),

("""
(1, 2
  , 3, 4)
""", 'body[0].value', 1, 2, """
(1, 3, 4)
""", """
(2
  ,)
""", """
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
        .elts[3]
        0] Constant 1 .. 0,1 -> 0,2
        1] Constant 3 .. 0,4 -> 0,5
        2] Constant 4 .. 0,7 -> 0,8
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 1,4
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx
    Load
"""),

("""
(1, 2  # comment
  , 3, 4)
""", 'body[0].value', 1, 2, """
(1, 3, 4)
""", """
(2  # comment
  ,)
""", """
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
        .elts[3]
        0] Constant 1 .. 0,1 -> 0,2
        1] Constant 3 .. 0,4 -> 0,5
        2] Constant 4 .. 0,7 -> 0,8
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 1,4
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx
    Load
"""),

("""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', None, None, """
if 1:
    ()
""", """
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", """
Module .. ROOT 0,0 -> 1,6
  .body[1]
  0] If .. 0,0 -> 1,6
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 1,6
      .value
        Tuple .. 1,4 -> 1,6
          .ctx
            Load
""", """
Tuple .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  2] Constant 3 .. 3,4 -> 3,5
  .ctx
    Load
"""),

("""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 0, 2, """
if 1:
    (       # hello
        3,  # third line
    )
""", """
(
    1,  # last line
    2,  # second line
)
""", """
Module .. ROOT 0,0 -> 3,5
  .body[1]
  0] If .. 0,0 -> 3,5
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 3,5
      .value
        Tuple .. 1,4 -> 3,5
          .elts[1]
          0] Constant 3 .. 2,8 -> 2,9
          .ctx
            Load
""", """
Tuple .. ROOT 0,0 -> 3,1
  .elts[2]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  .ctx
    Load
"""),

("""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 1, 2, """
if 1:
    (       # hello
        1,  # last line
        3,  # third line
    )
""", """
(
    2,  # second line
)
""", """
Module .. ROOT 0,0 -> 4,5
  .body[1]
  0] If .. 0,0 -> 4,5
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 4,5
      .value
        Tuple .. 1,4 -> 4,5
          .elts[2]
          0] Constant 1 .. 2,8 -> 2,9
          1] Constant 3 .. 3,8 -> 3,9
          .ctx
            Load
""", """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 1,4 -> 1,5
  .ctx
    Load
"""),

("""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 2, None, """
if 1:
    (       # hello
        1,  # last line
        2,  # second line
    )
""", """
(
    3,  # third line
)
""", """
Module .. ROOT 0,0 -> 4,5
  .body[1]
  0] If .. 0,0 -> 4,5
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 4,5
      .value
        Tuple .. 1,4 -> 4,5
          .elts[2]
          0] Constant 1 .. 2,8 -> 2,9
          1] Constant 2 .. 3,8 -> 3,9
          .ctx
            Load
""", """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 3 .. 1,4 -> 1,5
  .ctx
    Load
"""),

("""
{1: 2, **b, **c}
""", 'body[0].value', 1, 2, """
{1: 2, **c}
""", """
{**b}
""", """
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value
      Dict .. 0,0 -> 0,11
        .keys[2]
        0] Constant 1 .. 0,1 -> 0,2
        1] None
        .values[2]
        0] Constant 2 .. 0,4 -> 0,5
        1] Name 'c' Load .. 0,9 -> 0,10
""", """
Dict .. ROOT 0,0 -> 0,5
  .keys[1]
  0] None
  .values[1]
  0] Name 'b' Load .. 0,3 -> 0,4
"""),

("""
{1: 2, **b, **c}
""", 'body[0].value', None, None, """
{}
""", """
{1: 2, **b, **c}
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Dict .. 0,0 -> 0,2
""", """
Dict .. ROOT 0,0 -> 0,16
  .keys[3]
  0] Constant 1 .. 0,1 -> 0,2
  1] None
  2] None
  .values[3]
  0] Constant 2 .. 0,4 -> 0,5
  1] Name 'b' Load .. 0,9 -> 0,10
  2] Name 'c' Load .. 0,14 -> 0,15
"""),

("""
{1: 2, **b, **c}
""", 'body[0].value', 2, None, """
{1: 2, **b}
""", """
{**c}
""", """
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value
      Dict .. 0,0 -> 0,11
        .keys[2]
        0] Constant 1 .. 0,1 -> 0,2
        1] None
        .values[2]
        0] Constant 2 .. 0,4 -> 0,5
        1] Name 'b' Load .. 0,9 -> 0,10
""", """
Dict .. ROOT 0,0 -> 0,5
  .keys[1]
  0] None
  .values[1]
  0] Name 'c' Load .. 0,3 -> 0,4
"""),

("""
i =                (self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                id(self) & (_sys.maxsize*2 + 1))
""", 'body[0].value', 0, 3, """
i =                (
                id(self) & (_sys.maxsize*2 + 1),)
""", """
(self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),)
""", """
Module .. ROOT 0,0 -> 1,49
  .body[1]
  0] Assign .. 0,0 -> 1,49
    .targets[1]
    0] Name 'i' Store .. 0,0 -> 0,1
    .value
      Tuple .. 0,19 -> 1,49
        .elts[1]
        0] BinOp .. 1,16 -> 1,47
          .left
            Call .. 1,16 -> 1,24
              .func
                Name 'id' Load .. 1,16 -> 1,18
              .args[1]
              0] Name 'self' Load .. 1,19 -> 1,23
          .op
            BitAnd
          .right
            BinOp .. 1,28 -> 1,46
              .left
                BinOp .. 1,28 -> 1,42
                  .left
                    Attribute .. 1,28 -> 1,40
                      .value
                        Name '_sys' Load .. 1,28 -> 1,32
                      .attr
                        'maxsize'
                      .ctx
                        Load
                  .op
                    Mult
                  .right
                    Constant 2 .. 1,41 -> 1,42
              .op
                Add
              .right
                Constant 1 .. 1,45 -> 1,46
        .ctx
          Load
    .type_comment
      None
""", """
Tuple .. ROOT 0,0 -> 1,55
  .elts[3]
  0] Attribute .. 0,1 -> 0,24
    .value
      Attribute .. 0,1 -> 0,15
        .value
          Name 'self' Load .. 0,1 -> 0,5
        .attr
          '__class__'
        .ctx
          Load
    .attr
      '__name__'
    .ctx
      Load
  1] Attribute .. 0,26 -> 0,36
    .value
      Name 'self' Load .. 0,26 -> 0,30
    .attr
      '_name'
    .ctx
      Load
  2] BinOp .. 1,17 -> 1,52
    .left
      Attribute .. 1,17 -> 1,29
        .value
          Name 'self' Load .. 1,17 -> 1,21
        .attr
          '_handle'
        .ctx
          Load
    .op
      BitAnd
    .right
      BinOp .. 1,33 -> 1,51
        .left
          BinOp .. 1,33 -> 1,47
            .left
              Attribute .. 1,33 -> 1,45
                .value
                  Name '_sys' Load .. 1,33 -> 1,37
                .attr
                  'maxsize'
                .ctx
                  Load
            .op
              Mult
            .right
              Constant 2 .. 1,46 -> 1,47
        .op
          Add
        .right
          Constant 1 .. 1,50 -> 1,51
  .ctx
    Load
"""),

("""
i = namespace = {**__main__.__builtins__.__dict__,
             **__main__.__dict__}
""", 'body[0].value', 0, 1, """
i = namespace = {
             **__main__.__dict__}
""", """
{**__main__.__builtins__.__dict__,}
""", """
Module .. ROOT 0,0 -> 1,33
  .body[1]
  0] Assign .. 0,0 -> 1,33
    .targets[2]
    0] Name 'i' Store .. 0,0 -> 0,1
    1] Name 'namespace' Store .. 0,4 -> 0,13
    .value
      Dict .. 0,16 -> 1,33
        .keys[1]
        0] None
        .values[1]
        0] Attribute .. 1,15 -> 1,32
          .value
            Name '__main__' Load .. 1,15 -> 1,23
          .attr
            '__dict__'
          .ctx
            Load
    .type_comment
      None
""", """
Dict .. ROOT 0,0 -> 0,35
  .keys[1]
  0] None
  .values[1]
  0] Attribute .. 0,3 -> 0,33
    .value
      Attribute .. 0,3 -> 0,24
        .value
          Name '__main__' Load .. 0,3 -> 0,11
        .attr
          '__builtins__'
        .ctx
          Load
    .attr
      '__dict__'
    .ctx
      Load
"""),

("""
env = {
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1",
    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}
""", 'body[0].value', None, 2, """
env = {

    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}
""", """
{
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1",}
""", """
Module .. ROOT 0,0 -> 5,1
  .body[1]
  0] Assign .. 0,0 -> 5,1
    .targets[1]
    0] Name 'env' Store .. 0,0 -> 0,3
    .value
      Dict .. 0,6 -> 5,1
        .keys[3]
        0] Constant 'PYLAUNCHER_DRYRUN' .. 2,4 -> 2,23
        1] Constant 'PYLAUNCHER_LIMIT_TO_COMPANY' .. 3,4 -> 3,33
        2] None
        .values[3]
        0] Constant '1' .. 2,25 -> 2,28
        1] Constant '' .. 3,35 -> 3,37
        2] DictComp .. 4,6 -> 4,52
          .key
            Call .. 4,7 -> 4,16
              .func
                Attribute .. 4,7 -> 4,14
                  .value
                    Name 'k' Load .. 4,7 -> 4,8
                  .attr
                    'upper'
                  .ctx
                    Load
          .value
            Name 'v' Load .. 4,18 -> 4,19
          .generators[1]
          0] comprehension .. 4,24 -> 4,51
            .target
              Tuple .. 4,24 -> 4,28
                .elts[2]
                0] Name 'k' Store .. 4,24 -> 4,25
                1] Name 'v' Store .. 4,27 -> 4,28
                .ctx
                  Store
            .iter
              Call .. 4,32 -> 4,51
                .func
                  Attribute .. 4,32 -> 4,49
                    .value
                      BoolOp .. 4,33 -> 4,42
                        .op
                          Or
                        .values[2]
                        0] Name 'env' Load .. 4,33 -> 4,36
                        1] Dict .. 4,40 -> 4,42
                    .attr
                      'items'
                    .ctx
                      Load
            .is_async
              0
    .type_comment
      None
""", """
Dict .. ROOT 0,0 -> 2,29
  .keys[2]
  0] None
  1] Constant 'PYLAUNCHER_DEBUG' .. 2,4 -> 2,22
  .values[2]
  0] DictComp .. 1,6 -> 1,78
    .key
      Call .. 1,7 -> 1,16
        .func
          Attribute .. 1,7 -> 1,14
            .value
              Name 'k' Load .. 1,7 -> 1,8
            .attr
              'upper'
            .ctx
              Load
    .value
      Name 'v' Load .. 1,18 -> 1,19
    .generators[1]
    0] comprehension .. 1,24 -> 1,77
      .target
        Tuple .. 1,24 -> 1,28
          .elts[2]
          0] Name 'k' Store .. 1,24 -> 1,25
          1] Name 'v' Store .. 1,27 -> 1,28
          .ctx
            Store
      .iter
        Call .. 1,32 -> 1,50
          .func
            Attribute .. 1,32 -> 1,48
              .value
                Attribute .. 1,32 -> 1,42
                  .value
                    Name 'os' Load .. 1,32 -> 1,34
                  .attr
                    'environ'
                  .ctx
                    Load
              .attr
                'items'
              .ctx
                Load
      .ifs[1]
      0] Compare .. 1,54 -> 1,77
        .left
          Call .. 1,54 -> 1,63
            .func
              Attribute .. 1,54 -> 1,61
                .value
                  Name 'k' Load .. 1,54 -> 1,55
                .attr
                  'upper'
                .ctx
                  Load
        .ops[1]
        0] NotIn
        .comparators[1]
        0] Name 'ignore' Load .. 1,71 -> 1,77
      .is_async
        0
  1] Constant '1' .. 2,24 -> 2,27
"""),

("""
(None, False, True, 12345, 123.45, 'abcde', 'абвгд', b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
""", 'body[0].value', 5, 7, """
(None, False, True, 12345, 123.45, b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
""", """
('abcde', 'абвгд')
""", """
Module .. ROOT 0,0 -> 2,67
  .body[1]
  0] Expr .. 0,0 -> 2,67
    .value
      Tuple .. 0,0 -> 2,67
        .elts[11]
        0] Constant None .. 0,1 -> 0,5
        1] Constant False .. 0,7 -> 0,12
        2] Constant True .. 0,14 -> 0,18
        3] Constant 12345 .. 0,20 -> 0,25
        4] Constant 123.45 .. 0,27 -> 0,33
        5] Constant b'abcde' .. 0,35 -> 0,43
        6] Call .. 1,12 -> 1,55
          .func
            Attribute .. 1,12 -> 1,29
              .value
                Name 'datetime' Load .. 1,12 -> 1,20
              .attr
                'datetime'
              .ctx
                Load
          .args[6]
          0] Constant 2004 .. 1,30 -> 1,34
          1] Constant 10 .. 1,36 -> 1,38
          2] Constant 26 .. 1,40 -> 1,42
          3] Constant 10 .. 1,44 -> 1,46
          4] Constant 33 .. 1,48 -> 1,50
          5] Constant 33 .. 1,52 -> 1,54
        7] Call .. 2,12 -> 2,31
          .func
            Name 'bytearray' Load .. 2,12 -> 2,21
          .args[1]
          0] Constant b'abcde' .. 2,22 -> 2,30
        8] List .. 2,33 -> 2,42
          .elts[2]
          0] Constant 12 .. 2,34 -> 2,36
          1] Constant 345 .. 2,38 -> 2,41
          .ctx
            Load
        9] Tuple .. 2,44 -> 2,53
          .elts[2]
          0] Constant 12 .. 2,45 -> 2,47
          1] Constant 345 .. 2,49 -> 2,52
          .ctx
            Load
        10] Dict .. 2,55 -> 2,66
          .keys[1]
          0] Constant '12' .. 2,56 -> 2,60
          .values[1]
          0] Constant 345 .. 2,62 -> 2,65
        .ctx
          Load
""", """
Tuple .. ROOT 0,0 -> 0,18
  .elts[2]
  0] Constant 'abcde' .. 0,1 -> 0,8
  1] Constant 'абвгд' .. 0,10 -> 0,17
  .ctx
    Load
"""),

]  # END OF CUT_DATA

PUT_SLICE_DATA = [
("""
{
    a: 1
}
""", 'body[0].value', 0, 1, """
{}
""", """
{}
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Dict .. 0,0 -> 0,2
"""),

("""
{
    a: 1
}
""", 'body[0].value', 0, 1, """
{
}
""", """
{
}
""", """
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 0,0 -> 1,1
    .value
      Dict .. 0,0 -> 1,1
"""),

("""
{a: 1}
""", 'body[0].value', 0, 1, """
{}
""", """
{}
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Dict .. 0,0 -> 0,2
"""),

("""
{a: 1}
""", 'body[0].value', 0, 1, """
{
}
""", """
{
}
""", """
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 0,0 -> 1,1
    .value
      Dict .. 0,0 -> 1,1
"""),

("""
(1, 2)
""", 'body[0].value', 1, 2, """
()
""", """
(1,)
""", """
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value
      Tuple .. 0,0 -> 0,4
        .elts[1]
        0] Constant 1 .. 0,1 -> 0,2
        .ctx
          Load
"""),

("""
1, 2
""", 'body[0].value', 1, 2, """
()
""", """
1,
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Constant 1 .. 0,0 -> 0,1
        .ctx
          Load
"""),

("""
1, 2
""", 'body[0].value', 0, 2, """
()
""", """
()
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx
          Load
"""),

("""
(1, 2)
""", 'body[0].value', 1, 2, """
set()
""", """
(1,)
""", """
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value
      Tuple .. 0,0 -> 0,4
        .elts[1]
        0] Constant 1 .. 0,1 -> 0,2
        .ctx
          Load
"""),

("""
1, 2
""", 'body[0].value', 1, 2, """
set()
""", """
1,
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Constant 1 .. 0,0 -> 0,1
        .ctx
          Load
"""),

("""
1, 2
""", 'body[0].value', 0, 2, """
set()
""", """
()
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx
          Load
"""),

]  # END OF PUT_SLICE_DATA

def read(fnm):
    with open(fnm) as f:
        return f.read()


def walktest(ast):
    for ast in walk(ast):
        ast.f.loc


def dumptest(self, fst, dump, src):
    self.assertEqual(dump.strip(), '\n'.join(fst.dump(print=False)))
    self.assertEqual(src, fst.src)


class TestFST(unittest.TestCase):
    def test__dict_key_or_mock_loc(self):
        a = parse('''{
    a: """test
two  # fake comment start""", **b
            }''').body[0].value
        self.assertEqual((2, 30, 2, 32), a.f._dict_key_or_mock_loc(a.keys[1], a.values[1].f))

        a = parse('''{
    a: """test""", **  # comment
    b
            }''').body[0].value
        self.assertEqual((1, 19, 1, 21), a.f._dict_key_or_mock_loc(a.keys[1], a.values[1].f))

    def test__normalize_code(self):
        f = fst._normalize_code('i')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code('i', expr_=True)
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(['i'])
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(['i'], expr_=True)
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(ast_.parse('i'))
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(ast_.parse('i', mode='single'))
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(ast_.parse('i'), expr_=True)
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(ast_.parse('i', mode='eval'))
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(ast_.parse('i', mode='eval'), expr_=True)
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(FST.fromsrc('i'))
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(FST.fromsrc('i', mode='single'))
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(FST.fromsrc('i', mode='eval'))
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(FST.fromsrc('i'), expr_=True)
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(FST.fromsrc('i', mode='eval'), expr_=True)
        self.assertIsInstance(f.a, Name)

    def test_loc(self):
        # from children
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.loc)  # arguments
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((1, 7, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.loc)  # match_case
        self.assertEqual((0, 7, 0, 20), parse('[i for i in range(5)]').body[0].value.generators[0].f.loc)  # comprehension

    def test_bloc(self):
        ast = parse('@deco\nclass cls:\n @deco\n def meth():\n  @deco\n  class fcls: pass')

        self.assertEqual((0, 0, 5, 18), ast.f.loc)
        self.assertEqual((0, 0, 5, 18), ast.f.bloc)
        self.assertEqual((1, 0, 5, 18), ast.body[0].f.loc)
        self.assertEqual((0, 0, 5, 18), ast.body[0].f.bloc)
        self.assertEqual((3, 1, 5, 18), ast.body[0].body[0].f.loc)
        self.assertEqual((2, 1, 5, 18), ast.body[0].body[0].f.bloc)
        self.assertEqual((5, 2, 5, 18), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((4, 2, 5, 18), ast.body[0].body[0].body[0].f.bloc)

    def test_fromsrc_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromsrc(read(fnm))

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_False_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(ast_.unparse(ast_.parse(read(fnm)))), calc_loc=False)

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_True_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(read(fnm)), calc_loc=True)

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_copy_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(read(fnm)), calc_loc='copy')

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_verify(self):
        ast = parse('i = 1')
        ast.f.verify(raise_=True)

        ast.body[0].lineno = 100

        self.assertRaises(WalkFail, ast.f.verify, raise_=True)
        self.assertEqual(None, ast.f.verify(raise_=False))

    def test_walk(self):
        a = parse("""
def f(a, b=1, *c, d=2, **e): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.args[0].f)
        self.assertIs(l[2], a.args[1].f)
        self.assertIs(l[3], a.defaults[0].f)
        self.assertIs(l[4], a.vararg.f)
        self.assertIs(l[5], a.kwonlyargs[0].f)
        self.assertIs(l[6], a.kw_defaults[0].f)
        self.assertIs(l[7], a.kwarg.f)

        a = parse("""
def f(*, a, b, c=1, d=2, **e): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.kwonlyargs[0].f)
        self.assertIs(l[2], a.kwonlyargs[1].f)
        self.assertIs(l[3], a.kwonlyargs[2].f)
        self.assertIs(None, a.kw_defaults[0])
        self.assertIs(None, a.kw_defaults[1])
        self.assertIs(l[4], a.kw_defaults[2].f)
        self.assertIs(l[5], a.kwonlyargs[3].f)
        self.assertIs(l[6], a.kw_defaults[3].f)
        self.assertIs(l[7], a.kwarg.f)

        a = parse("""
def f(a, b=1, /, c=2, d=3, *e, f=4, **g): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.posonlyargs[0].f)
        self.assertIs(l[2], a.posonlyargs[1].f)
        self.assertIs(l[3], a.defaults[0].f)
        self.assertIs(l[4], a.args[0].f)
        self.assertIs(l[5], a.defaults[1].f)
        self.assertIs(l[6], a.args[1].f)
        self.assertIs(l[7], a.defaults[2].f)
        self.assertIs(l[8], a.vararg.f)
        self.assertIs(l[9], a.kwonlyargs[0].f)
        self.assertIs(l[10], a.kw_defaults[0].f)
        self.assertIs(l[11], a.kwarg.f)

        a = parse("""
def f(a=1, /, b=2): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.posonlyargs[0].f)
        self.assertIs(l[2], a.defaults[0].f)
        self.assertIs(l[3], a.args[0].f)
        self.assertIs(l[4], a.defaults[1].f)

        a = parse("""
call(a, b=1, *c, d=2, **e)
            """.strip()).body[0].value
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.func.f)
        self.assertIs(l[2], a.args[0].f)
        self.assertIs(l[3], a.keywords[0].f)
        self.assertIs(l[4], a.keywords[0].value.f)
        self.assertIs(l[5], a.args[1].f)
        self.assertIs(l[6], a.args[1].value.f)
        self.assertIs(l[7], a.keywords[1].f)
        self.assertIs(l[8], a.keywords[1].value.f)
        self.assertIs(l[9], a.keywords[2].f)
        self.assertIs(l[10], a.keywords[2].value.f)

        a = parse("""
i = 1
self.save_reduce(obj=obj, *rv)
            """.strip()).body[1].value
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.func.f)
        self.assertIs(l[2], a.func.value.f)
        self.assertIs(l[3], a.keywords[0].f)
        self.assertIs(l[4], a.keywords[0].value.f)
        self.assertIs(l[5], a.args[0].f)
        self.assertIs(l[6], a.args[0].value.f)

    def test_walk_scope(self):
        fst = FST.fromsrc("""
def f(a, /, b, *c, d, **e):
    f = 1
    [i for i in g if i]
    {k: v for k, v in h if k and v}
    @deco1
    def func(l=m): hidden
    @deco2
    class sup(cls, meta=moto): hidden
    lambda n=o, **kw: hidden
            """.strip()).a.body[0].f
        self.assertEqual(['f', 'g', 'h', 'deco1', 'm', 'deco2', 'cls', 'moto', 'o'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])
        self.assertEqual(['a', 'b', 'c', 'd', 'e'],
                         [f.a.arg for f in fst.walk(scope=True) if isinstance(f.a, arg)])

        l = []
        for f in (gen := fst.walk(True, scope=True)):
            if isinstance(f.a, Name):
                l.append(f.a.id)
            elif isinstance(f.a, ClassDef):
                gen.send(True)
        self.assertEqual(['f', 'g', 'h', 'deco1', 'm', 'deco2', 'cls', 'moto', 'hidden', 'o'], l)

        fst = FST.fromsrc("""[z for a in b if (c := a)]""".strip()).a.body[0].value.f
        self.assertEqual(['z', 'a', 'c', 'a'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

        fst = FST.fromsrc("""[z for a in b if (c := a)]""".strip()).a.body[0].f
        self.assertEqual(['b', 'c'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

        fst = FST.fromsrc("""[z for a in b if b in [c := i for i in j if i in {d := k for k in l}]]""".strip()).a.body[0].value.f
        self.assertEqual(['z', 'a', 'b', 'c', 'j', 'd'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

    def test_walk_bulk(self):
        for fnm in PYFNMS:
            ast       = FST.fromsrc(read(fnm)).a
            bln, bcol = 0, 0

            for f in (gen := ast.f.walk(True)):
                if isinstance(f.a, JoinedStr):  # these are borked
                    gen.send(False)

                    continue

                self.assertTrue(f.bln > bln or (f.bln == bln and f.bcol >= bcol))

                lof = list(f.walk(True, walk_self=False, recurse=False))
                lob = list(f.walk(True, walk_self=False, recurse=False, back=True))

                self.assertEqual(lof, lob[::-1])

                lf, c = [], None
                while c := f.next_child(c, True): lf.append(c)
                self.assertEqual(lf, lof)

                lb, c = [], None
                while c := f.prev_child(c, True): lb.append(c)
                self.assertEqual(lb, lob)

                bln, bcol = f.bln, f.bcol

    def test_next_prev(self):
        fst = parse('a and b and c and d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.op.f)
        self.assertIs((f := fst.next_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.op.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        if sys.version_info[:2] >= (3, 12):
            fst = parse('@deco\ndef f[T, U](a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
            a = fst.a
            f = None
            self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, True)), a.args.f)
            self.assertIs((f := fst.next_child(f, True)), a.returns.f)
            self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, True)), None)
            f = None
            self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, False)), a.args.f)
            self.assertIs((f := fst.next_child(f, False)), a.returns.f)
            self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, False)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, True)), a.args.f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, True)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, False)), a.args.f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('@deco\ndef f(a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.args.f)
        self.assertIs((f := fst.next_child(f, True)), a.returns.f)
        self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.args.f)
        self.assertIs((f := fst.next_child(f, False)), a.returns.f)
        self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, True)), a.args.f)
        self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, False)), a.args.f)
        self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('a <= b == c >= d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.left.f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.left.f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.left.f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.left.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('match a:\n case {1: a, 2: b, **rest}: pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('match a:\n case cls(1, 2, a=3, b=4): pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.cls.f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.cls.f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

    def test_next_prev_vs_walk(self):
        def test1(src):
            f = FST.fromsrc(src).a.body[0].args.f
            m = list(f.walk(True, walk_self=False, recurse=False))

            l, c = [], None
            while c := f.next_child(c): l.append(c)
            self.assertEqual(l, m)

            l, c = [], None
            while c := f.prev_child(c): l.append(c)
            self.assertEqual(l, m[::-1])

        test1('def f(**a): apass')
        test1('def f(*, e, d, c=3, b=2, **a): pass')
        test1('def f(*f, e, d, c=3, b=2, **a): pass')
        test1('def f(g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(h, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(i, /, h, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j, i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, e, d, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, **a): pass')
        test1('def f(j, i, /, h, g, **a): pass')
        test1('def f(j, i, /, **a): pass')
        test1('def f(j, i, /, *f, **a): pass')
        test1('def f(j=7, i=6, /, **a): pass')
        test1('def f(**a): pass')
        test1('def f(b=1, **a): pass')
        test1('def f(a, /): pass')
        test1('def f(a, /, b): pass')
        test1('def f(a, /, b, c=1): pass')
        test1('def f(a, /, b, c=1, *d): pass')
        test1('def f(a, /, b, c=1, *d, e): pass')
        test1('def f(a, /, b, c=1, *d, e, f=2): pass')
        test1('def f(a, /, b, c=1, *d, e, f=2, **g): pass')
        test1('def f(a=1, b=2, *e): pass')
        test1('def f(a, b, /, c, d, *e): pass')
        test1('def f(a, b, /, c, d=1, *e): pass')
        test1('def f(a, b, /, c=2, d=1, *e): pass')
        test1('def f(a, b=3, /, c=2, d=1, *e): pass')
        test1('def f(a=4, b=3, /, c=2, d=1, *e): pass')
        test1('def f(a, b=1, /, c=2, d=3, *e, f=4, **g): pass')
        test1('def __init__(self, max_size=0, *, ctx, pending_work_items, shutdown_lock, thread_wakeup): pass')

        def test2(src):
            f = FST.fromsrc(src).a.body[0].value.f
            m = list(f.walk(True, walk_self=False, recurse=False))

            l, c = [], None
            while c := f.next_child(c): l.append(c)
            self.assertEqual(l, m)

            l, c = [], None
            while c := f.prev_child(c): l.append(c)
            self.assertEqual(l, m[::-1])

        test2('call(a=1, *b)')
        test2('call()')
        test2('call(a, b)')
        test2('call(c=1, d=1)')
        test2('call(a, b, c=1, d=1)')
        test2('call(a, b, *c, d)')
        test2('call(a, b, *c, d=2)')
        test2('call(a, b=1, *c, d=2)')
        test2('call(a, b=1, *c, d=2, **e)')
        test2('system_message(message, level=level, type=type,*children, **kwargs)')

    def test_get_indent(self):
        ast = parse('i = 1; j = 2')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual('', ast.body[1].f.get_indent())

        ast = parse('def f(): \\\n i = 1')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())

        ast = parse('class cls: i = 1')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())

        ast = parse('class cls: i = 1; \\\n    j = 2')

        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[1].f.get_indent())

        ast = parse('class cls:\n  i = 1; \\\n    j = 2')

        self.assertEqual('  ', ast.body[0].body[0].f.get_indent())
        self.assertEqual('  ', ast.body[0].body[1].f.get_indent())

        ast = parse('class cls:\n   def f(): i = 1')

        self.assertEqual('   ', ast.body[0].body[0].f.get_indent())
        self.assertEqual('   ' + ast.f.root.indent, ast.body[0].body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   1').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): 1').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1').body[0].body[0].f.get_indent())

        self.assertEqual('    ', parse('class cls:\n def f():\n    1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('     ', parse('class cls:\n def f(): 1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('     ', parse('class cls:\n def f(): \\\n   1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('class cls:\n def f(): # \\\n   1').body[0].body[0].body[0].f.get_indent())

        self.assertEqual('  ', parse('if 1:\n  2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: 2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: \\\n 2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('if 1: # \\\n  2\nelse:\n   3').body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('if 1:\n  2\nelse:\n   3').body[0].orelse[0].f.get_indent())
        self.assertEqual('    ', parse('if 1:\n  2\nelse: 3').body[0].orelse[0].f.get_indent())
        self.assertEqual('    ', parse('if 1:\n  2\nelse: \\\n 3').body[0].orelse[0].f.get_indent())
        self.assertEqual('   ', parse('if 1:\n  2\nelse: # \\\n   3').body[0].orelse[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): 1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1; 2').body[0].body[1].f.get_indent())

        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[1].f.get_indent())

        self.assertEqual('', parse('\\\ni').body[0].f.get_indent())
        self.assertEqual('    ', parse('try: i\nexcept: pass').body[0].body[0].f.get_indent())

    def test__indentable_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = "... \\\n2"\n else:\n  j \\\n=\\\n 2'
        ast = parse(src)

        self.assertEqual({1, 2, 5, 7, 8, 9, 10}, ast.f._indentable_lns(1))
        self.assertEqual({0, 1, 2, 5, 7, 8, 9, 10}, ast.f._indentable_lns(0))

        f = FST.fromsrc('''
def _splitext(p, sep, altsep, extsep):
    """Split the extension from a pathname.

    Extension is everything from the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work for text and bytes strings.

    sepIndex = p.rfind(sep)
            '''.strip())
        self.assertEqual({0, 1, 2, 3, 4, 5, 6, 7}, f._indentable_lns(docstring=True))
        self.assertEqual({0, 1, 5, 6, 7}, f._indentable_lns(docstring=False))

        f = FST.fromsrc(r'''
_CookiePattern = re.compile(r"""
    \s*                            # Optional whitespace at start of cookie
    (?P<key>                       # Start of group 'key'
    [""" + _LegalKeyChars + r"""]+?   # Any word of at least one letter
    )                              # End of group 'key'
    (                              # Optional group: there may not be a value.
    \s*=\s*                          # Equal Sign
    (?P<val>                         # Start of group 'val'
    "(?:[^\\"]|\\.)*"                  # Any doublequoted string
    |                                  # or
    \w{3},\s[\w\d\s-]{9,11}\s[\d:]{8}\sGMT  # Special case for "expires" attr
    |                                  # or
    [""" + _LegalValueChars + r"""]*      # Any word or empty string
    )                                # End of group 'val'
    )?                             # End of optional value group
    \s*                            # Any number of spaces.
    (\s+|;|$)                      # Ending either at space, semicolon, or EOS.
    """, re.ASCII | re.VERBOSE)    # re.ASCII may be removed if safe.
            '''.strip())
        self.assertEqual({0}, f._indentable_lns(docstring=True))
        self.assertEqual({0}, f._indentable_lns(docstring=False))

        f = FST.fromsrc('''
"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0, 1}, f._indentable_lns(docstring=True))
        self.assertEqual({0}, f._indentable_lns(docstring=False))

    def test__offset(self):
        src = 'i = 1\nj = 2\nk = 3'

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 5, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1, inc=True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 3, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1, inc=True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        def get():
            m = parse('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nbbbb\ncccc')

            m.body[0] = m.body[0].value
            m.body[1] = m.body[1].value
            m.body[2] = m.body[2].value

            m.body[0].lineno         = 1
            m.body[0].end_lineno     = 1
            m.body[0].col_offset     = 2
            m.body[0].end_col_offset = 6
            m.body[1].lineno         = 1
            m.body[1].end_lineno     = 1
            m.body[1].col_offset     = 6
            m.body[1].end_col_offset = 10
            m.body[2].lineno         = 1
            m.body[2].end_lineno     = 1
            m.body[2].col_offset     = 6
            m.body[2].end_col_offset = 6

            return m

        m = get()
        m.f._offset(0, 6, 0, 2, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 8, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, True)
        self.assertEqual((0, 2, 0, 8), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

    def test__offset_cols(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j = 2'

        ast = parse(src)
        lns = ast.f._indentable_lns(1)
        ast.f._offset_cols(1, lns)
        self.assertEqual({1, 2, 5, 6, 7}, lns)
        self.assertEqual((0, 0, 7, 7), ast.f.loc)
        self.assertEqual((0, 0, 7, 8), ast.body[0].f.loc)
        self.assertEqual((1, 2, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 5, 1, 9), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].f._indentable_lns(1)
        ast.body[0].body[0].f._offset_cols(1, lns)
        self.assertEqual({2, 5, 6, 7}, lns)
        self.assertEqual((1, 1, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 4, 1, 8), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._indentable_lns(1)
        ast.body[0].body[0].body[0].f._offset_cols(1, lns)
        self.assertEqual(set(), lns)
        self.assertEqual((2, 2, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 6, 4, 3), ast.body[0].body[0].body[0].value.f.loc)

    def test__offset_cols_mapped(self):
        src = 'i = 1\nj = 2\nk = 3\nl = \\\n4'
        ast = parse(src)
        off = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

        ast.f._offset_cols_mapped(off)
        self.assertEqual((0, 0, 4, 1), ast.f.loc)
        self.assertEqual((0, 0, 0, 5), ast.body[0].f.loc)
        self.assertEqual((0, 0, 0, 1), ast.body[0].targets[0].f.loc)
        self.assertEqual((0, 4, 0, 5), ast.body[0].value.f.loc)
        self.assertEqual((1, 1, 1, 6), ast.body[1].f.loc)
        self.assertEqual((1, 1, 1, 2), ast.body[1].targets[0].f.loc)
        self.assertEqual((1, 5, 1, 6), ast.body[1].value.f.loc)
        self.assertEqual((2, 2, 2, 7), ast.body[2].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[2].targets[0].f.loc)
        self.assertEqual((2, 6, 2, 7), ast.body[2].value.f.loc)
        self.assertEqual((3, 3, 4, 5), ast.body[3].f.loc)
        self.assertEqual((3, 3, 3, 4), ast.body[3].targets[0].f.loc)
        self.assertEqual((4, 4, 4, 5), ast.body[3].value.f.loc)

    def test__indent_tail(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._indent_tail('  ')
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n   if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._indent_tail('  ')
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._indent_tail('  ')
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._indent_tail('  ')
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n  =\\\n   2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.f._indent_tail('  ')
        self.assertEqual({1, 2}, lns)
        self.assertEqual('@decorator\n  class cls:\n   pass', ast.f.src)

    def test__dedent_tail(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._dedent_tail(' ')
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\nif True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._dedent_tail(' ')
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._dedent_tail(' ')
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._dedent_tail(' ')
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.body[0].body[0].f._dedent_tail(' ')
        self.assertEqual(set(), lns)
        self.assertEqual('@decorator\nclass cls:\n pass', ast.f.src)

        # ast = parse(src)
        # lns = ast.body[0].body[0].f._dedent_tail(' ', skip=0)
        # self.assertEqual({2}, lns)
        # self.assertEqual('@decorator\nclass cls:\npass', ast.f.src)

    def test_dedent_multiline_strings(self):
        f = parse('''
class cls:
    def func():
        i = """This is a
        normal
        multiline string"""

        j = ("This is a "
        "split "
        "multiline string")

        k = f"""This is a
        normal
        multiline f-string"""

        l = (f"This is a "
        "split "
        f"multiline f-string")
            '''.strip()).body[0].body[0].f
        self.assertEqual('''
def func():
    i = """This is a
        normal
        multiline string"""

    j = ("This is a "
    "split "
    "multiline string")

    k = f"""This is a
        normal
        multiline f-string"""

    l = (f"This is a "
    "split "
    f"multiline f-string")
            '''.strip(), f.copy().src)

        f = parse('''
class cls:
    def func():
        l = (f"This is a "
        f"split " """
        super
        special
        """
        f"multiline f-string")
            '''.strip()).body[0].body[0].f
        self.assertEqual('''
def func():
    l = (f"This is a "
    f"split " """
        super
        special
        """
    f"multiline f-string")
            '''.strip(), f.copy().src)

    def test_copy_lines(self):
        src = 'class cls:\n if True:\n  i = 1\n else:\n  j = 2'
        ast = parse(src)

        self.assertEqual(src.split('\n'), ast.f.copy_lines())
        self.assertEqual(src.split('\n'), ast.body[0].f.copy_lines())
        self.assertEqual('if True:\n  i = 1\n else:\n  j = 2'.split('\n'), ast.body[0].body[0].f.copy_lines())
        self.assertEqual(['i = 1'], ast.body[0].body[0].body[0].f.copy_lines())
        self.assertEqual(['j = 2'], ast.body[0].body[0].orelse[0].f.copy_lines())

        self.assertEqual(['True:', '  i'], ast.f.root.copyl_lines(1, 4, 2, 3))

    def test_put_lines(self):
        f = FST(Load(), lines=[bistr('')])
        f.putl_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['test'])
        f.putl_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['testtest'])
        f.putl_src('tost', 0, 0, 0, 8)
        self.assertEqual(f.lines, ['tost'])
        f.putl_src('a\nb\nc', 0, 2, 0, 2)
        self.assertEqual(f.lines, ['toa', 'b', 'cst'])
        f.putl_src('', 0, 3, 2, 1)
        self.assertEqual(f.lines, ['toast'])
        f.putl_src('a\nb\nc\nd', 0, 0, 0, 5)
        self.assertEqual(f.lines, ['a', 'b', 'c', 'd'])
        f.putl_src('efg\nhij', 1, 0, 2, 1)
        self.assertEqual(f.lines, ['a', 'efg', 'hij', 'd'])
        f.putl_src('***', 1, 2, 2, 1)
        self.assertEqual(f.lines, ['a', 'ef***ij', 'd'])

    def test_fix(self):
        f = FST.fromsrc('if 1:\n a\nelif 2:\n b')
        fc = f.a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual(fc.lines[0], 'elif 2:')
        fc.fix(inplace=True)
        self.assertEqual(fc.lines[0], 'if 2:')
        fc.verify(raise_=True)

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual(fc.src, '1 +\n2')
        fc.fix(inplace=True)
        self.assertEqual(fc.src, '(1 +\n2)')
        fc.verify(raise_=True)

        f = FST.fromsrc('i = 1')
        self.assertIs(f.a.body[0].targets[0].ctx.__class__, Store)
        fc = f.a.body[0].targets[0].f.copy(fix=False)
        self.assertIs(fc.a.ctx.__class__, Store)
        fc.fix(inplace=True)
        self.assertIs(fc.a.ctx.__class__, Load)
        fc.verify(raise_=True)

        f = FST.fromsrc('if 1: pass\nelif 2: pass').a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual('elif 2: pass', f.src)

        g = f.fix(inplace=False)
        self.assertIsNot(g, f)
        self.assertEqual('if 2: pass', g.src)
        self.assertEqual('elif 2: pass', f.src)

        g = f.fix(inplace=True)
        self.assertIs(g, f)
        self.assertEqual('if 2: pass', g.src)
        self.assertEqual('if 2: pass', f.src)

        f = FST.fromsrc('i, j = 1, 2').a.body[0].targets[0].f.copy(fix=False)
        self.assertEqual('i, j', f.src)
        self.assertIsNot(f, f.fix(inplace=False))

        g = f.fix(inplace=False)
        self.assertFalse(compare_asts(f.a, g.a))
        self.assertIs(g, g.fix(inplace=False))

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(fix=False)
        self.assertEqual('w := x,', f.src)

        g = f.fix(inplace=False)
        self.assertEqual('(w := x,)', g.src)
        self.assertTrue(compare_asts(f.a, g.a, locs=False))
        self.assertFalse(compare_asts(f.a, g.a, locs=True))
        self.assertIs(g, g.fix(inplace=False))

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('1 +\n2', fc.src)
        fd = fc.fix(inplace=False)
        self.assertEqual('(1 +\n2)', fd.src)
        fc.fix(inplace=True)
        self.assertEqual('(1 +\n2)', fc.src)

        f = FST.fromsrc('yield a1, a2')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('yield a1, a2', fc.src)
        fd = fc.fix(inplace=False)
        self.assertEqual('(yield a1, a2)', fd.src)
        fc.fix(inplace=True)
        self.assertEqual('(yield a1, a2)', fc.src)

        f = FST.fromsrc("""[
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format
]""".strip())
        fc = f.a.body[0].value.elts[0].f.copy(fix=False)
        self.assertEqual("""
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format""".strip(), fc.src)
        fd = fc.fix(inplace=False)
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fd.src)
        fc.fix(inplace=True)
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fc.src)

        f = FST.fromsrc("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))
        """.strip())
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual("""
(is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute))""".strip(), fc.src)
        fd = fc.fix(inplace=False)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fd.src)
        fc.fix(inplace=True)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fc.src)

        if sys.version_info[:2] >= (3, 12):
            fc = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(fix=False)
            self.assertEqual('*tuple[int, ...]', fc.src)
            fd = fc.fix(inplace=False)
            self.assertEqual('(*tuple[int, ...],)', fd.src)
            fc.fix(inplace=True)
            self.assertEqual('(*tuple[int, ...],)', fc.src)

    def test_copy(self):
        f = FST.fromsrc('@decorator\nclass cls:\n  pass')
        self.assertEqual(f.a.body[0].f.copy(fix=False).src, '@decorator\nclass cls:\n  pass')
        self.assertEqual(f.a.body[0].f.copy(decos=False, fix=False).src, 'class cls:\n  pass')

        l = FST.fromsrc("['\\u007f', '\\u0080', 'ʁ', 'ᛇ', '時', '🐍', '\\ud800', 'Źdźbło']").a.body[0].value.elts
        self.assertEqual("'\\u007f'", l[0].f.copy().src)
        self.assertEqual("'\\u0080'", l[1].f.copy().src)
        self.assertEqual("'ʁ'", l[2].f.copy().src)
        self.assertEqual("'ᛇ'", l[3].f.copy().src)
        self.assertEqual("'時'", l[4].f.copy().src)
        self.assertEqual("'🐍'", l[5].f.copy().src)
        self.assertEqual("'\\ud800'", l[6].f.copy().src)
        self.assertEqual("'Źdźbło'", l[7].f.copy().src)

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(fix=True)
        self.assertEqual('(w := x,)', f.src)

        f = FST.fromsrc('a[1:2, 3:4]').a.body[0].value.slice.f.copy(fix=False)
        self.assertIs(f.fix(inplace=False), f)
        # self.assertRaises(SyntaxError, f.fix)
        # self.assertIs(None, f.fix(raise_=False))

        f = FST.fromsrc('''
if 1:
    def f():
        """
        docstring
        """
        """
        regular text
        """
            '''.strip())
        self.assertEqual('''
def f():
    """
    docstring
    """
    """
        regular text
        """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    async def f():
        """
        docstring
        """
        """
        regular text
        """
            '''.strip())
        self.assertEqual('''
async def f():
    """
    docstring
    """
    """
        regular text
        """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        docstring
        """
        """
        regular text
        """
          '''.strip())
        self.assertEqual('''
class cls:
    """
    docstring
    """
    """
        regular text
        """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
# start

"""docstring"""

i = 1

# end
            '''.strip())
        self.assertEqual(f.copy().copy_src(), f.src)

        if sys.version_info[:2] >= (3, 12):
            f = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(fix=True)
            self.assertEqual('(*tuple[int, ...],)', f.src)

    def test_copy_bulk(self):
        for fnm in PYFNMS:
            ast = FST.fromsrc(read(fnm)).a

            for a in walk(ast):
                if a.f.is_parsable():
                    f = a.f.copy(fix=True)
                    f.verify(raise_=True)

    def test_slice_stmt(self):
        self.assertEqual('\n'.join(parse("""
def f():
    i = 1
    j = 1
    k = 1
    l = 1
            """.strip()).body[0].f.get_slice(-2).dump(print=False)), """
Module .. ROOT 0,0 -> 1,5
  .body[2]
  0] Assign .. 0,0 -> 0,5
    .targets[1]
    0] Name .. 0,0 -> 0,1
      .id
        'k'
      .ctx
        Store
    .value
      Constant .. 0,4 -> 0,5
        .value
          1
        .kind
          None
    .type_comment
      None
  1] Assign .. 1,0 -> 1,5
    .targets[1]
    0] Name .. 1,0 -> 1,1
      .id
        'l'
      .ctx
        Store
    .value
      Constant .. 1,4 -> 1,5
        .value
          1
        .kind
          None
    .type_comment
      None
            """.strip())

        self.assertEqual('\n'.join(parse("""
try: pass
except ValueError: pass
except RuntimeError: pass
except IndexError: pass
except TypeError: pass
            """.strip()).body[0].f.get_slice(-1, field='handlers').dump(print=False)), """
Module .. ROOT 0,0 -> 0,22
  .body[1]
  0] ExceptHandler .. 0,0 -> 0,22
    .type
      Name .. 0,7 -> 0,16
        .id
          'TypeError'
        .ctx
          Load
    .name
      None
    .body[1]
    0] Pass .. 0,18 -> 0,22
            """.strip())

        self.assertEqual('\n'.join(parse("""
match a:
    case 1: pass
    case f: pass
    case None: pass
    case 3 | 4: pass
            """.strip()).body[0].f.get_slice(1, 3).dump(print=False)), """
Module .. ROOT 0,0 -> 1,15
  .body[2]
  0] match_case .. 0,0 -> 0,7
    .pattern
      MatchAs .. 0,0 -> 0,1
        .pattern
          None
        .name
          'f'
    .guard
      None
    .body[1]
    0] Pass .. 0,3 -> 0,7
  1] match_case .. 1,5 -> 1,15
    .pattern
      MatchSingleton .. 1,5 -> 1,9
        .value
          None
    .guard
      None
    .body[1]
    0] Pass .. 1,11 -> 1,15
            """.strip())


        dumptest(self, parse("""
if 1: pass
elif 2: pass
            """.strip()).body[0].f.get_slice(field='orelse'), """
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] If .. 0,0 -> 0,10
    .test
      Constant .. 0,3 -> 0,4
        .value
          2
        .kind
          None
    .body[1]
    0] Pass .. 0,6 -> 0,10
            """.strip(), 'if 2: pass')

        dumptest(self, parse("""
if 1: pass
else:
  if 2: pass
            """.strip()).body[0].f.get_slice(field='orelse'), """
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] If .. 0,0 -> 0,10
    .test
      Constant .. 0,3 -> 0,4
        .value
          2
        .kind
          None
    .body[1]
    0] Pass .. 0,6 -> 0,10
            """.strip(), 'if 2: pass')

    def test_slice_seq_expr_1(self):
        dumptest(self, parse("""
(1, 2, 3, 4)
            """.strip()).body[0].value.f.get_slice(1, 3), """
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), '(2, 3)')

        dumptest(self, parse("""
(1, 2, 3, 4)
            """.strip()).body[0].value.f.get_slice(-1), """
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      4
    .kind
      None
  .ctx
    Load
            """.strip(), '(4,)')

        dumptest(self, parse("""
(1, 2, 3, 4)
            """.strip()).body[0].value.f.get_slice(), """
Tuple .. ROOT 0,0 -> 0,12
  .elts[4]
  0] Constant .. 0,1 -> 0,2
    .value
      1
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      2
    .kind
      None
  2] Constant .. 0,7 -> 0,8
    .value
      3
    .kind
      None
  3] Constant .. 0,10 -> 0,11
    .value
      4
    .kind
      None
  .ctx
    Load
            """.strip(), '(1, 2, 3, 4)')

        dumptest(self, parse("""
(1, 2, 3, 4)
            """.strip()).body[0].value.f.get_slice(1, 1), """
Tuple .. ROOT 0,0 -> 0,2
  .ctx
    Load
            """.strip(), '()')

        dumptest(self, parse("""
[1, 2, 3, 4]
            """.strip()).body[0].value.f.get_slice(1, 3), """
List .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), '[2, 3]')

        dumptest(self, parse("""
[1, 2, 3, 4]
            """.strip()).body[0].value.f.get_slice(-1), """
List .. ROOT 0,0 -> 0,3
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      4
    .kind
      None
  .ctx
    Load
            """.strip(), '[4]')

        dumptest(self, parse("""
[1, 2, 3, 4]
            """.strip()).body[0].value.f.get_slice(), """
List .. ROOT 0,0 -> 0,12
  .elts[4]
  0] Constant .. 0,1 -> 0,2
    .value
      1
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      2
    .kind
      None
  2] Constant .. 0,7 -> 0,8
    .value
      3
    .kind
      None
  3] Constant .. 0,10 -> 0,11
    .value
      4
    .kind
      None
  .ctx
    Load
            """.strip(), '[1, 2, 3, 4]')

        dumptest(self, parse("""
[1, 2, 3, 4]
            """.strip()).body[0].value.f.get_slice(1, 1), """
List .. ROOT 0,0 -> 0,2
  .ctx
    Load
            """.strip(), '[]')

        dumptest(self, parse("""
{1, 2, 3, 4}
            """.strip()).body[0].value.f.get_slice(1, 3), """
Set .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      3
    .kind
      None
            """.strip(), '{2, 3}')

        dumptest(self, parse("""
{1, 2, 3, 4}
            """.strip()).body[0].value.f.get_slice(-1), """
Set .. ROOT 0,0 -> 0,3
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      4
    .kind
      None
            """.strip(), '{4}')

        dumptest(self, parse("""
{1, 2, 3, 4}
            """.strip()).body[0].value.f.get_slice(), """
Set .. ROOT 0,0 -> 0,12
  .elts[4]
  0] Constant .. 0,1 -> 0,2
    .value
      1
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      2
    .kind
      None
  2] Constant .. 0,7 -> 0,8
    .value
      3
    .kind
      None
  3] Constant .. 0,10 -> 0,11
    .value
      4
    .kind
      None
            """.strip(), '{1, 2, 3, 4}')

        dumptest(self, parse("""
{1, 2, 3, 4}
            """.strip()).body[0].value.f.get_slice(1, 1), """
Call .. ROOT 0,0 -> 0,5
  .func
    Name .. 0,0 -> 0,3
      .id
        'set'
      .ctx
        Load
            """.strip(), 'set()')

        dumptest(self, parse("""

(1, 2, 3, 4)
            """.strip()).body[0].value.f.get_slice(1, 3), """
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), '(2, 3)')

        dumptest(self, parse("""
{1: 2, 3: 4, 5: 6, 7: 8}
            """.strip()).body[0].value.f.get_slice(1, 3), """
Dict .. ROOT 0,0 -> 0,12
  .keys[2]
  0] Constant .. 0,1 -> 0,2
    .value
      3
    .kind
      None
  1] Constant .. 0,7 -> 0,8
    .value
      5
    .kind
      None
  .values[2]
  0] Constant .. 0,4 -> 0,5
    .value
      4
    .kind
      None
  1] Constant .. 0,10 -> 0,11
    .value
      6
    .kind
      None
            """.strip(), '{3: 4, 5: 6}')

        dumptest(self, parse("""
{1: 2, 3: 4, 5: 6, 7: 8}
            """.strip()).body[0].value.f.get_slice(-1), """
Dict .. ROOT 0,0 -> 0,6
  .keys[1]
  0] Constant .. 0,1 -> 0,2
    .value
      7
    .kind
      None
  .values[1]
  0] Constant .. 0,4 -> 0,5
    .value
      8
    .kind
      None
            """.strip(), '{7: 8}')

        dumptest(self, parse("""
{1: 2, 3: 4, 5: 6, 7: 8}
            """.strip()).body[0].value.f.get_slice(), """
Dict .. ROOT 0,0 -> 0,24
  .keys[4]
  0] Constant .. 0,1 -> 0,2
    .value
      1
    .kind
      None
  1] Constant .. 0,7 -> 0,8
    .value
      3
    .kind
      None
  2] Constant .. 0,13 -> 0,14
    .value
      5
    .kind
      None
  3] Constant .. 0,19 -> 0,20
    .value
      7
    .kind
      None
  .values[4]
  0] Constant .. 0,4 -> 0,5
    .value
      2
    .kind
      None
  1] Constant .. 0,10 -> 0,11
    .value
      4
    .kind
      None
  2] Constant .. 0,16 -> 0,17
    .value
      6
    .kind
      None
  3] Constant .. 0,22 -> 0,23
    .value
      8
    .kind
      None
            """.strip(), '{1: 2, 3: 4, 5: 6, 7: 8}')

        dumptest(self, parse("""
{1: 2, 3: 4, 5: 6, 7: 8}
            """.strip()).body[0].value.f.get_slice(1, 1), """
Dict .. ROOT 0,0 -> 0,2
            """.strip(), '{}')

    def test_slice_seq_expr_2(self):
        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)           """.strip()).body[0].value.f.get_slice(), """
Tuple .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant .. 1,4 -> 1,5
    .value
      1
    .kind
      None
  1] Constant .. 2,4 -> 2,5
    .value
      2
    .kind
      None
  2] Constant .. 3,4 -> 3,5
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), """
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.get_slice(0, 2), """
Tuple .. ROOT 0,0 -> 3,1
  .elts[2]
  0] Constant .. 1,4 -> 1,5
    .value
      1
    .kind
      None
  1] Constant .. 2,4 -> 2,5
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(
    1,  # first line
    2,  # second line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.get_slice(1, 2), """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant .. 1,4 -> 1,5
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(
    2,  # second line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.get_slice(2), """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant .. 1,4 -> 1,5
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), """
(
    3,  # third line
)
            """.strip())

        dumptest(self, parse("""
(           # hello
    1, 2, 3 # last line
)
            """.strip()).body[0].value.f.get_slice(), """
Tuple .. ROOT 0,0 -> 2,1
  .elts[3]
  0] Constant .. 1,4 -> 1,5
    .value
      1
    .kind
      None
  1] Constant .. 1,7 -> 1,8
    .value
      2
    .kind
      None
  2] Constant .. 1,10 -> 1,11
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), """
(           # hello
    1, 2, 3 # last line
)
            """.strip())

        dumptest(self, parse("""
(           # hello
    1, 2, 3 # last line
)
            """.strip()).body[0].value.f.get_slice(0, 2), """
Tuple .. ROOT 0,0 -> 1,9
  .elts[2]
  0] Constant .. 1,4 -> 1,5
    .value
      1
    .kind
      None
  1] Constant .. 1,7 -> 1,8
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(
    1, 2)
            """.strip())

        dumptest(self, parse("""
(           # hello
    1, 2, 3 # last line
)
            """.strip()).body[0].value.f.get_slice(1, 2), """
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(2,)
            """.strip())

        dumptest(self, parse("""
(           # hello
    1, 2, 3 # last line
)
            """.strip()).body[0].value.f.get_slice(2), """
Tuple .. ROOT 0,0 -> 1,1
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), """
(3, # last line
)
            """.strip())

    def test_slice_seq_expr_3(self):
        dumptest(self, parse("""
1, 2, 3, 4
            """.strip()).body[0].value.f.get_slice(1, 3), """
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), """
(2, 3)
            """.strip())

        dumptest(self, parse("""
1, 2, 3, 4
            """.strip()).body[0].value.f.get_slice(-1), """
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      4
    .kind
      None
  .ctx
    Load
            """.strip(), """
(4,)
            """.strip())

        dumptest(self, parse("""
1, 2, 3, 4
            """.strip()).body[0].value.f.get_slice(), """
Tuple .. ROOT 0,0 -> 0,12
  .elts[4]
  0] Constant .. 0,1 -> 0,2
    .value
      1
    .kind
      None
  1] Constant .. 0,4 -> 0,5
    .value
      2
    .kind
      None
  2] Constant .. 0,7 -> 0,8
    .value
      3
    .kind
      None
  3] Constant .. 0,10 -> 0,11
    .value
      4
    .kind
      None
  .ctx
    Load
            """.strip(), """
(1, 2, 3, 4)
            """.strip())

        dumptest(self, parse("""
1, 2, 3, 4
            """.strip()).body[0].value.f.get_slice(1, 1), """
Tuple .. ROOT 0,0 -> 0,2
  .ctx
    Load
            """.strip(), """
()
            """.strip())

    def test_slice_seq_expr_4(self):
        dumptest(self, parse("""
(1, 2
  ,  # comment
3, 4)
            """.strip()).body[0].value.f.get_slice(1, 2), """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(2
  ,  # comment
)
            """.strip())

        dumptest(self, parse("""
(1, 2
  ,
3, 4)
            """.strip()).body[0].value.f.get_slice(1, 2), """
Tuple .. ROOT 0,0 -> 1,4
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(2
  ,)
            """.strip())

        dumptest(self, parse("""
(1, 2
  , 3, 4)
            """.strip()).body[0].value.f.get_slice(1, 2), """
Tuple .. ROOT 0,0 -> 1,4
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(2
  ,)
            """.strip())

        dumptest(self, parse("""
(1, 2  # comment
  , 3, 4)
            """.strip()).body[0].value.f.get_slice(1, 2), """
Tuple .. ROOT 0,0 -> 1,4
  .elts[1]
  0] Constant .. 0,1 -> 0,2
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(2  # comment
  ,)
            """.strip())

    def test_slice_seq_expr_5(self):
        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.get_slice(), """
Tuple .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant .. 1,4 -> 1,5
    .value
      1
    .kind
      None
  1] Constant .. 2,4 -> 2,5
    .value
      2
    .kind
      None
  2] Constant .. 3,4 -> 3,5
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), """
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.get_slice(0, 2), """
Tuple .. ROOT 0,0 -> 3,1
  .elts[2]
  0] Constant .. 1,4 -> 1,5
    .value
      1
    .kind
      None
  1] Constant .. 2,4 -> 2,5
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(
    1,  # first line
    2,  # second line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.get_slice(1, 2), """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant .. 1,4 -> 1,5
    .value
      2
    .kind
      None
  .ctx
    Load
            """.strip(), """
(
    2,  # second line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.get_slice(2), """
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant .. 1,4 -> 1,5
    .value
      3
    .kind
      None
  .ctx
    Load
            """.strip(), """
(
    3,  # third line
)
            """.strip())

    def test_cut(self):
        for src, elt, start, stop, src_cut, slice_cut, src_dump, slice_dump in CUT_DATA:
            src   = src.strip()
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.get_slice(start, stop, cut=True)
            tsrc  = t.f.src
            ssrc  = s.src
            tdump = t.f.dump(print=False, compact=True)
            sdump = s.dump(print=False, compact=True)

            self.assertEqual(tsrc, src_cut.strip())
            self.assertEqual(ssrc, slice_cut.strip())
            self.assertEqual(tdump, src_dump.strip().split('\n'))
            self.assertEqual(sdump, slice_dump.strip().split('\n'))

    def test_put_slice(self):
        for dst, elt, start, stop, src, put_src, put_dump in PUT_SLICE_DATA:
            dst = dst.strip()
            src = src.strip()
            t   = parse(dst)
            f   = eval(f't.{elt}', {'t': t}).f

            f.put_slice(src, start, stop)

            tdst  = t.f.src
            tdump = t.f.dump(print=False, compact=True)

            self.assertEqual(tdst, put_src.strip())
            self.assertEqual(tdump, put_dump.strip().split('\n'))


def regen_cut_data():
    newlines = []

    for src, elt, start, stop, *_ in CUT_DATA:
        src   = src.strip()
        t     = parse(src)
        f     = eval(f't.{elt}', {'t': t}).f
        s     = f.get_slice(start, stop, cut=True)
        tsrc  = t.f.src
        ssrc  = s.src
        tdump = t.f.dump(print=False, compact=True)
        sdump = s.dump(print=False, compact=True)

        assert not tsrc.startswith('\n') or tsrc.endswith('\n')
        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        t.f.verify()
        s.verify()

        newlines.append('("""')
        newlines.extend(f'''{src}\n""", {elt!r}, {start}, {stop}, """\n{tsrc}\n""", """\n{ssrc}\n""", """'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('""", """')
        newlines.extend(sdump)
        newlines.append('"""),\n')

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('CUT_DATA = [')
    stop  = lines.index(']  # END OF CUT_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_data():
    newlines = []

    for dst, elt, start, stop, src, put_src, put_dump in PUT_SLICE_DATA:
        dst = dst.strip()
        src = src.strip()
        t   = parse(dst)
        f   = eval(f't.{elt}', {'t': t}).f

        f.put_slice(src, start, stop)

        tdst  = t.f.src
        tdump = t.f.dump(print=False, compact=True)

        assert not tdst.startswith('\n') or tdst.endswith('\n')

        t.f.verify()

        newlines.append('("""')
        newlines.extend(f'''{dst}\n""", {elt!r}, {start}, {stop}, """\n{src}\n""", """\n{tdst}\n""", """'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='python -m fst')

    parser.add_argument('--regen-cut', default=False, action='store_true', help="regenerate cut test data")
    parser.add_argument('--regen-put-slice', default=False, action='store_true', help="regenerate put slice test data")

    args = parser.parse_args()

    if args.regen_cut:
        print('Regenerating cut test data...')
        regen_cut_data()

    if args.regen_put_slice:
        print('Regenerating put slice test data...')
        regen_put_slice_data()

    if not args.regen_cut and not args.regen_put_slice:
        unittest.main()
