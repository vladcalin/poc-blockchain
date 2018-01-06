import re

from pycoin.wallet import WalletManager
from pycoin.wallet.wallet import Wallet


def test_wallet_manager_create_wallet():
    wallet = WalletManager.create_wallet('password')
    assert wallet.verify_key is not None
    assert wallet.sign_key is not None
    assert isinstance(wallet.verify_key, str)
    assert isinstance(wallet.sign_key, str)
    assert re.match(r'^[0-9a-f]{64}$', wallet.verify_key)
    assert re.match(r'^[0-9a-f]{208}$', wallet.sign_key)
    assert False


def test_wallet_sign():
    data = b'hello there'
    wallet = Wallet(
        # verify key
        '2952a47a18e130b01e319a43703ddc58eb5372d22d526d24f2a2847aab08ad45',
        # sign key
        'c58bf65e928d37119f8361842b39e4aae138cd9589e34f0fde7f67098b74e5c7'
        '2bf4993ec359ad0953075b2e4a39e8e4d1c940c1d61505f30526b0c734139ef5'
        '0577bd0628dc982b4cc1443ef2375d103f553efdc4a76409ac9082f21842dc7d'
        '6273c07c2494f7d4',
        locked=True)
    wallet.unlock('password')
    signed = wallet.sign(data)
    wallet.verify(data, signed)
    assert False
