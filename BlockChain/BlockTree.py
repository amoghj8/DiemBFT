import Block
import QC
import Ledger

class BlockTree:
    
    def __init__(self, pending_votes, high_qc, high_commit_qc, pending_block_tree):
        self.pending_votes = pending_votes
        self.high_qc = high_qc
        self.high_commit_qc = high_commit_qc
        self.pending_block_tree = pending_block_tree

    def process_qc(self, qc):
        if qc.ledger_commit_info.commit_state_id is not None:
            if Ledger.commit(qc.vote_info.parent_id):
                # parent id becomes the new root of the pending block tree
                # prune the pending Block Tree
                pass
            else:
                # handle the case when commit fails
                pass
            self.high_commit_qc = max(self.high_commit_qc, qc.vote_info.round)
        self.high_qc = max(self.high_qc, qc.vote_info.round)
        
    def prune_pending_block_tree(self, parent_id):
        self.pending_block_tree = self.pending_block_tree.children[parent_id]        

    def execute_and_insert(self, b):
        Ledger.speculate(b.qc.block_id, b.id, b.payload)
        self.pending_block_tree.children.append(b)
        
    def process_vote(self, voteMessage):
        self.process_qc(voteMessage.high_commit_qc)
        vote_idx = hash(voteMessage.ledger_commit_info)
        self.pending_votes[vote_idx] = self.pending_votes[vote_idx] or voteMessage.signature
        #Change to proper value of f
        f = 3
        if (len(self.pending_votes[vote_idx]) == 2 * f + 1):
            qc = QC(voteMessage.vote_info, self.pending_votes[vote_idx], "Author 1", "Signature 1")
            return qc
        return None

    def generate_block(self, txns, current_round):
        return Block("Block Author 1", current_round, txns, self.high_qc, hash("Author 1" + current_round + txns + self.high_qc.vote_info.id + self.high_qc.signatures))
