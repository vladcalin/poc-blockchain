import getpass
import os.path

import click
import sys

from blockchain.transaction import Transaction, SignedTransaction
from blockchain.wallet import Wallet

STORAGE = '.poc-blockchain'


@click.group()
def cli():
    pass


@cli.command('create')
@click.argument('name')
def wallet_create(name):
    if not os.path.isdir(STORAGE):
        os.mkdir(STORAGE)
    wallet_path = os.path.join(STORAGE, name + '.wallet')
    if os.path.isfile(wallet_path):
        click.echo(
            click.style(
                'Wallet already exists. Choose another name', fg='red'))
        sys.exit(-1)
    password = getpass.getpass('Wallet password: ')
    click.echo(click.style('Creating wallet...', fg='green'))
    wallet = Wallet.create_new(name, password)
    wallet.write_to_file(wallet_path)
    click.echo(click.style('Done.', fg='green'))
    click.echo('Wallet created at ' + wallet_path)


@cli.command('inspect')
@click.argument('name')
@click.option('-t', '--with-transactions', is_flag=True)
def wallet_inspect(name, with_transactions=False):
    wallet_path = os.path.join(STORAGE, name + '.wallet')
    try:
        wallet = Wallet.load_from_file(wallet_path)
    except Exception as e:
        click.echo(click.style(
            'Unable to open wallet: {}'.format(e), fg='red'))
        sys.exit(-1)
    click.echo(click.style('Wallet info', fg='yellow'))
    click.echo('- Name:\t\t{}'.format(wallet.name))
    click.echo('- Address:\t{}'.format(wallet.address))
    click.echo('- Balance:\t{}'.format(wallet.get_current_balance()))
    if with_transactions:
        click.echo('- Transactions:')
        for transaction in wallet.get_transactions():
            click.echo(
                click.style('- Transaction ID: {}'.format(transaction.id),
                            fg='yellow'))


@cli.command('list')
def wallet_list():
    if not os.path.isdir(STORAGE):
        return
    click.echo(click.style('Wallets:', fg='yellow'))
    for file in sorted(os.listdir(STORAGE)):
        if not file.endswith('.wallet'):
            continue
        click.echo('\t> {}'.format(file.replace('.wallet', '')))


@cli.group('transaction')
def wallet_transaction():
    pass


@wallet_transaction.command('create')
@click.argument('wallet')
@click.argument('receiver')
@click.argument('amount', type=click.FLOAT)
def wallet_transaction_create(wallet, receiver, amount):
    try:
        wallet_path = os.path.join(STORAGE, wallet + '.wallet')
        wallet = Wallet.load_from_file(wallet_path)
    except Exception as e:
        click.echo(
            click.style('Unable to open wallet {}: {}'.format(wallet, e),
                        fg='red'))
        sys.exit(-1)
    click.echo('Loaded wallet')
    click.echo('Sender address: {}'.format(wallet.address))
    tx = Transaction.create(
        sender=wallet.address, receiver=receiver, amount=amount
    )
    password = getpass.getpass('Wallet password: ')
    try:
        signed_tx = SignedTransaction.from_tx(tx,
                                              wallet.private_key,
                                              wallet.public_key,
                                              password=password)
    except Exception as e:
        click.echo(
            click.style('Unable to open wallet {}: {}'.format(wallet.name, e),
                        fg='red'))
        sys.exit(-1)
    click.echo('Signed transaction')
    print(signed_tx.to_binary())


if __name__ == '__main__':
    cli()
