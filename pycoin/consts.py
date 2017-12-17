import os.path


def ensure_dir(dirname):
    os.makedirs(dirname, exist_ok=True)


class Paths:
    ROOT_DIR = os.path.expanduser('~/.pycoin')
    WALLET_DIR = os.path.join(ROOT_DIR, 'wallets')
    BLOCKCHAIN_DATA = os.path.join(ROOT_DIR, 'data')


ensure_dir(Paths.WALLET_DIR)
ensure_dir(Paths.BLOCKCHAIN_DATA)
