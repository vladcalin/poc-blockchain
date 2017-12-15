import datetime
import json
import uuid

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from blockchain.block.content.base import BaseContent

TX_REPR = """Transaction:
    - sender:   {}
    - receiver: {}
    - amount:   {}
    - ts:       {}
"""

SIGNED_TX_REPR = """SignedTransaction:
    - tx: {}
    - signature: {}
    - pub_key: {}
"""


class TransactionSigner(object):
    def __init__(self):
        pass

    def sign(self, tx, private_key, public_key, password=None):
        private_key = serialization.load_pem_private_key(
            private_key.encode(),
            password=password.encode(),
            backend=default_backend()
        )
        message = tx.to_binary()
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        signature = signature.hex()
        public_key = public_key.encode().hex()
        return SignedTransaction(tx, signature, public_key)

    def verify(self, signed_tx):
        public_key_data = bytes.fromhex(signed_tx.pub_key)
        public_key_from_pem = load_pem_public_key(public_key_data,
                                                  default_backend())
        message = signed_tx.tx.to_binary()
        signature = bytes.fromhex(signed_tx.signature)
        public_key_from_pem.verify(signature,
                                   message,
                                   padding.PSS(
                                       mgf=padding.MGF1(hashes.SHA256()),
                                       salt_length=padding.PSS.MAX_LENGTH
                                   ),
                                   hashes.SHA256())


class SignedTransaction(BaseContent):
    """A signed transaction

    Attributes:
        tx (Transaction):
            The transaction that is signed
        signature (str):
            The signature of the transaction, if available, as a hex string
        pub_key (str):
            The public key for verifying the transaction signature, if 
            available. Is a hex string
    """
    fields = ['tx', 'signature', 'pub_key']

    def __init__(self, tx, signature, pub_key):
        """Wraps a transaction"""
        self.tx = tx
        self.signature = signature
        self.pub_key = pub_key

    def to_binary(self):
        tx = self.tx.to_dict()
        return json.dumps({'tx': tx, 'signature': self.signature,
                           'pub_key': self.pub_key}, sort_keys=True).encode()

    @classmethod
    def from_binary(cls, binary):
        data = json.loads(binary.decode())
        return cls(Transaction.from_binary(data['tx'].encode()), data['signature'],
                   data['pub_key'])

    def __repr__(self):
        return SIGNED_TX_REPR.format(
            self.tx, self.signature, self.pub_key
        )


class Transaction(BaseContent):
    TS_FORMAT = '%Y-%m-%d %H:%M:%S:%f'
    fields = ['sender', 'receiver', 'amount', 'ts']

    def __init__(self, sender, receiver, amount, ts=None, id=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.ts = ts or datetime.datetime.now().strftime(self.TS_FORMAT)

    @classmethod
    def create(cls, sender, receiver, amount):
        return cls(sender, receiver, amount)

    def __repr__(self):
        return TX_REPR.format(self.sender, self.receiver, self.amount, self.ts)

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'ts': self.ts
        }
