from collections import defaultdict

from QC import QC

class Block:
    def __init__(self, author : int, round : int, payload : str, qc : QC, id : str):
        self.author = author
        self.round = round
        self.payload = payload
        self.qc = qc
        self.id = id
        self.children = []
        #Parent id is redundant. Get from qc.vote info.parent id
        #Also not needed
