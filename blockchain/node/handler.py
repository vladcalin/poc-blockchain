import logging
import pickle
import threading

import flask
import time

from blockchain.block.content.transaction import SignedTransaction, \
    TransactionSigner
from blockchain.blockchain import Blockchain
from blockchain.node.discovery.udp_broadcast import UdpBroadcastPeerDiscovery

app = flask.Flask('node')

blockchain = Blockchain()
discovery = UdpBroadcastPeerDiscovery()
logger = logging.getLogger('blockchain')


def discover_peers():
    while True:
        peers = discovery.discover()
        for peer in peers:
            blockchain.add_peer(peer)
        time.sleep(30)


threading.Thread(target=discovery.discover).start()


@app.route('/')
def index():
    return 'PoC Blockchain Node by Vlad Calin - version 0.0.1'


@app.route('/peers/count')
def peer_count():
    return str(blockchain.get_peer_count())


@app.route('/peers')
def peers():
    return '\n'.join(blockchain.iter_peers())


@app.route('/transactions/create', methods=['POST'])
def create_transaction():
    data = flask.request.get_data()
    transaction = SignedTransaction.from_binary(data)
    TransactionSigner().verify(transaction)
    return 'ok'
