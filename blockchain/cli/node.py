import os.path

import click
import logging

import sys

from blockchain.node import NodeHandler
from blockchain.node.handler import NodeServer
from blockchain.network import NETWORK_PORT, STORAGE_DATA

STORAGE = STORAGE_DATA
if not os.path.isdir(STORAGE):
    os.makedirs(STORAGE, exist_ok=True)

logger = logging.getLogger('blockchain')
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


@click.group()
def cli():
    pass


@cli.command('start')
@click.option('--log', type=click.Choice(
    ('debug', 'info', 'warning', 'error', 'critical')), default='info')
def start(log):
    # init logging
    log_level = getattr(logging, log.upper())
    handler.setLevel(log_level)
    logger.setLevel(log_level)

    with NodeServer(('0.0.0.0', NETWORK_PORT), NodeHandler) as node:
        logger.info('Starting node')
        node.serve_forever()


if __name__ == '__main__':
    cli()
