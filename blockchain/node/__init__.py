from .handler import Actions, NodeHandler


class NodeDiscoveryStrategy(object):
    def discovery(self):
        pass


class UdpBroadcastDiscoveryStrategy(NodeDiscoveryStrategy):
    pass
