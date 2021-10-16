from TimeoutInfo import TimeoutInfo
import Ledger
from VoteInfo import VoteInfo
from LedgerCommitInfo import LedgerCommitInfo
from VoteMsg import VoteMsg

class Safety:
    def __init__(self, private_key, public_keys, ledger = None, block_tree = None):
        self.__private_key = private_key
        self.__public_keys = public_keys
        self.__highest_vote_round = -2
        self.__highest_qc_round = -2
        self.ledger = ledger
        self.block_tree = block_tree
    
    def __increase_highest_vote_round(self, round):
        self.__highest_vote_round = max(round, self.__highest_vote_round)
    
    def __update_highest_qc_round(self, qc_round):
        self.__highest_qc_round = max(qc_round, self.__highest_qc_round)

    def __consecutive(self, block_round, round):
        print("QC Round = " + str(round) + "... Block Round = " + str(block_round))
        return (round + 1 == block_round)

    def __safe_to_extend(self, block_round, qc_round, tc):
        return (self.__consecutive(block_round) and qc_round >= max(tc.tmo_high_qc_rounds))

    def __safe_to_vote(self, block_round, qc_round, tc):
        if block_round <= max(self.__highest_vote_round, qc_round):
            print("No.......")
            return False
        return (self.__consecutive(block_round, qc_round) and qc_round >= max(tc.tmo_high_qc_rounds))

    def __safe_to_timeout(self, round, qc_round, tc):
        # print("qc_round = " + qc_round)

        if(qc_round < self.__highest_qc_round or round <= max(self.__highest_vote_round - 1, qc_round)):
            return False
        return (self.__consecutive(round, qc_round) or self.__consecutive(round, tc.round))

    def __commit_state_id_candidate(self, block_round, qc):
        if(self.__consecutive(block_round, qc.vote_info.round)):
            return Ledger.pending_state(qc.id)

        else:
            return None


    def make_vote(self, b, last_tc):
        qc_round = b.qc.vote_info.round
        print("Make Vote")
        if self.__safe_to_vote(b.round, qc_round, last_tc):
            print("Making Vote")
            self.__update_highest_qc_round(qc_round)
            self.__increase_highest_vote_round(b.round)
            vote_info = VoteInfo(b.id, b.round, b.qc.vote_info.id, qc_round, self.ledger.pending_state(b.id))
            ledger_commit_info = LedgerCommitInfo(self.__commit_state_id_candidate(b.round, b.qc), hash(vote_info))
            return VoteMsg(vote_info, ledger_commit_info, self.block_tree.high_commit_qc)
        return None

    def make_timeout(self, round, high_qc, last_tc):
        qc_round = high_qc.vote_info.round
        if self.__safe_to_timeout(round, qc_round, last_tc):
            self.__increase_highest_vote_round(round)
            #To do
            return TimeoutInfo(round, high_qc, 1, "")
        return None
