#!/usr/bin/python

import datetime
import functools
import os
import random
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
    def testAgreeVote(self):
        self.sp.Init(10)

        for i in xrange(6):
            self.sp.SignAgreement(random.randint(0, 9), random.randint(0, 9))
            self.sp.CurrentRanking()

        for i in xrange(1000):
            self.sp.Vote(10 + i, random.randint(0, 9))
            self.sp.CurrentRanking()

        self.sp.CurrentRanking()

    @emit_test_name
    def testVoteAgreeVote(self):
        self.sp.Init(10)

        for i in xrange(10):
            self.sp.Vote(i, random.randint(0, 10))
            self.sp.CurrentRanking()

        for i in xrange(20):
            self.sp.SignAgreement(random.randint(0, 9), random.randint(0, 9))
            self.sp.CurrentRanking()

        for i in xrange(1000):
            self.sp.Vote(10 + i, random.randint(0, 9))
            self.sp.CurrentRanking()

        self.sp.CurrentRanking()

    @emit_test_name
    def testPureFuzz(self):
        for _ in xrange(1000):
            action = random.randint(1, 80)
            if action < 10:
                self.sp.Init(random.randint(1, 100))
            elif action < 50:
                self.sp.Vote(random.randint(-100, 1000),
                             random.randint(-10, 100))
            elif action < 70:
                self.sp.SignAgreement(random.randint(-10, 100),
                                      random.randint(-10, 100))
            else:
                self.sp.Quit()
            self.sp.CurrentRanking()


if __name__ == '__main__':
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    TEST_OUTPUT_PATH = os.path.join(os.getcwd(), 'test-output',
                                    'simple', timestamp)
    os.makedirs(TEST_OUTPUT_PATH)
    unittest.main()
