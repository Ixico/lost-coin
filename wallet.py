import os
from pathlib import Path
from common import logger, CommonException
import crypto

BASE_WALLET_PATH = 'wallets'
master_keys = {}


def get_wallet_path(node_id):
    """
    Zwraca ścieżkę do portfela dla konkretnego węzła.
    """
    return os.path.join(BASE_WALLET_PATH, f'wallet_{node_id}')


def get_metadata_path(node_id):
    """
    Zwraca ścieżkę do metadanych portfela dla konkretnego węzła.
    """
    return os.path.join(get_wallet_path(node_id), 'metadata.txt')


def exists(node_id):
    """
    Sprawdza, czy portfel dla danego węzła istnieje.
    """
    return os.path.exists(get_wallet_path(node_id))


def create(node_id, password):
    """
    Tworzy nowy portfel dla danego węzła.
    """
    wallet_path = get_wallet_path(node_id)
    key_metadata = crypto.prepare_key_metadata(password)
    os.makedirs(wallet_path, exist_ok=True)
    metadata_path = get_metadata_path(node_id)
    with open(metadata_path, 'w') as file:
        file.write(key_metadata)
    unlock(node_id, password)
    logger.info(f'Wallet for node {node_id} created successfully.')


def unlock(node_id, password):
    """
    Odblokowuje portfel dla danego węzła.
    """
    global master_keys
    metadata_path = get_metadata_path(node_id)
    if not os.path.exists(metadata_path):
        raise CommonException(f"Wallet for node {node_id} does not exist.")
    with open(metadata_path, 'r') as file:
        key_metadata = file.readline()
    master_keys[node_id] = crypto.derive_valid_key(password, key_metadata)
    logger.info(f'Wallet for node {node_id} unlocked successfully.')


def create_identity(node_id, name):
    """
    Tworzy nową tożsamość w portfelu dla danego węzła.
    """
    wallet_path = get_wallet_path(node_id)
    if node_id not in master_keys:
        raise ValueError(f"Wallet for node {node_id} is not unlocked. Please unlock it first.")
    generated_keys = crypto.generate_keys(master_keys[node_id])
    identity_file_name = os.path.join(wallet_path, f"{name}.pem")
    if os.path.exists(identity_file_name):
        logger.warn(f'Identity {name} already exists for node {node_id}.')
        raise CommonException()
    with open(identity_file_name, 'wb') as file:
        file.write(generated_keys)
    logger.info(f'Identity {name} created successfully for node {node_id}.')
    return True


def get_identities(node_id):
    """
    Pobiera wszystkie tożsamości dla danego węzła.
    """
    wallet_path = get_wallet_path(node_id)
    if not os.path.exists(wallet_path):
        raise CommonException(f"Wallet for node {node_id} does not exist.")
    directory = Path(wallet_path)
    return [file.stem for file in directory.glob('*.pem')]


def get_private_key(node_id, identity_name):
    """
    Pobiera klucz prywatny użytkownika na podstawie nazwy tożsamości i węzła.
    """
    wallet_path = get_wallet_path(node_id)
    identity_file_name = os.path.join(wallet_path, f"{identity_name}.pem")
    if not os.path.exists(identity_file_name):
        raise FileNotFoundError(f"Identity {identity_name} does not exist for node {node_id}.")
    with open(identity_file_name, 'rb') as file:
        return file.read()


def sign_transaction(node_id, transaction_id, identity_name):
    """
    Podpisuje ID transakcji za pomocą klucza prywatnego dla konkretnej tożsamości węzła.
    """
    private_key = get_private_key(node_id, identity_name)
    from Crypto.Signature import pkcs1_15
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256

    key = RSA.import_key(private_key)
    h = SHA256.new(transaction_id.encode())
    return pkcs1_15.new(key).sign(h).hex()
