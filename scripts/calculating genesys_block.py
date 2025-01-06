import hashlib
import json
from datetime import datetime
def hash_block(block):
    """
    Calculates the SHA-256 hash of a block.
    """
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def calculate_genesis_nonce():
    """
    Calculates the nonce for the genesis block.
    """
    # Define the genesis block structure
    genesis_block = {
    'previous_hash': 64 * '0',
    'content': [{
        "id": "0",
        "sender_address": None,
        "recipient_address": 'b95226e8fe7ca8163ee5c7acc5cb3d53d3b41bb14ef1a9b7d30f0d9c264f8e4e',
        "amount": 100,
        "public_key": None,
        "signature": None
    }],
    'date': int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
    'nonce': '21179738'
}

    difficulty = 6  # Number of leading zeros required
    target_prefix = "0" * difficulty

    nonce = 0
    while True:
        genesis_block["nonce"] = nonce
        block_hash = hash_block(genesis_block)
        if block_hash.startswith(target_prefix):
            print(f"Genesis block found! Nonce: {nonce}, Hash: {block_hash}")
            return genesis_block
        nonce += 1

# Calculate the nonce for the genesis block
genesis_block = calculate_genesis_nonce()
