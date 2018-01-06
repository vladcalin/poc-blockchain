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

from pycoin.client import BlockchainHttpClient
from pycoin.consts import Paths, Network
from pycoin.exceptions import ClientError
from pycoin.validators import is_valid_address
from pycoin.wallet.mnemonic import mnemonic_generate_sequence
from pycoin.wallet.serializers import KeySerializer


class Wallet(object):
    def __init__(self, pub_key, priv_key, locked=False):
        self.verify_key = self.validate_is_hex(pub_key)
        self.sign_key = self.validate_is_hex(priv_key)
        self.locked = locked

    def lock(self, password):
        if self.locked:
            raise RuntimeError('Wallet already locked')
        print('before lock')
        print('signing_key = ', self.sign_key)
        print('verify_key = ', self.verify_key)
        box = self.get_secret_box_from_password(password)
        locked_key = box.encrypt(self.sign_key.encode(),
                                 encoder=nacl.encoding.HexEncoder)
        self.sign_key = locked_key.decode()
        self.locked = True
        print('after lock')
        print('signing_key = ', self.sign_key)
        print('verify_key = ', self.verify_key)

    def unlock(self, password):
        if not self.locked:
            raise RuntimeError('Cannot unlock wallet twice')
        box = self.get_secret_box_from_password(password)
        print('before unlock')
        print('signing_key = ', self.sign_key)
        print('verify_key = ', self.verify_key)
        unlocked_key = box.decrypt(self.sign_key.encode(),
                                   encoder=nacl.encoding.HexEncoder)
        self.sign_key = unlocked_key.decode()
        self.locked = False
        print('after unlock')
        print('signing_key = ', self.sign_key)
        print('verify_key = ', self.verify_key)

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
            raise RuntimeError('Cannot sign with locked wallet')
        if isinstance(data, str):
            data = data.encode()
        sign_key = nacl.signing.SigningKey(bytes.fromhex(self.sign_key))
        signed = sign_key.sign(data, encoder=nacl.encoding.HexEncoder)
        return signed.signature.decode()

    def verify(self, message, signed):
        if isinstance(signed, str):
            signed = signed.encode()
        if isinstance(message, str):
            message = message.encode()
        verify_key = nacl.signing.VerifyKey(self.verify_key,
                                            encoder=nacl.encoding.HexEncoder)
        return verify_key.verify(message, signed)


class WalletManager(object):
    @classmethod
    def list_wallets(cls):
        return os.listdir(Paths.WALLET_DIR)

    @classmethod
    def create_wallet(cls, password):
        click.echo('Generating keys')
        mnemonic = ' '.join(mnemonic_generate_sequence())
        mnemonic_seed = hashlib.sha256(mnemonic.encode()).digest()
        signing_key = nacl.signing.SigningKey(mnemonic_seed)
        verify_key = signing_key.verify_key
        # create the wallet
        wallet = Wallet(
            verify_key.encode(encoder=nacl.encoding.HexEncoder).decode(),
            signing_key.encode(encoder=nacl.encoding.HexEncoder).decode(),
            locked=False
        )
        print('signing_key = ', wallet.sign_key)
        print('verify_key = ', wallet.verify_key)
        wallet.lock(password)
        return wallet

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
