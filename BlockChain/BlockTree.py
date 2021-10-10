class BlockTree:
    def __init__(self, pending_block_tree, pending_votes, high_qc, high_commit_qc):
        self.pending_block_tree = pending_block_tree
        self.pending_votes = pending_votes
        self.high_qc = high_qc
        self.high_commit_qc = high_commit_qc