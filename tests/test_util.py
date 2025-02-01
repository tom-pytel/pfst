#!/usr/bin/env python

import unittest
from fst.util import *


class TestUtil(unittest.TestCase):
    def test_aststr(self):
        s = aststr('\x7f' * 127)

        self.assertEqual(s.c2b(0), 0)
        self.assertEqual(s.b2c(0), 0)
        self.assertEqual(s.c2b(127), 127)
        self.assertEqual(s.b2c(127), 127)
        self.assertEqual(s.c2b(128), 128)
        self.assertEqual(s.b2c(128), 128)
        self.assertEqual(s.c2b(-1), -1)
        self.assertEqual(s.b2c(-1), -1)
        self.assertEqual(s.c2b(-128), -128)
        self.assertEqual(s.b2c(-128), -128)
        self.assertEqual(s.c2b(-129), -129)
        self.assertEqual(s.b2c(-129), -129)

        s = aststr('\u00ff' * 127)

        self.assertEqual(s.c2b(0), 0)
        self.assertEqual(s.b2c(0), 0)
        self.assertEqual(s.c2b(127), 254)
        self.assertEqual(s.b2c(254), 127)
        self.assertEqual(s.c2b(-1), 254)
        self.assertEqual(s.b2c(-1), 127)
        self.assertEqual(s.c2b(-128), 0)
        self.assertEqual(s.b2c(-255), 0)
        self.assertRaises(IndexError, s.c2b, 128)
        self.assertRaises(IndexError, s.b2c, 255)
        self.assertRaises(IndexError, s.c2b, -129)
        self.assertRaises(IndexError, s.b2c, -256)
        self.assertEqual(getattr(s, '_aststr__c2b').typecode, 'B')
        self.assertEqual(getattr(s, '_aststr__b2c').typecode, 'B')

        for i in range(127):
            self.assertEqual(i, s.b2c(s.c2b(i)))
            self.assertIsNone(s.b2c(2*i + 1))

        s = aststr('\u00ff' * 128)

        self.assertEqual(s.c2b(0), 0)
        self.assertEqual(s.b2c(0), 0)
        self.assertEqual(s.c2b(128), 256)
        self.assertEqual(s.b2c(256), 128)
        self.assertEqual(s.c2b(-1), 256)
        self.assertEqual(s.b2c(-1), 128)
        self.assertEqual(s.c2b(-129), 0)
        self.assertEqual(s.b2c(-257), 0)
        self.assertRaises(IndexError, s.c2b, 129)
        self.assertRaises(IndexError, s.b2c, 257)
        self.assertRaises(IndexError, s.c2b, -130)
        self.assertRaises(IndexError, s.b2c, -258)
        self.assertEqual(getattr(s, '_aststr__c2b').typecode, 'H')
        self.assertEqual(getattr(s, '_aststr__b2c').typecode, 'B')

        for i in range(128):
            self.assertEqual(i, s.b2c(s.c2b(i)))
            self.assertIsNone(s.b2c(2*i + 1))

        s = aststr('\u00ff' * 256)

        self.assertEqual(s.c2b(0), 0)
        self.assertEqual(s.b2c(0), 0)
        self.assertEqual(s.c2b(256), 512)
        self.assertEqual(s.b2c(512), 256)
        self.assertEqual(s.c2b(-1), 512)
        self.assertEqual(s.b2c(-1), 256)
        self.assertEqual(s.c2b(-257), 0)
        self.assertEqual(s.b2c(-513), 0)
        self.assertRaises(IndexError, s.c2b, 257)
        self.assertRaises(IndexError, s.b2c, 513)
        self.assertRaises(IndexError, s.c2b, -258)
        self.assertRaises(IndexError, s.b2c, -514)

        self.assertEqual(getattr(s, '_aststr__c2b').typecode, 'H')
        self.assertEqual(getattr(s, '_aststr__b2c').typecode, 'H')

        for i in range(256):
            self.assertEqual(i, s.b2c(s.c2b(i)))
            self.assertIsNone(s.b2c(2*i + 1))


if __name__ == '__main__':
    unittest.main()
