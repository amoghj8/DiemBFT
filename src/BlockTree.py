from Block import Block
from LedgerCommitInfo import LedgerCommitInfo
from QC import QC
from Ledger import Ledger
import hashlib
import config
import logging

from VoteInfo import VoteInfo
from collections import defaultdict

"""
BlockTree
"""
class BlockTree:
    """
    init
    """
    def __init__(self, ledger, replica_id, signatures, logger, f):
        self.pending_votes = defaultdict(list)
        ledger_commit_info = LedgerCommitInfo("state_id", "hash")

        #VoteInfo and QC of Parent of Genesis
        vote_info = VoteInfo("Genesis-1", -2, "Genesis-2", -3, "")
        qc = QC(vote_info, "", "", "", ledger_commit_info)

        #VoteInfo and QC of Genesis Block
        self.pending_block_tree = Block(-1, -1, "", qc, "Genesis", "txn_id")
        vote_info_1 = VoteInfo("Genesis", -1, "Genesis-1", -2, "")
        self.high_qc = QC(vote_info_1, "", "", "", ledger_commit_info)
        self.high_commit_qc = self.high_qc
        self.f = f

        self.ledger = ledger
        self.current_round = 0
        self.replica_id = replica_id
        self.signatures = signatures
        self.logger = logger
        self.logger.debug('BlockTree init complete')

    """
    Process qc
    """
    def process_qc(self, qc):
        self.logger.debug('Processing QC from sender ')
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

    """
    Prune pending block tree
    """
    def prune_pending_block_tree(self, node, id):
        #Doesn't work always. Possible that direct children of pending block tree
        #is what we wish to prune to
        #Assume levels of non-TC yet wrong sequence ids, and later the pruning happens
        #Should be dfs till the level where voteinfo.id == parent_id and set that node]
        self.logger.debug('Pruning pending block tree')
        self.pending_block_tree = self.find_block(node, id)

    """
    Execute and insert block
    """
    def execute_and_insert(self, b):
        # Sending block as ledger speculate function is expecting block
        self.ledger.speculate(b)
        parentBlock = self.find_block(self.pending_block_tree, b.qc.vote_info.id)
        if(parentBlock is None):
            parentBlock = self.pending_block_tree
        self.logger.debug('Inserting block')
        parentBlock.children.append(b)

    """
    Process vote
    """
    def process_vote(self, voteMessage, leader):
        self.logger.debug('Processing vote')
        self.process_qc(voteMessage.high_commit_qc)
        vote_idx = self.hashIt(  str(voteMessage.ledger_commit_info.vote_info_hash) + str(voteMessage.ledger_commit_info.commit_state_id))
        self.pending_votes[vote_idx].append(voteMessage.signature)
        #Change to proper value of f
        #f = 1
        if (len(self.pending_votes[vote_idx]) == 2 * self.f + 1):
            qc = QC(voteMessage.vote_info, self.pending_votes[vote_idx], leader, str(self.signatures[leader]), voteMessage.ledger_commit_info)
            return qc
        return None

    """
    Generating block
    """
    def generate_block(self, txns, current_round, txn_id):
        self.logger.debug('Generating block')
        return Block(self.replica_id, current_round, txns, self.high_qc, self.hashIt(str(self.replica_id)+ str(current_round) + str(txns) + str(self.high_qc.vote_info.id) + str(self.signatures[self.replica_id])), txn_id)

    """
    Finding block
    """
    def find_block(self, node, id):
        self.logger.debug('Searching block with id')
        if(node.id == id):
            return node
        for child in node.children:
            self.find_block(child, id)

    """
    Hashing 
    """
    def hashIt(self, str):
        return hashlib.sha256(str.encode('ascii')).hexdigest()
