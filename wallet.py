import os, crypto
from pathlib import Path

WALLET_PATH = 'wallet'
METADATA_PATH = os.path.join(WALLET_PATH, 'metadata.txt')
master_key = None


def exists():
    return os.path.exists(WALLET_PATH)


def create(password):
    key_metadata = crypto.prepare_key_metadata(password)
    os.makedirs(WALLET_PATH)
    with open(METADATA_PATH, 'w') as file:
        file.write(key_metadata)
    unlock(password)


def unlock(password):
    global master_key
    with open(METADATA_PATH, 'r') as file:
        key_metadata = file.readline()
    try:
        master_key = crypto.derive_valid_key(password, key_metadata)
        return True
    except crypto.CryptoException:
        return False


def create_identity(name):
    generated_keys = crypto.generate_keys(master_key)
    identity_file_name = os.path.join(WALLET_PATH, f"{name}.pem")
    if os.path.exists(identity_file_name):
        raise WalletException(f"Identity with name {name} already exists.")
    with open(identity_file_name, 'wb') as file:
        file.write(generated_keys)


def get_identities():
    directory = Path(WALLET_PATH)
    return [file.stem for file in directory.glob('*.pem')]


class WalletException(Exception):
    pass
