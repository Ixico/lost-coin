import os, crypto

WALLET_PATH = 'wallet'
METADATA_PATH = os.path.join(WALLET_PATH, 'metadata.txt')
IDENTITY_PATH = os.path.join(WALLET_PATH, 'identity')


def exists():
    return os.path.exists(WALLET_PATH)


def create(password):
    key_metadata = crypto.prepare_key_metadata(password)
    os.makedirs(WALLET_PATH)
    with open(METADATA_PATH, 'w') as file:
        file.write(key_metadata)
    with open(IDENTITY_PATH, 'w'):
        pass


def unlock(password):
    key_metadata = None
    with open(METADATA_PATH, 'r') as file:
        key_metadata = file.readline()
    key = crypto.derive_valid_key(password, key_metadata)



def create_identity(name):
    with open(os.path.join(IDENTITY_PATH, name)) as file:
        file.write()
