class QC:
    def __init__(self, vote_info, ledger_commit_info, signatures, author, author_signature):
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.signatures = signatures
        self.author = author
        self.author_signature = author_signature