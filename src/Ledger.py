import json
from datetime import datetime
import Block
import QC
import Ledger
import hashlib
import logging

class Ledger():
    """Ledger Module"""
    def __init__(self, server_name, mempool, logger):
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        self.file_name = 'ledger_' +  str(server_name) + "_" + str(ts) + ".json"
        self.file = open(self.file_name, "x")
        self.file.close()
        self.root = LedgerNode("Genesis", "Genesis-1", "")
        self.curr = self.root
        self.pending_blocks = {}
        self.commited_blocks = {}
        self.prev_commit_id = self.root.block_id
        self.mempool = mempool
        self.logger = logger
        self.logger.debug('Ledger module init complete')

    """
    Add the block to the Speculative Ledger Branch and return the new Ledger State
    """
    def speculate(self, blk):
        if blk.id in self.pending_blocks:
            return self.pending_state(blk.id)

        prev_block_id = blk.qc.vote_info.id
        node = self.getLedgerNode(prev_block_id, self.root)
        if node is None:
            node = self.root
        ledgerNode = LedgerNode(blk.id, node.id, blk.payload) # curr_node.id = Previous Level Ledger State Id for new Ledger Node
        node.children.append(ledgerNode)
        self.pending_blocks[blk.id] = blk
        self.logger.debug("New ledger state ")
        return ledgerNode.id


    """
    Return the Ledger State of the associated Block Id
    """
    def pending_state(self, block_id):
        self.logger.debug('Leadger state is ')
        return self.getLedgerNode(block_id, self.root).id


    """
    Commit all the transactions from Previous Commit(root) to the current Ledger State
    Prune other Ledger State Branches
    Cache the Block for future Reference
    """
    def commit(self, block_id):
        if block_id in self.commited_blocks or block_id == "Genesis" or block_id == "Genesis-1":
            return
        self.getTransactions(self.root, block_id, [])
        self.root = self.getLedgerNode(block_id, self.root)
        self.mempool.commitTransactions(self.commited_blocks[block_id].txn_id)
        self.logger.debug('Committing transactions')

    """
    Returns The Block that was recently commited
    """
    def committed_block(self, block_id):
        return self.commited_blocks[block_id] if block_id in self.commited_blocks else None
        # return self.commited_blocks[block_id] if self.commited_blocks.has_key(block_id) else None


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
                if val.block_id == "Genesis" or  val.block_id == "Genesis-1" or val.block_id in self.commited_blocks: #and val.parent_id == -1:
                    continue # genesis Block
                print("writing to file ", val.txns)
                self.file.write(val.txns + "\n")

                if val.block_id in self.pending_blocks:
                    self.commited_blocks[val.block_id] = self.pending_blocks[val.block_id]
                    del self.pending_blocks[val.block_id]

    """
    Takes Block Id and returns the Ledger Node( Ledger State )
    """
    def getLedgerNode(self, id, lnode):
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
        self.id = self.hashIt(str(parent_id) + str(txns))
        self.parent_id = parent_id
        self.children = []
        self.block_id = block_id

    def hashIt(self, str):
        return hashlib.sha256(str.encode('ascii')).hexdigest()
