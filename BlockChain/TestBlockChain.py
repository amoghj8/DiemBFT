import Block
import BlockTree
import QC
import VoteInfo
import unittest


class TestBlockTreeMethods (unittest.TestCase):

    def test_constructor(self):
        pending_votes = [1, 2, 3]
        high_qc = 1
        high_commit_qc = 1
        pending_block_tree = None
        blockTree = BlockTree.BlockTree(pending_votes, high_qc, high_commit_qc, pending_block_tree)
        self.assertEqual(blockTree.pending_votes, pending_votes)
        self.assertEqual(blockTree.high_qc, high_qc)
        self.assertEqual(blockTree.high_commit_qc, high_commit_qc)
        self.assertEqual(blockTree.pending_block_tree, pending_block_tree)

if __name__ == '__main__':
    unittest.main()
