# pfst

**High-level Python AST manipulation that preserves formatting**

[![PyPI version](https://img.shields.io/badge/pypi-0.2.6-orange.svg)](https://pypi.org/project/pfst/)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14%20%7C%203.15a-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

This module exists in order to facilitate quick and easy high level editing of Python source in the form of an `AST` tree while preserving formatting. It is meant to allow you to change Python code functionality while not having to deal with the details of:

- Operator precedence and parentheses
- Indentation and line continuations
- Commas, semicolons, and tuple edge cases
- Comments and docstrings
- Various Python version-specific syntax quirks
- Etc...

See [Example Recipes](https://tom-pytel.github.io/pfst/fst/docs/d13_examples.html) for more in-depth examples. Or go straight to the [Documentation](https://tom-pytel.github.io/pfst/fst.html).

```py
>>> import fst  # pip install pfst, import fst

>>> ext_ast = parse('logger.info("message", extra=extra)  # done')

>>> ext_ast.f.body[0].value.insert('\nid=CID  # comment', -1)

>>> print(fst.unparse(ext_ast))
logger.info('message',
            id=CID,  # comment
            extra=extra)  # done
```

The tree is just normal `AST` with metadata, so if you know `AST`, you know `FST`.

```py
>>> import ast

>>> print(ast.unparse(ext_ast))
logger.info('message', id=CID, extra=extra)
```

## Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)

## Install

From PyPI:

    pip install pfst

From GitHub using pip:

    pip install git+https://github.com/tom-pytel/pfst.git

From GitHub, after cloning for development:

    pip install -e .[dev]

### TODO

This module is not finished but functional enough that it can be useful.

* Put one to:
  * `FormattedValue.conversion`
  * `FormattedValue.format_spec`
  * `Interpolation.str`
  * `Interpolation.conversion`
  * `Interpolation.format_spec`

* Prescribed get / put slice from / to:
  * `MatchClass.patterns+kwd_attrs:kwd_patterns`
  * `JoinedStr.values`
  * `TemplateStr.values`

* Improve comment and whitespace handling, especially allow get / put comments in single element non-statement
operations where it may apply (where comment may belong to expression instead of statement). Allow specify insert line.
Direct comment manipulation functions.

* Indentation of multiline sequences should be better, decide between primitive or node ops on primitive fields,
different source encodings, code cleanups, API additions for real-world use, optimization, testing, bughunting, etc...

* Finish `reconcile()`. Proper comment handling, locations and deduplication. Make it use all slice operations to
preserve more formatting.


### Trivia

The "F" in FST stands for "Fun".
