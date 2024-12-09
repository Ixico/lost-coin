import wallet
from Crypto.Hash import SHA256


# Przykładowe dane użytkownika
node_id = "user1"
identity_name = "user_id_1"

try:
    address = wallet.generate_address(node_id, identity_name)
    print(f"Generated address for node_id={node_id}, identity_name={identity_name}: {address}")
except Exception as e:
    print(f"Error generating address: {e}")