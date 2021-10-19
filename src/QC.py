
"""
QC
"""
class QC:
    def __init__(self, vote_info, signatures, author, author_signature, ledger_commit_info = None):
        self.vote_info = vote_info
        self.signatures = signatures
        self.author = author
        self.author_signature = author_signature
        self.ledger_commit_info = ledger_commit_info
