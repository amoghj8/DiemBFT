import Ledger

class Safety:
    def __init__(self, private_key, public_keys):
        self.__private_key = private_key
        self.__public_keys = public_keys
        self.__highest_vote_round = 0
        self.__highest_qc_round = 0
    
    def __increase_highest_vote_round(self, round):
        self.__highest_vote_round = max(round, self.__highest_vote_round)
    
    def __update_highest_qc_round(self, qc_round):
        self.__highest_qc_round = max(qc_round, self.__highest_qc_round)

    def __consecutive(self, block_round, round):
        return (round + 1 == block_round)

    def __safe_to_extend(self, block_round, qc_round, tc):
        return (self.consecutive(block_round) and qc_round >= max(tc.tmo_high_rounds))

    def __safe_to_vote(self, block_round, qc_round, tc):
        if block_round <= max(self.__highest_vote_round, qc_round):
            return False
        return (self.consecutive(block_round, qc_round) and qc_round >= max(tc.tmo_high_rounds))

    def __safe_to_timeout(self, round, qc_round, tc):
        if(qc_round < self.__highest_qc_round or round <= max(self.__highest_vote_round - 1, qc_round)):
            return False
        return (self.consecutive(round, qc_round) or self.consecutive(round, tc.round))

    def __commit_state_id_candidate(self, block_round, qc):
        if(self.consecutive(block_round, qc.vote_info.round)):
            return Ledger.pending_state(qc.id)

        else:
            return None
