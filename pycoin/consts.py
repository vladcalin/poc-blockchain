import os.path


def ensure_dir(dirname):
    os.makedirs(dirname, exist_ok=True)


class Paths:
    ROOT_DIR = os.path.expanduser('~/.pycoin')
    WALLET_DIR = os.path.join(ROOT_DIR, 'wallets')
    BLOCKCHAIN_DATA = os.path.join(ROOT_DIR, 'data')
    BLOCKCHAIN_DB = os.path.join(BLOCKCHAIN_DATA, 'blockchain.db')


class Network:
    NODE_PORT = 64788


ensure_dir(Paths.WALLET_DIR)
ensure_dir(Paths.BLOCKCHAIN_DATA)
