import pickle
import socketserver
import threading

import time

import logging

from blockchain.blockchain import Blockchain
from blockchain.network import NETWORK_PORT
from blockchain.node.discovery.udp_broadcast import UdpBroadcastPeerDiscovery
from .actions import Actions

blockchain = Blockchain()
discovery = UdpBroadcastPeerDiscovery()
logger = logging.getLogger('blockchain')


def add_peer(peer):
    blockchain.add_peer(peer)


class NodeServer(socketserver.ThreadingUDPServer):
    discovery_interval = 60

    def __init__(self, *args, **kwargs):
        super(NodeServer, self).__init__(*args, **kwargs)
        logger.info('Node started')
        threading.Thread(target=self.run_discovery).start()

    def shutdown(self):
        print('Shutting down node')

    def run_discovery(self):
        while True:
            nodes = discovery.discover()
            for node in nodes:
                logger.debug('Discovered peer {}'.format(node))
                add_peer(node)
            time.sleep(self.discovery_interval)


class NodeHandler(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        super(NodeHandler, self).__init__(*args, **kwargs)

    def handle(self):
        message, args = self.get_next_message()
        logger.debug('Known peers : {}'.format(blockchain.get_peer_count()))
        logger.debug('Message from {}: {}, {}'.format(
            self.client_address[0], message, args)
        )
        if message == Actions.HELLO:
            self.register_node(self.client_address[0])
            self.send_message(Actions.HELLO_RCV, None)
        elif message == Actions.HELLO_RCV:
            self.register_node(self.client_address[0])

    def send_message(self, header, args):
        self.request[1].sendto(pickle.dumps((header, args)),
                               (self.client_address[0], NETWORK_PORT))

    def get_next_message(self):
        message_header, args = pickle.loads(self.request[0].strip())
        return message_header, args

    def register_node(self, addr):
        logging.debug('Discovered peer: {}'.format(addr))
        add_peer(addr)
