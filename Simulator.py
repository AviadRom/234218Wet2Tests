#!/usr/bin/python

import functools
import os
import subprocess
import threading
import Queue

class Candidate(object):
    def __init__(self, candId):
        self.id = candId
        self.numOfVotes = 0
    def set_num_of_votes(self, votes):
        self.numOfVotes = votes
    def vote(self):
        self.numOfVotes += 1


class UFSet(object):
    def __init__(self, id):
        self.id = id
        self.members = [Candidate(id)]
        self.size = 1

    def getMembers(self):
        return self.members


class UnionFind(object):
    def __init__(self, n):
        self.numOfElements = n
        self.sets = []
        for i in range(n):
            self.sets.append(UFSet(i))
        self.numOfSets = n

    def find(self, element):
        if element < 0 or element > self.numOfElements:
            return -1
        for i in range(self.numOfElements):
            members = self.sets[i].getMembers()
            for j in range(len(members)):
                if members[j].id == element:
                    return i

    def union(self, var1, var2):
        if var1 < 0 or var1 >= self.numOfElements or var2 < 0 or var2 >= self.numOfElements:
            return -1
        set1 = self.find(var1)
        set2 = self.find(var2)
        if set1 == set2:
            return -1
        self.sets[set1].members += self.sets[set2].members
        self.sets.remove(self.sets[set2])
        self.numOfSets -= 1

    def updateCandidate(self, cand, votes):
        if cand < 0 or cand > self.numOfElements-1:
            return 'error in updateElement'
        elemSet = self.find(cand)
        for i in range(len(self.sets[elemSet].members)):
            if self.sets[elemSet].members[i].id == cand:
                self.sets[elemSet].members[i].set_num_of_votes(votes)
                return


def assertInit(name):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            self = args[0]
            if (not self._init):
                return '%s: Invalid_input\n' % name
            else:
                return f(*args, **kwargs)
        return wrapper
    return decorator


class Wet2Sim(object):
    def __init__(self, *args, **kwargs):
        self._init = False

    def isLeader(self, cand):
        candSetIndex = self.unionfind.find(cand)
        maxVotes = -1
        candSet = self.unionfind.sets[candSetIndex]
        for i in range(len(candSet.members)):
            if candSet.members[i].numOfVotes > maxVotes:
                maxVotes = candSet.members[i].numOfVotes
        if self.candidates[cand].numOfVotes == maxVotes:
            return True
        return False


    def Init(self, n):
        if self._init:
            return  'Init was already called.\n'
        self.candidates = []
        for i in range(n):
            self.candidates.append(Candidate(i))
        self.unionfind = UnionFind(n)
        self.voters = []
        self._init = True
        return 'Init done.\n'

    @assertInit('Vote')
    def Vote(self, voter, candidate):
        if voter < 0 or candidate < 0 or candidate >= len(self.candidates):
            return 'Vote: Invalid_input\n'
        if voter in self.voters:
            return 'Vote: Failure\n'
        self.voters.append(voter)
        self.candidates[candidate].vote()
        self.unionfind.updateCandidate(candidate, self.candidates[candidate].numOfVotes)
        return 'Vote: Success\n'

    @assertInit('SignAgreement')
    def SignAgreement(self, cand1, cand2):
        if cand1 < 0 or cand2 < 0 or cand1 >= len(self.candidates) or cand2 >= len(self.candidates):
            return 'SignAgreement: Invalid_input\n'
        set1 = self.unionfind.find(cand1)
        set2 = self.unionfind.find(cand2)
        if set1 == set2:
            return 'SignAgreement: Failure\n'
        if not self.isLeader(cand1) or not self.isLeader(cand2):
            return 'SignAgreement: Failure\n'
        self.unionfind.union(cand1, cand2)
        return 'SignAgreement: Success\n'

    @assertInit('CampLeader')
    def CampLeader(self, cand):
        if cand < 0 or cand >= len(self.candidates):
            return 'CampLeader: Invalid_input\n'
        candSetIndex = self.unionfind.find(cand)
        candSet = self.unionfind.sets[candSetIndex]
        leadId = -1
        leadVotes = -1
        for i in range(len(candSet.members)):
            candId = candSet.members[i].id
            if self.candidates[candId].numOfVotes > leadVotes:
                leadVotes = self.candidates[candId].numOfVotes
                leadId = self.candidates[candId].id
            elif candSet.members[i].numOfVotes == leadVotes and candSet.members[i].id > leadId:
                leadId = self.candidates[candId].id
        ret = 'CampLeader: Success ' + str(leadId) + '\n'
        return ret

    def sortCandidates(self, candidates):
        candCopy = list(candidates)
        length = len(candidates)
        ret = []
        while len(ret) < length:
            max_id = -1
            max_vote = -1
            max_index = -1
            for i in range(len(candCopy)):
                if candCopy[i].numOfVotes > max_vote:
                    max_vote = candCopy[i].numOfVotes
                    max_id = candCopy[i].id
                    max_index = i
                elif candCopy[i].numOfVotes == max_vote and candCopy[i].id > max_id:
                    max_id = candCopy[i].id
                    max_index = i
            ret.append((max_id, max_index))
            del candCopy[max_index]
        return ret

    @assertInit('CurrentRanking')
    def CurrentRanking(self):
        sortedCandidates = self.sortCandidates(self.candidates)
        camps = []
        for i in range(len(sortedCandidates)):
            camp = self.unionfind.find(sortedCandidates[i][0])
            if camp not in camps:
                camps.append(camp)
        ret = 'CurrentRanking: Success, '
        for camp in range(len(camps)):
            campset = self.sortCandidates(self.unionfind.sets[camps[camp]].members)
            for i in range(len(campset)):
                toAdd = '(%d,%d),' % (campset[i][0], self.candidates[campset[i][0]].numOfVotes)
                ret += toAdd
        return ret[:len(ret)-1]

    def Quit(self):
        if self._init:
            self._init = False
            del self.candidates
            del self.unionfind
            del self.voters
        return 'Quit done.\n'


    def Comment(self, c):
        return '#%s\n' %c




