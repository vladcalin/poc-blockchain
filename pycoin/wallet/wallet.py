import base64
import getpass
import hashlib
import json
import os.path
import pprint
import re
import time
import sys
import urllib.request
import urllib.parse

import click
import nacl.signing
import nacl.encoding
import nacl.secret
from nacl.exceptions import CryptoError

from pycoin.client import BlockchainHttpClient
from pycoin.consts import Paths, Network
from pycoin.exceptions import ClientError
from pycoin.validators import is_valid_address
from pycoin.wallet.mnemonic import mnemonic_generate_sequence
from pycoin.wallet.serializers import KeySerializer


class WalletError(Exception):
    """Generic wallet exception"""


class InvalidPasswordError(WalletError):
    """The password does not match for the wallet"""


class InvalidOperationError(WalletError):
    """An invalid operation was attempted over the wallet"""


class Wallet(object):
    def __init__(self, pub_key, priv_key, locked=False):
        self.verify_key = self.validate_is_hex(pub_key)
        self.sign_key = self.validate_is_hex(priv_key)
        self.locked = locked
        self.mnemonic_seed = None

    def lock(self, password):
        if self.locked:
            raise InvalidOperationError('Wallet already locked')
        box = self.get_secret_box_from_password(password)
        locked_key = box.encrypt(self.sign_key.encode(),
                                 encoder=nacl.encoding.HexEncoder)
        self.sign_key = locked_key.decode()
        self.locked = True

    def unlock(self, password):
        if not self.locked:
            raise InvalidOperationError('Cannot unlock wallet twice')
        box = self.get_secret_box_from_password(password)
        try:
            unlocked_key = box.decrypt(self.sign_key.encode(),
                                       encoder=nacl.encoding.HexEncoder)
        except CryptoError:
            raise InvalidPasswordError()
        self.sign_key = unlocked_key.decode()
        self.locked = False

    def get_secret_box_from_password(self, password):
        if isinstance(password, str):
            password = password.encode()
        password_to_secret = hashlib.sha256(password).digest()
        return nacl.secret.SecretBox(password_to_secret)

    def validate_is_hex(self, key):
        assert re.match(r'^[a-f0-9]+$', key) is not None
        return key

    @property
    def address(self):
        digest = hashlib.sha256(self.verify_key.encode())
        data = digest.digest()
        return base64.urlsafe_b64encode(data)[:35].decode() + ".py"

    def to_dict(self):
        if not self.locked:
            raise InvalidOperationError(
                'Cannot serialize while unlocked. It will leak '
                'the private key of the wallet')
        return {
            'public_key': self.verify_key,
            'private_key': self.sign_key,
            'address': self.address
        }

    def create_tx(self, receiver_addr, amount):
        tx_data = {
            'from': self.address,
            'to': receiver_addr,
            'amount': amount,
            'ts': time.time(),
            'public_key': self.verify_key
        }
        signature = self.sign(json.dumps(tx_data, sort_keys=True))
        tx_data['signature'] = signature.hex()
        return tx_data

    def sign(self, data):
        if self.locked:
            raise InvalidOperationError('Cannot sign with locked wallet')
        if isinstance(data, str):
            data = data.encode()
        sign_key_raw = bytes.fromhex(self.sign_key)
        sign_key = nacl.signing.SigningKey(sign_key_raw)
        signed_hex = sign_key.sign(data,
                                   encoder=nacl.encoding.HexEncoder).decode()
        return signed_hex

    def verify(self, signed):
        if isinstance(signed, str):
            signed = signed.encode()
        verify_key_raw = nacl.signing.VerifyKey(self.verify_key.encode(),
                                                encoder=nacl.encoding.HexEncoder)
        return verify_key_raw.verify(signed, encoder=nacl.encoding.HexEncoder)


class WalletManager(object):
    @classmethod
    def list_wallets(cls):
        return os.listdir(Paths.WALLET_DIR)

    @classmethod
    def create_wallet(cls, password):
        click.echo('Generating keys')
        mnemonic = ' '.join(mnemonic_generate_sequence(words=32))
        return cls.create_from_mnemonic_and_password(mnemonic, password)

    @classmethod
    def wallet_exists(cls, name):
        return os.path.isfile(os.path.join(Paths.WALLET_DIR, name))

    @classmethod
    def get_wallet(cls, name):
        if not cls.wallet_exists(name):
            click.echo(click.style('Wallet does not exist', fg='red'))
            return None
        with open(os.path.join(Paths.WALLET_DIR, name)) as f:
            data = json.load(f)
        pub_key = data['public_key']
        priv_key = data['private_key']
        return Wallet(pub_key, priv_key)

    @classmethod
    def create_from_mnemonic_and_password(cls, mnemonic, password):
        mnemonic_seed = hashlib.sha256(mnemonic.encode()).digest()[:32]
        signing_key = nacl.signing.SigningKey(mnemonic_seed)
        verify_key = signing_key.verify_key
        # create the wallet
        wallet = Wallet(
            verify_key.encode(encoder=nacl.encoding.HexEncoder).decode(),
            signing_key.encode(encoder=nacl.encoding.HexEncoder).decode(),
            locked=False
        )
        wallet.lock(password)
        wallet.mnemonic_seed = mnemonic
        return wallet
