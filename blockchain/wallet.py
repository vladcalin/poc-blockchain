import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key


class Wallet(object):
    def __init__(self, name, private_key, public_key):
        self.name = name
        self.private_key = private_key
        self.public_key = public_key

    @classmethod
    def create_new(cls, name, password):
        if isinstance(password, str):
            password = password.encode()
        private_key = generate_private_key(public_exponent=65537,
                                           key_size=4096,
                                           backend=default_backend())
        public_key = private_key.public_key()
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return Wallet(name, private_key_pem.decode(), public_key_pem.decode())

    def write_to_file(self, filename):
        with open(filename, 'w') as f:
            data = {'name': self.name,
                    'private': self.private_key,
                    'publick': self.public_key}
            json.dump(data, f)

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls(data['name'], data['private'], data['public'])