PATH_TO_EXEC = os.environ['WET2_EXEC']


class Wet2Proxy(object):
    def __init__(self, command_log=None, valgrind=False, valgrind_log=None):
        cmd = []
        if valgrind:
            cmd = ['valgrind', '--leak-check=full']
            if valgrind_log:
                cmd.append('--log-file=%s' % valgrind_log)
        cmd.append(PATH_TO_EXEC)
        self._proc = subprocess.Popen(cmd, bufsize=1,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        self._queue = Queue.Queue()

        def enqueue():
            for line in iter(self._proc.stdout.readline, b''):
                self._queue.put(line)

        self._thread = threading.Thread(target=enqueue)
        self._thread.daemon = True
        self._thread.start()
        if command_log:
            self._command_log = open(command_log, 'w')
        else:
            self._command_log = None

    def _query_proc(self, q):
        self._proc.stdin.write(q + '\n')
        self._proc.stdin.flush()
        if self._command_log:
            self._command_log.write(q + '\n')
        try:
            return self._queue.get(timeout=1)
        except Queue.Empty:
            return ''

    def Init(self, k):
        return self._query_proc('Init %d' % k)

    def Vote(self, voterId, candidate):
        return self._query_proc('Vote %d %d' % (voterId, candidate))

    def SignAgreement(self, candidate1, candidate2):
        return self._query_proc('SignAgreement %d %d' % (candidate1, candidate2))

    def CampLeader(self, candidate):
        return self._query_proc('CampLeader %d' % candidate)

    def CurrentRanking(self):
        return self._query_proc('CurrentRanking')

    def Quit(self):
        return self._query_proc('Quit')

    def Comment(self, c):
        return self._query_proc('#%s' % c)


class SimulatedWet2ProxyException(RuntimeError):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return '"%s" != "%s"' % (self.a.strip(), self.b.strip())


class SimulatedWet2Proxy:
    def __init__(self, proxy_output=None, sim_output=None, *args, **kwargs):
        self.proxy_stdout, self.sim_stdout = None, None
        if proxy_output:
            self.proxy_stdout = open(proxy_output, 'w')
        if sim_output:
            self.sim_stdout = open(sim_output, 'w')
        self._p = Wet2Proxy(*args, **kwargs)
        self._s = Wet2Sim(*args, **kwargs)

    def _assertEqual(self, a, b):
        if (a != b):
            raise SimulatedWet2ProxyException(a, b)

    def _runOnBoth(self, func):
        sim_output = func(self._s).strip()
        proxy_output = func(self._p).strip()
        self.sim_stdout.write(sim_output + '\n')
        self.proxy_stdout.write(proxy_output + '\n')
        self._assertEqual(proxy_output, sim_output)

    def Init(self, k):
        self._runOnBoth(lambda x: x.Init(k))

    def Vote(self, voterId, candidate):
        self._runOnBoth(lambda x: x.Vote(voterId, candidate))

    def SignAgreement(self, candidate1, candidate2):
        self._runOnBoth(lambda x: x.SignAgreement(candidate1, candidate2))

    def CampLeader(self, candidate):
        self._runOnBoth(lambda x: x.CampLeader(candidate))

    def CurrentRanking(self):
        self._runOnBoth(lambda x: x.CurrentRanking())

    def Quit(self):
        self._runOnBoth(lambda x: x.Quit())

    def Comment(self, c):
        self._runOnBoth(lambda x: x.Comment(c))

if __name__ == '__main__':
    pass
