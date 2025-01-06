import os
import sys
from common import logger
from Crypto.Hash import SHA256

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now you can import project modules
BASE_WALLET_PATH = os.path.join(os.path.join(project_root, 'wallets'))

def get_wallet_path(user_id):
    """
    Returns the wallet path for a specific user.
    """
    return os.path.join(BASE_WALLET_PATH, f'wallet_{user_id}')

# Example user data
user_id = "user2"
identity_name = "user_id_2"

def get_public_key(user_id, identity_name):
    wallet_path = get_wallet_path(user_id)
    identity_public_file_name = os.path.join(wallet_path, f"{identity_name}_public.pem")
    if not os.path.exists(identity_public_file_name):
        logger.error(f"Public key not found at path: {identity_public_file_name}")
        raise FileNotFoundError(f"Public key for identity {identity_name} does not exist for user {user_id}.")
    with open(identity_public_file_name, 'rb') as file:
        return file.read()



try:
    public_key_bytes = get_public_key(user_id, identity_name)
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    rsa_key = RSA.import_key(public_key_bytes)
    address = SHA256.new(rsa_key.public_key().export_key()).hexdigest()
    print(f"Public key for user_id={user_id}, identity_name={identity_name}: Address(SHA256) {address}")

except Exception as e:
    print(f"Error getting public key: {e}")
