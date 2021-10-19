from collections import defaultdict

"""
Block 
"""
class Block:
    def __init__(self, author, round, payload, qc, id, txn_id):
        self.author = author
        self.round = round
        self.payload = payload
        self.qc = qc
        self.id = id
        self.txn_id = txn_id
        self.children = []
        #Parent id is redundant. Get from qc.vote info.parent id
        #Also not needed
