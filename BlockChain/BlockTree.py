from Block import Block
from QC import QC
from Ledger import Ledger

from VoteInfo import VoteInfo
from collections import defaultdict

class BlockTree:
    
    def __init__(self, ledger, public_key_list_replica):
        self.pending_votes = defaultdict(list)

        #Create a genesis block and set it to pending block tree
        #Vote info for genesis block
        #id = None
        #round = 0
        #parent_id = None
        #parent_round = -1
        #exec_state_id = None
        vote_info_for_genesis = VoteInfo("idGenesis", 0, None, -1, None)

        #Make a QC for the Genesis block
        #Let author for Genesis block QC be 0 and 0 is assumed to be the leader
        #Every block b (except for a known genesis block P0) is chained to a parent via b.qc,
        # a Quorum Certiﬁcate (QC) that consists of a quorum of votes for the parent block
        self.pending_block_tree = Block(0, 0, "", None, "idGenesis")
        self.high_qc = QC(vote_info_for_genesis, public_key_list_replica, 0, public_key_list_replica[0])
        self.high_commit_qc = None
        self.ledger = ledger

    def process_qc(self, qc):
        if qc is not None and qc.ledger_commit_info is not None:
            if qc.ledger_commit_info.commit_state_id is not None:
                print("qc.vote_info.parent_id", qc.vote_info.parent_id)
                self.ledger.commit(qc.vote_info.parent_id)
                    # parent id becomes the new root of the pending block tree
                    # prune the pending Block Tree
                self.prune_pending_block_tree(self.pending_block_tree, qc.vote_info.parent_id)
                # else:
                #     # handle the case when commit fails
                #     pass
                if self.high_commit_qc is None or (qc.vote_info.round > self.high_commit_qc.vote_info.round):
                    self.high_commit_qc = qc
        if qc is not None and qc.vote_info is not None and qc.vote_info.round > self.high_qc.vote_info.round:
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
        parentBlock = self.find_block(self.pending_block_tree, b.qc.vote_info.id)
        print("sample", b.qc.vote_info.id, " ", parentBlock.id)
        parentBlock.children.append(b)
        
    def process_vote(self, voteMessage, author, signature):
        self.process_qc(voteMessage.high_commit_qc)
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
                return self.find_block(child, id)
        return None