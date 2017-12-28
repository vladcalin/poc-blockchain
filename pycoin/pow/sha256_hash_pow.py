import hashlib
import json
import re


class Sha256ProofOfWork(object):
    regex = re.compile(r'^0{3}.*')

    def __init__(self, tx_data: dict):
        self.tx_data = tx_data

    def search_for_correct_hash(self):
        current_nonce = 0
        while True:
            data = self.tx_data.copy()
            data['nonce'] = current_nonce
            current_hash = self.hash_block(data)
            if self.hash_is_valid(current_hash):
                return current_nonce, current_hash
            current_nonce += 1

    def hash_block(self, block):
        content = json.dumps(block, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def hash_is_valid(self, current_hash):
        return self.regex.match(current_hash) is not None
