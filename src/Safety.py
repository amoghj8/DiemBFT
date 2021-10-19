from TimeoutInfo import TimeoutInfo
import Ledger
from VoteInfo import VoteInfo
from LedgerCommitInfo import LedgerCommitInfo
from VoteMsg import VoteMsg
import hashlib

"""
Safety
"""
class Safety:
    def __init__(self, private_key, public_keys, ledger = None, block_tree = None, logger=None):
        self.__private_key = private_key
        self.__public_keys = public_keys
        self.__highest_vote_round = -2
        self.__highest_qc_round = -2
        self.ledger = ledger
        self.block_tree = block_tree
        self.logger = logger
        self.logger.debug('Safety module init complete')

    """
    Increase highest vote round
    """
    def __increase_highest_vote_round(self, round):
        self.__highest_vote_round = max(round, self.__highest_vote_round)

    """
    Update highest qc round
    """
    def __update_highest_qc_round(self, qc_round):
        self.__highest_qc_round = max(qc_round, self.__highest_qc_round)

    """
    Consecutive
    """
    def __consecutive(self, block_round, round):
        return (round + 1 == block_round)

    """
    Safe to extend
    """
    def __safe_to_extend(self, block_round, qc_round, tc):
        lst_high_qc_val = [ qc_obj.vote_info.round for qc_obj in tc.tmo_high_qc_rounds ]
        return (self.__consecutive(block_round, tc.round) and qc_round >= max(lst_high_qc_val))

    """
    Safe to vote
    """
    def __safe_to_vote(self, block_round, qc_round, tc):
        if block_round <= max(self.__highest_vote_round, qc_round):
            return False
        return (self.__consecutive(block_round, qc_round) or self.__safe_to_extend(block_round, qc_round, tc))

    """
    Creating a Logger
    """
    def __safe_to_timeout(self, round, qc_round, tc):
        if(qc_round < self.__highest_qc_round or round <= max(self.__highest_vote_round - 1, qc_round)):
            return False
        return (self.__consecutive(round, qc_round) or self.__consecutive(round, tc.round))

    """
    Commit state id candidate
    """
    def __commit_state_id_candidate(self, block_round, qc):
        if(self.__consecutive(block_round, qc.vote_info.round)):
            return self.ledger.pending_state(qc.vote_info.id)
        else:
            return None

    """
    Set highest vote round
    """
    def set_highest_vote_round(self, value):
        self.__highest_vote_round = value


    """
    Make vote
    """
    def make_vote(self, b, last_tc, leader, signature):
        qc_round = b.qc.vote_info.round
        if self.__safe_to_vote(b.round, qc_round, last_tc):
            self.__update_highest_qc_round(qc_round)
            self.__increase_highest_vote_round(b.round)
            vote_info = VoteInfo(b.id, b.round, b.qc.vote_info.id, qc_round, self.ledger.pending_state(b.id))
            vote_info_hash = self.hashIt( str(b.id) + str(b.round) + str(b.qc.vote_info.id) + str(qc_round) + str(self.ledger.pending_state(b.id)) )
            ledger_commit_info = LedgerCommitInfo(self.__commit_state_id_candidate(b.round, b.qc), vote_info_hash)
            return VoteMsg(vote_info, ledger_commit_info, self.block_tree.high_commit_qc, leader, str(signature)) #need to change
        return None

    """
    Make timeout
    """
    def make_timeout(self, round, high_qc, last_tc):
        qc_round = high_qc.vote_info.round
        if self.__safe_to_timeout(round, qc_round, last_tc):
            self.__increase_highest_vote_round(round)
            #To do
            return TimeoutInfo(round, high_qc, self.block_tree.replica_id, "")
        return None

    def hashIt(self, str):
        return hashlib.sha256(str.encode('ascii')).hexdigest()
