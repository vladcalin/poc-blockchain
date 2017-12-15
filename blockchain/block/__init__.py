class Block(object):
    def __init__(self):
        self.content = []

    def add_content(self, content):
        self.content.append(content)


class ProducedBlock(object):
    def __init__(self, block, hash, nonce, prev_block_hash):
        self.block = block
        self.hash = hash
        self.nonce = nonce
        self.prev_block_hash = prev_block_hash
