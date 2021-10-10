from BlockChain.Block import Block
from BlockChain.QC import QC


class BlockTree:
    def __init__(self, pending_block_tree, pending_votes, high_qc, high_commit_qc):
        self.pending_block_tree = pending_block_tree
        self.pending_votes = pending_votes
        self.high_qc = high_qc
        self.high_commit_qc = high_commit_qc

    def process_vote(self, voteMessage):
        process_qc(voteMessage.high_commit_qc)
        vote_idx = hash(voteMessage.ledger_commit_info)
        pending_votes[vote_idx] = pending_votes[vote_idx] or voteMessage.signature
        if (len(pending_votes[vote_idx]) == 2 * f + 1):
            qc = QC(voteMessage.vote_info, pending_votes[vote_idx], "Author 1", "Signature 1")
            return qc
        return None

    def generate_block(self, txns, current_round):
        return Block("Block Author 1", current_round, txns, self.high_qc, hash("Author 1" + current_round + txns + self.high_qc.vote_info.id + self.high_qc.signatures))

