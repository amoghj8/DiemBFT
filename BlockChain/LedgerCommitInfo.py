import hashlib

class LedgerCommitInfo():
	"""LedgerCommitInfo"""
	def __init__(self, commit_state_id, vote_info_hash):
		super(LedgerCommitInfo, self).__init__()
		self.commit_state_id = commit_state_id
		self.vote_info_hash = vote_info_hash

	def get_hash(self):
		s = str(self.commit_state_id) + str(self.vote_info_hash)
		return hashlib.sha224(s.encode('ascii')).hexdigest()
		