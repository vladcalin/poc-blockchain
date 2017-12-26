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
    

class InitialCapital:
    INITIAL_CAPITAL = 50
    INITIAL_OWNERS = [
        'Ft2MXvu4sZUV42zD9AP-FBvB4k5fogDHX5z.py',
        'WpY7LfGKQCxwBgVIzdSuCaRyelwsa9jKMaP.py'
    ]


ensure_dir(Paths.WALLET_DIR)
ensure_dir(Paths.BLOCKCHAIN_DATA)
