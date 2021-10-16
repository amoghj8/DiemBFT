from Block import Block
from QC import QC
from Ledger import Ledger

from VoteInfo import VoteInfo
from collections import defaultdict

class BlockTree:
    
    def __init__(self, ledger):
        self.pending_votes = defaultdict(list)
        vote_info = VoteInfo("", -2, "", -3, "")
        qc = QC(vote_info, "", "", "")
        self.pending_block_tree = Block("", -1, "", qc, "Genesis")
        self.high_qc = qc
        self.high_commit_qc = qc
        self.ledger = ledger

    def process_qc(self, qc):
        if qc.ledger_commit_info.commit_state_id is not None:
            if self.ledger.commit(qc.vote_info.parent_id):
                # parent id becomes the new root of the pending block tree
                # prune the pending Block Tree
                self.prune_pending_block_tree(self.pending_block_tree, qc.vote_info.parent_id)
            else:
                # handle the case when commit fails
                pass
            if qc.vote_info.round > self.high_commit_qc.vote_info.round:
                self.high_commit_qc = qc
        if qc.vote_info.round > self.high_qc.vote_info.round:
            self.high_qc = qc

    def prune_pending_block_tree(self, node, id):
        #Doesn't work always. Possible that direct children of pending block tree
        #is what we wish to prune to
        #Assume levels of non-TC yet wrong sequence ids, and later the pruning happens
        #Should be dfs till the level where voteinfo.id == parent_id and set that node]
        self.pending_block_tree = self.find_block(node, id)

    def execute_and_insert(self, b):
        # Sending block as ledger speculate function is expecting block
        self.ledger.speculate(b)
        parentBlock = self.find_block(b.qc.vote_info.id)
        parentBlock.children.append(b)
        
    def process_vote(self, voteMessage):
        self.process_qc(voteMessage.high_commit_qc)
        vote_idx = hash(voteMessage.ledger_commit_info)
        self.pending_votes[vote_idx] = self.pending_votes[vote_idx].union(voteMessage.signature)
        #Change to proper value of f
        f = 1
        if (len(self.pending_votes[vote_idx]) == 2 * f + 1):
            qc = QC(voteMessage.vote_info, self.pending_votes[vote_idx], "Author 1", "Signature 1")
            return qc
        return None

    def generate_block(self, txns, current_round):
        return Block("Block Author 1", current_round, txns, self.high_qc, hash("Author 1" + str(current_round) + str(txns) + str(self.high_qc.vote_info.id) + str(self.high_qc.signatures)))

    def find_block(self, node, id):
        if(node.id == id):
            return node
        for child in node.children:
            self.find_block(self, child, id)