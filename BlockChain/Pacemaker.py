from sys import _current_frames
import Safety
import BlockTree
import QC
import VoteInfo
import TC
from collections import defaultdict

class Pacemaker:
    
    def __init__(self, replica):
        self.current_round = None
        self.last_round_tc = None
        self.pending_timeouts = defaultdict(list)
        self.replica = replica

    # set based on the config
    def get_round_timer(self, r):
        delta = 5              # Todo - fetch from config
        return 4 * delta

    
    #In Replica
    # Not required - Implement in Replica
    def start_timer(self, new_round):
        self.replica.round_done = True  # stop_timer(self.current_round)
        self.current_round = new_round
        # start_local_timer(self.get_round_timer())
        
    
    # In Replica
    # Function to be triggered on Timeout - in Replica
    def local_timeout_round(self):
        timeout_info = Safety.make_timeout(self.current_round, BlockTree.high_qc, self.last_round_tc)
        # Todo - Send BroadCast message

    
    def process_remote_timeout(self, tmo):
        tmo_info = tmo.tmo_info
        if tmo_info.round < self.current_round:
            return None

        lst_sender = [tmo_v.sender for tmo_v in self.pending_timeouts[tmo_info.round]]

        if tmo_info.sender not in lst_sender:
            self.pending_timeouts[tmo_info.round].append(tmo_info)
            lst_sender.append(tmo_info.sender)

        # Todo - read f from config
        f = 3
        if len(lst_sender) == f+1:
            # stop_timer(self.current_round)
            self.replica.round_done = True # Todo - Not sure if we shld stop timer
            self.local_timeout_round()

        lst_high_qc_round = [tmo_v.high_qc for tmo_v in self.pending_timeouts[tmo_info.round]]
        lst_signature     = [tmo_v.signature for tmo_v in self.pending_timeouts[tmo_info.round]]

        if len(lst_sender) == 2*f+1:
            return TC(tmo_info.round, lst_high_qc_round, lst_signature)
            
        return None


    def advance_round_tc(self, tc):
        if tc == None or tc.round < self.current_round:
            return False
        self.last_round_tc = tc
        self.start_timer(tc.round + 1)
        return True


    def advance_round_qc(self, qc):
        if qc.vote_info.round < self.current_round:
            return False
        self.last_round_tc = None
        self.start_timer(qc.vote_info + 1)
        return True