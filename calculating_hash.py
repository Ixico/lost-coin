from wallet import generate_address, create, create_identity, unlock
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256


# Przykładowe dane użytkownika
node_id = "user2"
identity_name = "user_id_2"

try:
    address = generate_address(node_id, identity_name)
    print(f"Generated address for node_id={node_id}, identity_name={identity_name}: {address}")
except Exception as e:
    print(f"Error generating address: {e}")