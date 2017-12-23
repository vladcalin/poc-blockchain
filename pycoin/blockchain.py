import json
import time
import hashlib
import sqlite3
import os.path

from pycoin.consts import Paths

"""

block = {
    'index': 1,
    'data': [data_entry...],
    'previous_hash': '....',
    'timestamp': ...,
    'hash': '...',
    'nonce': '...'
}   

data_entry = {
    'type': 'tx',
    'from': '...',
    'to': '...',
    'signature': '...',
    'public_key': '...',
    'amount': '...',
    'ts': ...
}

"""


class Blockchain(object):
    def __init__(self):
        self.db = []
        if len(self.db) == 0:
            genesis_block = self.get_genesis_block()
            hash = self.hash_block(genesis_block)
            genesis_block['hash'] = hash
            self.db.append(genesis_block)

    def get_block_count(self):
        return len(self.db)

    def get_blocks(self, start_index, end_index):
        start_index = self.force_int(start_index, default=0)
        end_index = self.force_int(end_index, default=self.get_block_count())
        return self.db[start_index:end_index]

    def force_int(self, item, *, default=None):
        try:
            return int(item)
        except (TypeError, ValueError):
            return default

    def get_genesis_block(self):
        return {
            'index': 0,
            'data': [],
            'previous_hash': 0,
            'timestamp': time.time(),
            'nonce': 0
        }

    def hash_block(self, block):
        content = json.dumps(block, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def format_content_entry(self, content_entry):
        if content_entry['type'] == 'tx':
            return json.dumps(content_entry, sort_keys=True)
