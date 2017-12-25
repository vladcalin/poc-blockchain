import json
import time
import hashlib
import os.path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from pycoin.consts import Paths, InitialCapital
from pycoin.exceptions import NotEnoughBalanceError
from pycoin.wallet import KeySerializer
from pycoin.persistence.models import Block, Transaction, BlockData, Reward, db

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
    TX_PER_BLOCK = 1

    def __init__(self):
        if self.get_block_count() == 0:
            genesis_block = self.get_genesis_block()
            hash = self.hash_block(genesis_block)
            genesis_block['hash'] = hash
            self.persist_block(genesis_block)
        self.tx_queue = []

    def get_block_count(self):
        return Block.select().count()

    def get_blocks(self, start_index, end_index):
        start_index = self.force_int(start_index, default=0)
        end_index = self.force_int(end_index, default=self.get_block_count())
        return [b.to_dict() for b in
                Block.select().where(Block.index >= start_index,
                                     Block.index < end_index)]

    def force_int(self, item, *, default=None):
        try:
            return int(item)
        except (TypeError, ValueError):
            return default

    def get_genesis_block(self):
        return {
            'index': 0,
            'data': self.get_initial_capital_rewards(),
            'previous_hash': '',
            'timestamp': time.time(),
            'nonce': 0
        }

    def hash_block(self, block):
        content = json.dumps(block, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def format_content_entry(self, content_entry):
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
        if self.get_addr_balance(from_addr) < amount:
            raise NotEnoughBalanceError()
        tx_data['signature'] = signature
        tx_data['type'] = 'tx'
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
        return Block.select().where(
            Block.index == self.get_block_count() - 1).first()

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
            'index': last_block.index + 1,
            'previous_hash': last_block.hash,
            'timestamp': time.time(),
            'nonce': 0,
            'data': transactions
        }
        new_block['hash'] = self.hash_block(new_block)
        self.persist_block(new_block)
        self.tx_queue = []

    def persist_block(self, block_data):
        if isinstance(block_data, dict):
            block = Block.create(index=block_data['index'],
                                 previous_hash=block_data['previous_hash'],
                                 hash=block_data['hash'],
                                 ts=block_data['timestamp'],
                                 nonce=block_data['nonce'])
            for item in block_data['data']:
                if item['type'] == 'tx':
                    tx_obj = Transaction.create(from_addr=item['from'],
                                                to_addr=item['to'],
                                                amount=item['amount'],
                                                ts=item['ts'],
                                                signature=item['signature'],
                                                public_key=item['public_key'])
                    # create relation between block and current tx
                    block_relation = BlockData.create(block=block,
                                                      transaction=tx_obj,
                                                      reward=None)
                elif item['type'] == 'reward':
                    reward = Reward.create(to_addr=item['to'],
                                           amount=item['amount'],
                                           ts=item['ts'],
                                           reason=item['reason'],
                                           block=item.get('block'))
                    # create relation between block and current reward
                    block_relation = BlockData.create(block=block,
                                                      transaction=None,
                                                      reward=reward)
                else:
                    raise ValueError(
                        'Invalid block data type: {}'.format(item['type']))
        else:
            raise TypeError('Expected dict, got {} instead'.format(
                type(block_data).__name__
            ))
        db.commit()
        return block

    def get_address_info(self, address, items=('balance', 'txes')):
        txes = []
        balance = 0
        for item in Transaction.select().where(
                        (Transaction.to_addr == address) | (
                            Transaction.from_addr == address)):
            if item.to_addr == address:
                if 'txes' in items:
                    txes.append(
                        {'received': item.amount, 'from': item.from_addr,
                         'ts': item.ts})
                if 'balance' in items:
                    balance += item.amount
            else:
                if 'txes' in items:
                    txes.append(
                        {'sent': item.amount, 'to': item.to_addr,
                         'ts': item.ts})
                if 'balance' in items:
                    balance -= item.amount
        for item in Reward.select().where(Reward.to_addr == address):
            if 'txes' in items:
                txes.append({'reward': item.amount, 'ts': item.ts})
            if 'balance' in items:
                balance += item.amount
        txes = list(sorted(txes, key=lambda x: x['ts']))
        data = {}
        if 'txes' in items:
            data['transactions'] = txes
        if 'balance' in items:
            data['balance'] = balance
        return data

    def get_addr_balance(self, address):
        return self.get_address_info(address, items=('balance',))['balance']

    def get_initial_capital_rewards(self):
        rewards = []
        for owner in InitialCapital.INITIAL_OWNERS:
            rewards.append({
                'type': 'reward',
                'to': owner,
                'amount': InitialCapital.INITIAL_CAPITAL,
                'ts': time.time(),
                'reason': Reward.INITIAL_CAPITAL
            })
        return rewards
