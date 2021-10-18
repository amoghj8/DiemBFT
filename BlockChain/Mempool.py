from collections import OrderedDict

class Mempool:
    def __init__(self):
        self.initial_transactions = OrderedDict()
        self.pending_transactions = OrderedDict()
        self.committed_transactions = {}
        self.acknowledged_transactions = {}
    
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
            del self.initial_transactions[key]
    
    """
    Remove the Transaction from pending(executing) queue - on TC
    """
    def removePendingTransaction(self, key):
        if key in self.pending_transactions:
            del self.pending_transactions[key]