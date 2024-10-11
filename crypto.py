import hashlib
import secrets


def prepare_key_metadata(password: str):
    salt = secrets.token_bytes(16)
    return f"{salt.hex()}:{hash_key(calculate_pbkdf2(password.encode(), salt))}"


def derive_valid_key(password: str, key_metadata: str):
    salt, key_hash = key_metadata.split(':')
    derived_key = calculate_pbkdf2(password.encode(), bytes.fromhex(salt))
    if hash_key(derived_key) != key_hash:
        raise Exception('Invalid password')
    return derived_key.hex()


def calculate_pbkdf2(password: bytes, salt: bytes):
    iterations = 100_000
    key_length = 32
    return hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=key_length)


def hash_key(key: bytes):
    return hashlib.sha256(key).hexdigest()


def is_password_strong(password):
    return len(password) > 12


def keys():
    from Crypto.PublicKey import RSA
    # Generate RSA key pair (2048 bits)
    key = RSA.generate(2048)

    return key.publickey().export_key(format='DER'),  key.export_key(format='DER').hex()