import base64
import getpass
import json
import os.path
import re
import time
import sys

import click
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

from pycoin.consts import Paths


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


if __name__ == '__main__':
    cli()
