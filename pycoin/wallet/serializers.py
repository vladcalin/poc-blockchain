

class KeySerializer(object):
    @classmethod
    def pub_key_to_hex(cls, pub_key):
        serialized = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized.hex()

    @classmethod
    def priv_key_to_hex(cls, priv_key, password):
        if isinstance(password, str):
            password = password.encode()
        encrypted_plain = priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        return encrypted_plain.hex()

    @classmethod
    def hex_to_pub_key(cls, pub_key):
        pub_key_raw = bytes.fromhex(pub_key)
        pub_key_obj = serialization.load_pem_public_key(
            pub_key_raw, backend=default_backend())
        return pub_key_obj

    @classmethod
    def hex_to_priv_key(cls, priv_key, password):
        if isinstance(password, str):
            password = password.encode()
        priv_key_raw = bytes.fromhex(priv_key)
        return serialization.load_pem_private_key(
            priv_key_raw, password, default_backend()
        )
