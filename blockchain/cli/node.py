import os.path
import socketserver

import click

from blockchain.node import NodeHandler

STORAGE = os.path.join('.poc-blockchain', 'data')
if not os.path.isdir(STORAGE):
    os.makedirs(STORAGE, exist_ok=True)
NETWORK_PORT = 63889
NETWORK_BIND = '0.0.0.0'


@click.group()
def cli():
    pass


@cli.command('start')
def start():
    with socketserver.ThreadingUDPServer((NETWORK_BIND, NETWORK_PORT),
                                         NodeHandler) as node:
        node.serve_forever()


if __name__ == '__main__':
    cli()
