import hashlib


class Sha256ProofOfWork(object):
    def prepare_block(self, current_block, prev_block):
        prev_block_hash = prev_block

    def block_to_hash(self, block):
        h = hashlib.sha256(block.to_binary())
