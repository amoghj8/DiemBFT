import TimeoutInfo

class TimeoutMsg:
    count = 0
    def __init__(self, tmo_info, last_round_tc, high_commit_qc):
        self.id = self.count
        self.count+=1
        self.tmo_info = tmo_info
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc