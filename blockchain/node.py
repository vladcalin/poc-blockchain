import socketserver


class NodeDiscoveryStrategy(object):
    def discovery(self):
        pass


class UdpBroadcastDiscoveryStrategy(NodeDiscoveryStrategy):
    pass


class Actions:
    HELLO = 'hello'


class NodeHandler(socketserver.BaseRequestHandler):
    def handle(self):
        pass
