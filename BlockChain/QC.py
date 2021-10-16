from typing import List
from VoteInfo import VoteInfo
import nacl.bindings
from nacl.signing import SigningKey
class QC:
    def __init__(self, vote_info : VoteInfo, signatures : List[nacl.signing.SignedMessage], author : int, author_signature : nacl.signing.SignedMessage, ledger_commit_info = None):
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.signatures = signatures
        self.author = author
        self.author_signature = author_signature