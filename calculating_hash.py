import os
import sys
from Crypto.Hash import SHA256

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now you can import project modules
import wallet

# Example user data
user_id = "user2"
identity_name = "user_id_2"

try:
    address = wallet.generate_address(user_id, identity_name)
    print(f"Generated address for user_id={user_id}, identity_name={identity_name}: {address}")
except Exception as e:
    print(f"Error generating address: {e}")
