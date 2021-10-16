import json
from datetime import datetime
import Block
import QC
import Ledger
import hashlib

class Ledger():
    """Ledger Module"""
    def __init__(self, server_name):
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        self.file_name = str(server_name) + "_" + str(ts) + ".json"
        # self.file_name = "test.json"
        self.file = open(self.file_name, "x")
        self.file.close()
        self.root = LedgerNode("idGenesis", None, "")
        self.curr = self.root
        self.pending_blocks = {}
        self.commited_blocks = {}
    
    
    """
    Add the block to the Speculative Ledger Branch and return the new Ledger State
    """
    def speculate(self, blk):
        prev_block_id = blk.qc.vote_info.id
        block_id = blk.id
        txns = blk.payload
        curr_node = self.root
        if self.curr.block_id == prev_block_id:
            curr_node = self.curr
        
        curr_node = self.getLedgerNode(prev_block_id, curr_node)
        if curr_node == None:
            curr_node = self.root
        
        ledgerNode = LedgerNode(block_id, curr_node.id, txns) # curr_node.id = Previous Level Ledger State Id for new Ledger Node
        curr_node.children.append(ledgerNode)
        self.curr = ledgerNode                                # Saving it here for faster lookup
        self.pending_blocks[block_id] = blk
        return ledgerNode.id

    
    """
    Return the Ledger State of the associated Block Id
    """
    def pending_state(self, block_id):
        return self.getLedgerNode(block_id, self.root).id

    
    """
    Commit all the transactions from Previous Commit(root) to the current Ledger State
    Prune other Ledger State Branches
    Cache the Block for future Reference
    """
    def commit(self, block_id):
        self.getTransactions(self.root, block_id, [])
        pass


    """
    Returns The Block that was recently commited
    """
    def committed_block(self, block_id):
        return self.commited_blocks[block_id] if self.commited_blocks.has_key(block_id) else None

    
    """
    Fetch All the Transactions from root to the Block Id till where the commit has to be done
    Call the Function write_to_file
    """
    def getTransactions(self, lnode, blk_id, lst ):
        lst.append(lnode)
        if( lnode.block_id == blk_id ):
            self.write_to_file(lst)
        for child in lnode.children:
            self.getTransactions(child, blk_id, lst)
        lst = lst[:-1]
    
    
    """
    Writes the Transactions to the file. Caches the committed Blocks 
    """
    def write_to_file(self, lst):
        with open(self.file_name, "a") as self.file:
            for val in lst:
                # if val.block_id == 0 and val.parent_id == -1:
                if val.block_id == "idGenesis" and val.parent_id == None:
                    continue # genesis Block
                print("hereeeee")
                self.file.write(val.txns + "\n")
                self.commited_blocks[val.block_id] = self.pending_blocks[val.block_id]
                del self.pending_blocks[val.block_id]

    
    """
    Takes Block Id and returns the Ledger Node( Ledger State )
    """
    def getLedgerNode(self, id, lnode):
        # print("keys", self.pending_blocks.keys())
        if(lnode.block_id == id):
            return lnode 
        
        my_node = None
        for val in lnode.children:
            my_node = self.getLedgerNode(id, val)
            if my_node is not None:
                return my_node

        return my_node

    
""" 
    block id : Id of the Block associated with the current Ledger State
    parent_id : Id of the parent Ledger Node
    txns : Transactions associated with the state
    id : Id formed by the hash of parent Ledger Id and Transactions - to maintain History
"""
class LedgerNode:
    def __init__(self, block_id, parent_id, txns = None):
        self.txns = txns
        # s = str(parent_id) + str(txns)
        # self.id = hashlib.sha224(s.encode('ascii')).hexdigest()
        self.id = block_id
        self.parent_id = parent_id
        self.children = []
        self.block_id = block_id