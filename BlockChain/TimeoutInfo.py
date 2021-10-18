"""
Timeout Info
"""
class TimeoutInfo:
    def __init__(self, round, high_qc, sender, signature):
        self.round = round
        self.high_qc = high_qc
        self.sender = sender
        self.signature = signature
