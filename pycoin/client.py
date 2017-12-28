import json
import urllib.parse
import urllib.request

from pycoin.exceptions import ClientError


class BlockchainHttpClient(object):
    API_WALLET_INFO = '/wallets/info/{address}'
    API_TX_SUBMIT = '/tx/submit'

    def __init__(self, node_addr):
        self.node_addr = node_addr

    def get_node_addr(self):
        return 'http://{}/'.format(self.node_addr)

    def get_api_url(self, api_uri):
        return urllib.parse.urljoin(self.get_node_addr(), api_uri)

    def get_balance(self, address):
        req = urllib.request.Request(
            self.get_api_url(self.API_WALLET_INFO.format(address=address))
        )
        try:
            resp = urllib.request.urlopen(req)
        except urllib.request.HTTPError as e:
            txt = e.read().decode()
            err = ClientError(txt)
            err.message = txt
            raise err
        return json.loads(resp.read().decode())

    def submit_tx(self, tx_info):
        url = self.get_api_url(self.API_TX_SUBMIT)
        request = urllib.request.Request(
            url, data=urllib.parse.urlencode(tx_info).encode())
        try:
            resp = urllib.request.urlopen(request)
        except urllib.request.HTTPError as e:
            err = e.read().decode()
            err_obj = ClientError()
            err_obj.message = err
            raise err_obj
        return resp.read().decode()
