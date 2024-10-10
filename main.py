import os
import crypto
import getpass

WALLET_PATH = 'wallet'
METADATA_PATH = os.path.join(WALLET_PATH, 'metadata.txt')


def wallet_exists():
    return os.path.exists(WALLET_PATH)


def create_wallet(key_info):
    os.makedirs(WALLET_PATH)
    with open(METADATA_PATH, 'w') as file:
        file.write(':'.join(map(str, key_info)))


def get_wallet_metadata():
    with open(METADATA_PATH, 'r') as file:
        return tuple(file.readline().split(':'))


def create_identity():
    pass


if wallet_exists():
    password = input('Enter password to unlock the wallet:\n')
    metadata = get_wallet_metadata()
    key_info = crypto.derive_key(password, metadata[0])
    print(crypto.hash_key(key_info[1]) == get_wallet_metadata()[1])
else:
    password = input('Enter strong password to create the wallet (min 12 characters):\n')
    if not crypto.is_password_strong(password):
        print("Password is too short.")
        exit()
    key_info = crypto.derive_key(password)
    print(key_info)
    create_wallet(key_info)
