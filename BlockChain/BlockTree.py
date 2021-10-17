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

        vote_info_for_genesis = VoteInfo("idGenesis", 0, None, -1, None)
        self.pending_block_tree = Block(0, 0, "", None, "idGenesis")
        self.high_qc = QC(vote_info_for_genesis, signatures, 0, signatures[0])
        self.high_commit_qc = None
        self.ledger = ledger
        self.current_round = 1
        self.replica_id = replica_id
        self.signatures = signatures

    def process_qc(self, qc, mempool):
        if qc is not None and qc.ledger_commit_info is not None:
            if qc.ledger_commit_info.commit_state_id is not None:
                self.ledger.commit(qc.vote_info.parent_id, mempool)
                    # parent id becomes the new root of the pending block tree
                    # prune the pending Block Tree
                self.prune_pending_block_tree(self.pending_block_tree, qc.vote_info.parent_id)
                if self.high_commit_qc is None or (qc.vote_info.round > self.high_commit_qc.vote_info.round):
                    self.high_commit_qc = qc
        if qc is not None and qc.vote_info is not None and qc.vote_info.round > self.high_qc.vote_info.round:
            self.high_qc = qc

    def prune_pending_block_tree(self, node, id):
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
        
    def process_vote(self, voteMessage, author, signature, mempool):
        self.process_qc(voteMessage.high_commit_qc, mempool)
        vote_idx = voteMessage.ledger_commit_info.get_hash()
        self.pending_votes[vote_idx].append(voteMessage.signature)
        #Change to proper value of f
        f = 1
        if (len(self.pending_votes[vote_idx]) == 2 * f + 1):
            qc = QC(voteMessage.vote_info, self.pending_votes[vote_idx], author, signature, voteMessage.ledger_commit_info)
            print("QC Also obtained")
            return qc
        return None

    def generate_block(self, u, current_round, txns, id):
        return Block(u, current_round, txns, self.high_qc, id)

    def find_block(self, block, id):
        if block is not None:
            if(block.id == id):
                return block
            for child in block.children:
                if child is not None:
                    return self.find_block(child, id)
        return None

    def hashIt(self, str):
        return hashlib.sha224(str.encode('ascii')).hexdigest()