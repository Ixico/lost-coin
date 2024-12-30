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
    Calculates the nonce for the given genesis block.
    """
    genesis_block = {
        'previous_hash': '0' * 64,
        'content': [{
            "id": None,
            "type": "coinbase",
            "inputs": [],
            "outputs": [{"address": "b5a83945ed36e72cda3a3f26357bd17bfa78b0a79dee0ad95b32b52241008ad7", "amount": 100}],
            "date": int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
            "block_index": 0,
            "signature": None
        }],
        'date': int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
        'nonce': ''
    }

    difficulty = 4  # Number of leading zeros required
    target_prefix = "0" * difficulty

    nonce = 0
    while True:
        genesis_block['nonce'] = nonce
        block_hash = hash_block(genesis_block)
        if block_hash.startswith(target_prefix):
            return genesis_block, block_hash
        nonce += 1

# Execute the calculation
genesis_block, block_hash = calculate_genesis_nonce()
print("Genesis Block:", genesis_block)
print("Block Hash:", block_hash)