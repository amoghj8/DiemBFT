class VoteInfo():
    """VoteInfo"""
    def __init__(self, id, round, parent_id, parent_round, exec_state_id):
        super(VoteInfo, self).__init__()
        self.id = id
        self.round = round
        self.parent_id = parent_id
        self.parent_round = parent_round
        self.exec_state_id = exec_state_id
        