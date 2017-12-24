import json
import time
import hashlib
import sqlite3
import os.path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from pycoin.consts import Paths
from pycoin.wallet import KeySerializer

"""

block = {
    'index': 1,
    'data': [data_entry...],
    'previous_hash': '....',
    'timestamp': ...,
    'hash': '...',
    'nonce': '...'
}   

transaction = {
    'type': 'tx',
    'from': '...',
    'to': '...',
    'signature': '...',
    'public_key': '...',
    'amount': '...',
    'ts': ...
}

reward = {
    'type': 'reward'
    'to': '...',
    'amount': ...,
    'ts': ...,
    'reason': {
        'id': 'mine|initial',
        ['block': 1]  // only for mine
    }
}

"""


class Blockchain(object):
    TX_PER_BLOCK = 3

    def __init__(self):
        self.db = []
        if len(self.db) == 0:
            genesis_block = self.get_genesis_block()
            hash = self.hash_block(genesis_block)
            genesis_block['hash'] = hash
            self.db.append(genesis_block)
        self.tx_queue = []

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

    def submit_transaction(self, from_addr, to_addr, amount, ts, signature,
                           public_key):
        signature_binary = bytes.fromhex(signature)
        tx_data = {'from': from_addr, 'to': to_addr, 'amount': amount,
                   'ts': ts, 'public_key': public_key}
        self.check_signature(
            json.dumps(tx_data, sort_keys=True).encode(),
            signature_binary,
            public_key)
        tx_data['signature'] = signature
        self.add_tx_to_queue(tx_data)
        self.trigger_generate_block()

    def check_signature(self, data, signature, public_key_hex):
        key = KeySerializer.hex_to_pub_key(public_key_hex)
        key.verify(
            signature, data, padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def get_last_block(self):
        return self.db[-1]

    def add_tx_to_queue(self, tx_data):
        self.tx_queue.append(tx_data)

    def trigger_generate_block(self):
        if len(self.tx_queue) >= self.TX_PER_BLOCK:
            print('Currently {} transactions in queue. '
                  'Generating new block'.format(len(self.tx_queue)))
            self.generate_new_block()

    def generate_new_block(self):
        last_block = self.get_last_block()
        transactions = self.tx_queue[:]
        new_block = {
            'index': last_block['index'] + 1,
            'previous_hash': last_block['hash'],
            'timestamp': time.time(),
            'nonce': 0,
            'data': transactions
        }
        new_block['hash'] = self.hash_block(new_block)
        self.db.append(new_block)
        self.tx_queue = []
