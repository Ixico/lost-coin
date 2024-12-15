import os
from pathlib import Path
from Crypto.PublicKey import RSA
from common import logger, CommonException
import crypto

BASE_WALLET_PATH = 'wallets'
master_keys = {}


def get_wallet_path(user_id):
    """
    Returns the wallet path for a specific user.
    """
    return os.path.join(BASE_WALLET_PATH, f'wallet_{user_id}')


def get_metadata_path(user_id):
    """
    Returns the metadata path for a specific user's wallet.
    """
    return os.path.join(get_wallet_path(user_id), 'metadata.txt')


def exists(user_id):
    """
    Checks if a wallet exists for the given user.
    """
    return os.path.exists(get_wallet_path(user_id))


def create(user_id, password):
    """
    Creates a new wallet for the given user.
    """
    wallet_path = get_wallet_path(user_id)
    key_metadata = crypto.prepare_key_metadata(password)
    os.makedirs(wallet_path, exist_ok=True)
    metadata_path = get_metadata_path(user_id)
    with open(metadata_path, 'w') as file:
        file.write(key_metadata)
    unlock(user_id, password)
    logger.info(f'Wallet for user {user_id} created successfully.')


def unlock(user_id, password):
    """
    Unlocks the wallet for the given user.
    """
    global master_keys
    metadata_path = get_metadata_path(user_id)
    if not os.path.exists(metadata_path):
        raise CommonException(f"Wallet for user {user_id} does not exist.")
    with open(metadata_path, 'r') as file:
        key_metadata = file.readline()
    master_keys[user_id] = crypto.derive_valid_key(password, key_metadata)
    logger.info(f'Wallet for user {user_id} unlocked successfully.')


def create_identity(user_id, name):
    """
    Creates a new identity in the wallet for the given user.
    Automatically generates a private and public key pair, saving both.
    """
    wallet_path = get_wallet_path(user_id)
    if user_id not in master_keys:
        raise ValueError(f"Wallet for user {user_id} is not unlocked. Please unlock it first.")

    # Generate key pair
    private_key, public_key = crypto.generate_keys(master_keys[user_id])
    identity_file_name = os.path.join(wallet_path, f"{name}.pem")
    identity_public_file_name = os.path.join(wallet_path, f"{name}_public.pem")

    # Check if identity already exists
    if os.path.exists(identity_file_name):
        logger.warn(f'Identity {name} already exists for user {user_id}.')
        raise CommonException()

    # Save private key
    with open(identity_file_name, 'wb') as file:
        file.write(private_key)

    # Save public key
    with open(identity_public_file_name, 'wb') as public_file:
        public_file.write(public_key)

    logger.info(f'Identity {name} created successfully for user {user_id}.')
    return True


def get_identities(user_id):
    """
    Retrieves all identities for the given user, ensuring both private and public key files exist.
    """
    wallet_path = get_wallet_path(user_id)
    if not os.path.exists(wallet_path):
        raise CommonException(f"Wallet for user {user_id} does not exist.")

    directory = Path(wallet_path)
    identities = []

    for private_key_file in directory.glob('*.pem'):
        if not private_key_file.name.endswith('_public.pem'):
            identity_name = private_key_file.stem
            public_key_file = directory / f"{identity_name}_public.pem"
            if public_key_file.exists():
                identities.append(identity_name)

    return identities


def get_private_key(user_id, identity_name, password):
    """
    Retrieves the private key for a user's identity, decrypted with the password.
    """
    wallet_path = get_wallet_path(user_id)
    identity_file_name = os.path.join(wallet_path, f"{identity_name}.pem")
    salt_file_name = get_metadata_path(user_id)
    if not os.path.exists(identity_file_name):
        raise FileNotFoundError(f"Private key for identity {identity_name} does not exist for user {user_id}.")
    with open(salt_file_name, 'r') as file:
        line = file.readline()
        salt = line.split(':')[0]
    salt = bytes.fromhex(salt)
    with open(identity_file_name, 'rb') as file:
        encrypted_key = file.read()

    return crypto.restore_key(encrypted_key, password, salt)


def get_public_key(user_id, identity_name):
    """
    Retrieves the public key for a user's identity.
    """
    wallet_path = get_wallet_path(user_id)
    identity_public_file_name = os.path.join(wallet_path, f"{identity_name}_public.pem")
    if not os.path.exists(identity_public_file_name):
        raise FileNotFoundError(f"Public key for identity {identity_name} does not exist for user {user_id}.")
    with open(identity_public_file_name, 'rb') as file:
        return file.read()


def generate_address(user_id, identity_name):
    """
    Generates a SHA256 address for a user's identity based on the public key.
    """
    public_key_bytes = get_public_key(user_id, identity_name)
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    rsa_key = RSA.import_key(public_key_bytes)
    address = SHA256.new(rsa_key.public_key().export_key()).hexdigest()

    return address
