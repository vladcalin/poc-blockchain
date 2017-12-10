import datetime
import uuid

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

TX_REPR = """Transaction:
    - id:       {}
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


class SignedTransaction(object):
    """A signed transaction
    
    Attributes:
        tx (Transaction):
            The transaction that is signed
        sig (str):
            The signature of the transaction, if available, as a hex string
        pub_key (str):
            The public key for verifying the transaction signature, if 
            available. Is a hex string
    """

    def __init__(self, tx):
        """Wraps a transaction
        
        Args:
            tx (Transaction):
                The transaction that is signed
        """
        self.tx = tx
        self.sig = None
        self.pub_key = None

    def sign(self, private_key, public_key, password=None):
        private_key = serialization.load_pem_private_key(
            private_key.encode(),
            password=password.encode(),
            backend=default_backend()
        )
        message = self.tx.to_binary()
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        self.sig = signature.hex()
        self.pub_key = public_key.encode().hex()

        public_key_from_pem = load_pem_public_key(public_key.encode(),
                                                  default_backend())
        public_key_from_pem.verify(signature,
                                   message,
                                   padding.PSS(
                                       mgf=padding.MGF1(hashes.SHA256()),
                                       salt_length=padding.PSS.MAX_LENGTH
                                   ),
                                   hashes.SHA256())

    def verify(self):
        public_key = bytes.fromhex(self.pub_key)
        public_key_from_pem = load_pem_public_key(public_key,
                                                  default_backend())
        signature = bytes.fromhex(self.sig)
        message = self.tx.to_binary()
        public_key_from_pem.verify(signature,
                                   message,
                                   padding.PSS(
                                       mgf=padding.MGF1(hashes.SHA256()),
                                       salt_length=padding.PSS.MAX_LENGTH
                                   ),
                                   hashes.SHA256())

    @classmethod
    def from_tx(cls, tx, private_key, public_key, password=None):
        signed = cls(tx)
        signed.sign(private_key, public_key, password=password)
        return signed

    def __repr__(self):
        return SIGNED_TX_REPR.format(
            self.tx, self.sig, self.pub_key
        )

    def to_binary(self):
        parts = [self.tx.to_binary().decode(), self.sig, self.pub_key]
        return ';'.join(parts).encode()

    @classmethod
    def from_binary(cls, binary):
        parts = binary.split(b';')
        tx_id, tx_sender, tx_receiver, tx_amount, tx_ts, sig, pubkey = parts
        tx_bin = b';'.join([tx_id, tx_sender, tx_receiver, tx_amount, tx_ts])
        tx = Transaction.from_binary(tx_bin)
        instance = cls(tx)
        instance.sig = sig
        instance.pub_key = pubkey


class Transaction(object):
    TS_FORMAT = '%Y-%m-%d %H:%M:%S:%f'

    def __init__(self, sender, receiver, amount, ts=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.ts = ts or datetime.datetime.now()

    def to_binary(self):
        parts = [self.id, self.sender, self.receiver, str(self.amount),
                 self.format_ts(self.ts)]
        return ';'.join(parts).encode()

    @classmethod
    def from_binary(cls, binary_string):
        id, sender, receiver, amount, ts = binary_string.split(b';')
        amount = float(amount)
        ts = datetime.datetime.strptime(ts, cls.TS_FORMAT)
        return cls(sender.decode(),
                   receiver.decode(),
                   amount,
                   ts,
                   id=id.decode())

    def format_ts(self, ts):
        return ts.strftime(self.TS_FORMAT)

    @classmethod
    def create(cls, sender, receiver, amount):
        return cls(sender, receiver, amount)

    def __repr__(self):
        return TX_REPR.format(
            self.id, self.sender, self.receiver, self.amount, self.ts)
