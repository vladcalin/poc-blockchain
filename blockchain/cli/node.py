import os.path
import sys

import click
import logging
from gunicorn.app.base import Application

from blockchain.node.handler import app
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

    os.system('gunicorn -w 4 -b 0.0.0.0:{} blockchain.node.handler:app'.format(
        NETWORK_PORT))


if __name__ == '__main__':
    cli()
