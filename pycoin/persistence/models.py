import peewee

from pycoin.consts import Paths

print(Paths.BLOCKCHAIN_DB)
db = peewee.SqliteDatabase(Paths.BLOCKCHAIN_DB)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Transaction(BaseModel):
    from_addr = peewee.CharField(index=True)
    to_addr = peewee.CharField(index=True)
    amount = peewee.FloatField()
    ts = peewee.FloatField()
    signature = peewee.CharField(max_length=1500)
    public_key = peewee.CharField(max_length=2000)


class Reward(BaseModel):
    REASON_MINE = 'mine'
    INITIAL_CAPITAL = 'initial'

    to_addr = peewee.CharField()
    amount = peewee.FloatField()
    ts = peewee.FloatField()
    reason = peewee.CharField(choices=(INITIAL_CAPITAL, REASON_MINE))
    block = peewee.IntegerField(null=True)


class Block(BaseModel):
    index = peewee.IntegerField(primary_key=True)
    hash = peewee.CharField()
    previous_hash = peewee.CharField()
    nonce = peewee.IntegerField(default=0)
    ts = peewee.FloatField()

    def to_dict(self):
        print(
            self.index, self.hash, self.previous_hash, self.nonce, self.ts,
            self.get_data_as_list()
        )
        return {
            'index': self.index,
            'hash': self.hash,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'timestamp': self.ts,
            'data': self.get_data_as_list()
        }

    def get_data_as_list(self):
        data = []
        for item in self.data:
            if item.transaction is not None:
                tx = item.transaction
                data.append({
                    'type': 'tx',
                    'from': tx.from_addr,
                    'to': tx.from_addr,
                    'amount': tx.amount,
                    'ts': tx.ts,
                    'signature': tx.signature,
                    'public_key': tx.public_key
                })
            else:
                data.append({
                    'type': 'reward',
                    'to': item.reward.to_addr,
                    'amount': item.reward.amount,
                    'reason': item.reward.reason,
                    'block': item.reward.block
                })
        return data


class BlockData(BaseModel):
    block = peewee.ForeignKeyField(Block, related_name='data')
    transaction = peewee.ForeignKeyField(Transaction, null=True)
    reward = peewee.ForeignKeyField(Reward, null=True)


db.create_tables([Transaction, Reward, Block, BlockData], safe=True)
