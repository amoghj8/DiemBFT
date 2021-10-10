class VoteMsg:
    def __init__(self, vote_info, ledger_comit_info, high_comit_qc, sender, signature):
        self.vote_info = vote_info
        self.ledger_comit_info = ledger_comit_info
        self.high_comit_qc = high_comit_qc
        self.sender = sender
        self.signature = signature