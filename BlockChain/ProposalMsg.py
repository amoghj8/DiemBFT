import QC
import Block
import TC

class ProposalMsg:
    count = 0
    def __init__(self, block, last_round_tc, high_commit_qc, signature):
        self.id = self.count
        self.count+=1
        self.block = block
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc
        self.signature = signature