#!/usr/bin/env python

import unittest

from fst import *
from fst.astutil import re_identifier, re_identifier_only
from fst.parsex import parse_expr
from fst.code import code_as_identifier

IDENTIFIERS = [
    'ä',
    'µ',          # normalization
    '蟒',
    'x󠄀',           # variation selector
    '𝔘𝔫𝔦𝔠𝔬𝔡𝔢',      # normalization
    'абвгд',
    'Źdźbło',
    'العربية',    # Arabic
    '中文',        # Chinese
    'кириллица',  # Cyrillic
    'Ελληνικά',   # Greek
    'עִברִית',       # Hebrew
    '日本語',      # Japanese
    '한국어',       # Korean
    'ไทย',        # Thai
    'देवनागरी',      # Devanagari
]


class TestFSTUnicode(unittest.TestCase):
    def test_re_identifier(self):
        for ident in IDENTIFIERS:
            self.assertTrue(m := re_identifier.match(ident))
            self.assertEqual(ident, m.group())

            self.assertTrue(m := re_identifier_only.match(ident))
            self.assertEqual(ident, m.group())

    def test_same_as_parse(self):
        for ident in IDENTIFIERS:
            f = parse_expr(ident)
            i = code_as_identifier(ident)
            self.assertEqual(i, f.id)


if __name__ == '__main__':
    unittest.main()
