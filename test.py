import random
import string

from blockchain.block.content.transaction import Transaction, SignedTransaction, \
    TransactionSigner
from blockchain.wallet import Wallet
from blockchain.block import Block

if __name__ == '__main__':
    genesis_block = Block()

    block = Block()
    for _ in range(5):
        tx = Transaction.create(random.choice(string.ascii_lowercase),
                                random.choice(string.ascii_lowercase),
                                random.randint(0, 100) + random.random())
        wallet = Wallet.load_from_file('.poc-blockchain/vlad.wallet')
        signed_tx = TransactionSigner().sign(
            tx, wallet.private_key, wallet.public_key, 'P@ssw0rd'
        )
        TransactionSigner().verify(signed_tx)

        block.add_content(signed_tx)
    print(block.content)
