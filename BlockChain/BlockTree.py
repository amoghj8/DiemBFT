from Block import Block
from LedgerCommitInfo import LedgerCommitInfo
from QC import QC
from Ledger import Ledger
import hashlib

from VoteInfo import VoteInfo
from collections import defaultdict

class BlockTree:
    
    def __init__(self, ledger, replica_id, signatures):
        self.pending_votes = defaultdict(list)
        ledger_commit_info = LedgerCommitInfo("state_id", "hash")

        #VoteInfo and QC of Parent of Genesis
        vote_info = VoteInfo("Genesis-1", -2, "Genesis-2", -3, "")
        qc = QC(vote_info, "", "", "", ledger_commit_info)

        #VoteInfo and QC of Genesis Block
        self.pending_block_tree = Block(-1, -1, "", qc, "Genesis")
        vote_info_1 = VoteInfo("Genesis", -1, "Genesis-1", -2, "")
        self.high_qc = QC(vote_info_1, "", "", "", ledger_commit_info)
        self.high_commit_qc = self.high_qc

        self.ledger = ledger
        self.current_round = 0
        self.replica_id = replica_id
        self.signatures = signatures

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
        # print("current round = " + str(self.current_round))
        self.ledger.speculate(b)
        parentBlock = self.find_block(self.pending_block_tree, b.qc.vote_info.id)
        if(parentBlock is None):
            parentBlock = self.pending_block_tree
        print("Current id = [" + str(b.id) + "] search pid = [" + str(b.qc.vote_info.id) + "] Parent Id = " + str(parentBlock.id))
        parentBlock.children.append(b)
        
    def process_vote(self, voteMessage):
        self.process_qc(voteMessage.high_commit_qc)
        vote_idx = self.hashIt(  str(voteMessage.ledger_commit_info.vote_info_hash) + str(voteMessage.ledger_commit_info.commit_state_id))
        self.pending_votes[vote_idx].append(voteMessage.signature)
        #Change to proper value of f
        f = 1
        if (len(self.pending_votes[vote_idx]) == 2 * f + 1):
            qc = QC(voteMessage.vote_info, self.pending_votes[vote_idx], "Author 1", "Signature 1", voteMessage.ledger_commit_info)
            return qc
        return None

    def generate_block(self, txns, current_round):
        return Block(self.replica_id, current_round, txns, self.high_qc, self.hashIt("Author 1" + str(current_round) + str(txns) + str(self.high_qc.vote_info.id) + str(self.signatures[self.replica_id])))

    def find_block(self, node, id):
        if(node.id == id):
            return node
        for child in node.children:
            self.find_block(child, id)

    def hashIt(self, str):
        return hashlib.sha224(str.encode('ascii')).hexdigest()