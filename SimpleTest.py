#!/usr/bin/python

import datetime
import functools
import os
import unittest
import Simulator as sim

glob_ctr = 0
DO_VALGRIND = int(os.environ.get('WET2_VALGRIND', 0)) == 1


def emit_test_name(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        self.sp.Comment('Test: %s' % func.func_name)
        return func(*args, **kwargs)

    return wrapper


class Wet2TestCases(unittest.TestCase):
    def setUp(self):
        global glob_ctr
        global TEST_OUTPUT_PATH
        global DO_VALGRIND
        cls_name = self.__class__.__name__
        make_name = lambda infix: os.path.join(TEST_OUTPUT_PATH,
                                               '%s-%s-%02d' % (cls_name,
                                                               infix,
                                                               glob_ctr))
        self.sp = sim.SimulatedWet2Proxy(command_log=make_name('commands'),
                                         valgrind=DO_VALGRIND,
                                         valgrind_log=make_name('valgrind'),
                                         proxy_output=make_name('out-actual'),
                                         sim_output=make_name('out-expected'))
        glob_ctr += 1

    def tearDown(self):
        # self.sp._p._proc.kill()
        self.sp.Quit()
        self.sp._p._proc.stdin.write('\n\n')
        self.sp._p._proc.wait()
        del self.sp

    @emit_test_name
    def testInitOnce(self):
        self.sp.Init(10)

    @emit_test_name
    def testInitTwice(self):
        self.sp.Init(10)
        self.sp.Init(123)

    @emit_test_name
    def testVote(self):
        self.sp.Init(10)
        self.sp.Vote(1, 2)

    @emit_test_name
    def testVoteTwiceSameVoter(self):
        self.sp.Init(10)
        self.sp.Vote(1, 2)
        self.sp.Vote(1, 2)

    @emit_test_name
    def testAdd100Votes(self):
        self.sp.Init(10)
        for i in xrange(100):
            self.sp.Vote(10 * i, 1)

    @emit_test_name
    def testSignAgreement(self):
        self.sp.Init(10)
        self.sp.SignAgreement(-1, 2)
        self.sp.SignAgreement(1, 2)
        self.sp.SignAgreement(1, 2)

    @emit_test_name
    def testCampLeader(self):
        self.sp.Init(10)
        self.sp.CampLeader(-1)
        self.sp.CampLeader(10)
        self.sp.CampLeader(5)

    @emit_test_name
    def testCampLeaderAfterAgreement(self):
        self.sp.Init(5)
        self.sp.SignAgreement(0,1)
        self.sp.Vote(0, 0)
        self.sp.SignAgreement(1,2)
        self.sp.SignAgreement(0,1)

    @emit_test_name
    def testCurrentRanking(self):
        self.sp.Init(5)
        self.sp.CurrentRanking()
        self.sp.Vote(0, 0)
        for i in range(10):
            self.sp.Vote((i+3), (i % 2)+1)
        self.sp.CurrentRanking()
        self.sp.SignAgreement(2, 0)
        self.sp.CurrentRanking()

if __name__ == '__main__':
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    TEST_OUTPUT_PATH = os.path.join(os.getcwd(), 'test-output',
                                    'simple', timestamp)
    os.makedirs(TEST_OUTPUT_PATH)
    unittest.main()
