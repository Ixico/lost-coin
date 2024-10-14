from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes


def prepare_key_metadata(password: str):
    salt = get_random_bytes(16)
    return f"{salt.hex()}:{hash_key(calculate_pbkdf2(password, salt))}"


def derive_valid_key(password: str, key_metadata: str):
    salt, key_hash = key_metadata.split(':')
    derived_key = calculate_pbkdf2(password, bytes.fromhex(salt))
    if hash_key(derived_key) != key_hash:
        raise Exception('Invalid password')
    return derived_key.hex()


def calculate_pbkdf2(password: str, salt: bytes):
    return PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA256)


def hash_key(key: bytes):
    h = SHA256.new()
    h.update(key)
    return h.hexdigest()


def is_password_strong(password):
    return len(password) > 12


def keys():
    from Crypto.PublicKey import RSA
    # Generate RSA key pair (2048 bits)
    key = RSA.generate(2048)
    key.public_key()
    return key.publickey().export_key(), key.export_key(passphrase=pwd,
                                                        pkcs=8,
                                                        protection='PBKDF2WithHMAC-SHA512AndAES256-CBC',
                                                        prot_params={'iteration_count': 131072}).export_key()
