import getpass
import os.path

import click
import sys

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
            click.style('Wallet already exists. Choose another name', fg='red'))
        sys.exit(-1)
    password = getpass.getpass('Wallet password: ')
    click.echo(click.style('Creating wallet...', fg='green'))
    wallet = Wallet.create_new(name, password)
    wallet.write_to_file(wallet_path)
    click.echo(click.style('Done.', fg='green'))
    click.echo('Wallet created at ' + wallet_path)


@cli.command('list')
def wallet_list():
    if not os.path.isdir(STORAGE):
        return
    click.echo(click.style('Wallets:', fg='yellow'))
    for file in sorted(os.listdir(STORAGE)):
        click.echo('\t> {}'.format(file.replace('.wallet', '')))


if __name__ == '__main__':
    cli()
