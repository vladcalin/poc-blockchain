import datetime


class Transaction(object):
    TS_FORMAT = '%Y-%m-%d %H:%M:%S:%f'

    def __init__(self, sender, receiver, amount, ts=None, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.ts = ts or datetime.datetime.now()
        self.signature = signature or self.sign()

    def sign(self):
        """Signs the current transaction"""
        return b''

    def to_binary(self):
        return '{};{};{};{};'.format(
            self.sender, self.receiver, self.amount,
            self.format_ts(self.ts), self.signature.hex()
        ).encode()

    @classmethod
    def from_binary(cls, binary_string):
        sender, receiver, amount, ts, signature_hex = binary_string.split(';')
        amount = float(amount)
        ts = datetime.datetime.strptime(ts, cls.TS_FORMAT)
        signature = bytes.fromhex(signature_hex)
        return cls(sender, receiver, amount, ts, signature)

    def format_ts(self, ts):
        return ts.strftime(self.TS_FORMAT)
