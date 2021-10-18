import hashlib

class VoteInfo():
    """VoteInfo"""
    def __init__(self, id : str, round : int, parent_id : str, parent_round : int, exec_state_id : str):
        super(VoteInfo, self).__init__()
        self.id = id
        self.round = round
        self.parent_id = parent_id
        self.parent_round = parent_round
        self.exec_state_id = exec_state_id
    
    def get_hash(self):
        s = str(self.id) + str(self.round) + str(self.parent_id) + str(self.parent_round)
        return hashlib.sha256(s.encode('ascii')).hexdigest()