import hashlib
import secrets


def prepare_key_metadata(password: str):
    password = password.encode()
    salt = secrets.token_bytes(16)
    iterations = 100_000
    key_length = 32
    return f"{salt.hex()}:{hash_key(hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=key_length))}"


def derive_key(password, key_metadata):
    password = password.encode()
    salt = secrets.token_bytes(16)
    iterations = 100_000
    key_length = 32
    return salt.hex(), hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=key_length).hex()


def calculate_pbkdf2(password: bytes):
    salt = secrets.token_bytes(16)
    iterations = 100_000
    key_length = 32
    return salt, hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=key_length)


def hash_key(key: bytes):
    return hashlib.sha256(key).hexdigest()


def is_password_strong(password):
    return len(password) > 12
