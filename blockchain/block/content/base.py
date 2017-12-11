import pickle


class BaseContent(object):
    @classmethod
    def from_binary(cls, binary):
        return pickle.loads(binary)

    def to_binary(self):
        return pickle.dumps(self)
