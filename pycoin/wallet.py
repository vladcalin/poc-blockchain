import base64
import getpass
import json
import os.path
import pprint
import re
import time
import sys
import urllib.request
import urllib.parse

import click
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from pycoin.consts import Paths, Network


class Wallet(object):
    def __init__(self, pub_key, priv_key, password=None):
        self.pub_key = self.validate_is_hex(pub_key)
        self.priv_key = self.validate_is_hex(priv_key)
        self.password = password

    def validate_is_hex(self, key):
        assert re.match(r'^[a-f0-9]+$', key) is not None
        return key

    @property
    def address(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(self.pub_key.encode())
        data = digest.finalize()
        return base64.urlsafe_b64encode(data)[:35].decode() + ".py"

    def to_dict(self):
        return {
            'public_key': self.pub_key,
            'private_key': self.priv_key,
            'address': self.address
        }

    def create_tx(self, receiver_addr, amount):
        tx_data = {
            'from': self.address,
            'to': receiver_addr,
            'amount': amount,
            'ts': time.time(),
            'public_key': self.pub_key
        }
        signature = self.sign(json.dumps(tx_data, sort_keys=True))
        tx_data['signature'] = signature.hex()
        return tx_data

    def sign(self, data):
        if isinstance(data, str):
            data = data.encode()
        pub_key = KeySerializer.hex_to_pub_key(self.pub_key)
        priv_key = KeySerializer.hex_to_priv_key(self.priv_key, self.password)
        signature = priv_key.sign(data,
                                  padding.PSS(
                                      mgf=padding.MGF1(hashes.SHA256()),
                                      salt_length=padding.PSS.MAX_LENGTH
                                  ),
                                  hashes.SHA256())
        return signature


class KeySerializer(object):
    @classmethod
    def pub_key_to_hex(cls, pub_key):
        serialized = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized.hex()

    @classmethod
    def priv_key_to_hex(cls, priv_key, password):
        if isinstance(password, str):
            password = password.encode()
        encrypted_plain = priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        return encrypted_plain.hex()

    @classmethod
    def hex_to_pub_key(cls, pub_key):
        pub_key_raw = bytes.fromhex(pub_key)
        pub_key_obj = serialization.load_pem_public_key(
            pub_key_raw, backend=default_backend())
        return pub_key_obj

    @classmethod
    def hex_to_priv_key(cls, priv_key, password):
        if isinstance(password, str):
            password = password.encode()
        priv_key_raw = bytes.fromhex(priv_key)
        return serialization.load_pem_private_key(
            priv_key_raw, password, default_backend()
        )


class WalletManager(object):
    wallet_dir = os.path.join

    @classmethod
    def list_wallets(cls):
        return os.listdir(Paths.WALLET_DIR)

    @classmethod
    def create_wallet(cls, password):
        click.echo('Generating keys')
        private_key = rsa.generate_private_key(
            65537, key_size=4096, backend=default_backend()
        )
        public_key = private_key.public_key()
        wallet = Wallet(
            KeySerializer.pub_key_to_hex(public_key),
            KeySerializer.priv_key_to_hex(private_key, password),
            password
        )
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


@click.group()
def cli():
    pass


@cli.command('list')
def wallet_list():
    wallets = WalletManager.list_wallets()
    if not wallets:
        click.echo(click.style('No wallets found', fg='yellow'))
        sys.exit(-1)
    for wallet in os.listdir(Paths.WALLET_DIR):
        click.echo(wallet)


@cli.command('create')
@click.argument('name')
def wallet_create(name):
    if WalletManager.wallet_exists(name):
        click.echo(click.style('Wallet already exists', fg='red'))
        sys.exit(-1)
    password = getpass.getpass('Password: ')
    wallet = WalletManager.create_wallet(password)
    click.echo('Writing to file')
    with open(os.path.join(Paths.WALLET_DIR, name), 'w') as f:
        json.dump(wallet.to_dict(), f)


@cli.command('inspect')
@click.argument('name')
def wallet_inspect(name):
    if not WalletManager.wallet_exists(name):
        click.echo(click.style('Wallet does not exist', fg='red'))
        sys.exit(-1)
    with open(os.path.join(Paths.WALLET_DIR, name), 'r') as f:
        data = json.load(f)
    click.echo(click.style('Wallet info', fg='yellow'))
    click.echo('address = {}'.format(data['address']))


# Transactions

@cli.group('transaction')
def cli_transactions():
    pass


@cli_transactions.command('create')
@click.argument('wallet')
@click.argument('to')
@click.argument('amount', type=click.FLOAT)
@click.option('--node', default='127.0.0.1:{}'.format(Network.NODE_PORT))
def create_tx(wallet, to, amount, node):
    wallet = WalletManager.get_wallet(wallet)
    if not wallet:
        sys.exit(-1)
    click.echo('Sender address: {}'.format(wallet.address))
    wallet.password = getpass.getpass('Wallet password: ')
    tx = wallet.create_tx(to, amount)
    request = urllib.request.Request('http://' + node + '/tx/submit',
                                     data=urllib.parse.urlencode(tx).encode())
    resp = urllib.request.urlopen(request)
    click.echo(click.style(resp.read().decode(), fg='green'))


# End Transactions


if __name__ == '__main__':
    cli()
