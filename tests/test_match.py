#!/usr/bin/env python

import os
import re
import unittest

from fst import *

from fst.common import PYLT14, PYGE12, PYGE13
from fst.match import *

from support import SubCases, assertRaises


DIR_NAME = os.path.dirname(__file__)
DATA_SUB = SubCases(os.path.join(DIR_NAME, 'data/data_sub.py'))


def regen_sub_data():
    DATA_SUB.generate()
    DATA_SUB.write()


class TestMatch(unittest.TestCase):
    """Match, search and substitute."""

    maxDiff = None

    def test_match_pat_repr(self):
        self.assertEqual("M('pat')", repr(M('pat')))
        self.assertEqual("M(pat_tag='pat')", repr(M(pat_tag='pat')))
        self.assertEqual("M('pat', static1='stag1', static2='stag2')", repr(M('pat', static1='stag1', static2='stag2')))
        self.assertEqual("M(pat_tag='pat', static1='stag1', static2='stag2')", repr(M(pat_tag='pat', static1='stag1', static2='stag2')))

        self.assertEqual("MNOT('pat')", repr(MNOT('pat')))
        self.assertEqual("MNOT(pat_tag='pat')", repr(MNOT(pat_tag='pat')))
        self.assertEqual("MNOT('pat', static1='stag1', static2='stag2')", repr(MNOT('pat', static1='stag1', static2='stag2')))
        self.assertEqual("MNOT(pat_tag='pat', static1='stag1', static2='stag2')", repr(MNOT(pat_tag='pat', static1='stag1', static2='stag2')))

        self.assertEqual("MOR('pat1', 'pat2')", repr(MOR('pat1', 'pat2')))
        self.assertEqual("MOR(tag1='tpat1', tag2='tpat2')", repr(MOR(tag1='tpat1', tag2='tpat2')))
        self.assertEqual("MOR('pat1', 'pat2', tag1='tpat1', tag2='tpat2')", repr(MOR('pat1', 'pat2', tag1='tpat1', tag2='tpat2')))

        self.assertEqual("MAND('pat1', 'pat2')", repr(MAND('pat1', 'pat2')))
        self.assertEqual("MAND(tag1='tpat1', tag2='tpat2')", repr(MAND(tag1='tpat1', tag2='tpat2')))
        self.assertEqual("MAND('pat1', 'pat2', tag1='tpat1', tag2='tpat2')", repr(MAND('pat1', 'pat2', tag1='tpat1', tag2='tpat2')))

        self.assertEqual("MTYPES((If, With))", repr(MTYPES((If, With))))
        self.assertEqual("MTYPES((If, With), body=[...], orelse=[...])", repr(MTYPES((If, With), body=[...], orelse=[...])))

        self.assertEqual("MOPT('pat')", repr(MOPT('pat')))
        self.assertEqual("MOPT(pat_tag='pat')", repr(MOPT(pat_tag='pat')))
        self.assertEqual("MOPT('pat', static1='stag1', static2='stag2')", repr(MOPT('pat', static1='stag1', static2='stag2')))
        self.assertEqual("MOPT(pat_tag='pat', static1='stag1', static2='stag2')", repr(MOPT(pat_tag='pat', static1='stag1', static2='stag2')))

        self.assertEqual("MRE(re.compile('re_pat'))", repr(MRE('re_pat')))
        self.assertEqual("MRE(re.compile('re_pat', re.VERBOSE))", repr(MRE('re_pat', re.VERBOSE)))
        self.assertEqual("MRE(re.compile('re_pat'), search=True)", repr(MRE('re_pat', search=True)))
        self.assertEqual("MRE(re.compile('re_pat', re.VERBOSE), search=True)", repr(MRE('re_pat', re.VERBOSE, True)))
        self.assertEqual("MRE(re.compile('re_pat'), static1='stag1', static2='stag2')", repr(MRE('re_pat', static1='stag1', static2='stag2')))
        self.assertEqual("MRE(re.compile('re_pat', re.VERBOSE), static1='stag1', static2='stag2')", repr(MRE('re_pat', re.VERBOSE, static1='stag1', static2='stag2')))
        self.assertEqual("MRE(re.compile('re_pat'), search=True, static1='stag1', static2='stag2')", repr(MRE('re_pat', search=True, static1='stag1', static2='stag2')))
        self.assertEqual("MRE(re.compile('re_pat', re.VERBOSE), search=True, static1='stag1', static2='stag2')", repr(MRE('re_pat', re.VERBOSE, True, static1='stag1', static2='stag2')))

        self.assertEqual("MCB(TestMatch.test_match_pat_repr)", repr(MCB(TestMatch.test_match_pat_repr)))
        self.assertEqual("MCB(TestMatch.test_match_pat_repr, fail_obj='fail')", repr(MCB(TestMatch.test_match_pat_repr, fail_obj='fail')))
        self.assertEqual("MCB(cb=TestMatch.test_match_pat_repr)", repr(MCB(cb=TestMatch.test_match_pat_repr)))
        self.assertEqual("MCB(cb=TestMatch.test_match_pat_repr, fail_obj='fail')", repr(MCB(cb=TestMatch.test_match_pat_repr, fail_obj='fail')))
        self.assertEqual("MCB(cb=TestMatch.test_match_pat_repr, tag_ret=True)", repr(MCB(cb=TestMatch.test_match_pat_repr, tag_ret=True)))
        self.assertEqual("MCB(cb=TestMatch.test_match_pat_repr, tag_ret=True, fail_obj='fail')", repr(MCB(cb=TestMatch.test_match_pat_repr, tag_ret=True, fail_obj='fail')))
        self.assertEqual("MCB(TestMatch.test_match_pat_repr, static1='stag1', static2='stag2')", repr(MCB(TestMatch.test_match_pat_repr, static1='stag1', static2='stag2')))
        self.assertEqual("MCB(TestMatch.test_match_pat_repr, fail_obj='fail', static1='stag1', static2='stag2')", repr(MCB(TestMatch.test_match_pat_repr, fail_obj='fail', static1='stag1', static2='stag2')))
        self.assertEqual("MCB(cb=TestMatch.test_match_pat_repr, static1='stag1', static2='stag2')", repr(MCB(cb=TestMatch.test_match_pat_repr, static1='stag1', static2='stag2')))
        self.assertEqual("MCB(cb=TestMatch.test_match_pat_repr, fail_obj='fail', static1='stag1', static2='stag2')", repr(MCB(cb=TestMatch.test_match_pat_repr, fail_obj='fail', static1='stag1', static2='stag2')))
        self.assertEqual("MCB(cb=TestMatch.test_match_pat_repr, tag_ret=True, static1='stag1', static2='stag2')", repr(MCB(cb=TestMatch.test_match_pat_repr, tag_ret=True, static1='stag1', static2='stag2')))
        self.assertEqual("MCB(cb=TestMatch.test_match_pat_repr, tag_ret=True, fail_obj='fail', static1='stag1', static2='stag2')", repr(MCB(cb=TestMatch.test_match_pat_repr, tag_ret=True, fail_obj='fail', static1='stag1', static2='stag2')))

        self.assertEqual("MTAG('tag')", repr(MTAG('tag')))
        self.assertEqual("MTAG(pat_tag='tag')", repr(MTAG(pat_tag='tag')))
        self.assertEqual("MTAG('tag', static1='stag1', static2='stag2')", repr(MTAG('tag', static1='stag1', static2='stag2')))
        self.assertEqual("MTAG(pat_tag='tag', static1='stag1', static2='stag2')", repr(MTAG(pat_tag='tag', static1='stag1', static2='stag2')))

        self.assertEqual("MQ('pat', min=1, max=2)", repr(MQ('pat', 1, 2)))
        self.assertEqual("MQ(pat_tag='pat', min=1, max=2)", repr(MQ(pat_tag='pat', min=1, max=2)))
        self.assertEqual("MQ('pat', min=1, max=2, static1='stag1', static2='stag2')", repr(MQ('pat', 1, 2, static1='stag1', static2='stag2')))
        self.assertEqual("MQ(pat_tag='pat', min=1, max=2, static1='stag1', static2='stag2')", repr(MQ(pat_tag='pat', min=1, max=2, static1='stag1', static2='stag2')))

        self.assertEqual("MQSTAR('pat')", repr(MQSTAR('pat')))
        self.assertEqual("MQSTAR(pat_tag='pat')", repr(MQSTAR(pat_tag='pat')))
        self.assertEqual("MQSTAR('pat', static1='stag1', static2='stag2')", repr(MQSTAR('pat', static1='stag1', static2='stag2')))
        self.assertEqual("MQSTAR(pat_tag='pat', static1='stag1', static2='stag2')", repr(MQSTAR(pat_tag='pat', static1='stag1', static2='stag2')))

        self.assertEqual("MQPLUS('pat')", repr(MQPLUS('pat')))
        self.assertEqual("MQPLUS(pat_tag='pat')", repr(MQPLUS(pat_tag='pat')))
        self.assertEqual("MQPLUS('pat', static1='stag1', static2='stag2')", repr(MQPLUS('pat', static1='stag1', static2='stag2')))
        self.assertEqual("MQPLUS(pat_tag='pat', static1='stag1', static2='stag2')", repr(MQPLUS(pat_tag='pat', static1='stag1', static2='stag2')))

        self.assertEqual("MQ01('pat')", repr(MQ01('pat')))
        self.assertEqual("MQ01(pat_tag='pat')", repr(MQ01(pat_tag='pat')))
        self.assertEqual("MQ01('pat', static1='stag1', static2='stag2')", repr(MQ01('pat', static1='stag1', static2='stag2')))
        self.assertEqual("MQ01(pat_tag='pat', static1='stag1', static2='stag2')", repr(MQ01(pat_tag='pat', static1='stag1', static2='stag2')))

        self.assertEqual("MQMIN('pat', min=1)", repr(MQMIN('pat', 1)))
        self.assertEqual("MQMIN(pat_tag='pat', min=1)", repr(MQMIN(pat_tag='pat', min=1)))
        self.assertEqual("MQMIN('pat', min=1, static1='stag1', static2='stag2')", repr(MQMIN('pat', 1, static1='stag1', static2='stag2')))
        self.assertEqual("MQMIN(pat_tag='pat', min=1, static1='stag1', static2='stag2')", repr(MQMIN(pat_tag='pat', min=1, static1='stag1', static2='stag2')))

        self.assertEqual("MQMAX('pat', max=1)", repr(MQMAX('pat', 1)))
        self.assertEqual("MQMAX(pat_tag='pat', max=1)", repr(MQMAX(pat_tag='pat', max=1)))
        self.assertEqual("MQMAX('pat', max=1, static1='stag1', static2='stag2')", repr(MQMAX('pat', 1, static1='stag1', static2='stag2')))
        self.assertEqual("MQMAX(pat_tag='pat', max=1, static1='stag1', static2='stag2')", repr(MQMAX(pat_tag='pat', max=1, static1='stag1', static2='stag2')))

        self.assertEqual("MQN('pat', n=1)", repr(MQN('pat', 1)))
        self.assertEqual("MQN(pat_tag='pat', n=1)", repr(MQN(pat_tag='pat', n=1)))
        self.assertEqual("MQN('pat', n=1, static1='stag1', static2='stag2')", repr(MQN('pat', 1, static1='stag1', static2='stag2')))
        self.assertEqual("MQN(pat_tag='pat', n=1, static1='stag1', static2='stag2')", repr(MQN(pat_tag='pat', n=1, static1='stag1', static2='stag2')))

    def test_match_FSTMatch(self):
        # invalid tags

        assertRaises(ValueError("invalid tag 'tags' shadows match class attribute"), M, tags=...)
        assertRaises(ValueError("invalid tag 'tags' shadows match class attribute"), MNOT, tags=...)
        assertRaises(ValueError("invalid tag 'tags' shadows match class attribute"), MOR, tags=...)
        assertRaises(ValueError("invalid tag 'tags' shadows match class attribute"), MAND, tags=...)
        assertRaises(ValueError("invalid tag 'tags' shadows match class attribute"), MRE, tags='')
        assertRaises(ValueError("invalid tag 'tags' shadows match class attribute"), MCB, tags=lambda x: False)

        assertRaises(ValueError("invalid tag 'pattern' shadows match class attribute"), M, pattern=...)
        assertRaises(ValueError("invalid tag 'matched' shadows match class attribute"), M, matched=...)
        assertRaises(ValueError("invalid tag 'get' shadows match class attribute"), M, get=...)

        for n in dir(FSTMatch):
            assertRaises(ValueError(f"invalid tag {n!r} shadows match class attribute"), M, **{n: ...})

        # MQ

        assertRaises(ValueError('MQ min cannot be negative'), MQ, None, -1, None)
        assertRaises(ValueError('MQ max cannot be negative'), MQ, None, 0, -1)
        assertRaises(ValueError('MQ max cannot be lower than min'), MQ, None, 2, 1)

        # match object attribute access

        self.assertIs(FST('a').match(M(Name('a'), tag=True)).tag, True)
        self.assertIs(FST('a').match(M(Name('a'), tag=True)).noexist, NotSet)
        self.assertIs(FST('a').match(M(Name('a'), __tag__=True)).__tag__, True)
        self.assertRaises(AttributeError, lambda: FST('a').match(M(Name('a'), __tag__=True)).__noexist__)

        # get FST node

        f = FST('a = b')
        pat = MAssign(value='b')
        self.assertIs(f.match(pat).matched, f)
        self.assertIs(pat.match(f.a).matched, f.a)
        self.assertIs(pat.match(a := Assign(Name('a'), Name('b'))).matched, a)

    def test_match_basic(self):
        self.assertTrue(FST(Load()).match, ...)

        # expr_context

        self.assertTrue(FST(Load()).match(Load))
        self.assertTrue(FST(Load()).match(MLoad))
        self.assertTrue(FST(Load()).match(expr_context))
        self.assertTrue(FST(Load()).match(Mexpr_context))
        self.assertTrue(FST(Load()).match(AST))
        self.assertTrue(FST(Load()).match(MAST))
        self.assertFalse(FST(Load()).match(Store))
        self.assertFalse(FST(Load()).match(MStore))
        self.assertFalse(FST(Load()).match(stmt))
        self.assertFalse(FST(Load()).match(Mstmt))

        # type

        self.assertTrue(FST('a = 1').match(Assign))
        self.assertTrue(FST('a = 1').match(MAssign))
        self.assertTrue(FST('a = 1').match(stmt))
        self.assertTrue(FST('a = 1').match(Mstmt))
        self.assertTrue(FST('a = 1').match(AST))
        self.assertTrue(FST('a = 1').match(MAST))
        self.assertFalse(FST('a = 1').match(expr))
        self.assertFalse(FST('a = 1').match(Mexpr))

        # ctx

        self.assertTrue(FST(Load()).match(Load()))
        self.assertTrue(FST(Load()).match(Store()))
        self.assertTrue(FST(Load()).match(Del()))
        self.assertTrue(FST(Load()).match(Load(), ast_ctx=True))
        self.assertFalse(FST(Load()).match(Store(), ast_ctx=True))
        self.assertFalse(FST(Load()).match(Del(), ast_ctx=True))
        self.assertTrue(FST(Load()).match(MLoad()))
        self.assertFalse(FST(Load()).match(MStore()))
        self.assertFalse(FST(Load()).match(MDel()))

        self.assertTrue(FST(Name('i')).match(Name('i', Load())))
        self.assertTrue(FST(Name('i')).match(Name('i', Store())))
        self.assertTrue(FST(Name('i')).match(Name('i', Del())))
        self.assertTrue(FST(Name('i')).match(Name('i', Load()), ast_ctx=True))
        self.assertFalse(FST(Name('i')).match(Name('i', Store()), ast_ctx=True))
        self.assertFalse(FST(Name('i')).match(Name('i', Del()), ast_ctx=True))

        # str

        self.assertTrue(FST(Name('i')).match('i'))
        self.assertTrue(FST(arg('i')).match('i'))
        self.assertTrue(FST('i', 'withitem').match('i'))
        self.assertTrue(FST('a, /, b, *, c', 'arguments').match('a, /, b, *, c'))

        # re.Pattern

        self.assertTrue(FST(Name('i')).match(re.compile('i')))
        self.assertFalse(FST(Name('j')).match(re.compile('i')))
        self.assertTrue(FST(Name('i')).match(Name(re.compile('i'))))
        self.assertFalse(FST(Name('j')).match(Name(re.compile('i'))))
        self.assertTrue(FST(Name('i')).match(MName(re.compile('i'))))
        self.assertFalse(FST(Name('j')).match(MName(re.compile('i'))))

        # numbers

        self.assertTrue(FST(Constant(False)).match(Constant(False)))
        self.assertFalse(FST(Constant(False)).match(Constant(0)))
        self.assertFalse(FST(Constant(False)).match(Constant(0.0)))
        self.assertFalse(FST(Constant(False)).match(Constant(0j)))

        self.assertFalse(FST(Constant(0)).match(Constant(False)))
        self.assertTrue(FST(Constant(0)).match(Constant(0)))
        self.assertFalse(FST(Constant(0)).match(Constant(0.0)))
        self.assertFalse(FST(Constant(0)).match(Constant(0j)))

        self.assertFalse(FST(Constant(0.0)).match(Constant(False)))
        self.assertFalse(FST(Constant(0.0)).match(Constant(0)))
        self.assertTrue(FST(Constant(0.0)).match(Constant(0.0)))
        self.assertFalse(FST(Constant(0.0)).match(Constant(0j)))

        self.assertFalse(FST(Constant(0j)).match(Constant(False)))
        self.assertFalse(FST(Constant(0j)).match(Constant(0)))
        self.assertFalse(FST(Constant(0j)).match(Constant(0.0)))
        self.assertTrue(FST(Constant(0j)).match(Constant(0j)))

        # list

        f = FST('[a, b, c]')
        self.assertTrue(f.match(List(['a', 'b', 'c'])))
        self.assertFalse(f.match(List(['a'])))
        self.assertEqual({'obj': f.elts[0]}, f.match(List([M(obj='a'), MQSTAR])).tags)
        self.assertEqual({'obj': f.elts[0]}, f.match(List([MQSTAR, M(obj='a'), MQSTAR])).tags)
        self.assertEqual({'obj': f.elts[1]}, f.match(List([MQSTAR, M(obj='b'), MQSTAR])).tags)
        self.assertFalse(f.match(List([MQSTAR, M(obj='b')])))
        self.assertEqual({'obj': f.elts[2]}, f.match(List([MQSTAR, M(obj='c'), MQSTAR])).tags)
        self.assertEqual({'obj': f.elts[2]}, f.match(List([MQSTAR, M(obj='c')])).tags)
        self.assertTrue(f.match(List([MQSTAR, 'a', MQSTAR, 'b', MQSTAR, 'c', MQSTAR])))

        # single element wildcard ...

        f = FST('a + b')
        self.assertTrue(f.match(BinOp(..., ..., ...)))
        self.assertTrue(f.match(BinOp('a', ..., 'b')))
        self.assertFalse(f.match(BinOp('z', ..., 'b')))
        self.assertFalse(f.match(BinOp('a', ..., 'z')))
        self.assertTrue(f.match(BinOp(..., '+', ...)))
        self.assertFalse(f.match(BinOp(..., '-', ...)))

        # wildcard ... is concrete value for Constant

        self.assertTrue(FST(Constant(...)).match(Constant(...)))
        self.assertFalse(FST(Constant(1)).match(Constant(...)))
        self.assertFalse(FST(Constant(...)).match(Constant(1)))

        # # non-list pattern in list field position

        # f = FST('[]')

        # assertRaises(MatchError('MRE can never match a list field'), f.match, List(MRE('')))
        # assertRaises(MatchError('list can never match a non-list field'), f.match, List([], []))
        # assertRaises(MatchError('str can never match a list field'), f.match, List('str'))
        # assertRaises(MatchError('int can never match a list field'), f.match, List(1))
        # assertRaises(MatchError('Pass can never match a list field'), f.match, List(Pass()))
        # assertRaises(MatchError('Constant can never match a list field'), f.match, List(Constant(1)))
        # assertRaises(MatchError('Load can never match a list field'), f.match, List(Load()))
        # assertRaises(MatchError('type can never match a list field'), f.match, List(stmt))
        # assertRaises(MatchError('re.Pattern can never match a list field'), f.match, List(re.compile('i')))
        # assertRaises(MatchError('None can never match a list field'), f.match, List(None))

        # assertRaises(MatchError('MRE can never match a list field'), MList(MRE('')).match, f.a)
        # assertRaises(MatchError('list can never match a non-list field'), MList([], []).match, f.a)
        # assertRaises(MatchError('str can never match a list field'), MList('str').match, f.a)
        # assertRaises(MatchError('int can never match a list field'), MList(1).match, f.a)
        # assertRaises(MatchError('Pass can never match a list field'), MList(Pass()).match, f.a)
        # assertRaises(MatchError('Constant can never match a list field'), MList(Constant(1)).match, f.a)
        # assertRaises(MatchError('Load can never match a list field'), MList(Load()).match, f.a)
        # assertRaises(MatchError('type can never match a list field'), MList(stmt).match, f.a)
        # assertRaises(MatchError('re.Pattern can never match a list field'), MList(re.compile('i')).match, f.a)
        # assertRaises(MatchError('None can never match a list field'), MList(None).match, f.a)

        # non-leaf arbitrary fields

        pat = MAST(elts=['a', MQSTAR])
        self.assertTrue(FST('a,').match(pat))
        self.assertTrue(FST('(a, b)').match(pat))
        self.assertTrue(FST('[a]').match(pat))
        self.assertTrue(FST('{a}').match(pat))
        self.assertFalse(FST('{a: b}').match(pat))

        pat = Mstmt(body=[MQSTAR, 'a', MQSTAR])
        self.assertTrue(FST('if 1:\n a\n b').match(pat))
        self.assertTrue(FST('while 1: c;a;b').match(pat))
        self.assertTrue(FST('for _ in _:\n c\n a').match(pat))
        self.assertTrue(FST('try:\n c\n a\n b\nfinally: pass').match(pat))
        self.assertFalse(FST('a if b else c').match(pat))

        pat = MAST(body=[MQSTAR, 'a', MQSTAR])
        self.assertTrue(FST('if 1:\n a\n b').match(pat))
        self.assertFalse(FST('a if b else c').match(pat))  # this is not a list field, ensure non-match instead of error

        # arbitrary fields ignore list check

        self.assertTrue(MTYPES((If, IfExp), body=[MQSTAR]).match(FST('if 1: pass')))
        self.assertFalse(MTYPES((If, IfExp), body=[MQSTAR]).match(FST('a if b else c')))
        self.assertFalse(MTYPES((If, IfExp), body='a').match(FST('if 1: pass')))
        self.assertTrue(MTYPES((If, IfExp), body='a').match(FST('a if b else c')))

        self.assertTrue(MAST(body=[MQSTAR]).match(FST('if 1: pass')))
        self.assertFalse(MAST(body=[MQSTAR]).match(FST('a if b else c')))
        self.assertFalse(MAST(body='a').match(FST('if 1: pass')))
        self.assertTrue(MAST(body='a').match(FST('a if b else c')))

        # # list checks turned back on below arbitrary fields

        # self.assertTrue(MTYPES((If, IfExp), body=[MIf(body=[...])]).match(FST('if 1:\n if 2: pass')))
        # assertRaises(MatchError('str can never match a list field'), MTYPES((If, IfExp), body=[MIf(body='a')]).match, FST('if 1:\n if 2: pass'))
        # assertRaises(MatchError('str can never match a list field'), MTYPES((If, IfExp), body=MList(elts='a')).match, FST('[1] if b else c'))
        # self.assertTrue(MTYPES((If, IfExp), body=MList(elts=[...])).match(FST('[1] if b else c')))

        # self.assertTrue(MAST(body=[MIf(body=[...])]).match(FST('if 1:\n if 2: pass')))
        # assertRaises(MatchError('str can never match a list field'), MAST(body=[MIf(body='a')]).match, FST('if 1:\n if 2: pass'))
        # assertRaises(MatchError('str can never match a list field'), MAST(body=MList(elts='a')).match, FST('[1] if b else c'))
        # self.assertTrue(MAST(body=MList(elts=[...])).match(FST('[1] if b else c')))

    def test_match_M_Pattern(self):
        # re.Pattern

        self.assertTrue(MOR(re.compile('i')).match(FST(Name('i')).a))
        self.assertFalse(MOR(re.compile('i')).match(FST(Name('j')).a))
        self.assertTrue(MOR(re.compile('i')).match(Name('i')))
        self.assertFalse(MOR(re.compile('i')).match(Name('j')))
        self.assertTrue(MOR(re.compile('i')).match('i'))
        self.assertFalse(MOR(re.compile('i')).match('j'))
        self.assertFalse(MOR(re.compile('i')).match(b'i'))
        self.assertTrue(MOR(re.compile(b'i')).match(b'i'))
        self.assertFalse(MOR(re.compile(b'i')).match(b'j'))
        self.assertFalse(MOR(re.compile(b'i')).match('i'))

        # MRE

        self.assertTrue(MRE(re.compile('i')).match(FST(Name('i')).a))
        self.assertFalse(MRE(re.compile('i')).match(FST(Name('j')).a))
        self.assertTrue(MRE(re.compile('i')).match(Name('i')))
        self.assertFalse(MRE(re.compile('i')).match(Name('j')))
        self.assertTrue(MRE(re.compile('i')).match('i'))
        self.assertFalse(MRE(re.compile('i')).match('j'))
        self.assertFalse(MRE(re.compile('i')).match(b'i'))
        self.assertTrue(MRE(re.compile(b'i')).match(b'i'))
        self.assertFalse(MRE(re.compile(b'i')).match(b'j'))
        self.assertFalse(MRE(re.compile(b'i')).match('i'))

        self.assertTrue(MRE('i').match(FST(Name('i')).a))
        self.assertFalse(MRE('i').match(FST(Name('j')).a))
        self.assertTrue(MRE('i').match(Name('i')))
        self.assertFalse(MRE('i').match(Name('j')))
        self.assertTrue(MRE('i').match('i'))
        self.assertFalse(MRE('i').match('j'))
        self.assertFalse(MRE('i').match(b'i'))
        self.assertTrue(MRE(b'i').match(b'i'))
        self.assertFalse(MRE(b'i').match(b'j'))
        self.assertFalse(MRE(b'i').match('i'))

        self.assertTrue(MRE('i').match('i'))
        self.assertFalse(MRE('i').match('j'))
        self.assertFalse(MRE('i').match('ai'))
        self.assertTrue(MRE('i', search=True).match('ai'))
        self.assertFalse(MRE('i j').match('ij'))
        self.assertTrue(MRE('i j', re.VERBOSE).match('ij'))

        m = MRE(tag='i').match('i')
        self.assertEqual(['tag'], list(m.tags))
        self.assertEqual('i', m.tags['tag'].group())

        m = MRE(tag='i', search=True).match('ai')
        self.assertEqual(['tag'], list(m.tags))
        self.assertEqual('i', m.tags['tag'].group())

        m = MRE(tag='i j', flags=re.VERBOSE).match('ij')
        self.assertEqual(['tag'], list(m.tags))
        self.assertEqual('ij', m.tags['tag'].group())

        m = MRE(tag='i', t2=2, t3='3').match('i')
        self.assertEqual(['tag', 't2', 't3'], list(m.tags))
        self.assertEqual('i', m.tags['tag'].group())
        self.assertEqual(2, m.tags['t2'])
        self.assertEqual('3', m.tags['t3'])

        m = MRE(tag='i', search=True, t2=2, t3='3').match('ai')
        self.assertEqual(['tag', 't2', 't3'], list(m.tags))
        self.assertEqual('i', m.tags['tag'].group())
        self.assertEqual(2, m.tags['t2'])
        self.assertEqual('3', m.tags['t3'])

        m = MRE(tag='i j', flags=re.VERBOSE, t2=2, t3='3').match('ij')
        self.assertEqual(['tag', 't2', 't3'], list(m.tags))
        self.assertEqual('ij', m.tags['tag'].group())
        self.assertEqual(2, m.tags['t2'])
        self.assertEqual('3', m.tags['t3'])

        # MOR

        pat = M(obj=MOR(Constant, Name))
        self.assertIsNone(pat.match(FST('a + b').a))
        self.assertIsNone(pat.match(FST('a = b').a))
        self.assertEqual({'obj': (f := FST('name')).a}, pat.match(f.a).tags)
        self.assertEqual({'obj': (f := FST('123')).a}, pat.match(f.a).tags)

        pat = MOR('b', 'c')
        self.assertFalse(pat.match(FST('a').a))
        self.assertTrue(pat.match(FST('b').a))
        self.assertTrue(pat.match(FST('c').a))
        self.assertFalse(pat.match(FST('a').a))

        pat = MOR(Constant(2), Constant(3))
        self.assertFalse(pat.match(FST('1').a))
        self.assertTrue(pat.match(FST('2').a))
        self.assertTrue(pat.match(FST('3').a))
        self.assertFalse(pat.match(FST('4').a))

        pat = MTuple(MOR(['b', 'c'], ['c', 'd']))
        self.assertFalse(pat.match(FST('a, b').a))
        self.assertTrue(pat.match(FST('b, c').a))
        self.assertTrue(pat.match(FST('c, d').a))
        self.assertFalse(pat.match(FST('d, e').a))

        # misc

        pat = MAST(value=MCall)
        self.assertTrue(pat.match(FST('return f()').a))
        self.assertTrue(pat.match(FST('await something(a, b, c)').a))
        self.assertFalse(pat.match(FST('yield x').a))
        self.assertFalse(pat.match(FST('*(a, b, c)').a))

        pat = Mstmt(body=[MExpr(MConstant(str)), MQSTAR])
        self.assertTrue(pat.match(FST('def f(): "doc"; pass').a))
        self.assertTrue(pat.match(FST('class cls: "doc"').a))
        self.assertFalse(pat.match(FST('class cls: 1').a))
        self.assertFalse(pat.match(FST('class cls: 1; "doc"').a))
        self.assertFalse(pat.match(FST('class cls: pass').a))

        f = FST('a')
        f.a = None
        assertRaises(ValueError('Mstmt.match() called with dead FST node'), pat.match, f)

        class MyM(M): pass
        assertRaises(RuntimeError('subclassing M_Pattern not supported'), MyM(...).match, FST('a'))

    def test_match_M(self):
        # M

        assertRaises(ValueError('M requires pattern'), M)
        self.assertTrue(M(None))
        self.assertTrue(M(tag=None))

        f = FST('i = j')
        self.assertEqual({'obj': f.value}, f.match(Assign(..., M(obj='j'))).tags)
        self.assertEqual({'is_obj': True}, f.match(Assign(..., M('j', is_obj=True))).tags)
        self.assertEqual({'obj': f.targets[0], 'is_j': 'yay', 'is_j2': 'hoho'}, f.match(Assign([M(obj=...)], M('j', is_j='yay', is_j2='hoho'))).tags)
        self.assertEqual({'obj': f.a.targets, 'obj2': f.a.value}, MAssign(M(obj=...), M(obj2=...)).match(f.a).tags)
        self.assertEqual({'obj': f.targets[0], 'obj2': f.value}, f.match(Assign([M(obj=...)], M(obj2=...))).tags)

        f = FST('a')
        self.assertEqual({'a': f, 'b': True}, f.match(M(a=MName('a'), b=True)).tags)
        self.assertFalse(f.match(M(a=MName('b'), b=True)))
        self.assertEqual({'a': 'a', 'b': True}, f.match(MName(M(a='a', b=True))).tags)
        self.assertFalse(f.match(MName(M(a='b', b=True))))
        self.assertEqual({'a': f.ctx, 'b': True}, f.match(MName('a', M(a=MLoad(), b=True))).tags)
        self.assertFalse(f.match(MName('a', M(a=MStore(), b=True))))
        self.assertEqual({'a': f, 'b': True}, f.match(M(a=Mexpr(), b=True)).tags)
        self.assertFalse(f.match(M(a=Mstmt(), b=True)))

        f = FST('1')
        self.assertEqual({'a': f, 'b': True}, f.match(M(a=MConstant(1), b=True)).tags)
        self.assertFalse(f.match(M(a=MConstant(2), b=True)))
        self.assertEqual({'a': 1, 'b': True}, f.match(MConstant(M(a=1, b=True))).tags)
        self.assertFalse(f.match(MConstant(M(a=2, b=True))))

        f = FST('u"a"')
        self.assertEqual({'a': f, 'b': True}, f.match(M(a=MConstant('a', ...), b=True)).tags)
        self.assertEqual({'a': f, 'b': True}, f.match(M(a=MConstant('a', 'u'), b=True)).tags)
        self.assertFalse(f.match(M(a=MConstant('a', None), b=True)))
        self.assertFalse(f.match(M(a=MConstant('b'), b=True)))
        self.assertEqual({'a': f, 'b': True}, f.match(M(a=MConstant('a', MOR(None, 'u')), b=True)).tags)

        # MNOT

        assertRaises(ValueError('MNOT requires pattern'), MNOT)
        self.assertTrue(MNOT(None))
        self.assertTrue(MNOT(tag=None))

        f = FST('a')
        self.assertFalse(f.match(MNOT(a=MName('a'), b=True)))
        self.assertEqual({'a': f, 'b': True}, f.match(MNOT(a=MName('b'), b=True)).tags)
        self.assertFalse(f.match(MName(MNOT(a='a', b=True))))
        self.assertEqual({'a': 'a', 'b': True}, f.match(MName(MNOT(a='b', b=True))).tags)
        self.assertFalse(f.match(MName('a', MNOT(a=MLoad(), b=True))))
        self.assertEqual({'a': f.ctx, 'b': True}, f.match(MName('a', MNOT(a=MStore(), b=True))).tags)
        self.assertFalse(f.match(MNOT(a=Mexpr(), b=True)))
        self.assertEqual({'a': f, 'b': True}, f.match(MNOT(a=Mstmt(), b=True)).tags)

        f = FST('1')
        self.assertEqual({'a': f, 'b': True}, f.match(MNOT(a=MConstant(2), b=True)).tags)
        self.assertFalse(f.match(MNOT(a=MConstant(1), b=True)))
        self.assertEqual({'a': 1, 'b': True}, f.match(MConstant(MNOT(a=2, b=True))).tags)
        self.assertFalse(f.match(MConstant(MNOT(a=1, b=True))))

        f = FST('u"a"')
        self.assertFalse(f.match(MNOT(a=MConstant('a', ...), b=True)))
        self.assertFalse(f.match(MNOT(a=MConstant('a', 'u'), b=True)))
        self.assertEqual({'a': f, 'b': True}, f.match(MNOT(a=MConstant('a', None), b=True)).tags)
        self.assertEqual({'a': f, 'b': True}, f.match(MNOT(a=MConstant('b'), b=True)).tags)
        self.assertFalse(f.match(MNOT(a=MConstant('a', MOR(None, 'u')), b=True)))

        # MOR

        assertRaises(ValueError('MOR requires at least one pattern'), MOR)
        self.assertTrue(MOR(None))
        self.assertTrue(MOR(tag=None))

        pat = M(obj=MOR(Constant, Name))
        self.assertFalse(FST('a + b').match(pat))
        self.assertFalse(FST('a = b').match(pat))
        self.assertEqual({'obj': (f := FST('name'))}, f.match(pat).tags)
        self.assertEqual({'obj': (f := FST('123'))}, f.match(pat).tags)

        self.assertFalse(FST('a').match(MOR('b', 'c')))
        self.assertTrue(FST('b').match(MOR('b', 'c')))
        self.assertTrue(FST('c').match(MOR('b', 'c')))
        self.assertFalse(FST('a').match(MOR('b', 'c')))

        self.assertFalse(FST('1').match(MOR(Constant(2), Constant(3))))
        self.assertTrue(FST('2').match(MOR(Constant(2), Constant(3))))
        self.assertTrue(FST('3').match(MOR(Constant(2), Constant(3))))
        self.assertFalse(FST('4').match(MOR(Constant(2), Constant(3))))

        self.assertFalse(FST('a, b').match(Tuple(MOR(['b', 'c'], ['c', 'd']))))
        self.assertTrue(FST('b, c').match(Tuple(MOR(['b', 'c'], ['c', 'd']))))
        self.assertTrue(FST('c, d').match(Tuple(MOR(['b', 'c'], ['c', 'd']))))
        self.assertFalse(FST('d, e').match(Tuple(MOR(['b', 'c'], ['c', 'd']))))

        # MOR tagged patterns

        pat = List([MOR(a='a', b='b', c='c')])
        self.assertEqual({'a': (f := FST('[a]')).elts[0]}, f.match(pat).tags)
        self.assertEqual({'b': (f := FST('[b]')).elts[0]}, f.match(pat).tags)
        self.assertEqual({'c': (f := FST('[c]')).elts[0]}, f.match(pat).tags)

        # MOR passthrough tags

        pat = M(MOR(M('a', is_a=True), M('b', is_b=True)), is_one=True)
        self.assertEqual({'is_a': True, 'is_one': True}, FST('a').match(pat).tags)
        self.assertEqual({'is_b': True, 'is_one': True}, FST('b').match(pat).tags)
        self.assertFalse(FST('c').match(pat))

        # MAND

        assertRaises(ValueError('MAND requires at least one pattern'), MAND)
        self.assertTrue(MAND(None))
        self.assertTrue(MAND(tag=None))

        f = FST('a + b')
        self.assertTrue(f.match(MAND(BinOp('a', ..., ...), BinOp(..., '+', ...), BinOp(..., ..., 'b'))))
        self.assertFalse(f.match(MAND(BinOp('z', ..., ...), BinOp(..., '+', ...), BinOp(..., ..., 'b'))))
        self.assertFalse(f.match(MAND(BinOp('a', ..., ...), BinOp(..., 'z', ...), BinOp(..., ..., 'b'))))
        self.assertFalse(f.match(MAND(BinOp('a', ..., ...), BinOp(..., '+', ...), BinOp(..., ..., 'z'))))

        self.assertEqual({'a': f, 'plus': f, 'b': f}, f.match(MAND(a=BinOp('a', ..., ...), plus=BinOp(..., '+', ...), b=BinOp(..., ..., 'b'))).tags)
        self.assertEqual({'a': f.left, 'plus': f.op, 'b': f.right}, f.match(MAND(BinOp(M(a='a'), ..., ...), BinOp(..., M(plus='+'), ...), BinOp(..., ..., M(b='b')))).tags)

        # MRE

        assertRaises(ValueError('MRE requires pattern'), MRE)
        # assertRaises(ValueError('MRE requires pattern'), MRE, None)

        # MTYPES

        pat = MTYPES((If, For), body=[MQSTAR, 'a', MQSTAR])
        self.assertTrue(FST('if 1:\n a\n b').match(pat))
        self.assertFalse(FST('while 1: c;a;b').match(pat))
        self.assertTrue(FST('for _ in _:\n c\n a').match(pat))
        self.assertFalse(FST('try:\n c\n a\n b\nfinally: pass').match(pat))
        self.assertFalse(FST('a if b else c').match(pat))

        # MOPT

        self.assertEqual("<FSTMatch <FunctionDef ROOT 0,0..0,13>>", str(MFunctionDef(returns=MOPT('int')).match(FST('def f(): pass'))))
        self.assertEqual("<FSTMatch <FunctionDef ROOT 0,0..0,20>>", str(MFunctionDef(returns=MOPT('int')).match(FST('def f() -> int: pass'))))
        self.assertEqual("None", str(MFunctionDef(returns=MOPT('int')).match(FST('def f() -> str: pass'))))
        self.assertEqual("<FSTMatch <FunctionDef ROOT 0,0..0,13> {'t': []}>", str(MFunctionDef(returns=MOPT(t='int')).match(FST('def f(): pass'))))
        self.assertEqual("<FSTMatch <FunctionDef ROOT 0,0..0,20> {'t': <Name 0,11..0,14>}>", str(MFunctionDef(returns=MOPT(t='int')).match(FST('def f() -> int: pass'))))
        self.assertEqual("<FSTMatch <FunctionDef ROOT 0,0..0,20> {'m': <Name 0,11..0,14>, 't': <Name 0,11..0,14>}>", str(MFunctionDef(returns=MOPT(t=M(m='int'))).match(FST('def f() -> int: pass'))))

        p = MFunctionDef(returns=MOPT(t='int'))
        f = FST('def f() -> int: pass')
        m = p.match(f)
        self.assertIs(m.t, f.returns)

        p = MFunctionDef(returns=MOPT(t=M(m='int')))
        f = FST('def f() -> int: pass')
        m = p.match(f)
        self.assertIs(m.t, f.returns)
        self.assertIs(m.m, f.returns)

        # MCB

        pat = MCB(lambda a: a.id == 'x')
        self.assertEqual({}, FST('x').match(pat).tags)
        self.assertFalse(FST('y').match(pat))

        pat = MCB(lambda f: f.a.id == 'x')
        self.assertEqual({}, FST('x').match(pat).tags)
        self.assertFalse(FST('y').match(pat))

        pat = MCB(tag=lambda a: a.id == 'x' and a, tag_ret=True)
        self.assertEqual({'tag': (f := FST('x')).a}, pat.match(f.a).tags)  # pat.match() because there is no match() on AST
        self.assertFalse(FST('y').match(pat))

        pat = MCB(tag=lambda f: f.a.id == 'x' and f.a, tag_ret=True)  # make sure AST is preserved as a tag in an FST call
        self.assertEqual({'tag': (f := FST('x')).a}, f.match(pat).tags)
        self.assertFalse(FST('y').match(pat))

        pat = MCB(tag=lambda f: f.a.id == 'x' and f, tag_ret=True)
        self.assertEqual({'tag': (f := FST('x'))}, f.match(pat).tags)
        self.assertFalse(FST('y').match(pat))

    def test_match_quantifiers(self):
        # no quantifier direct children

        for kls, args in [
            (MQ, (0, None)),
            (MQ.NG, (0, None)),
            (MQSTAR, ()),
            (MQSTAR.NG, ()),
            (MQPLUS, ()),
            (MQPLUS.NG, ()),
            (MQ01, ()),
            (MQ01.NG, ()),
            (MQMIN, (0,)),
            (MQMIN.NG, (0,)),
            (MQMAX, (None,)),
            (MQMAX.NG, (None,)),
            (MQN, (1,)),
            (MQN.NG, (1,)),
        ]:
            error = ValueError(f'{kls.__qualname__} cannot have another quantifier as a direct child pattern')

            assertRaises(error, kls, MQ(..., 0, None), *args)
            assertRaises(error, kls, MQ.NG(..., 0, None), *args)
            assertRaises(error, kls, MQSTAR, *args)
            assertRaises(error, kls, MQSTAR.NG, *args)
            assertRaises(error, kls, MQPLUS, *args)
            assertRaises(error, kls, MQPLUS.NG, *args)
            assertRaises(error, kls, MQ01, *args)
            assertRaises(error, kls, MQ01.NG, *args)
            assertRaises(error, kls, MQMIN(..., 0), *args)
            assertRaises(error, kls, MQMIN.NG(..., 0), *args)
            assertRaises(error, kls, MQMAX(..., None), *args)
            assertRaises(error, kls, MQMAX.NG(..., None), *args)
            assertRaises(error, kls, MQN(..., 1), *args)
            assertRaises(error, kls, MQN.NG(..., 1), *args)

        # no infinite-loop quantifier sublists

        for kls, args in [
            (MQ, (0, None)),
            (MQ.NG, (0, None)),
            (MQSTAR, ()),
            (MQSTAR.NG, ()),
            (MQPLUS, ()),
            (MQPLUS.NG, ()),
            (MQMIN, (0,)),
            (MQMIN.NG, (0,)),
            (MQMAX, (None,)),
            (MQMAX.NG, (None,)),
        ]:
            error = ValueError(f'unbounded {kls.__qualname__} with sublist cannot have possible zero-length matches')

            assertRaises(error, kls, [MQ(..., 0, None)], *args)
            assertRaises(error, kls, [MQ.NG(..., 0, None)], *args)
            assertRaises(error, kls, [MQSTAR], *args)
            assertRaises(error, kls, [MQSTAR.NG], *args)
            assertRaises(error, kls, [MQ01], *args)
            assertRaises(error, kls, [MQ01.NG], *args)
            assertRaises(error, kls, [MQMIN(..., 0)], *args)
            assertRaises(error, kls, [MQMIN.NG(..., 0)], *args)
            assertRaises(error, kls, [MQMAX(..., None)], *args)
            assertRaises(error, kls, [MQMAX.NG(..., None)], *args)
            assertRaises(error, kls, [MQN(..., 0)], *args)
            assertRaises(error, kls, [MQN.NG(..., 0)], *args)

            assertRaises(error, kls, [MQN([MQ(..., 0, None)], 1)], *args)
            assertRaises(error, kls, [MQN([MQ.NG(..., 0, None)], 1)], *args)
            assertRaises(error, kls, [MQN([MQSTAR], 1)], *args)
            assertRaises(error, kls, [MQN([MQSTAR.NG], 1)], *args)
            assertRaises(error, kls, [MQN([MQ01], 1)], *args)
            assertRaises(error, kls, [MQN([MQ01.NG], 1)], *args)
            assertRaises(error, kls, [MQN([MQMIN(..., 0)], 1)], *args)
            assertRaises(error, kls, [MQN([MQMIN.NG(..., 0)], 1)], *args)
            assertRaises(error, kls, [MQN([MQMAX(..., None)], 1)], *args)
            assertRaises(error, kls, [MQN([MQMAX.NG(..., None)], 1)], *args)
            assertRaises(error, kls, [MQN([MQN(..., 0)], 1)], *args)
            assertRaises(error, kls, [MQN([MQN.NG(..., 0)], 1)], *args)

        # MQ tags in lists

        patl = MList([MQ(MOR(is_a='a', is_b='b'), min=1, max=2, static='y')])

        f = FST('[a]')
        self.assertEqual({'is_a': f.elts[0], 'static': 'y'}, patl.match(f).tags)

        f = FST('[a, a]')
        self.assertEqual({'is_a': f.elts[1], 'static': 'y'}, patl.match(f).tags)

        f = FST('[a, b]')
        self.assertEqual({'is_a': f.elts[0], 'is_b': f.elts[1], 'static': 'y'}, patl.match(f).tags)

        patl = MList([MQ(mn=MOR(is_a='a', is_b='b'), min=1, max=2, static='y')])

        f = FST('[a]')
        m = patl.match(f)
        self.assertEqual(['mn', 'static'], list(m.tags))
        self.assertEqual({'is_a': f.elts[0]}, m.mn[0].tags)
        self.assertEqual(m.static, 'y')

        f = FST('[a, a]')
        m = patl.match(f)
        self.assertEqual(['mn', 'static'], list(m.tags))
        self.assertEqual({'is_a': f.elts[0]}, m.mn[0].tags)
        self.assertEqual({'is_a': f.elts[1]}, m.mn[1].tags)
        self.assertEqual(m.static, 'y')

        f = FST('[a, b]')
        m = patl.match(f)
        self.assertEqual(['mn', 'static'], list(m.tags))
        self.assertEqual({'is_a': f.elts[0]}, m.mn[0].tags)
        self.assertEqual({'is_b': f.elts[1]}, m.mn[1].tags)
        self.assertEqual(m.static, 'y')

        # MQ logic correctness, merged tags

        self.assertEqual({}, FST('[]').match(List([MQ('a', 0, 0)])).tags)
        self.assertFalse(FST('[a]').match(List([MQ('a', 0, 0)])))
        self.assertEqual({}, FST('[a]').match(List([MQ('a', 0, 0), MQSTAR])).tags)
        self.assertEqual({}, FST('[a]').match(List([MQ(M(is_a='a'), 0, 0), MQSTAR])).tags)
        self.assertEqual({'is_a': (f := FST('[a]')).elts[0]}, f.match(List([MQ(M(is_a='a'), 0, 1), MQSTAR])).tags)
        self.assertEqual({'is_a': (f := FST('[a, a]')).elts[0]}, f.match(List([MQ(M(is_a='a'), 0, 1), MQSTAR])).tags)
        self.assertEqual({'is_a': (f := FST('[a, a]')).elts[1]}, f.match(List([MQ(M(is_a='a'), 0, 2), MQSTAR])).tags)
        self.assertEqual({'is_a': (f := FST('[a, a, a]')).elts[1]}, f.match(List([MQ(M(is_a='a'), 0, 2), MQSTAR])).tags)
        self.assertEqual({'is_a': (f := FST('[a, a, a]')).elts[2]}, f.match(List([MQ(M(is_a='a'), 0, None), MQSTAR])).tags)
        self.assertEqual({'is_a': (f := FST('[a, a, a, a]')).elts[3]}, f.match(List([MQ(M(is_a='a'), 0, None), MQSTAR])).tags)
        self.assertFalse(FST('[]').match(List([MQ(M(is_a='a'), 1, 1), MQSTAR])))
        self.assertEqual({'is_a': (f := FST('[a]')).elts[0]}, f.match(List([MQ(M(is_a='a'), 1, 1), MQSTAR])).tags)
        self.assertFalse(FST('[a, a]').match(List([MQ(M(is_a='a'), 1, 1)])))
        self.assertEqual({'is_a': (f := FST('[a, a]')).elts[0]}, f.match(List([MQ(M(is_a='a'), 1, 1), MQSTAR])).tags)

        self.assertEqual({'is_a': (f := FST('[a, a]')).elts[0]}, f.match(List([MQSTAR.NG, MQ(M(is_a='a'), 1, 1), MQSTAR])).tags)
        self.assertEqual({'is_a': (f := FST('[b, a]')).elts[1]}, f.match(List([MQSTAR, MQ(M(is_a='a'), 1, 1), MQSTAR])).tags)
        self.assertEqual({'is_a1': (f := FST('[a, a]')).elts[0], 'is_a2': f.elts[1]}, f.match(List([MQ(M(is_a1='a'), 1, 1), MQ(M(is_a2='a'), 1, 1)])).tags)
        self.assertEqual({'is_a1': (f := FST('[a, a]')).elts[0], 'is_a2': f.elts[1]}, f.match(List([MQSTAR, MQ(M(is_a1='a'), 1, 1), MQ(M(is_a2='a'), 1, 1), MQSTAR])).tags)
        self.assertEqual({'is_a1': (f := FST('[a, a]')).elts[0], 'is_a2': f.elts[1]}, f.match(List([MQSTAR, MQ(M(is_a1='a'), 1, 1), MQSTAR, MQ(M(is_a2='a'), 1, 1), MQSTAR])).tags)
        self.assertEqual({'is_a1': (f := FST('[a, a]')).elts[0], 'is_a2': f.elts[1]}, f.match(List([MQSTAR.NG, MQ(M(is_a1='a'), 0, 1), MQSTAR.NG, MQ(M(is_a2='a'), 0, 1), MQSTAR])).tags)
        self.assertEqual({'is_a1': (f := FST('[a, a]')).elts[1]}, f.match(List([MQSTAR.NG, MQ(M(is_a1='a'), 0, 2), MQSTAR.NG, MQ(M(is_a2='a'), 0, 0), MQSTAR])).tags)
        self.assertEqual({'is_a2': (f := FST('[a, a]')).elts[1]}, f.match(List([MQSTAR.NG, MQ(M(is_a1='a'), 0, 0), MQSTAR.NG, MQ(M(is_a2='a'), 0, 2), MQSTAR])).tags)
        self.assertEqual({'is_a1': (f := FST('[a, b, a]')).elts[0], 'is_a2': f.elts[2]}, f.match(List([MQSTAR.NG, MQ(M(is_a1='a'), 0, 1), MQSTAR.NG, 'b', MQSTAR.NG, MQ(M(is_a2='a'), 0, 1), MQSTAR])).tags)
        self.assertEqual({'is_a1': (f := FST('[a, b, a]')).elts[0], 'is_a2': f.elts[2]}, f.match(List([MQSTAR.NG, MQ(M(is_a1='a'), 0, 2), MQSTAR.NG, 'b', MQSTAR.NG, MQ(M(is_a2='a'), 0, 2), MQSTAR])).tags)

        # MQ individual tags

        self.assertEqual("{'t': []}", str(FST('[]').match(List([MQ(t='a', min=0, max=0)])).tags))
        self.assertEqual('None', str(FST('[a]').match(List([MQ(t='a', min=0, max=0)]))))
        self.assertEqual("{'t': []}", str(FST('[a]').match(List([MQ(t='a', min=0, max=0), MQSTAR])).tags))
        self.assertEqual("{'t': []}", str(FST('[a]').match(List([MQ(t=M(is_a='a'), min=0, max=0), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>]}", str(FST('[a]').match(List([MQ(t=M(is_a='a'), min=0, max=1), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>]}", str(FST('[a, a]').match(List([MQ(t=M(is_a='a'), min=0, max=1), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'is_a': <Name 0,4..0,5>}>]}", str(FST('[a, a]').match(List([MQ(t=M(is_a='a'), min=0, max=2), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'is_a': <Name 0,4..0,5>}>]}", str(FST('[a, a, a]').match(List([MQ(t=M(is_a='a'), min=0, max=2), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'is_a': <Name 0,4..0,5>}>, <FSTMatch <Name 0,7..0,8> {'is_a': <Name 0,7..0,8>}>]}", str(FST('[a, a, a]').match(List([MQ(t=M(is_a='a'), min=0, max=None), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'is_a': <Name 0,4..0,5>}>, <FSTMatch <Name 0,7..0,8> {'is_a': <Name 0,7..0,8>}>, <FSTMatch <Name 0,10..0,11> {'is_a': <Name 0,10..0,11>}>]}", str(FST('[a, a, a, a]').match(List([MQ(t=M(is_a='a'), min=0, max=None), MQSTAR])).tags))
        self.assertEqual('None', str(FST('[]').match(List([MQ(t=M(is_a='a'), min=1, max=1), MQSTAR]))))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>]}", str(FST('[a]').match(List([MQ(t=M(is_a='a'), min=1, max=1), MQSTAR])).tags))
        self.assertEqual('None', str(FST('[a, a]').match(List([MQ(t=M(is_a='a'), min=1, max=1)]))))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>]}", str(FST('[a, a]').match(List([MQ(t=M(is_a='a'), min=1, max=1), MQSTAR])).tags))

        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a': <Name 0,1..0,2>}>]}", str(FST('[a, a]').match(List([MQSTAR.NG, MQ(t=M(is_a='a'), min=1, max=1), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,4..0,5> {'is_a': <Name 0,4..0,5>}>]}", str(FST('[b, a]').match(List([MQSTAR, MQ(t=M(is_a='a'), min=1, max=1), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a1': <Name 0,1..0,2>}>], 'u': [<FSTMatch <Name 0,4..0,5> {'is_a2': <Name 0,4..0,5>}>]}", str(FST('[a, a]').match(List([MQ(t=M(is_a1='a'), min=1, max=1), MQ(u=M(is_a2='a'), min=1, max=1)])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a1': <Name 0,1..0,2>}>], 'u': [<FSTMatch <Name 0,4..0,5> {'is_a2': <Name 0,4..0,5>}>]}", str(FST('[a, a]').match(List([MQSTAR, MQ(t=M(is_a1='a'), min=1, max=1), MQ(u=M(is_a2='a'), min=1, max=1), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a1': <Name 0,1..0,2>}>], 'u': [<FSTMatch <Name 0,4..0,5> {'is_a2': <Name 0,4..0,5>}>]}", str(FST('[a, a]').match(List([MQSTAR, MQ(t=M(is_a1='a'), min=1, max=1), MQSTAR, MQ(u=M(is_a2='a'), min=1, max=1), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a1': <Name 0,1..0,2>}>], 'u': [<FSTMatch <Name 0,4..0,5> {'is_a2': <Name 0,4..0,5>}>]}", str(FST('[a, a]').match(List([MQSTAR.NG, MQ(t=M(is_a1='a'), min=0, max=1), MQSTAR.NG, MQ(u=M(is_a2='a'), min=0, max=1), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a1': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'is_a1': <Name 0,4..0,5>}>], 'u': []}", str(FST('[a, a]').match(List([MQSTAR.NG, MQ(t=M(is_a1='a'), min=0, max=2), MQSTAR, MQ(u=M(is_a2='a'), min=0, max=0), MQSTAR])).tags))
        self.assertEqual("{'t': [], 'u': [<FSTMatch <Name 0,1..0,2> {'is_a2': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'is_a2': <Name 0,4..0,5>}>]}", str(FST('[a, a]').match(List([MQSTAR.NG, MQ(t=M(is_a1='a'), min=0, max=0), MQSTAR.NG, MQ(u=M(is_a2='a'), min=0, max=2), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a1': <Name 0,1..0,2>}>], 'u': [<FSTMatch <Name 0,7..0,8> {'is_a2': <Name 0,7..0,8>}>]}", str(FST('[a, b, a]').match(List([MQSTAR.NG, MQ(t=M(is_a1='a'), min=0, max=1), MQSTAR.NG, 'b', MQSTAR.NG, MQ(u=M(is_a2='a'), min=0, max=1), MQSTAR])).tags))
        self.assertEqual("{'t': [<FSTMatch <Name 0,1..0,2> {'is_a1': <Name 0,1..0,2>}>], 'u': [<FSTMatch <Name 0,7..0,8> {'is_a2': <Name 0,7..0,8>}>]}", str(FST('[a, b, a]').match(List([MQSTAR.NG, MQ(t=M(is_a1='a'), min=0, max=2), MQSTAR.NG, 'b', MQSTAR.NG, MQ(u=M(is_a2='a'), min=0, max=2), MQSTAR])).tags))

        # MQ with MTYPES

        m = FST('[1, (b,), (x,), [y], {z}, {b}, -1]').match(MList([MQSTAR.NG, MQ(t=MTYPES((Tuple, List, Set), elts=[MOR('x', 'y', 'z')]), min=1, max=None), MQSTAR]))
        self.assertEqual("['(x,)', '[y]', '{z}']", str([mm.matched.src for mm in m.t]))

        # MQSTAR with MRE

        f = FST('nonlocal abc, bcd')
        m = f.match(MNonlocal([MQSTAR(MRE(r='.*'))]))
        self.assertEqual("<FSTMatch <Nonlocal ROOT 0,0..0,17> {'r': <re.Match object; span=(0, 3), match='bcd'>}>", str(m))
        m = f.match(MNonlocal([MQSTAR(t=MRE(r='.*'))]))
        # self.assertEqual("<FSTMatch <Nonlocal ROOT 0,0..0,17> {'t': [<FSTMatch 'abc' {'r': <re.Match object; span=(0, 3), match='abc'>}>, <FSTMatch 'bcd' {'r': <re.Match object; span=(0, 3), match='bcd'>}>]}>", str(m))
        self.assertEqual("<FSTMatch <Nonlocal ROOT 0,0..0,17> {'t': [<FSTMatch <<Nonlocal ROOT 0,0..0,17>.names[:1]> {'r': <re.Match object; span=(0, 3), match='abc'>}>, <FSTMatch <<Nonlocal ROOT 0,0..0,17>.names[1:2]> {'r': <re.Match object; span=(0, 3), match='bcd'>}>]}>", str(m))

        # greedy vs. non-greedy

        f = FST('[a, a, a]')

        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>], 't': [<FSTMatch <Name 0,7..0,8>>]}>", str(MList(elts=[MQ(h='a', min=1, max=2), MQ(t='a', min=1, max=2)]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>], 't': [<FSTMatch <Name 0,7..0,8>>]}>", str(MList(elts=[MQ(h='a', min=1, max=2), MQ.NG(t='a', min=1, max=2)]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>], 't': [<FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>", str(MList(elts=[MQ.NG(h='a', min=1, max=2), MQ(t='a', min=1, max=2)]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>], 't': [<FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>", str(MList(elts=[MQ.NG(h='a', min=1, max=2), MQ.NG(t='a', min=1, max=2)]).match(f)))

        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>", str(MList(elts=[MQSTAR(h='a'), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': []}>", str(MList(elts=[MQSTAR.NG(h='a'), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQSTAR(h='a'), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQSTAR.NG(h='a'), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>]}>", str(MList(elts=[MQSTAR.NG(h='a'), ..., ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': []}>", str(MList(elts=[MQSTAR.NG(h='a'), ..., ..., ...]).match(f)))

        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>", str(MList(elts=[MQPLUS(h='a'), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>]}>", str(MList(elts=[MQPLUS.NG(h='a'), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQPLUS(h='a'), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQPLUS.NG(h='a'), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>]}>", str(MList(elts=[MQPLUS.NG(h='a'), ..., ...]).match(f)))
        self.assertEqual("None", str(MList(elts=[MQPLUS.NG(h='a'), ..., ..., ...]).match(f)))

        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>]}>", str(MList(elts=[MQ01(h='a'), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': []}>", str(MList(elts=[MQ01.NG(h='a'), MQSTAR]).match(f)))
        self.assertEqual("None", str(MList(elts=[MQ01(h='a'), ...]).match(f)))
        self.assertEqual("None", str(MList(elts=[MQ01.NG(h='a'), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>]}>", str(MList(elts=[MQ01.NG(h='a'), ..., ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': []}>", str(MList(elts=[MQ01.NG(h='a'), ..., ..., ...]).match(f)))

        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>", str(MList(elts=[MQMIN(h='a', min=1), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>]}>", str(MList(elts=[MQMIN.NG(h='a', min=1), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQMIN(h='a', min=1), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQMIN.NG(h='a', min=1), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>]}>", str(MList(elts=[MQMIN.NG(h='a', min=1), ..., ...]).match(f)))
        self.assertEqual("None", str(MList(elts=[MQMIN.NG(h='a', min=1), ..., ..., ...]).match(f)))

        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQMAX(h='a', max=2), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': []}>", str(MList(elts=[MQMAX.NG(h='a', max=2), MQSTAR]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQMAX(h='a', max=2), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>", str(MList(elts=[MQMAX.NG(h='a', max=2), ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': [<FSTMatch <Name 0,1..0,2>>]}>", str(MList(elts=[MQMAX.NG(h='a', max=2), ..., ...]).match(f)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,9> {'h': []}>", str(MList(elts=[MQMAX.NG(h='a', max=2), ..., ..., ...]).match(f)))

        # sublists

        self.assertEqual("<FSTMatch <List ROOT 0,0..0,12> {'t': [<FSTMatch [<Name 0,1..0,2>, <Name 0,4..0,5>]>, <FSTMatch [<Name 0,7..0,8>, <Name 0,10..0,11>]>]}>", str(MList(elts=[MQSTAR(t=['a', 'b'])]).match(FST('[a, b, a, b]'))))
        self.assertEqual("None", str(MList(elts=[MQSTAR(t=['a', 'b'])]).match(FST('[a, b, a, b, c]'))))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,15> {'t': [<FSTMatch [<Name 0,1..0,2>, <Name 0,4..0,5>]>, <FSTMatch [<Name 0,7..0,8>, <Name 0,10..0,11>]>]}>", str(MList(elts=[MQSTAR(t=['a', 'b']), MQSTAR]).match(FST('[a, b, a, b, c]'))))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,12> {'t': [<FSTMatch [<Name 0,1..0,2>, <Name 0,4..0,5>]>, <FSTMatch [<Name 0,7..0,8>, <Name 0,10..0,11>]>]}>", str(MList(elts=[MQSTAR.NG(t=['a', 'b'])]).match(FST('[a, b, a, b]'))))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,12> {'t': []}>", str(MList(elts=[MQSTAR.NG(t=['a', 'b']), MQSTAR]).match(FST('[a, b, a, b]'))))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,12> {'t': [<FSTMatch [<Name 0,1..0,2>, <Name 0,4..0,5>]>]}>", str(MList(elts=[MQPLUS.NG(t=['a', 'b']), MQSTAR]).match(FST('[a, b, a, b]'))))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,12> {'t': [<FSTMatch [<Name 0,1..0,2>, <Name 0,4..0,5>]>, <FSTMatch [<Name 0,7..0,8>, <Name 0,10..0,11>]>]}>", str(MList(elts=[MQPLUS.NG(t=['a', 'b']), MQSTAR('c')]).match(FST('[a, b, a, b]'))))

        # partially built tags available to other patterns

        def cb(tgt, get_tag):
            lines.append(f"{tgt=}")
            lines.append(f"es={get_tag('es')}")
            lines.append(f"all_tagss={get_tag.__self__.all_tagss}")
            lines.append('')

            return True

        cb.__qualname__ = 'cb'
        f = FST('[a, b, c, d, e]')
        lines = []

        for mq in [
            MQ(MCB(cb, pass_tags=True), min=2, max=4, static1=True, static2=False),
            MQ(es=MCB(cb, pass_tags=True), min=2, max=4, static1=True, static2=False),
            MQ(MCB(cb=cb, pass_tags=True), min=2, max=4, static1=True, static2=False),
            MQ(es=MCB(cb=cb, pass_tags=True), min=2, max=4, static1=True, static2=False),
        ]:
            lines.append(f'{mq=}')
            lines.append('')
            m = MList([mq, MQSTAR]).match(f)
            lines.append(str(m))
            lines.extend(('', ''))

        self.assertEqual('\n'.join(lines).strip(), """
mq=MQ(MCB(cb), min=2, max=4, static1=True, static2=False)

tgt=<Name 0,1..0,2>
es=<NotSet>
all_tagss=[[], [], []]

tgt=<Name 0,4..0,5>
es=<NotSet>
all_tagss=[[], [], [{}]]

tgt=<Name 0,7..0,8>
es=<NotSet>
all_tagss=[[], [], [{}, {}, {'static1': True, 'static2': False}]]

tgt=<Name 0,10..0,11>
es=<NotSet>
all_tagss=[[], [], [{}, {}, {}, {'static1': True, 'static2': False}]]

<FSTMatch <List ROOT 0,0..0,15> {'static1': True, 'static2': False}>


mq=MQ(es=MCB(cb), min=2, max=4, static1=True, static2=False)

tgt=<Name 0,1..0,2>
es=[]
all_tagss=[[], [], [{'es': []}]]

tgt=<Name 0,4..0,5>
es=[<FSTMatch <Name 0,1..0,2>>]
all_tagss=[[], [], [{'es': [<FSTMatch <Name 0,1..0,2>>]}]]

tgt=<Name 0,7..0,8>
es=[<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]
all_tagss=[[], [], [{'es': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}, {'static1': True, 'static2': False}]]

tgt=<Name 0,10..0,11>
es=[<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]
all_tagss=[[], [], [{'es': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}, {'static1': True, 'static2': False}]]

<FSTMatch <List ROOT 0,0..0,15> {'es': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>, <FSTMatch <Name 0,10..0,11>>], 'static1': True, 'static2': False}>


mq=MQ(MCB(cb=cb), min=2, max=4, static1=True, static2=False)

tgt=<Name 0,1..0,2>
es=<NotSet>
all_tagss=[[], [], []]

tgt=<Name 0,4..0,5>
es=<NotSet>
all_tagss=[[], [], [{'cb': <Name 0,1..0,2>}]]

tgt=<Name 0,7..0,8>
es=<NotSet>
all_tagss=[[], [], [{'cb': <Name 0,1..0,2>}, {'cb': <Name 0,4..0,5>}, {'static1': True, 'static2': False}]]

tgt=<Name 0,10..0,11>
es=<NotSet>
all_tagss=[[], [], [{'cb': <Name 0,1..0,2>}, {'cb': <Name 0,4..0,5>}, {'cb': <Name 0,7..0,8>}, {'static1': True, 'static2': False}]]

<FSTMatch <List ROOT 0,0..0,15> {'cb': <Name 0,10..0,11>, 'static1': True, 'static2': False}>


mq=MQ(es=MCB(cb=cb), min=2, max=4, static1=True, static2=False)

tgt=<Name 0,1..0,2>
es=[]
all_tagss=[[], [], [{'es': []}]]

tgt=<Name 0,4..0,5>
es=[<FSTMatch <Name 0,1..0,2> {'cb': <Name 0,1..0,2>}>]
all_tagss=[[], [], [{'es': [<FSTMatch <Name 0,1..0,2> {'cb': <Name 0,1..0,2>}>]}]]

tgt=<Name 0,7..0,8>
es=[<FSTMatch <Name 0,1..0,2> {'cb': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'cb': <Name 0,4..0,5>}>]
all_tagss=[[], [], [{'es': [<FSTMatch <Name 0,1..0,2> {'cb': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'cb': <Name 0,4..0,5>}>]}, {'static1': True, 'static2': False}]]

tgt=<Name 0,10..0,11>
es=[<FSTMatch <Name 0,1..0,2> {'cb': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'cb': <Name 0,4..0,5>}>, <FSTMatch <Name 0,7..0,8> {'cb': <Name 0,7..0,8>}>]
all_tagss=[[], [], [{'es': [<FSTMatch <Name 0,1..0,2> {'cb': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'cb': <Name 0,4..0,5>}>, <FSTMatch <Name 0,7..0,8> {'cb': <Name 0,7..0,8>}>]}, {'static1': True, 'static2': False}]]

<FSTMatch <List ROOT 0,0..0,15> {'es': [<FSTMatch <Name 0,1..0,2> {'cb': <Name 0,1..0,2>}>, <FSTMatch <Name 0,4..0,5> {'cb': <Name 0,4..0,5>}>, <FSTMatch <Name 0,7..0,8> {'cb': <Name 0,7..0,8>}>, <FSTMatch <Name 0,10..0,11> {'cb': <Name 0,10..0,11>}>], 'static1': True, 'static2': False}>
        """.strip())

    def test_match_AST(self):
        pat = MConstant(M(t=...))

        self.assertIs((f := FST('...')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f.a).t)

        pat = MAST(value=M(t=...))

        self.assertIs((f := FST('...')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f.a).t)

        pat = Mexpr(value=M(t=...))

        self.assertIs((f := FST('...')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f.a).t)

        pat = Mexpr(value=MNOT(t='z'))

        self.assertIs((f := FST('...')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f.a).t)

        pat = MConstant(MCB(t=lambda v: True))

        self.assertIs((f := FST('...')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f.a).t)

        pat = MConstant(MCB(t=lambda v: v, tag_ret=True))

        self.assertIs((f := FST('...')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f.a).t)
        # self.assertIs((f := FST('False')).a.value, pat.match(f.a).t)
        # self.assertIs((f := FST('None')).a.value, pat.match(f.a).t)

        pat = MConstant(MOR('z', t=...))

        self.assertIs((f := FST('...')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f.a).t)

        pat = MConstant(MAND(u=..., t=MTAG('u')))

        self.assertIs((f := FST('...')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f.a).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f.a).t)

        self.assertIs((f := FST('global abc')).a.names[0], MGlobal([M(t='abc')]).match(f.a).t)

        self.assertIs((f := FST('global a, b')).a.names, MGlobal(M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('a, b')).a.elts, MTuple(M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('(a, b)')).a.elts, MTuple(M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('[a, b]')).a.elts, MList(M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('{a, b}')).a.elts, MSet(M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('a; b')).a.body, MModule(M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('a\nb')).a.body, MModule(M(t=['a', 'b'])).match(f.a).t)

        self.assertIs((f := FST('global a, b')).a.names, MAST(names=M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('a, b')).a.elts, MAST(elts=M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('(a, b)')).a.elts, MAST(elts=M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('[a, b]')).a.elts, MAST(elts=M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('{a, b}')).a.elts, MAST(elts=M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('a; b')).a.body, MAST(body=M(t=['a', 'b'])).match(f.a).t)
        self.assertIs((f := FST('a\nb')).a.body, MAST(body=M(t=['a', 'b'])).match(f.a).t)

        # patterns in various structural locations

        tgt_mod = FST('a', 'exec').copy_ast()
        tgt_list = FST('[a]').copy_ast()

        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Expr(value=Name(id='a'))}>", str(MModule(body=[M(t=...)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': [Expr(value=Name(id='a'))]}>", str(MModule(body=M(t=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Module(body=[Expr(value=Name(id='a'))], type_ignores=[])}>", str(M(t=MModule(body=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': Name(id='a')}>", str(MList(elts=[M(t=...)]).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': [Name(id='a')]}>", str(MList(elts=M(t=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': List(elts=[Name(id='a')])}>", str(M(t=MList(elts=[...])).match(tgt_list)))

        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Expr(value=Name(id='a'))}>", str(MModule(body=[MNOT(t='NO!')]).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': [Expr(value=Name(id='a'))]}>", str(MModule(body=MNOT(t=['NO!'])).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Module(body=[Expr(value=Name(id='a'))], type_ignores=[])}>", str(MNOT(t=MModule(body=['NO!'])).match(tgt_mod)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': Name(id='a')}>", str(MList(elts=[MNOT(t='NO!')]).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': [Name(id='a')]}>", str(MList(elts=MNOT(t=['NO!'])).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': List(elts=[Name(id='a')])}>", str(MNOT(t=MList(elts=['NO!'])).match(tgt_list)))

        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Expr(value=Name(id='a'))}>", str(MModule(body=[MOR(t=...)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': [Expr(value=Name(id='a'))]}>", str(MModule(body=MOR(t=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Module(body=[Expr(value=Name(id='a'))], type_ignores=[])}>", str(MOR(t=MModule(body=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': Name(id='a')}>", str(MList(elts=[MOR(t=...)]).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': [Name(id='a')]}>", str(MList(elts=MOR(t=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': List(elts=[Name(id='a')])}>", str(MOR(t=MList(elts=[...])).match(tgt_list)))

        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Expr(value=Name(id='a'))}>", str(MModule(body=[MAND(t=...)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': [Expr(value=Name(id='a'))]}>", str(MModule(body=MAND(t=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Module(body=[Expr(value=Name(id='a'))], type_ignores=[])}>", str(MAND(t=MModule(body=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': Name(id='a')}>", str(MList(elts=[MAND(t=...)]).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': [Name(id='a')]}>", str(MList(elts=MAND(t=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': List(elts=[Name(id='a')])}>", str(MAND(t=MList(elts=[...])).match(tgt_list)))

        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Expr(value=Name(id='a'))}>", str(MModule(body=[MOPT(t=...)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': [Expr(value=Name(id='a'))]}>", str(MModule(body=MOPT(t=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Module(body=[Expr(value=Name(id='a'))], type_ignores=[])}>", str(MOPT(t=MModule(body=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': Name(id='a')}>", str(MList(elts=[MOPT(t=...)]).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': [Name(id='a')]}>", str(MList(elts=MOPT(t=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': List(elts=[Name(id='a')])}>", str(MOPT(t=MList(elts=[...])).match(tgt_list)))

        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Expr(value=Name(id='a'))}>", str(MModule(body=[MCB(t=lambda t: t, tag_ret=True)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': [Expr(value=Name(id='a'))]}>", str(MModule(body=MCB(t=lambda t: t, tag_ret=True)).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Module(body=[Expr(value=Name(id='a'))], type_ignores=[])}>", str(MCB(t=lambda t: t, tag_ret=True).match(tgt_mod)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': Name(id='a')}>", str(MList(elts=[MCB(t=lambda t: t, tag_ret=True)]).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': [Name(id='a')]}>", str(MList(elts=MCB(t=lambda t: t, tag_ret=True)).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': List(elts=[Name(id='a')])}>", str(MCB(t=lambda t: t, tag_ret=True).match(tgt_list)))

        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': <re.Match object; span=(0, 1), match='a'>}>", str(MModule(body=[MRE(t='a$')]).match(tgt_mod)))
        self.assertEqual("None", str(MModule(body=MRE(t='a$')).match(tgt_mod)))  # because is a list[AST], not clear what text to compare against
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': <re.Match object; span=(0, 1), match='a'>}>", str(MRE(t='a$').match(tgt_mod)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': <re.Match object; span=(0, 1), match='a'>}>", str(MList(elts=[MRE(t='a$')]).match(tgt_list)))
        self.assertEqual("None", str(MList(elts=MRE(t='a$')).match(tgt_list)))  # because is a list[AST], not clear what text to compare against
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': <re.Match object; span=(0, 3), match='[a]'>}>", str(MRE(t=r'\[a\]$').match(tgt_list)))

        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Expr(value=Name(id='a')), 'u': Expr(value=Name(id='a'))}>", str(MModule(body=[MAND(M(t=...), MTAG(u='t'))]).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': [Expr(value=Name(id='a'))], 'u': [Expr(value=Name(id='a'))]}>", str(MModule(body=MAND(M(t=[...]), MTAG(u='t'))).match(tgt_mod)))
        self.assertEqual("<FSTMatch Module(body=[Expr(value=Name(id='a'))], type_ignores=[]) {'t': Module(body=[Expr(value=Name(id='a'))], type_ignores=[]), 'u': Module(body=[Expr(value=Name(id='a'))], type_ignores=[])}>", str(MAND(M(t=MModule(body=[...])), MTAG(u='t')).match(tgt_mod)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': Name(id='a'), 'u': Name(id='a')}>", str(MList(elts=[MAND(M(t=...), MTAG(u='t'))]).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': [Name(id='a')], 'u': [Name(id='a')]}>", str(MList(elts=MAND(M(t=[...]), MTAG(u='t'))).match(tgt_list)))
        self.assertEqual("<FSTMatch List(elts=[Name(id='a')]) {'t': List(elts=[Name(id='a')]), 'u': List(elts=[Name(id='a')])}>", str(MAND(M(t=MList(elts=[...])), MTAG(u='t')).match(tgt_list)))

    def test_match_FST(self):
        pat = MConstant(M(t=...))

        self.assertIs((f := FST('...')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f).t)

        pat = MAST(value=M(t=...))

        self.assertIs((f := FST('...')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f).t)

        pat = Mexpr(value=M(t=...))

        self.assertIs((f := FST('...')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f).t)

        pat = Mexpr(value=MNOT(t='z'))

        self.assertIs((f := FST('...')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f).t)

        pat = MConstant(MCB(t=lambda v: True))

        self.assertIs((f := FST('...')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f).t)

        pat = MConstant(MCB(t=lambda v: v, tag_ret=True))

        self.assertIs((f := FST('...')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f).t)
        # self.assertIs((f := FST('False')).a.value, pat.match(f).t)
        # self.assertIs((f := FST('None')).a.value, pat.match(f).t)

        pat = MConstant(MOR('z', t=...))

        self.assertIs((f := FST('...')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f).t)

        pat = MConstant(MAND(u=..., t=MTAG('u')))

        self.assertIs((f := FST('...')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234.0')).a.value, pat.match(f).t)
        self.assertIs((f := FST('1234j')).a.value, pat.match(f).t)
        self.assertIs((f := FST('"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('b"1234"')).a.value, pat.match(f).t)
        self.assertIs((f := FST('True')).a.value, pat.match(f).t)
        self.assertIs((f := FST('False')).a.value, pat.match(f).t)
        self.assertIs((f := FST('None')).a.value, pat.match(f).t)

        # self.assertIs((f := FST('global abc')).names[0], MGlobal([M(t='abc')]).match(f).t)
        self.assertEqual(str((f := FST('global abc')).names[0]), str(MGlobal([M(t='abc')]).match(f).t))
        self.assertEqual("<<Global ROOT 0,0..0,10>.names[:1]>", str(MGlobal([M(t='abc')]).match(FST('global abc')).t))

        self.assertEqual(str((f := FST('global a, b')).names), str(MGlobal(M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('a, b')).elts), str(MTuple(M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('(a, b)')).elts), str(MTuple(M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('[a, b]')).elts), str(MList(M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('{a, b}')).elts), str(MSet(M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('a; b')).body), str(MModule(M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('a\nb')).body), str(MModule(M(t=['a', 'b'])).match(f).t))

        self.assertEqual(str((f := FST('global a, b')).names), str(MAST(names=M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('a, b')).elts), str(MAST(elts=M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('(a, b)')).elts), str(MAST(elts=M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('[a, b]')).elts), str(MAST(elts=M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('{a, b}')).elts), str(MAST(elts=M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('a; b')).body), str(MAST(body=M(t=['a', 'b'])).match(f).t))
        self.assertEqual(str((f := FST('a\nb')).body), str(MAST(body=M(t=['a', 'b'])).match(f).t))

        # patterns in various structural locations

        tgt_mod = FST('a', 'exec')
        tgt_list = FST('[a]')
        tgt_dict = FST('{a: a}')
        tgt_arguments = FST('a: int = 1', 'arguments')

        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Expr 0,0..0,1>}>", str(MModule(body=[M(t=...)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <<Module ROOT 0,0..0,1>.body>}>", str(MModule(body=M(t=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Module ROOT 0,0..0,1>}>", str(M(t=MModule(body=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <Name 0,1..0,2>}>", str(MList(elts=[M(t=...)]).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <<List ROOT 0,0..0,3>.elts>}>", str(MList(elts=M(t=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <List ROOT 0,0..0,3>}>", str(M(t=MList(elts=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all[:1]>}>", str(MDict(_all=[M(t=...)]).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all>}>", str(MDict(_all=M(t=[...])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <Dict ROOT 0,0..0,6>}>", str(M(t=MDict(_all=[...])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[:1]>}>", str(Marguments(_all=[M(t=...)]).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all>}>", str(Marguments(_all=M(t=[...])).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <arguments ROOT 0,0..0,10>}>", str(M(t=Marguments(_all=[...])).match(tgt_arguments)))

        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Expr 0,0..0,1>}>", str(MModule(body=[MNOT(t='NO!')]).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <<Module ROOT 0,0..0,1>.body>}>", str(MModule(body=MNOT(t=['NO!'])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Module ROOT 0,0..0,1>}>", str(MNOT(t=MModule(body=['NO!'])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <Name 0,1..0,2>}>", str(MList(elts=[MNOT(t='NO!')]).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <<List ROOT 0,0..0,3>.elts>}>", str(MList(elts=MNOT(t=['NO!'])).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <List ROOT 0,0..0,3>}>", str(MNOT(t=MList(elts=['NO!'])).match(tgt_list)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all[:1]>}>", str(MDict(_all=[MNOT(t='NO!')]).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all>}>", str(MDict(_all=MNOT(t=['NO!'])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <Dict ROOT 0,0..0,6>}>", str(MNOT(t=MDict(_all=['NO!'])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[:1]>}>", str(Marguments(_all=[MNOT(t='NO!')]).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all>}>", str(Marguments(_all=MNOT(t=['NO!'])).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <arguments ROOT 0,0..0,10>}>", str(MNOT(t=Marguments(_all=['NO!'])).match(tgt_arguments)))

        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Expr 0,0..0,1>}>", str(MModule(body=[MOR(t=...)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <<Module ROOT 0,0..0,1>.body>}>", str(MModule(body=MOR(t=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Module ROOT 0,0..0,1>}>", str(MOR(t=MModule(body=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <Name 0,1..0,2>}>", str(MList(elts=[MOR(t=...)]).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <<List ROOT 0,0..0,3>.elts>}>", str(MList(elts=MOR(t=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <List ROOT 0,0..0,3>}>", str(MOR(t=MList(elts=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all[:1]>}>", str(MDict(_all=[MOR(t=...)]).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all>}>", str(MDict(_all=MOR(t=[...])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <Dict ROOT 0,0..0,6>}>", str(MOR(t=MDict(_all=[...])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[:1]>}>", str(Marguments(_all=[MOR(t=...)]).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all>}>", str(Marguments(_all=MOR(t=[...])).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <arguments ROOT 0,0..0,10>}>", str(MOR(t=Marguments(_all=[...])).match(tgt_arguments)))

        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Expr 0,0..0,1>}>", str(MModule(body=[MAND(t=...)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <<Module ROOT 0,0..0,1>.body>}>", str(MModule(body=MAND(t=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Module ROOT 0,0..0,1>}>", str(MAND(t=MModule(body=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <Name 0,1..0,2>}>", str(MList(elts=[MAND(t=...)]).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <<List ROOT 0,0..0,3>.elts>}>", str(MList(elts=MAND(t=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <List ROOT 0,0..0,3>}>", str(MAND(t=MList(elts=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all[:1]>}>", str(MDict(_all=[MAND(t=...)]).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all>}>", str(MDict(_all=MAND(t=[...])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <Dict ROOT 0,0..0,6>}>", str(MAND(t=MDict(_all=[...])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[:1]>}>", str(Marguments(_all=[MAND(t=...)]).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all>}>", str(Marguments(_all=MAND(t=[...])).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <arguments ROOT 0,0..0,10>}>", str(MAND(t=Marguments(_all=[...])).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Expr 0,0..0,1>}>", str(MModule(body=[MOPT(t=...)]).match(tgt_mod)))

        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <<Module ROOT 0,0..0,1>.body>}>", str(MModule(body=MOPT(t=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Module ROOT 0,0..0,1>}>", str(MOPT(t=MModule(body=[...])).match(tgt_mod)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <Name 0,1..0,2>}>", str(MList(elts=[MOPT(t=...)]).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <<List ROOT 0,0..0,3>.elts>}>", str(MList(elts=MOPT(t=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <List ROOT 0,0..0,3>}>", str(MOPT(t=MList(elts=[...])).match(tgt_list)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all[:1]>}>", str(MDict(_all=[MOPT(t=...)]).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all>}>", str(MDict(_all=MOPT(t=[...])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <Dict ROOT 0,0..0,6>}>", str(MOPT(t=MDict(_all=[...])).match(tgt_dict)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[:1]>}>", str(Marguments(_all=[MOPT(t=...)]).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all>}>", str(Marguments(_all=MOPT(t=[...])).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <arguments ROOT 0,0..0,10>}>", str(MOPT(t=Marguments(_all=[...])).match(tgt_arguments)))

        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Expr 0,0..0,1>}>", str(MModule(body=[MCB(t=lambda t: t, tag_ret=True)]).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <<Module ROOT 0,0..0,1>.body>}>", str(MModule(body=MCB(t=lambda t: t, tag_ret=True)).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Module ROOT 0,0..0,1>}>", str(MCB(t=lambda t: t, tag_ret=True).match(tgt_mod)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <Name 0,1..0,2>}>", str(MList(elts=[MCB(t=lambda t: t, tag_ret=True)]).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <<List ROOT 0,0..0,3>.elts>}>", str(MList(elts=MCB(t=lambda t: t, tag_ret=True)).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <List ROOT 0,0..0,3>}>", str(MCB(t=lambda t: t, tag_ret=True).match(tgt_list)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all[:1]>}>", str(MDict(_all=[MCB(t=lambda t: t, tag_ret=True)]).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all>}>", str(MDict(_all=MCB(t=lambda t: t, tag_ret=True)).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <Dict ROOT 0,0..0,6>}>", str(MCB(t=lambda t: t, tag_ret=True).match(tgt_dict)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[:1]>}>", str(Marguments(_all=[MCB(t=lambda t: t, tag_ret=True)]).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all>}>", str(Marguments(_all=MCB(t=lambda t: t, tag_ret=True)).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <arguments ROOT 0,0..0,10>}>", str(MCB(t=lambda t: t, tag_ret=True).match(tgt_arguments)))

        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <re.Match object; span=(0, 1), match='a'>}>", str(MModule(body=[MRE(t='a$')]).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <re.Match object; span=(0, 1), match='a'>}>", str(MModule(body=MRE(t='a$')).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <re.Match object; span=(0, 1), match='a'>}>", str(MRE(t='a$').match(tgt_mod)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <re.Match object; span=(0, 1), match='a'>}>", str(MList(elts=[MRE(t='a$')]).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <re.Match object; span=(0, 1), match='a'>}>", str(MList(elts=MRE(t='a$')).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <re.Match object; span=(0, 3), match='[a]'>}>", str(MRE(t=r'\[a\]$').match(tgt_list)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <re.Match object; span=(0, 4), match='a: a'>}>", str(MDict(_all=[MRE(t='a: a$')]).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <re.Match object; span=(0, 4), match='a: a'>}>", str(MDict(_all=MRE(t='a: a$')).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <re.Match object; span=(0, 6), match='{a: a}'>}>", str(MRE(t='{a: a}$').match(tgt_dict)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <re.Match object; span=(0, 10), match='a: int = 1'>}>", str(Marguments(_all=[MRE(t='a: int = 1$')]).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <re.Match object; span=(0, 10), match='a: int = 1'>}>", str(Marguments(_all=MRE(t='a: int = 1$')).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <re.Match object; span=(0, 10), match='a: int = 1'>}>", str(MRE(t='a: int = 1$').match(tgt_arguments)))

        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Expr 0,0..0,1>, 'u': <Expr 0,0..0,1>}>", str(MModule(body=[MAND(M(t=...), MTAG(u='t'))]).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <<Module ROOT 0,0..0,1>.body>, 'u': <<Module ROOT 0,0..0,1>.body>}>", str(MModule(body=MAND(M(t=[...]), MTAG(u='t'))).match(tgt_mod)))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..0,1> {'t': <Module ROOT 0,0..0,1>, 'u': <Module ROOT 0,0..0,1>}>", str(MAND(M(t=MModule(body=[...])), MTAG(u='t')).match(tgt_mod)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <Name 0,1..0,2>, 'u': <Name 0,1..0,2>}>", str(MList(elts=[MAND(M(t=...), MTAG(u='t'))]).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <<List ROOT 0,0..0,3>.elts>, 'u': <<List ROOT 0,0..0,3>.elts>}>", str(MList(elts=MAND(M(t=[...]), MTAG(u='t'))).match(tgt_list)))
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,3> {'t': <List ROOT 0,0..0,3>, 'u': <List ROOT 0,0..0,3>}>", str(MAND(M(t=MList(elts=[...])), MTAG(u='t')).match(tgt_list)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all[:1]>, 'u': <<Dict ROOT 0,0..0,6>._all[:1]>}>", str(MDict(_all=[MAND(M(t=...), MTAG(u='t'))]).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <<Dict ROOT 0,0..0,6>._all>, 'u': <<Dict ROOT 0,0..0,6>._all>}>", str(MDict(_all=MAND(M(t=[...]), MTAG(u='t'))).match(tgt_dict)))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,6> {'t': <Dict ROOT 0,0..0,6>, 'u': <Dict ROOT 0,0..0,6>}>", str(MAND(M(t=MDict(_all=[...])), MTAG(u='t')).match(tgt_dict)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[:1]>, 'u': <<arguments ROOT 0,0..0,10>._all[:1]>}>", str(Marguments(_all=[MAND(M(t=...), MTAG(u='t'))]).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all>, 'u': <<arguments ROOT 0,0..0,10>._all>}>", str(Marguments(_all=MAND(M(t=[...]), MTAG(u='t'))).match(tgt_arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <arguments ROOT 0,0..0,10>, 'u': <arguments ROOT 0,0..0,10>}>", str(MAND(M(t=Marguments(_all=[...])), MTAG(u='t')).match(tgt_arguments)))

    def test_match_FSTView(self):
        self.assertTrue(MClassDef(_bases=['a', '*b', 'c=d', '**e']).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertFalse(MClassDef(_bases=['a', '*b', 'c=d', '**f']).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertTrue(MCall(_args=['a', '*b', 'c=d', '**e']).match(FST('call(a, *b, c=d, **e)')))
        self.assertFalse(MCall(_args=['a', '*b', 'c=d', '**f']).match(FST('call(a, *b, c=d, **e)')))
        self.assertFalse(MClassDef(body=['a', 'b', 'c']).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertTrue(MClassDef(_body=['a', 'b', 'c']).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertTrue(MGlobal(names=['a', 'b', 'c']).match(FST('global a, b, c')))
        self.assertFalse(MGlobal(names=['a', 'b', 'd']).match(FST('global a, b, c')))
        self.assertTrue(MNonlocal(names=['a', 'b', 'c']).match(FST('nonlocal a, b, c')))
        self.assertFalse(MNonlocal(names=['a', 'b', 'd']).match(FST('nonlocal a, b, c')))
        self.assertTrue(MCompare(_all=['a', 'b', 'c']).match(FST('a < b < c')))
        self.assertFalse(MCompare(_all=['a', 'b', 'd']).match(FST('a < b < c')))

        self.assertTrue(MClassDef(_bases=[MName('a'), MStarred(MName('b')), Mkeyword('c', MName('d')), Mkeyword(None, MName('e'))]).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertFalse(MClassDef(_bases=[MName('a'), MStarred(MName('b')), Mkeyword('c', MName('d')), Mkeyword(None, MName('f'))]).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertTrue(MCall(_args=[MName('a'), MStarred(MName('b')), Mkeyword('c', MName('d')), Mkeyword(None, MName('e'))]).match(FST('call(a, *b, c=d, **e)')))
        self.assertFalse(MCall(_args=[MName('a'), MStarred(MName('b')), Mkeyword('c', MName('d')), Mkeyword(None, MName('f'))]).match(FST('call(a, *b, c=d, **e)')))
        self.assertFalse(MClassDef(body=[MExpr(MName('a')), MExpr(MName('b')), MExpr(MName('c'))]).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertTrue(MClassDef(_body=[MExpr(MName('a')), MExpr(MName('b')), MExpr(MName('c'))]).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertTrue(MCompare(_all=[MName('a'), MName('b'), MName('c')]).match(FST('a < b < c')))
        self.assertFalse(MCompare(_all=[MName('a'), MName('b'), MName('d')]).match(FST('a < b < c')))

        self.assertTrue(MClassDef(_bases=[MQSTAR]).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertTrue(MCall(_args=[MQSTAR]).match(FST('call(a, *b, c=d, **e)')))
        self.assertTrue(MClassDef(body=[MQSTAR]).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertTrue(MClassDef(_body=[MQSTAR]).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertTrue(MGlobal(names=[MQSTAR]).match(FST('global a, b, c')))
        self.assertTrue(MNonlocal(names=[MQSTAR]).match(FST('nonlocal a, b, c')))
        self.assertTrue(MCompare(_all=[MQSTAR]).match(FST('a < b < c')))

    def test_match_FSTView_to_FSTView(self):
        # same type

        self.assertTrue(MClassDef(_bases=FST('class c(a, *b, c=d, **e): pass')._bases).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertFalse(MClassDef(_bases=FST('class c(a, *b, c=d, **f): pass')._bases).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertTrue(MCall(_args=FST('call(a, *b, c=d, **e)')._args).match(FST('call(a, *b, c=d, **e)')))
        self.assertFalse(MCall(_args=FST('call(a, *b, c=d, **f)')._args).match(FST('call(a, *b, c=d, **e)')))

        self.assertTrue(MClassDef(body=FST('class cls:\n """docstr"""\n a\n b\n c').body).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertFalse(MClassDef(body=FST('class cls:\n """docstr"""\n a\n b\n c')._body).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertFalse(MClassDef(_body=FST('class cls:\n """docstr"""\n a\n b\n c').body).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertTrue(MClassDef(_body=FST('class cls:\n """docstr"""\n a\n b\n c')._body).match(FST('class cls:\n """docstr"""\n a\n b\n c')))

        self.assertTrue(MGlobal(names=FST('global a, b, c').names).match(FST('global a, b, c')))
        self.assertFalse(MGlobal(names=FST('global a, b, d').names).match(FST('global a, b, c')))
        self.assertTrue(MNonlocal(names=FST('nonlocal a, b, c').names).match(FST('nonlocal a, b, c')))
        self.assertFalse(MNonlocal(names=FST('nonlocal a, b, d').names).match(FST('nonlocal a, b, c')))

        self.assertTrue(MCompare(_all=FST('a < b < c')._all).match(FST('a < b < c')))
        self.assertFalse(MCompare(_all=FST('a < b < d')._all).match(FST('a < b < c')))
        self.assertFalse(MCompare(_all=FST('a < b > d')._all).match(FST('a < b < c')))

        # different type

        self.assertTrue(MClassDef(_bases=FST('call(a, *b, c=d, **e)')._args).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertFalse(MClassDef(_bases=FST('call(a, *b, c=d, **f)')._args).match(FST('class c(a, *b, c=d, **e): pass')))
        self.assertTrue(MCall(_args=FST('class c(a, *b, c=d, **e): pass')._bases).match(FST('call(a, *b, c=d, **e)')))
        self.assertFalse(MCall(_args=FST('class c(a, *b, c=d, **f): pass')._bases).match(FST('call(a, *b, c=d, **e)')))

        self.assertTrue(MClassDef(body=FST('def f():\n """docstr"""\n a\n b\n c').body).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertFalse(MClassDef(body=FST('def f():\n """docstr"""\n a\n b\n c')._body).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertFalse(MClassDef(_body=FST('def f():\n """docstr"""\n a\n b\n c').body).match(FST('class cls:\n """docstr"""\n a\n b\n c')))
        self.assertTrue(MClassDef(_body=FST('def f():\n """docstr"""\n a\n b\n c')._body).match(FST('class cls:\n """docstr"""\n a\n b\n c')))

        self.assertTrue(MGlobal(names=FST('nonlocal a, b, c').names).match(FST('global a, b, c')))
        self.assertFalse(MGlobal(names=FST('nonlocal a, b, d').names).match(FST('global a, b, c')))
        self.assertTrue(MNonlocal(names=FST('global a, b, c').names).match(FST('nonlocal a, b, c')))
        self.assertFalse(MNonlocal(names=FST('global a, b, d').names).match(FST('nonlocal a, b, c')))

    def test_match_virtual_field_Compare(self):
        self.assertEqual("<FSTMatch <<Compare ROOT 0,0..0,5>._all[:0]>>", str(MCompare(NotSet, [], []).match(FST('a < b')._all[:0])))

        f = FST('a < b')
        del f[1]
        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,1>>", str(MCompare().match(f)))
        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,1>>", str(MCompare('a').match(f)))
        self.assertEqual("None", str(MCompare('b').match(f)))

        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,5>>", str(MCompare(_all=FST('a < b')._all).match(FST('a < b'))))
        self.assertEqual("None", str(MCompare(_all=FST('a > b')._all).match(FST('a < b'))))
        self.assertEqual("None", str(MCompare(_all=FST('a < c')._all).match(FST('a < b'))))

        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,9>>", str(MCompare(_all=FST('a < b < c')._all).match(FST('a < b < c'))))
        self.assertEqual("None", str(MCompare(_all=FST('a < b > c')._all).match(FST('a < b < c'))))
        self.assertEqual("None", str(MCompare(_all=FST('a < b < d')._all).match(FST('a < b < c'))))

        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,9> {'t': <Name 0,0..0,1>}>", str(MCompare(_all=MCompare(M(t='a'), ['<', '>'], ['b', 'c'])).match(FST('a < b > c'))))
        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,9> {'t': <Lt 0,2..0,3>}>", str(MCompare(_all=MCompare('a', [M(t='<'), '>'], ['b', 'c'])).match(FST('a < b > c'))))
        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,9> {'t': <Gt 0,6..0,7>}>", str(MCompare(_all=MCompare('a', ['<', M(t='>')], ['b', 'c'])).match(FST('a < b > c'))))
        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,9> {'t': <Name 0,4..0,5>}>", str(MCompare(_all=MCompare('a', ['<', '>'], [M(t='b'), 'c'])).match(FST('a < b > c'))))
        self.assertEqual("<FSTMatch <Compare ROOT 0,0..0,9> {'t': <Name 0,8..0,9>}>", str(MCompare(_all=MCompare('a', ['<', '>'], ['b', M(t='c')])).match(FST('a < b > c'))))

        self.assertFalse(MCompare(_all=MCompare('x', ['<', '>'], ['b', 'c'])).match(FST('a < b > c')))
        self.assertFalse(MCompare(_all=MCompare('a', ['>', '>'], ['b', 'c'])).match(FST('a < b > c')))
        self.assertFalse(MCompare(_all=MCompare('a', ['<', '<'], ['b', 'c'])).match(FST('a < b > c')))
        self.assertFalse(MCompare(_all=MCompare('a', ['<', '>'], ['x', 'c'])).match(FST('a < b > c')))

    def test_match_virtual_field_one_Dict(self):
        # string to multinode

        self.assertTrue(MDict(_all=['a: b']).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=['a: b']).match(FST('{ a: b }')))
        self.assertFalse(MDict(_all=['a: b']).match(FST('{a:b}')))
        self.assertFalse(MDict(_all=['a: b']).match(FST('{a:  b}')))

        self.assertTrue(MDict(_all=['** b']).match(FST('{** b}')))
        self.assertTrue(MDict(_all=['** b']).match(FST('{ ** b }')))
        self.assertFalse(MDict(_all=['** b']).match(FST('{**b}')))
        self.assertFalse(MDict(_all=['** b']).match(FST('{**  b}')))

        # regex to multinode

        self.assertTrue(MDict(_all=[re.compile(r'a\s*:\s*b')]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[re.compile(r'a\s*:\s*b')]).match(FST('{a:b}')))
        self.assertTrue(MDict(_all=[re.compile(r'a\s*:\s*b')]).match(FST('{ a : b }')))
        self.assertFalse(MDict(_all=[re.compile(r'a\s*:\s*b')]).match(FST('{a: c}')))

        self.assertTrue(MDict(_all=[re.compile(r'\*\*\s*b')]).match(FST('{**b}')))
        self.assertTrue(MDict(_all=[re.compile(r'\*\*\s*b')]).match(FST('{** b}')))
        self.assertFalse(MDict(_all=[re.compile(r'\*\*\s*b')]).match(FST('{**c}')))

        # MRE to multinode

        self.assertTrue(MDict(_all=[MRE(r'a\s*:\s*b')]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[MRE(r'a\s*:\s*b')]).match(FST('{a:b}')))
        self.assertTrue(MDict(_all=[MRE(r'a\s*:\s*b')]).match(FST('{ a : b }')))
        self.assertFalse(MDict(_all=[MRE(r'a\s*:\s*b')]).match(FST('{a: c}')))

        self.assertTrue(MDict(_all=[MRE(r'\*\*\s*b')]).match(FST('{**b}')))
        self.assertTrue(MDict(_all=[MRE(r'\*\*\s*b')]).match(FST('{** b}')))
        self.assertFalse(MDict(_all=[MRE(r'\*\*\s*b')]).match(FST('{**c}')))

        # Concrete pattern to multinode Dict

        # f = FST('{a: b}')
        # assertRaises(MatchError('matching a Dict pattern against Dict._all the pattern cannot have its own _all field'), MDict(_all=[MDict(_all=['a'])]).match, f)
        # assertRaises(MatchError('MQ quantifier pattern in invalid location'), MDict(_all=[MDict(keys=[MQ('a', 0, None)])]).match, f)
        # assertRaises(MatchError('MQ quantifier pattern in invalid location'), MDict(_all=[MDict(..., values=[MQ('a', 0, None)])]).match, f)
        # assertRaises(MatchError('matching a Dict pattern against Dict._all the pattern keys must be ... or a length-1 list'), MDict(_all=[MDict([], [])]).match, f)
        # assertRaises(MatchError('matching a Dict pattern against Dict._all the pattern values must be ... or a length-1 list'), MDict(_all=[MDict(['a'], [])]).match, f)
        # assertRaises(MatchError('matching a Dict pattern against Dict._all the pattern keys must be ... or a length-1 list'), MDict(_all=[MDict(['a', 'a'], [])]).match, f)
        # assertRaises(MatchError('matching a Dict pattern against Dict._all the pattern values must be ... or a length-1 list'), MDict(_all=[MDict(['a'], ['a', 'a'])]).match, f)

        self.assertTrue(MDict(_all=[FST('{a: b}').a]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[FST('{a: b}').a]).match(FST('{ a : b }')))
        self.assertTrue(MDict(_all=[MDict(['a'])]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[MDict(['a'])]).match(FST('{ a : c }')))
        self.assertFalse(MDict(_all=[MDict(['a'])]).match(FST('{x: b}')))
        self.assertTrue(MDict(_all=[MDict(values=['b'])]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[MDict(values=['b'])]).match(FST('{ c : b }')))
        self.assertFalse(MDict(_all=[MDict(values=['b'])]).match(FST('{a: x}')))

        self.assertTrue(MDict(_all=[FST('{**b}').a]).match(FST('{**b}')))
        self.assertFalse(MDict(_all=[FST('{**b}').a]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[MDict([None], ['b'])]).match(FST('{**b}')))
        self.assertFalse(MDict(_all=[MDict([None], ['b'])]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[MDict(..., ['b'])]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[MDict(..., ['b'])]).match(FST('{**b}')))
        self.assertTrue(MDict(_all=[MDict(..., ['b'])]).match(FST('{c: b}')))
        self.assertTrue(MDict(_all=[MDict([MOPT('a')], ['b'])]).match(FST('{a: b}')))
        self.assertTrue(MDict(_all=[MDict([MOPT('a')], ['b'])]).match(FST('{**b}')))
        self.assertFalse(MDict(_all=[MDict([MOPT('a')], ['b'])]).match(FST('{c: b}')))

        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,17> {'t': [<FSTMatch <<Dict ROOT 0,0..0,17>._all[:1]>>, <FSTMatch <<Dict ROOT 0,0..0,17>._all[1:2]>>]}>", str(MDict(_all=[MQ(t=MDict(..., ['b']), min=0, max=None), MQSTAR]).match(FST('{a: b, **b, c: d}'))))
        self.assertEqual('[<<Dict ROOT 0,0..0,17>._all[:1]>, <<Dict ROOT 0,0..0,17>._all[1:2]>]', str([m.matched for m in MDict(_all=[MQ(t=MDict(..., ['b']), min=0, max=None), MQSTAR]).match(FST('{a: b, **b, c: d}')).t]))
        self.assertEqual('[<Name 0,4..0,5>, <Name 0,9..0,10>]', str([m.v for m in MDict(_all=[MQ(t=MDict(..., [M(v='b')]), min=0, max=None), MQSTAR]).match(FST('{a: b, **b, c: d}')).t]))
        self.assertEqual('[<Name 0,1..0,2>, None]', str([m.k for m in MDict(_all=[MQ(t=MDict([M(k=MOPT('a'))]), min=0, max=None), MQSTAR]).match(FST('{a: b, **b, c: d}')).t]))

        pat = MList([M(t=MDict(..., ['b'])), MDict(_all=[MQPLUS(MTAG('t'))])])
        self.assertFalse(pat.match(FST('[{1: b}, {}]')))
        self.assertTrue(pat.match(FST('[{1: b}, {1: b}]')))
        self.assertTrue(pat.match(FST('[{1: b}, {1: b, 1: b}]')))
        self.assertFalse(pat.match(FST('[{1: b}, {1: c}]')))
        self.assertFalse(pat.match(FST('[{2: b}, {1: b}]')))
        self.assertTrue(pat.match(FST('[{2: b}, {2: b}]')))
        self.assertTrue(pat.match(FST('[{2: b}, {2: b, 2: b}]')))

        pat = MDict(_all=[M(t=...), MQSTAR, M(u=MTAG('t'))])
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,12> {'t': <<Dict ROOT 0,0..0,12>._all[:1]>, 'u': <<Dict ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('{1: a, 1: a}'))))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,18> {'t': <<Dict ROOT 0,0..0,18>._all[:1]>, 'u': <<Dict ROOT 0,0..0,18>._all[2:3]>}>", str(pat.match(FST('{1: a, 2: b, 1: a}'))))
        self.assertEqual("<FSTMatch <Dict ROOT 0,0..0,16> {'t': <<Dict ROOT 0,0..0,16>._all[:1]>, 'u': <<Dict ROOT 0,0..0,16>._all[2:3]>}>", str(pat.match(FST('{**a, 2: b, **a}'))))
        self.assertFalse(pat.match(FST('{1: a, 2: b, 1: a, **b}')))

        pat = MList([M(..., t=MDict([M(k=...)], [M(v=...)])), MDict(_all=[MTAG('t')])])
        self.assertEqual("<FSTMatch <List ROOT 0,0..0,16> {'t': MDict(keys=[M(k=...)], values=[M(v=...)]), 'k': <Constant 0,10..0,11>, 'v': <Name 0,13..0,14>}>", str(pat.match(FST('[filler, {1: a}]'))))

        # self.assertIsNone(MDict().match(FST('{1: a, 2: b}')._all))  # this is a truly unrealistic test, but hey, coverage

    def test_match_virtual_field_one_MatchMapping(self):
        # string to multinode

        self.assertTrue(MMatchMapping(_all=['1: b']).match(FST('{1: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=['1: b']).match(FST('{ 1: b }', pattern)))
        self.assertFalse(MMatchMapping(_all=['1: b']).match(FST('{1:b}', pattern)))
        self.assertFalse(MMatchMapping(_all=['1: b']).match(FST('{1:  b}', pattern)))

        self.assertTrue(MMatchMapping(_all=['** b']).match(FST('{** b}', pattern)))
        self.assertTrue(MMatchMapping(_all=['** b']).match(FST('{ ** b }', pattern)))
        self.assertFalse(MMatchMapping(_all=['** b']).match(FST('{**b}', pattern)))
        self.assertFalse(MMatchMapping(_all=['** b']).match(FST('{**  b}', pattern)))

        # regex to multinode

        self.assertTrue(MMatchMapping(_all=[re.compile(r'1\s*:\s*b')]).match(FST('{1: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[re.compile(r'1\s*:\s*b')]).match(FST('{1:b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[re.compile(r'1\s*:\s*b')]).match(FST('{ 1 : b }', pattern)))
        self.assertFalse(MMatchMapping(_all=[re.compile(r'1\s*:\s*b')]).match(FST('{1: c}', pattern)))

        self.assertTrue(MMatchMapping(_all=[re.compile(r'\*\*\s*b')]).match(FST('{**b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[re.compile(r'\*\*\s*b')]).match(FST('{** b}', pattern)))
        self.assertFalse(MMatchMapping(_all=[re.compile(r'\*\*\s*b')]).match(FST('{**c}', pattern)))

        # MRE to multinode

        self.assertTrue(MMatchMapping(_all=[MRE(r'1\s*:\s*b')]).match(FST('{1: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MRE(r'1\s*:\s*b')]).match(FST('{1:b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MRE(r'1\s*:\s*b')]).match(FST('{ 1 : b }', pattern)))
        self.assertFalse(MMatchMapping(_all=[MRE(r'1\s*:\s*b')]).match(FST('{1: c}', pattern)))

        self.assertTrue(MMatchMapping(_all=[MRE(r'\*\*\s*b')]).match(FST('{**b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MRE(r'\*\*\s*b')]).match(FST('{** b}', pattern)))
        self.assertFalse(MMatchMapping(_all=[MRE(r'\*\*\s*b')]).match(FST('{**c}', pattern)))

        # Concrete pattern to multinode MatchMapping

        # f = FST('{1: b}', pattern)
        # assertRaises(MatchError('matching a MatchMapping pattern against MatchMapping._all the pattern cannot have its own _all field'), MMatchMapping(_all=[MMatchMapping(_all=['a'])]).match, f)
        # assertRaises(MatchError('MQ quantifier pattern in invalid location'), MMatchMapping(_all=[MMatchMapping(keys=[MQ('a', min=0, max=None)])]).match, f)
        # assertRaises(MatchError('MQ quantifier pattern in invalid location'), MMatchMapping(_all=[MMatchMapping(..., patterns=[MQ('a', min=0, max=None)])]).match, f)
        # assertRaises(MatchError('matching a MatchMapping rest against MatchMapping._all the pattern keys and patterns must be ... or empty lists'), MMatchMapping(_all=[MMatchMapping(['a'], [], 'r')]).match, f)
        # assertRaises(MatchError('matching a MatchMapping rest against MatchMapping._all the pattern keys and patterns must be ... or empty lists'), MMatchMapping(_all=[MMatchMapping([], ['a'], 'r')]).match, f)
        # assertRaises(MatchError('matching a MatchMapping rest against MatchMapping._all the pattern keys and patterns must be ... or empty lists'), MMatchMapping(_all=[MMatchMapping(['a'], ['a'], 'r')]).match, f)
        # assertRaises(MatchError('matching a MatchMapping rest against MatchMapping._all the pattern keys and patterns must be ... or empty lists'), MMatchMapping(_all=[MMatchMapping(['a'], [], 'r')]).match, f)
        # assertRaises(MatchError('matching a MatchMapping rest against MatchMapping._all the pattern keys and patterns must be ... or empty lists'), MMatchMapping(_all=[MMatchMapping([], ['a'], 'r')]).match, f)
        # assertRaises(MatchError('matching a MatchMapping rest against MatchMapping._all the pattern keys and patterns must be ... or empty lists'), MMatchMapping(_all=[MMatchMapping(['a'], ['a'], 'r')]).match, f)
        # assertRaises(MatchError('matching a MatchMapping pattern against MatchMapping._all the pattern keys must be ... or a length-1 list'), MMatchMapping(_all=[MMatchMapping([], [])]).match, f)
        # assertRaises(MatchError('matching a MatchMapping pattern against MatchMapping._all the pattern patterns must be ... or a length-1 list'), MMatchMapping(_all=[MMatchMapping(['a'], [])]).match, f)
        # assertRaises(MatchError('matching a MatchMapping pattern against MatchMapping._all the pattern patterns must be ... or a length-1 list'), MMatchMapping(_all=[MMatchMapping(['a'], ['a', 'a'])]).match, f)
        # assertRaises(MatchError('matching a MatchMapping pattern against MatchMapping._all the pattern keys must be ... or a length-1 list'), MMatchMapping(_all=[MMatchMapping(['a', 'a'], ['a'])]).match, f)

        self.assertTrue(MMatchMapping(_all=[FST('{1: b}', pattern).a]).match(FST('{1: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[FST('{1: b}', pattern).a]).match(FST('{ 1 : b }', pattern)))
        self.assertTrue(MMatchMapping(_all=[MMatchMapping(['1'])]).match(FST('{1: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MMatchMapping(['1'])]).match(FST('{ 1 : c }', pattern)))
        self.assertFalse(MMatchMapping(_all=[MMatchMapping(['1'])]).match(FST('{2: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MMatchMapping(patterns=['b'])]).match(FST('{1: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MMatchMapping(patterns=['b'])]).match(FST('{ 2 : b }', pattern)))
        self.assertFalse(MMatchMapping(_all=[MMatchMapping(patterns=['b'])]).match(FST('{1: x}', pattern)))

        self.assertTrue(MMatchMapping(_all=[FST('{**b}', pattern).a]).match(FST('{**b}', pattern)))
        self.assertFalse(MMatchMapping(_all=[FST('{**b}', pattern).a]).match(FST('{1: b}', pattern)))
        self.assertFalse(MMatchMapping(_all=[MMatchMapping([None], ['b'])]).match(FST('{**b}', pattern)))
        self.assertFalse(MMatchMapping(_all=[MMatchMapping([None], ['b'])]).match(FST('{1: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MMatchMapping(..., ['b'])]).match(FST('{1: b}', pattern)))
        self.assertFalse(MMatchMapping(_all=[MMatchMapping(..., ['b'])]).match(FST('{**b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MMatchMapping(..., ['b'])]).match(FST('{2: b}', pattern)))
        self.assertTrue(MMatchMapping(_all=[MMatchMapping([MOPT('1')], ['b'])]).match(FST('{1: b}', pattern)))
        self.assertFalse(MMatchMapping(_all=[MMatchMapping([MOPT('1')], ['b'])]).match(FST('{**b}', pattern)))
        self.assertFalse(MMatchMapping(_all=[MMatchMapping([MOPT('1')], ['b'])]).match(FST('{2: b}', pattern)))

        self.assertEqual("<FSTMatch <MatchMapping ROOT 0,0..0,11> {'t': [<FSTMatch <<MatchMapping ROOT 0,0..0,11>._all[:1]>>]}>", str(MMatchMapping(_all=[MQ(t=MMatchMapping(..., ['b']), min=0, max=None), MQSTAR]).match(FST('{1: b, **b}', pattern))))
        self.assertEqual('[<<MatchMapping ROOT 0,0..0,11>._all[:1]>]', str([m.matched for m in MMatchMapping(_all=[MQ(t=MMatchMapping(..., ['b']), min=0, max=None), MQSTAR]).match(FST('{1: b, **b}', pattern)).t]))
        self.assertEqual("[<MatchAs 0,4..0,5>]", str([m.v for m in MMatchMapping(_all=[MQ(t=MMatchMapping(..., [M(v='b')]), min=0, max=None), MQSTAR]).match(FST('{1: b, **b}', pattern)).t]))
        self.assertEqual('[<Constant 0,1..0,2>]', str([m.k for m in MMatchMapping(_all=[MQ(t=MMatchMapping([M(k=MOPT('1'))]), min=0, max=None), MQSTAR]).match(FST('{1: b, **b}', pattern)).t]))

        pat = MMatchSequence([M(t=MMatchMapping(..., ['b'])), MMatchMapping(_all=[MQPLUS(MTAG('t'))])])
        self.assertFalse(pat.match(FST('[{1: b}, {}]', pattern)))
        self.assertTrue(pat.match(FST('[{1: b}, {1: b}]', pattern)))
        self.assertTrue(pat.match(FST('[{1: b}, {1: b, 1: b}]', pattern)))
        self.assertFalse(pat.match(FST('[{1: b}, {1: c}]', pattern)))
        self.assertFalse(pat.match(FST('[{2: b}, {1: b}]', pattern)))
        self.assertTrue(pat.match(FST('[{2: b}, {2: b}]', pattern)))
        self.assertTrue(pat.match(FST('[{2: b}, {2: b, 2: b}]', pattern)))

        pat = MMatchMapping(_all=[M(t=...), MQSTAR, M(u=MTAG('t'))])
        self.assertEqual("<FSTMatch <MatchMapping ROOT 0,0..0,12> {'t': <<MatchMapping ROOT 0,0..0,12>._all[:1]>, 'u': <<MatchMapping ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('{1: a, 1: a}', pattern))))
        self.assertEqual("<FSTMatch <MatchMapping ROOT 0,0..0,18> {'t': <<MatchMapping ROOT 0,0..0,18>._all[:1]>, 'u': <<MatchMapping ROOT 0,0..0,18>._all[2:3]>}>", str(pat.match(FST('{1: a, 2: b, 1: a}', pattern))))
        self.assertFalse(pat.match(FST('{1: a, 2: b, 1: a, **b}', pattern)))

        pat = MMatchSequence([MMatchMapping(_all=[MQSTAR, M(t=...)]), MMatchMapping(_all=[..., M(u=MTAG('t'))])])
        self.assertEqual("<FSTMatch <MatchSequence ROOT 0,0..0,20> {'t': <<MatchMapping 0,1..0,6>._all[:1]>, 'u': <<MatchMapping 0,8..0,19>._all[1:2]>}>", str(pat.match(FST('[{**b}, {1: a, **b}]', pattern))))

        pat = MMatchSequence([M(..., t=MMatchMapping([M(k=...)], [M(v=...)])), MMatchMapping(_all=[MTAG('t')])])
        self.assertEqual("<FSTMatch <MatchSequence ROOT 0,0..0,16> {'t': MMatchMapping(keys=[M(k=...)], patterns=[M(v=...)]), 'k': <Constant 0,10..0,11>, 'v': <MatchAs 0,13..0,14>}>", str(pat.match(FST('[filler, {1: a}]', pattern))))

        # self.assertIsNone(MMatchMapping().match(FST('{1: a, 2: b}', pattern)._all))  # this is a truly unrealistic test, but hey, coverage

    def test_match_virtual_field_one_arguments(self):
        self.assertTrue(Marguments().match(FST('a, b', arguments)._all))

        # string to multinode

        self.assertTrue(Marguments(_all=['a: int = 1']).match(FST('a: int = 1', arguments)))
        self.assertTrue(Marguments(_all=['a: int = 1']).match(FST('a: int = 1 ,', arguments)))
        self.assertFalse(Marguments(_all=['a: int = 1']).match(FST('a:int=1', arguments)))
        self.assertFalse(Marguments(_all=['a: int = 1']).match(FST('a  :  int  =  1', arguments)))

        # regex to multinode

        self.assertTrue(Marguments(_all=[re.compile(r'a\s*:\s*int\s*=\s*1')]).match(FST('a: int = 1', arguments)))
        self.assertTrue(Marguments(_all=[re.compile(r'a\s*:\s*int\s*=\s*1')]).match(FST('a:int=1', arguments)))
        self.assertTrue(Marguments(_all=[re.compile(r'a\s*:\s*int\s*=\s*1')]).match(FST('a :  int  =  1', arguments)))
        self.assertFalse(Marguments(_all=[re.compile(r'a\s*:\s*int\s*=\s*1')]).match(FST('a: int = 2', arguments)))

        # MRE to multinode

        self.assertTrue(Marguments(_all=[MRE(r'a\s*:\s*int\s*=\s*1')]).match(FST('a: int = 1', arguments)))
        self.assertTrue(Marguments(_all=[MRE(r'a\s*:\s*int\s*=\s*1')]).match(FST('a:int=1', arguments)))
        self.assertTrue(Marguments(_all=[MRE(r'a\s*:\s*int\s*=\s*1')]).match(FST('a :  int  =  1', arguments)))
        self.assertFalse(Marguments(_all=[MRE(r'a\s*:\s*int\s*=\s*1')]).match(FST('a: int = 2', arguments)))

        # Invalid concrete pattern to multinode arguments which will not use the single argument matching

        f = FST('a=1', arguments)
        self.assertFalse(Marguments(_all=[arguments([], [], ..., [], ['1'], ..., ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, [], ['1'], None, ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[Marguments(_all=['a'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(['a', 'a'], [], None, [], [], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], ['a', 'a'], None, [], [], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, ['a', 'a'], [], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(['a'], [], 'a', [], [], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(['a'], [], None, [], [], 'a', [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(['a'], [], None, [], ['1'], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], ['a'], None, [], ['1'], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, ['a'], [], None, ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], 'a', [], ['1'], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], 'a', [], [], None, ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, [], ['1'], 'a', [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, [], [], 'a', ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ..., ..., ..., ['1'], ..., ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ..., None, ..., ['1'], None, ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(['a', 'a'], ..., None, ..., ..., None, ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ['a', 'a'], None, ..., ..., None, ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ..., None, ['a', 'a'], ..., None, ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(['a'], ..., 'a', ..., ..., None, ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(['a'], ..., None, ..., ..., 'a', ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(['a'], ..., None, ..., ['1'], None, ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ['a'], None, ..., ['1'], None, ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ..., None, ['a'], ..., None, ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ..., 'a', ..., ['1'], None, ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ..., 'a', ..., ..., None, ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ..., None, ..., ['1'], 'a', ...)]).match(f))
        self.assertFalse(Marguments(_all=[arguments(..., ..., None, ..., ..., 'a', ['1'])]).match(f))
        self.assertFalse(Marguments(_all=[arguments('a', [], None, [], [], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], 'a', None, [], [], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, 'a', [], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, [], '1', None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, [], [], None, '1')]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, [], ['1', '1'], None, [])]).match(f))
        self.assertFalse(Marguments(_all=[arguments([], [], None, [], [], None, ['1', '1'])]).match(f))

        # Concrete pattern to multinode arguments (without defaults), also _strict

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(vararg=Marg(MRE('a|b'), MRE('int|str')))), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,7> {'t': <<arguments ROOT 0,0..0,7>._all[:1]>}>", str(pat.match(FST('*a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[:1]>}>", str(pat.match(FST('*a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,13> {'t': <<arguments ROOT 0,0..0,13>._all[1:2]>}>", str(pat.match(FST('x, *a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,10> {'t': <<arguments ROOT 0,0..0,10>._all[1:2]>}>", str(pat.match(FST('x, *a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,13> {'t': <<arguments ROOT 0,0..0,13>._all[1:2]>}>", str(pat.match(FST('x, *b: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,13> {'t': <<arguments ROOT 0,0..0,13>._all[1:2]>}>", str(pat.match(FST('x, *a: str, y', arguments))))
        self.assertFalse(pat.match(FST('x, *c: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *a: float, y', arguments)))
        self.assertFalse(pat.match(FST('**a: int', arguments)))
        pat = Marguments(_all=[MQSTAR, M(t=Marguments(vararg=Marg(MRE('a|b'), MRE('int|str')), _strict=None)), MQSTAR])
        self.assertFalse(pat.match(FST('x, *c: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *a: float, y', arguments)))
        self.assertFalse(pat.match(FST('**a: int', arguments)))

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(kwarg=Marg(MRE('a|b'), MRE('int|str')))), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,8> {'t': <<arguments ROOT 0,0..0,8>._all[:1]>}>", str(pat.match(FST('**a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,11> {'t': <<arguments ROOT 0,0..0,11>._all[1:2]>}>", str(pat.match(FST('x, **a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,11> {'t': <<arguments ROOT 0,0..0,11>._all[1:2]>}>", str(pat.match(FST('x, **b: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,11> {'t': <<arguments ROOT 0,0..0,11>._all[1:2]>}>", str(pat.match(FST('x, **a: str', arguments))))
        self.assertFalse(pat.match(FST('x, **c: int', arguments)))
        self.assertFalse(pat.match(FST('x, **a: float', arguments)))
        self.assertFalse(pat.match(FST('*a: int', arguments)))
        pat = Marguments(_all=[MQSTAR, M(t=Marguments(kwarg=Marg(MRE('a|b'), MRE('int|str')), _strict=None)), MQSTAR])
        self.assertFalse(pat.match(FST('x, **c: int', arguments)))
        self.assertFalse(pat.match(FST('x, **a: float', arguments)))
        self.assertFalse(pat.match(FST('*a: int', arguments)))

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(kwonlyargs=[Marg(MRE('a|b'), MRE('int|str'))])), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('*, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[:1]>}>", str(pat.match(FST('*, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, b: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, a: str, y', arguments))))
        self.assertFalse(pat.match(FST('x, *, c: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a: float, y', arguments)))
        self.assertFalse(pat.match(FST('*a: int', arguments)))
        self.assertFalse(pat.match(FST('**a: int', arguments)))
        self.assertFalse(pat.match(FST('a: int', arguments)))
        self.assertFalse(pat.match(FST('a: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: int', arguments)))
        self.assertFalse(pat.match(FST('x, b: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: str, y', arguments)))
        self.assertFalse(pat.match(FST('a: int, /', arguments)))
        self.assertFalse(pat.match(FST('a: int, /, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: int, /, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: int, /', arguments)))
        self.assertFalse(pat.match(FST('x, b: int, /, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: str, /, y', arguments)))
        pat = Marguments(_all=[MQSTAR, M(t=Marguments(kwonlyargs=[Marg(MRE('a|b'), MRE('int|str'))], _strict=None)), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[1:2]>}>", str(pat.match(FST('x, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, b: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: str, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('a: int, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[:1]>}>", str(pat.match(FST('a: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, a: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: int, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, b: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, a: str, /, y', arguments))))

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(posonlyargs=[Marg(MRE('a|b'), MRE('int|str'))])), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('a: int, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[:1]>}>", str(pat.match(FST('a: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, a: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: int, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, b: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, a: str, /, y', arguments))))
        self.assertFalse(pat.match(FST('x, c: int, /, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: float, /, y', arguments)))
        self.assertFalse(pat.match(FST('*a: int', arguments)))
        self.assertFalse(pat.match(FST('**a: int', arguments)))
        self.assertFalse(pat.match(FST('a: int', arguments)))
        self.assertFalse(pat.match(FST('a: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: int', arguments)))
        self.assertFalse(pat.match(FST('x, b: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: str, y', arguments)))
        self.assertFalse(pat.match(FST('*, a: int', arguments)))
        self.assertFalse(pat.match(FST('*, a: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a: int', arguments)))
        self.assertFalse(pat.match(FST('x, *, b: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a: str, y', arguments)))
        pat = Marguments(_all=[MQSTAR, M(t=Marguments(posonlyargs=[Marg(MRE('a|b'), MRE('int|str'))], _strict=None)), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[1:2]>}>", str(pat.match(FST('x, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, b: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: str, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('*, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[:1]>}>", str(pat.match(FST('*, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, b: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, a: str, y', arguments))))

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(args=[Marg(MRE('a|b'), MRE('int|str'))])), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[1:2]>}>", str(pat.match(FST('x, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, b: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: str, y', arguments))))
        self.assertFalse(pat.match(FST('x, c: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: float, y', arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('*, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[:1]>}>", str(pat.match(FST('*, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, b: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, *, a: str, y', arguments))))
        self.assertFalse(pat.match(FST('x, *, c: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a: float, y', arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('a: int, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[:1]>}>", str(pat.match(FST('a: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, a: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: int, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, b: int, /, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,15> {'t': <<arguments ROOT 0,0..0,15>._all[1:2]>}>", str(pat.match(FST('x, a: str, /, y', arguments))))
        self.assertFalse(pat.match(FST('x, c: int, /, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: float, /, y', arguments)))
        self.assertFalse(pat.match(FST('*a: int', arguments)))
        self.assertFalse(pat.match(FST('**a: int', arguments)))
        pat = Marguments(_all=[MQSTAR, M(t=Marguments(args=[Marg(MRE('a|b'), MRE('int|str'))], _strict=True)), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[1:2]>}>", str(pat.match(FST('x, a: int', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, b: int, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, a: str, y', arguments))))
        self.assertFalse(pat.match(FST('*, a: int', arguments)))
        self.assertFalse(pat.match(FST('*, a: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a: int', arguments)))
        self.assertFalse(pat.match(FST('x, *, b: int, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a: str, y', arguments)))
        self.assertFalse(pat.match(FST('a: int, /', arguments)))
        self.assertFalse(pat.match(FST('a: int, /, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: int, /, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: int, /', arguments)))
        self.assertFalse(pat.match(FST('x, b: int, /, y', arguments)))
        self.assertFalse(pat.match(FST('x, a: str, /, y', arguments)))

        # Concrete pattern to multinode arguments (with defaults)

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(kwonlyargs=[Marg(MRE('a|b'))], kw_defaults=[MRE('1|2')])), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('*, a=1', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('*, a=1, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, a=1, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[1:2]>}>", str(pat.match(FST('x, *, a=1', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, b=1, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, a=2, y', arguments))))
        self.assertFalse(pat.match(FST('x, *, c=1, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a=3, y', arguments)))
        self.assertFalse(pat.match(FST('a=1', arguments)))
        self.assertFalse(pat.match(FST('a=1, /', arguments)))

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(posonlyargs=[Marg(MRE('a|b'))], defaults=[MRE('1|2')])), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('a=1, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,11> {'t': <<arguments ROOT 0,0..0,11>._all[:1]>}>", str(pat.match(FST('a=1, /, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,14> {'t': <<arguments ROOT 0,0..0,14>._all[1:2]>}>", str(pat.match(FST('x, a=1, /, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[1:2]>}>", str(pat.match(FST('x, a=1, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,14> {'t': <<arguments ROOT 0,0..0,14>._all[1:2]>}>", str(pat.match(FST('x, b=1, /, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,14> {'t': <<arguments ROOT 0,0..0,14>._all[1:2]>}>", str(pat.match(FST('x, a=2, /, y=0', arguments))))
        self.assertFalse(pat.match(FST('x, c=1, /, y=0', arguments)))
        self.assertFalse(pat.match(FST('x, a=3, /, y=0', arguments)))
        self.assertFalse(pat.match(FST('a=1', arguments)))
        self.assertFalse(pat.match(FST('*, a=1', arguments)))

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(args=[Marg(MRE('a|b'))], defaults=[MRE('1|2')])), MQSTAR])
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,3> {'t': <<arguments ROOT 0,0..0,3>._all[:1]>}>", str(pat.match(FST('a=1', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,8> {'t': <<arguments ROOT 0,0..0,8>._all[:1]>}>", str(pat.match(FST('a=1, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,11> {'t': <<arguments ROOT 0,0..0,11>._all[1:2]>}>", str(pat.match(FST('x, a=1, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[1:2]>}>", str(pat.match(FST('x, a=1', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,11> {'t': <<arguments ROOT 0,0..0,11>._all[1:2]>}>", str(pat.match(FST('x, b=1, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,11> {'t': <<arguments ROOT 0,0..0,11>._all[1:2]>}>", str(pat.match(FST('x, a=2, y=0', arguments))))
        self.assertFalse(pat.match(FST('x, c=1, y=0', arguments)))
        self.assertFalse(pat.match(FST('x, a=3, y=0', arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('*, a=1', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[:1]>}>", str(pat.match(FST('*, a=1, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, a=1, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[1:2]>}>", str(pat.match(FST('x, *, a=1', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, b=1, y', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,12> {'t': <<arguments ROOT 0,0..0,12>._all[1:2]>}>", str(pat.match(FST('x, *, a=2, y', arguments))))
        self.assertFalse(pat.match(FST('x, *, c=1, y', arguments)))
        self.assertFalse(pat.match(FST('x, *, a=3, y', arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('a=1, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,11> {'t': <<arguments ROOT 0,0..0,11>._all[:1]>}>", str(pat.match(FST('a=1, /, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,14> {'t': <<arguments ROOT 0,0..0,14>._all[1:2]>}>", str(pat.match(FST('x, a=1, /, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,9> {'t': <<arguments ROOT 0,0..0,9>._all[1:2]>}>", str(pat.match(FST('x, a=1, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,14> {'t': <<arguments ROOT 0,0..0,14>._all[1:2]>}>", str(pat.match(FST('x, b=1, /, y=0', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,14> {'t': <<arguments ROOT 0,0..0,14>._all[1:2]>}>", str(pat.match(FST('x, a=2, /, y=0', arguments))))
        self.assertFalse(pat.match(FST('x, c=1, /, y=0', arguments)))
        self.assertFalse(pat.match(FST('x, a=3, /, y=0', arguments)))

        # Concrete pattern to multinode arguments (with different default types - concrete, wildcard or not present)

        farg_1 = FST('x=1', arguments)
        farg_2 = FST('x=2', arguments)
        farg_none = FST('x', arguments)
        fkw_1 = FST('*, x=1', arguments)
        fkw_2 = FST('*, x=2', arguments)
        fkw_none = FST('*, x', arguments)
        fpos_1 = FST('x=1, /', arguments)
        fpos_2 = FST('x=2, /', arguments)
        fpos_none = FST('x, /', arguments)

        pat_1 = Marguments(_all=[MQSTAR, M(t=Marguments(args=[...], defaults=['1'])), MQSTAR])  # we specify the args to force use of the defaults field
        pat_anyout = Marguments(_all=[MQSTAR, M(t=Marguments(args=[...], defaults=...)), MQSTAR])
        pat_anyin = Marguments(_all=[MQSTAR, M(t=Marguments(args=[...], defaults=[...])), MQSTAR])
        pat_none = Marguments(_all=[MQSTAR, M(t=Marguments(args=[...], defaults=[])), MQSTAR])

        self.assertTrue(pat_1.match(farg_1))
        self.assertTrue(pat_anyout.match(farg_1))
        self.assertTrue(pat_anyin.match(farg_1))
        self.assertFalse(pat_none.match(farg_1))
        self.assertFalse(pat_1.match(farg_2))
        self.assertTrue(pat_anyout.match(farg_2))
        self.assertTrue(pat_anyin.match(farg_2))
        self.assertFalse(pat_none.match(farg_2))
        self.assertFalse(pat_1.match(farg_none))
        self.assertTrue(pat_anyout.match(farg_none))
        self.assertTrue(pat_anyin.match(farg_none))
        self.assertTrue(pat_none.match(farg_none))
        self.assertTrue(pat_1.match(fkw_1))
        self.assertTrue(pat_anyout.match(fkw_1))
        self.assertTrue(pat_anyin.match(fkw_1))
        self.assertFalse(pat_none.match(fkw_1))
        self.assertFalse(pat_1.match(fkw_2))
        self.assertTrue(pat_anyout.match(fkw_2))
        self.assertTrue(pat_anyin.match(fkw_2))
        self.assertFalse(pat_none.match(fkw_2))
        self.assertFalse(pat_1.match(fkw_none))
        self.assertTrue(pat_anyout.match(fkw_none))
        self.assertTrue(pat_anyin.match(fkw_none))
        self.assertTrue(pat_none.match(fkw_none))
        self.assertTrue(pat_1.match(fpos_1))
        self.assertTrue(pat_anyout.match(fpos_1))
        self.assertTrue(pat_anyin.match(fpos_1))
        self.assertFalse(pat_none.match(fpos_1))
        self.assertFalse(pat_1.match(fpos_2))
        self.assertTrue(pat_anyout.match(fpos_2))
        self.assertTrue(pat_anyin.match(fpos_2))
        self.assertFalse(pat_none.match(fpos_2))
        self.assertFalse(pat_1.match(fpos_none))
        self.assertTrue(pat_anyout.match(fpos_none))
        self.assertTrue(pat_anyin.match(fpos_none))
        self.assertTrue(pat_none.match(fpos_none))

        pat_1 = Marguments(_all=[MQSTAR, M(t=Marguments(posonlyargs=[...], defaults=['1'])), MQSTAR])  # we specify the posonlyargs to force use of the defaults field
        pat_anyout = Marguments(_all=[MQSTAR, M(t=Marguments(posonlyargs=[...], defaults=...)), MQSTAR])
        pat_anyin = Marguments(_all=[MQSTAR, M(t=Marguments(posonlyargs=[...], defaults=[...])), MQSTAR])
        pat_none = Marguments(_all=[MQSTAR, M(t=Marguments(posonlyargs=[...], defaults=[])), MQSTAR])

        self.assertTrue(pat_1.match(farg_1))
        self.assertTrue(pat_anyout.match(farg_1))
        self.assertTrue(pat_anyin.match(farg_1))
        self.assertFalse(pat_none.match(farg_1))
        self.assertFalse(pat_1.match(farg_2))
        self.assertTrue(pat_anyout.match(farg_2))
        self.assertTrue(pat_anyin.match(farg_2))
        self.assertFalse(pat_none.match(farg_2))
        self.assertFalse(pat_1.match(farg_none))
        self.assertTrue(pat_anyout.match(farg_none))
        self.assertTrue(pat_anyin.match(farg_none))
        self.assertTrue(pat_none.match(farg_none))
        self.assertTrue(pat_1.match(fkw_1))
        self.assertTrue(pat_anyout.match(fkw_1))
        self.assertTrue(pat_anyin.match(fkw_1))
        self.assertFalse(pat_none.match(fkw_1))
        self.assertFalse(pat_1.match(fkw_2))
        self.assertTrue(pat_anyout.match(fkw_2))
        self.assertTrue(pat_anyin.match(fkw_2))
        self.assertFalse(pat_none.match(fkw_2))
        self.assertFalse(pat_1.match(fkw_none))
        self.assertTrue(pat_anyout.match(fkw_none))
        self.assertTrue(pat_anyin.match(fkw_none))
        self.assertTrue(pat_none.match(fkw_none))
        self.assertTrue(pat_1.match(fpos_1))
        self.assertTrue(pat_anyout.match(fpos_1))
        self.assertTrue(pat_anyin.match(fpos_1))
        self.assertFalse(pat_none.match(fpos_1))
        self.assertFalse(pat_1.match(fpos_2))
        self.assertTrue(pat_anyout.match(fpos_2))
        self.assertTrue(pat_anyin.match(fpos_2))
        self.assertFalse(pat_none.match(fpos_2))
        self.assertFalse(pat_1.match(fpos_none))
        self.assertTrue(pat_anyout.match(fpos_none))
        self.assertTrue(pat_anyin.match(fpos_none))
        self.assertTrue(pat_none.match(fpos_none))

        pat_1 = Marguments(_all=[MQSTAR, M(t=Marguments(kwonlyargs=[...], kw_defaults=['1'])), MQSTAR])  # we specify the kwonlyargs to force use of the kw_defaults field
        pat_anyout = Marguments(_all=[MQSTAR, M(t=Marguments(kwonlyargs=[...], kw_defaults=...)), MQSTAR])
        pat_anyin = Marguments(_all=[MQSTAR, M(t=Marguments(kwonlyargs=[...], kw_defaults=[...])), MQSTAR])
        pat_none = Marguments(_all=[MQSTAR, M(t=Marguments(kwonlyargs=[...], kw_defaults=[])), MQSTAR])

        self.assertFalse(pat_1.match(farg_1))
        self.assertTrue(pat_anyout.match(farg_1))
        self.assertTrue(pat_anyin.match(farg_1))
        self.assertFalse(pat_none.match(farg_1))
        self.assertFalse(pat_1.match(farg_2))
        self.assertTrue(pat_anyout.match(farg_2))
        self.assertTrue(pat_anyin.match(farg_2))
        self.assertFalse(pat_none.match(farg_2))
        self.assertFalse(pat_1.match(farg_none))
        self.assertTrue(pat_anyout.match(farg_none))
        self.assertTrue(pat_anyin.match(farg_none))
        self.assertTrue(pat_none.match(farg_none))
        self.assertTrue(pat_1.match(fkw_1))
        self.assertTrue(pat_anyout.match(fkw_1))
        self.assertTrue(pat_anyin.match(fkw_1))
        self.assertFalse(pat_none.match(fkw_1))
        self.assertFalse(pat_1.match(fkw_2))
        self.assertTrue(pat_anyout.match(fkw_2))
        self.assertTrue(pat_anyin.match(fkw_2))
        self.assertFalse(pat_none.match(fkw_2))
        self.assertFalse(pat_1.match(fkw_none))
        self.assertTrue(pat_anyout.match(fkw_none))
        self.assertTrue(pat_anyin.match(fkw_none))
        self.assertTrue(pat_none.match(fkw_none))
        self.assertFalse(pat_1.match(fpos_1))
        self.assertTrue(pat_anyout.match(fpos_1))
        self.assertTrue(pat_anyin.match(fpos_1))
        self.assertFalse(pat_none.match(fpos_1))
        self.assertFalse(pat_1.match(fpos_2))
        self.assertTrue(pat_anyout.match(fpos_2))
        self.assertTrue(pat_anyin.match(fpos_2))
        self.assertFalse(pat_none.match(fpos_2))
        self.assertFalse(pat_1.match(fpos_none))
        self.assertTrue(pat_anyout.match(fpos_none))
        self.assertTrue(pat_anyin.match(fpos_none))
        self.assertTrue(pat_none.match(fpos_none))

        # Concrete pattern to multinode arguments (just defaults)

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(defaults=['x'])), MQSTAR])  # this should match a default 'a' anywhere regardless of arg
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('a=x, /', arguments))))
        self.assertFalse(pat.match(FST('a=y, /', arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,3> {'t': <<arguments ROOT 0,0..0,3>._all[:1]>}>", str(pat.match(FST('a=x', arguments))))
        self.assertFalse(pat.match(FST('a=y', arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('*, a=x', arguments))))
        self.assertFalse(pat.match(FST('*, a=y', arguments)))
        pat = Marguments(_all=[MQSTAR, M(t=Marguments(defaults=['x'], _strict=True)), MQSTAR])  # this should match a default 'a' anywhere regardless of arg
        self.assertFalse(pat.match(FST('*, a=x', arguments)))

        pat = Marguments(_all=[MQSTAR, M(t=Marguments(kw_defaults=['x'])), MQSTAR])  # this should only match a kw_default 'a'
        self.assertFalse(pat.match(FST('a=x, /', arguments)))
        self.assertFalse(pat.match(FST('a=y, /', arguments)))
        self.assertFalse(pat.match(FST('a=x', arguments)))
        self.assertFalse(pat.match(FST('a=y', arguments)))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('*, a=x', arguments))))
        self.assertFalse(pat.match(FST('*, a=y', arguments)))
        pat = Marguments(_all=[MQSTAR, M(t=Marguments(kw_defaults=['x'], _strict=None)), MQSTAR])  # this should only match a kw_default 'a'
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,6> {'t': <<arguments ROOT 0,0..0,6>._all[:1]>}>", str(pat.match(FST('a=x, /', arguments))))
        self.assertEqual("<FSTMatch <arguments ROOT 0,0..0,3> {'t': <<arguments ROOT 0,0..0,3>._all[:1]>}>", str(pat.match(FST('a=x', arguments))))

        # previously matched args FSTView to target (any type to any type, pos/arg/kw)

        pat = MAST(body=[
            MFunctionDef(args=Marguments(_all=[M(t=Marguments(args=[...]))])),
            MFunctionDef(args=M(u=Marguments(_all=[MTAG('t')]))),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,23> {'t': <<arguments 0,6..0,16>._all[:1]>, 'u': <arguments 1,6..1,16>}>", str(pat.match(FST('def f(a: int = 1): pass\ndef g(a: int = 1): pass'))))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,26> {'t': <<arguments 0,6..0,16>._all[:1]>, 'u': <arguments 1,6..1,19>}>", str(pat.match(FST('def f(a: int = 1): pass\ndef g(*, a: int = 1): pass'))))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,26> {'t': <<arguments 0,6..0,16>._all[:1]>, 'u': <arguments 1,6..1,19>}>", str(pat.match(FST('def f(a: int = 1): pass\ndef g(a: int = 1, /): pass'))))
        self.assertFalse(pat.match(FST('def f(a: int = 1): pass\ndef g(a: int = 2): pass')))
        self.assertFalse(pat.match(FST('def f(a: int = 1): pass\ndef g(b: int = 1): pass')))
        self.assertFalse(pat.match(FST('def f(a: int = 1): pass\ndef g(a: int): pass')))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,19> {'t': <<arguments 0,6..0,12>._all[:1]>, 'u': <arguments 1,6..1,12>}>", str(pat.match(FST('def f(a: int): pass\ndef g(a: int): pass'))))
        self.assertFalse(pat.match(FST('def f(a: int): pass\ndef g(a: int = 1): pass')))

        pat = MAST(body=[
            MFunctionDef(args=Marguments(_all=[M(t=Marguments(kwonlyargs=[...]))])),
            MFunctionDef(args=M(u=Marguments(_all=[MTAG('t')]))),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,23> {'t': <<arguments 0,6..0,19>._all[:1]>, 'u': <arguments 1,6..1,16>}>", str(pat.match(FST('def f(*, a: int = 1): pass\ndef g(a: int = 1): pass'))))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,26> {'t': <<arguments 0,6..0,19>._all[:1]>, 'u': <arguments 1,6..1,19>}>", str(pat.match(FST('def f(*, a: int = 1): pass\ndef g(*, a: int = 1): pass'))))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,26> {'t': <<arguments 0,6..0,19>._all[:1]>, 'u': <arguments 1,6..1,19>}>", str(pat.match(FST('def f(*, a: int = 1): pass\ndef g(a: int = 1, /): pass'))))
        self.assertFalse(pat.match(FST('def f(*, a: int = 1): pass\ndef g(a: int = 2): pass')))
        self.assertFalse(pat.match(FST('def f(*, a: int = 1): pass\ndef g(b: int = 1): pass')))
        self.assertFalse(pat.match(FST('def f(*, a: int = 1): pass\ndef g(*, a: int): pass')))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,22> {'t': <<arguments 0,6..0,15>._all[:1]>, 'u': <arguments 1,6..1,15>}>", str(pat.match(FST('def f(*, a: int): pass\ndef g(*, a: int): pass'))))
        self.assertFalse(pat.match(FST('def f(*, a: int): pass\ndef g(*, a: int = 1): pass')))

        pat = MAST(body=[
            MFunctionDef(args=Marguments(_all=[M(t=Marguments(posonlyargs=[...]))])),
            MFunctionDef(args=M(u=Marguments(_all=[MTAG('t')]))),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,23> {'t': <<arguments 0,6..0,19>._all[:1]>, 'u': <arguments 1,6..1,16>}>", str(pat.match(FST('def f(a: int = 1, /): pass\ndef g(a: int = 1): pass'))))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,26> {'t': <<arguments 0,6..0,19>._all[:1]>, 'u': <arguments 1,6..1,19>}>", str(pat.match(FST('def f(a: int = 1, /): pass\ndef g(*, a: int = 1): pass'))))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,26> {'t': <<arguments 0,6..0,19>._all[:1]>, 'u': <arguments 1,6..1,19>}>", str(pat.match(FST('def f(a: int = 1, /): pass\ndef g(a: int = 1, /): pass'))))
        self.assertFalse(pat.match(FST('def f(a: int = 1, /): pass\ndef g(a: int = 2): pass')))
        self.assertFalse(pat.match(FST('def f(a: int = 1, /): pass\ndef g(b: int = 1): pass')))
        self.assertFalse(pat.match(FST('def f(a: int = 1, /): pass\ndef g(a: int, /): pass')))
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,22> {'t': <<arguments 0,6..0,15>._all[:1]>, 'u': <arguments 1,6..1,15>}>", str(pat.match(FST('def f(a: int, /): pass\ndef g(a: int, /): pass'))))
        self.assertFalse(pat.match(FST('def f(a: int, /): pass\ndef g(a: int = 1, /): pass')))

        # match tags present in pattern for FSTView

        pat = MAST(body=[
            MFunctionDef(args=M(Marguments, t=Marguments(defaults=[M(d=...)]))),
            MFunctionDef(args=M(u=Marguments(_all=[MTAG('t')]))),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,16> {'t': Marguments(defaults=[M(d=...)]), 'd': <Constant 1,8..1,9>, 'u': <arguments 1,6..1,9>}>", str(pat.match(FST('def f(): pass\ndef g(a=1): pass'))))

        pat = MAST(body=[
            MFunctionDef(args=M(Marguments, t=Marguments(args=[M(a=...)], defaults=[M(d=...)]))),
            MFunctionDef(args=M(u=Marguments(_all=[MTAG('t')]))),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,16> {'t': Marguments(args=[M(a=...)], defaults=[M(d=...)]), 'a': <arg 1,6..1,7>, 'd': <Constant 1,8..1,9>, 'u': <arguments 1,6..1,9>}>", str(pat.match(FST('def f(): pass\ndef g(a=1): pass'))))

        # make sure matched individual args are set to match every other type of arg (since they were matched we assume we want them to match other stuff)

        f = FST('''
def f(a: int = 1, /): pass
def g(a: int = 1, /, a: int = 1, *, a: int = 1): pass
        '''.strip())
        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=Marguments(_all=[MQPLUS(MTAG('t'))])),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,53> {'t': <<arguments 0,6..0,19>._all>}>", str(pat.match(f)))

        f = FST('''
def f(*, a: int = 1): pass
def g(a: int = 1, /, a: int = 1, *, a: int = 1): pass
        '''.strip())
        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=Marguments(_all=[MQPLUS(MTAG('t'))])),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,53> {'t': <<arguments 0,6..0,19>._all>}>", str(pat.match(f)))

        f = FST('''
def f(a: int = 1): pass
def g(a: int = 1, /, a: int = 1, *, a: int = 1): pass
        '''.strip())
        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=Marguments(_all=[MQPLUS(MTAG('t'))])),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,53> {'t': <<arguments 0,6..0,16>._all>}>", str(pat.match(f)))

        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=M(u=Marguments(_all=[MQPLUS(MTAG('t'))]))),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,53> {'t': <<arguments 0,6..0,16>._all>, 'u': <arguments 1,6..1,46>}>", str(pat.match(f)))

        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=Marguments(_all=M(u=[MQPLUS(MTAG('t'))]))),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,53> {'t': <<arguments 0,6..0,16>._all>, 'u': <<arguments 1,6..1,46>._all>}>", str(pat.match(f)))

        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=Marguments(_all=[MQPLUS(u=MTAG('t'))])),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,53> {'t': <<arguments 0,6..0,16>._all>, 'u': [<FSTMatch <<arguments 1,6..1,46>._all[:1]>>, <FSTMatch <<arguments 1,6..1,46>._all[1:2]>>, <FSTMatch <<arguments 1,6..1,46>._all[2:3]>>]}>", str(pat.match(f)))

        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=Marguments(_all=[MQPLUS(M(u=MTAG('t')))])),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,53> {'t': <<arguments 0,6..0,16>._all>, 'u': <<arguments 1,6..1,46>._all[2:3]>}>", str(pat.match(f)))

        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=Marguments(_all=[MQPLUS(MTAG(u='t'))])),
        ])
        self.assertEqual("<FSTMatch <Module ROOT 0,0..1,53> {'t': <<arguments 0,6..0,16>._all>, 'u': <<arguments 1,6..1,46>._all[2:3]>}>", str(pat.match(f)))

        # make sure matched args do NOT match where they shouldn't

        pat = MModule(body=[
            MFunctionDef(args=Marguments(_all=M(t=...))),
            MFunctionDef(args=Marguments(_all=[MQPLUS(MTAG('t'))])),
        ])

        f = FST('''
def f(a: int = 1): pass
def g(a: int = 1, /, a: int = 1, *, a: int): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(a: int = 1, /, a: int = 1, *, a: int = 2): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(a: int = 1, /, a: int = 1, *, a = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(a: int = 1, /, a: int = 1, *, b: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))

        f = FST('''
def f(a: int = 1): pass
def g(a: int, /, a: int, *, a: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(a: int = 1, /, a: int = 2, *, a: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(a: int = 1, /, a = 1, *, a: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(a: int = 1, /, b: int = 1, *, a: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))

        f = FST('''
def f(a: int = 1): pass
def g(a: int, /, a: int = 1, *, a: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(a: int = 2, /, a: int = 1, *, a: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(a = 1, /, a: int = 1, *, a: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))
        f = FST('''
def f(a: int = 1): pass
def g(b: int = 1, /, a: int = 1, *, a: int = 1): pass
        '''.strip())
        self.assertFalse(pat.match(f))

        # quantifiers in otherwise valid 1 vs. 1 match fall back to normal match

        self.assertFalse(Marguments(_all=[Marguments(args=[MQN(..., 0)])]).match(FST('a: int = 1', arguments)))
        self.assertTrue(Marguments(_all=[Marguments(args=[MQN(..., 1)])]).match(FST('a: int = 1', arguments)))
        self.assertFalse(Marguments(_all=[Marguments(args=[MQN(..., 2)])]).match(FST('a: int = 1', arguments)))

        self.assertFalse(Marguments(_all=[Marguments(defaults=[MQN(..., 0)])]).match(FST('a: int = 1', arguments)))
        self.assertTrue(Marguments(_all=[Marguments(defaults=[MQN(..., 1)])]).match(FST('a: int = 1', arguments)))
        self.assertFalse(Marguments(_all=[Marguments(defaults=[MQN(..., 2)])]).match(FST('a: int = 1', arguments)))

        # verify that normal argument comparisons are always strict

        self.assertFalse(Marguments(args=['a'], _strict=None).match(FST('a, /', arguments)))
        self.assertTrue(Marguments(args=['a'], _strict=None).match(FST('a', arguments)))
        self.assertFalse(Marguments(args=['a'], _strict=None).match(FST('*, a', arguments)))

        self.assertTrue(Marguments(posonlyargs=['a'], _strict=None).match(FST('a, /', arguments)))
        self.assertFalse(Marguments(posonlyargs=['a'], _strict=None).match(FST('a', arguments)))
        self.assertFalse(Marguments(posonlyargs=['a'], _strict=None).match(FST('*, a', arguments)))

        self.assertFalse(Marguments(kwonlyargs=['a'], _strict=None).match(FST('a, /', arguments)))
        self.assertFalse(Marguments(kwonlyargs=['a'], _strict=None).match(FST('a', arguments)))
        self.assertTrue(Marguments(kwonlyargs=['a'], _strict=None).match(FST('*, a', arguments)))

        # verify that _strict works for AST arguments

        pat = Marguments(_all=[p := arguments([], ['a'], None, [], [], None, [])])
        p._strict = True
        self.assertFalse(pat.match(FST('a, /', arguments)))
        self.assertTrue(pat.match(FST('a', arguments)))
        self.assertFalse(pat.match(FST('*, a', arguments)))
        p._strict = False
        self.assertTrue(pat.match(FST('a, /', arguments)))
        self.assertTrue(pat.match(FST('a', arguments)))
        self.assertTrue(pat.match(FST('*, a', arguments)))
        p._strict = None
        self.assertTrue(pat.match(FST('a, /', arguments)))
        self.assertTrue(pat.match(FST('a', arguments)))
        self.assertTrue(pat.match(FST('*, a', arguments)))

        pat = Marguments(_all=[p := arguments(['a'], [], None, [], [], None, [])])
        p._strict = True
        self.assertTrue(pat.match(FST('a, /', arguments)))
        self.assertFalse(pat.match(FST('a', arguments)))
        self.assertFalse(pat.match(FST('*, a', arguments)))
        p._strict = False
        self.assertTrue(pat.match(FST('a, /', arguments)))
        self.assertFalse(pat.match(FST('a', arguments)))
        self.assertFalse(pat.match(FST('*, a', arguments)))
        p._strict = None
        self.assertTrue(pat.match(FST('a, /', arguments)))
        self.assertTrue(pat.match(FST('a', arguments)))
        self.assertTrue(pat.match(FST('*, a', arguments)))

        pat = Marguments(_all=[p := arguments([], [], None, ['a'], [None], None, [])])
        p._strict = True
        self.assertFalse(pat.match(FST('a, /', arguments)))
        self.assertFalse(pat.match(FST('a', arguments)))
        self.assertTrue(pat.match(FST('*, a', arguments)))
        p._strict = False
        self.assertFalse(pat.match(FST('a, /', arguments)))
        self.assertFalse(pat.match(FST('a', arguments)))
        self.assertTrue(pat.match(FST('*, a', arguments)))
        p._strict = None
        self.assertTrue(pat.match(FST('a, /', arguments)))
        self.assertTrue(pat.match(FST('a', arguments)))
        self.assertTrue(pat.match(FST('*, a', arguments)))

    def test_match_coverage(self):
        from fst.view import FSTView_dummy

        self.assertEqual('MAST(elts=..., ctx=Store)', repr(MAST(elts=..., ctx=Store)))
        self.assertEqual('<NotSet>', repr(NotSet.__class__()))
        self.assertEqual('M(t=...)', repr(M(t=...)))
        self.assertEqual('M(t=..., st=True)', repr(M(t=..., st=True)))
        self.assertEqual('MOR(Constant, t=MConstant(value=1))', repr(MOR(Constant, t=MConstant(value=1))))
        self.assertEqual('MTYPES((Tuple,))', repr(MTYPES((Tuple,))))
        self.assertEqual('MTYPES((Tuple, List))', repr(MTYPES((Tuple, MList))))
        self.assertEqual('MTYPES((Tuple, List), elts=...)', repr(MTYPES((Tuple, MList), elts=...)))
        self.assertEqual("MRE(re.compile('a'), search=True)", repr(MRE("a", 0, True)))
        self.assertEqual("MTAG('tag')", repr(MTAG('tag')))
        self.assertEqual("MTAG('tag', st='static')", repr(MTAG('tag', st='static')))

        assertRaises(ValueError('MTYPES types can only be AST or MAST'), MTYPES, [1])
        assertRaises(ValueError('MTYPES types can only be AST or MAST'), MTYPES, [str])
        assertRaises(ValueError('MTYPES requires at least one AST type to match'), MTYPES, [])
        assertRaises(ValueError('MRE cannot take flags for already compiled re.Pattern'), MRE, re.compile('a'), re.M)
        assertRaises(ValueError('MCB can never tag the callback return since the callback does not have a tag'), MCB, lambda: False, tag_ret=True)
        assertRaises(ValueError('MQN requires a count value'), MQN, ...)
        assertRaises(ValueError('MQN count must be a non-negative integer'), MQN, ..., None)
        assertRaises(ValueError('MQN count must be a non-negative integer'), MQN, ..., -1)

        f = FST('i = 1')
        f.a.value.f = None
        assertRaises(MatchError('match found an AST node without an FST'), MAssign(value=M(t=Constant)).match, f)
        assertRaises(MatchError('match found an AST node without an FST'), MAssign(value=MNOT(t=Name)).match, f)
        assertRaises(MatchError('match found an AST node without an FST'), MAssign(value=MOR(t=...)).match, f)
        assertRaises(MatchError('match found an AST node without an FST'), MAssign(value=MAND(t=...)).match, f)
        assertRaises(MatchError('match found an AST node without an FST'), MAssign(value=MCB(lambda: False)).match, f)
        assertRaises(MatchError('match found an AST node without an FST'), MAssign(value=MOPT(t=Constant)).match, f)

        f = FST('i = i')
        self.assertEqual("<FSTMatch <Assign ROOT 0,0..0,5> {'t': <Name 0,0..0,1>, 'u': <Name 0,4..0,5>}>", str(MAssign([M(t=...)], value=MTAG(u='t')).match(f)))
        self.assertEqual("<FSTMatch <Assign ROOT 0,0..0,5> {'v': <Name 0,0..0,1>, 't': <Name 0,0..0,1>, 'u': <Name 0,4..0,5>}>", str(MAssign([M(t=M(v=...))], value=MTAG(u='t')).match(f)))
        self.assertEqual("<FSTMatch <Assign ROOT 0,0..0,5> {'t': M(v=...), 'v': <Name 0,4..0,5>, 'u': <Name 0,4..0,5>}>", str(MAssign([M(..., t=M(v=...))], value=MTAG(u='t')).match(f)))
        f.a.value.f = None
        assertRaises(MatchError('match found an AST node without an FST'), MAssign([M(t=...)], value=MTAG(u='t')).match, f)

        # f = FST('[a, a, a]')
        # f.a.elts[1].f = None
        # assertRaises(AttributeError("'NoneType' object has no attribute 'a'"), MList(MQ(t='a')).match, f)

        f = FST('i = 1')
        self.assertFalse(MRE(b'a').match(FST('a')))
        self.assertFalse(MRE(b'a').match(1))
        self.assertFalse(MTAG('notag').match(1))
        self.assertTrue(MBinOp(left=M(..., t=M(..., u=True)), right=MTAG('t')).match(FST('a + a')))
        assertRaises(MatchError('MQ quantifier pattern in invalid location'), MQ(2, 3, 4).match, 1)
        self.assertTrue(MAssign(value=MConstant(MOPT(1))).match(f))
        self.assertFalse(MAssign(value=MConstant(MOPT(2))).match(f))
        self.assertTrue(MAssign(value=(MOPT(M(t=MConstant), st='static'))).match(f))
        self.assertFalse(MList(['a']).match(FST('[]')))
        self.assertTrue(MList([MQSTAR, MQSTAR, MQSTAR]).match(FST('[]')))
        self.assertFalse(MList([MQSTAR, MQ('a', 1, None)]).match(FST('[b, c]')))
        self.assertFalse(MConstant(1).match(FST('a')))
        self.assertTrue(MConstant("a", M(u='u')).match(FST('u"a"')))
        self.assertFalse(MAssign(value=re.compile(b'v')).match(FST('a = v')))
        self.assertFalse(MConstant(re.compile('v')).match(FST('1')))
        self.assertTrue(MList(elts=[MQSTAR([MQPLUS(...)])]).match(FST('[a, b, c]')))
        self.assertFalse(MCompare(_all=[M(z=..., t=FST('a < b')[0:0]), MTAG('t'), MQSTAR]).match(FST('a < b')))
        self.assertTrue(MList(elts=FSTView_dummy(None, None, 0, None)).match(FST('[]')))
        assertRaises(MatchError('matching a Compare pattern against Compare._all the pattern cannot have its own _all field'), MCompare(_all=[...]).match, FST('a < b')._all)
        self.assertFalse(MCompare().match(FST('a < b')._all[0:0]))
        self.assertFalse(MGlobal(names=[stmt]).match(FST('global a')))
        self.assertFalse(MDict(_all=[stmt]).match(FST('{a: b}')))

        class subint(int): pass
        class substr(str): pass
        class sublist(list): pass

        self.assertTrue(MConstant(subint(1)).match(FST('1')))
        self.assertTrue(MConstant(substr('a')).match(FST('"a"')))
        self.assertTrue(MList(elts=sublist([...])).match(FST('[a]')))

        from fst.asttypes import ASTS_LEAF__ALL, ASTS_LEAF_STMT
        self.assertTrue(list(FST('1').search(MTYPES((AST,)))))
        self.assertTrue(list(FST('1').search(MTYPES((stmt, *(ASTS_LEAF__ALL - ASTS_LEAF_STMT))))))

        self.assertEqual("<FSTMatch <Constant ROOT 0,0..0,4> {'v': 'a', 'k': 'u'}>", str(MConstant(M(v='a'), M(k='u')).match(FST('u"a"'))))
        pat = Constant('a', M(k='u'))
        del pat.value
        self.assertEqual("<FSTMatch <Constant ROOT 0,0..0,4> {'k': 'u'}>", str(FST('u"a"').match(pat)))

        self.assertFalse(Marguments(_all=[MRE(b'a')]).match(FST('a', arguments)))

        self.assertTrue(next(FST('a').search(MOR(MCB(lambda t: True))), False))  # MOR._leaf_asts()

        assertRaises(ValueError('MQ requires min and max values'), MQ, ...)  # MQ.__init__()
        assertRaises(ValueError('MQ requires a max value'), MQ, ..., min=1)  # MQ.__init__()
        assertRaises(ValueError('MQ requires a min value'), MQ, ..., max=1)  # MQ.__init__()

    def test_search(self):
        f = FST('[1, a, x.y]')

        self.assertEqual(['a', 'x'], [m.matched.src for m in f.search(Name)])
        self.assertEqual(['x.y'], [m.matched.src for m in f.search(MAttribute)])
        self.assertEqual(['1'], [m.matched.src for m in f.search(Constant(1))])
        self.assertEqual(['[1, a, x.y]'], [m.matched.src for m in f.search(MTYPES((Tuple, List)))])

        # AST type pruning for walk()

        class substr(str): pass
        class subint(int): pass

        self.assertEqual(['[1, a, x.y]', '1', 'a', '', 'x.y', 'x', '', '', ''], [m.matched.src for m in f.search(MOR(Name, MNOT(Name)))])  # the '' are ctx nodes
        self.assertEqual(['[1, a, x.y]', '1', 'a', '', 'x.y', 'x', '', '', ''], [m.matched.src for m in f.search(MNOT(MAND(Name, MNOT(Name))))])
        self.assertEqual([], [m.matched.src for m in f.search(MNOT(MNOT(MAND(Name, MNOT(Name)))))])
        self.assertEqual([], [m.matched.src for m in f.search(MAND(MAND(Name, MNOT(Name))))])
        self.assertEqual(['[1, a, x.y]', '1', 'a', '', 'x.y', 'x', '', '', ''], [m.matched.src for m in f.search(MOR(MNOT(MAND(Name, MNOT(Name)))))])
        self.assertEqual(['1', 'a', 'x'], [m.matched.src for m in f.search(MOR(Name, Constant))])
        self.assertEqual(['a', 'x'], [m.matched.src for m in f.search(MAND(MOR(Name, Constant), MOR(Name, Attribute)))])
        self.assertEqual(['a'], [m.matched.src for m in f.search(MRE('a'))])
        self.assertEqual([], [m.matched.src for m in f.search(1)])
        self.assertEqual(['a'], [m.matched.src for m in f.search(substr('a'))])
        self.assertEqual([], [m.matched.src for m in f.search(subint(1))])

        # indeterminate types

        f = FST('pass')
        lines = []
        lambdaTrue = lambda t: True
        lambdaFalse = lambda t: False
        lambdaTrue.__qualname__ = lambdaFalse.__qualname__ = '<lambda>'

        for pat in [
            'pass',
            'zzz',
            MRE('.*'),
            MRE('zzz'),
            MCB(lambdaTrue),
            MCB(lambdaFalse),
            MTAG('yes'),
            MTAG('no'),
        ]:
            lines.append(str(pat))
            p = MAND(M(..., yes=...), pat)
            lines.append(str(list(f.search(p))))
            lines.append(str(f.match(p)))
            lines.append('')

            pat = MNOT(pat)
            lines.append(str(pat))
            p = MAND(M(..., yes=...), pat)
            lines.append(str(list(f.search(p))))
            lines.append(str(f.match(p)))
            lines.append('')

        self.assertEqual('\n'.join(lines).strip(), """
pass
[<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>]
<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>

MNOT('pass')
[]
None

zzz
[]
None

MNOT('zzz')
[<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>]
<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>

MRE(re.compile('.*'))
[<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>]
<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>

MNOT(MRE(re.compile('.*')))
[]
None

MRE(re.compile('zzz'))
[]
None

MNOT(MRE(re.compile('zzz')))
[<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>]
<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>

MCB(<lambda>)
[<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>]
<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>

MNOT(MCB(<lambda>))
[]
None

MCB(<lambda>)
[]
None

MNOT(MCB(<lambda>))
[<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>]
<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>

MTAG('yes')
[<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>]
<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>

MNOT(MTAG('yes'))
[]
None

MTAG('no')
[]
None

MNOT(MTAG('no'))
[<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>]
<FSTMatch <Pass ROOT 0,0..0,4> {'yes': ...}>
        """.strip())

        # passthrough parameters to walk()

        pat = MName('i')
        f = FST('def f(): i = [i := i for i in i]')

        self.assertEqual('[<Name 0,9..0,10>, <Name 0,14..0,15>, <Name 0,19..0,20>, <Name 0,25..0,26>, <Name 0,30..0,31>]', str(list(m.matched for m in f.search(pat))))
        self.assertEqual('[<Name 0,30..0,31>, <Name 0,25..0,26>, <Name 0,19..0,20>, <Name 0,14..0,15>, <Name 0,9..0,10>]', str(list(m.matched for m in f.search(pat, back=True))))
        self.assertEqual('[<Name 0,9..0,10>, <Name 0,14..0,15>, <Name 0,30..0,31>]', str(list(m.matched for m in f.search(pat, scope=True))))
        self.assertEqual('[<Name 0,30..0,31>, <Name 0,14..0,15>, <Name 0,9..0,10>]', str(list(m.matched for m in f.search(pat, scope=True, back=True))))
        self.assertEqual('[<Name 0,9..0,10>]', str(list(m.matched for m in f.body[0].search(pat, recurse=False))))
        self.assertEqual('[<Name 0,9..0,10>]', str(list(m.matched for m in f.body[0].search(pat, recurse=False, back=True))))
        self.assertEqual('[<Name 0,9..0,10>, <Name 0,14..0,15>, <Name 0,19..0,20>, <Name 0,25..0,26>, <Name 0,30..0,31>]', str(list(m.matched for m in f.search(pat, asts=[f.a.body[0]]))))
        self.assertEqual('[<Name 0,30..0,31>, <Name 0,25..0,26>, <Name 0,19..0,20>, <Name 0,14..0,15>, <Name 0,9..0,10>]', str(list(m.matched for m in f.search(pat, asts=[f.a.body[0]], back=True))))
        self.assertEqual('[<Name 0,9..0,10>, <Name 0,14..0,15>, <Name 0,30..0,31>]', str(list(m.matched for m in f.search(pat, scope=True, asts=[f.a.body[0]]))))
        self.assertEqual('[<Name 0,30..0,31>, <Name 0,14..0,15>, <Name 0,9..0,10>]', str(list(m.matched for m in f.search(pat, scope=True, asts=[f.a.body[0]], back=True))))
        self.assertEqual('[]', str(list(m.matched for m in f.search(pat, recurse=False, asts=[f.a.body[0]]))))
        self.assertEqual('[]', str(list(m.matched for m in f.search(pat, recurse=False, asts=[f.a.body[0]], back=True))))

    def test_search_nested(self):
        # nested and send()

        f = FST('([a, [b, [c]]], [d])')
        self.assertEqual('[a, [b, [c]]], [b, [c]], [c], [d]', ', '.join(m.matched.src for m in f.search(List, nested=True)))
        self.assertEqual('[a, [b, [c]]], [d]', ', '.join(m.matched.src for m in f.search(List, nested=False)))

        l = []
        for m in (gen := f.search(List, nested=True)):
            l.append((g := m.matched).src)
            if g.src == '[b, [c]]':
                gen.send(False)
                gen.send(False)
        self.assertEqual('[a, [b, [c]]], [b, [c]], [d]', ', '.join(l))

        l = []
        for m in (gen := f.search(List, nested=False)):
            l.append((g := m.matched).src)
            if g.src == '[a, [b, [c]]]':
                gen.send(True)
                gen.send(True)
        self.assertEqual('[a, [b, [c]]], [b, [c]], [d]', ', '.join(l))

    def test_sub(self):
        for case, rest in DATA_SUB.iterate(True):
            for rest_idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                self.assertEqual(c, r, f'{case.id()}, rest idx = {rest_idx}')

    def test_sub_coverage(self):
        assertRaises(MatchError('expected FST or FSTView, got NoneType'), FST('{**a}').sub, MDict(keys=[MQSTAR(t=[...])]), '__FST_t')
        assertRaises(MatchError('expected FSTMatch in list, got str'), FST('[a]').sub, MList(elts=[MQSTAR(..., t=['blah'])]), '__FST_t')
        assertRaises(MatchError('match substitution must be FST, None or str, got int'), FST('[a]').sub, M(MList, t=123), '__FST_t')

        self.assertEqual('[]', FST('[a]').sub(MList(elts=[MQ01(t=[MQSTAR('b')]), MQSTAR]), '[__FST_t]').src)
        self.assertEqual('""', FST('[a]').sub(M(MList, t=None), '"__FST_t"').src)
        self.assertEqual('"123"', FST('[a]').sub(M(MList, t='123'), '"__FST_t"').src)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-sub', default=False, action='store_true', help="regenerate sub test data")

    args, _ = parser.parse_known_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT14:
            raise RuntimeError('cannot regenerate on python version < 3.14')

    if args.regen_sub or args.regen_all:
        print('Regenerating parentheses test data...')
        regen_sub_data()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
