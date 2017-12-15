import json


class BaseContent(object):
    fields = []

    @classmethod
    def from_binary(cls, binary):
        data = json.loads(binary.decode())
        return cls(**data)

    def to_binary(self):
        data = {f: getattr(self, f) for f in self.fields}
        return json.dumps(data, sort_keys=True).encode()
