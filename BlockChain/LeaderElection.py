import math
from Ledger import Ledger
import random
from random import sample

"""
LeaderElection
"""
class LeaderElection:
    count = 0

    """
    Init
    """
    def __init__(self, validators, window_size, exclude_size, reputation_leaders, ledger, block_tree, logger):
        self.validators = validators
        self.window_size = window_size
        self.exclude_size = exclude_size
        self.reputation_leaders = reputation_leaders
        self.ledger = ledger
        self.block_tree = block_tree
        self.logger = logger
        self.logger.debug('LeaderElection init complete')

    """
    Electing reputation leader
    """
    def elect_reputation_leader(self, qc):
        activeValidators = set()
        lastAuthors = set()
        current_qc = qc
        for i in range(self.window_size + len(lastAuthors)):
            current_block = self.ledger.committed_block(current_qc.vote_info.parent_id)
            block_author = current_block.author
            if i < self.window_size:
                activeValidators  = activeValidators.union(current_qc.signatures.signers())
            if len(lastAuthors) < self.exclude_size:
                lastAuthors.add(block_author)
            current_qc = current_block.qc
        activeValidators = activeValidators - lastAuthors
        random.seed(qc.vote_info.round)
        self.logger.debug('Electing a leader')
        return sample(activeValidators, 1)

    """
    Updating leaders
    """
    def update_leaders(self, qc):
        self.logger.debug('updating leaders')
        self.count += 1
        # return self.count % len(self.validators)
        # extended_round = qc.vote_info.parent_round
        # qc_round = qc.vote_info.round
        # current_round = self.block_tree.current_round
        # if extended_round + 1 == qc_round and qc_round + 1 == current_round:
        #     # self.reputation_leaders[current_round + 1] = self.elect_reputation_leader(qc)
        #     pass

    """
    Get leader
    """
    def get_leader(self, round):
        self.logger.debug('new leader is ', round % len(self.validators))
        return round % len(self.validators)
        # if round in self.reputation_leaders:
        #     return self.reputation_leaders[round]
        # next_leader = self.count % len(self.validators)
        # self.count += 1
        # return next_leader % len(self.validators)
        # return self.validators[math.floor(round / 2) % len(self.validators)]
