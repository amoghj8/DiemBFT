from collections import OrderedDict
import logging

"""
Mempool
"""
class Mempool:
    def __init__(self, logger):
        self.initial_transactions = OrderedDict()
        self.pending_transactions = OrderedDict()
        self.committed_transactions = {}
        self.acknowledged_transactions = {}
        self.logger = logger
        self.logger.debug('Mempool init complete')

    """
    Check to see if there any transactions that need to be served
    """
    def exists(self):
        return True if self.initial_transactions else False

    """
    Add the trasaction if not commited/not currently executing/not in queue
    """
    def addTransaction(self, key, val):
        if key not in self.initial_transactions and key not in self.committed_transactions and key not in self.pending_transactions:
            self.initial_transactions[key] = val
            print("setting initial transaction with key", key, " and value", val)
            return True
        return False


    """
    Return the Next transaction to be served
    Move the transaction to pending - indicating it is currenlt being served
    """
    def getTransactions(self):
        if self.initial_transactions:
            first_key = next(iter(self.initial_transactions))
            value = self.initial_transactions[first_key]
            self.pending_transactions[first_key] = value
            print("setting pending transaction with key ", first_key, "and value", self.pending_transactions[first_key])
            del self.initial_transactions[first_key]
            return (first_key, value)
        else: return None


    """
    Commit the Transaction - on Ledger.commit
    Remove it from the initial and pending queue if it exists
    """
    def commitTransactions(self, key):
        if key in self.initial_transactions:
            self.committed_transactions[key] = self.initial_transactions[key]
            print("committed transaction with key ", key, "and value", self.initial_transactions[key])
            del self.initial_transactions[key]

        if key in self.pending_transactions:
            self.committed_transactions[key] = self.pending_transactions[key]
            del self.pending_transactions[key]


    """
    On Receiving proposal message
    Move from initial queue to pending queue
    """
    def processTransaction(self, key):
        if key in self.initial_transactions:
            self.pending_transactions[key] = self.initial_transactions[key]
            print("moving transaction to pending queue with key ", key, "and value", self.pending_transactions[key])
            del self.initial_transactions[key]

    """
    Remove the Transaction from pending(executing) queue - on TC
    """
    def removePendingTransaction(self, key):
        if key in self.pending_transactions:
            print("removing peding transaction with key ", key)
            del self.pending_transactions[key]
