class BlockContent(object):
    def __init__(self, transactions=None):
        self.transactions = transactions or []

    def add_tx(self, transaction):
        self.transactions.append(transaction)


class Block(object):
    def __init__(self, index, content, proof_of_work):
        self.index = index
        self.content = content
        self.proof_of_work = proof_of_work

    def validate_pow(self):
        pass
