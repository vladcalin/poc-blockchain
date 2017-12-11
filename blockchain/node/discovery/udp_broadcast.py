import pickle
import socket

from .base import BasePeerDiscovery
from blockchain.node.actions import Actions
from blockchain.network import NETWORK_PORT


class UdpBroadcastPeerDiscovery(BasePeerDiscovery):
    hello_action = pickle.dumps((Actions.HELLO, None))

    def discover(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(self.hello_action, ('255.255.255.255', NETWORK_PORT))
        return []
