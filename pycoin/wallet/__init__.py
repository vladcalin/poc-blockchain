import getpass
import urllib.request
import os.path
import json

import click
import sys

from pycoin.client import BlockchainHttpClient
from pycoin.consts import Network, Paths
from pycoin.exceptions import ClientError
from pycoin.validators import is_valid_address
from pycoin.wallet.wallet import WalletManager


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
@click.option('--node', default='127.0.0.1:{}'.format(Network.NODE_PORT))
def wallet_inspect(name, node):
    if not WalletManager.wallet_exists(name):
        if is_valid_address(name):
            address = name
        else:
            click.echo(
                click.style('Wallet does not exist and is not a valid address',
                            fg='red'))
            sys.exit(-1)
    else:
        with open(os.path.join(Paths.WALLET_DIR, name), 'r') as f:
            data = json.load(f)
        click.echo(click.style('Wallet info', fg='yellow'))
        click.echo('address = {}'.format(data['address']))
        address = data['address']
    client = BlockchainHttpClient(node)
    try:
        data = client.get_balance(address)
    except urllib.request.URLError as e:
        msg = 'Unable to contact node on {}: {}'.format(node, str(e))
        click.echo(click.style(msg, fg='red'))
        sys.exit(0)
    click.echo('balance = {}'.format(data['balance']))
    click.echo('transactions:')
    for tx in data['transactions']:
        if 'received' in tx:
            msg = '+ {} from {}'.format(tx['received'], tx['from'])
            color = 'green'
        elif 'reward' in tx:
            msg = '+ {} (reward)'.format(tx['reward'])
            color = 'green'
        else:
            msg = '- {} to {}'.format(tx['sent'], tx['to'])
            color = 'red'
        click.echo(click.style(msg, fg=color))


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
    try:
        client = BlockchainHttpClient(node)
        resp = client.submit_tx(tx)
    except ClientError as e:
        click.echo(click.style(str(e), fg='red'))
        sys.exit(-1)
    click.echo(click.style(resp, fg='green'))


# End Transactions


if __name__ == '__main__':
    cli()
