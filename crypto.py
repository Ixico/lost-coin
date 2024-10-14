from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

VALIDITY_TEST = b'lost_coin'


def prepare_key_metadata(password: str):
    salt = get_random_bytes(16)
    key = calculate_pbkdf2(password, salt)
    cipher = AES.new(key, AES.MODE_EAX)
    result = cipher.encrypt(VALIDITY_TEST)
    return ':'.join([salt.hex(), result.hex(), cipher.nonce.hex()])


def decrypt(content, key, nonce):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(content)


def derive_valid_key(password: str, key_metadata: str):
    salt, encrypted_validity_test, nonce = key_metadata.split(':')
    derived_key = calculate_pbkdf2(password, bytes.fromhex(salt))
    if decrypt(bytes.fromhex(encrypted_validity_test), derived_key, bytes.fromhex(nonce)) != VALIDITY_TEST:
        raise CryptoException('Invalid password')
    return derived_key.hex()


def calculate_pbkdf2(password: str, salt: bytes):
    return PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA256)


def is_password_strong(password):
    return len(password) > 12


def generate_keys(master_key):
    key = RSA.generate(2048)
    return key.export_key(
        passphrase=master_key,  # todo: it shouldn't be passed in hex probably
        pkcs=8,
        protection='PBKDF2WithHMAC-SHA256AndAES256-CBC',
        prot_params={'iteration_count': 1000}
    )

class CryptoException(Exception):
    pass

