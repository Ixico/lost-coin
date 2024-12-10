import hashlib
from datetime import datetime

import json
from common import logger
from crypto import hash

BLOCKS = [{
    'previous_hash': 64 * '0',
    'content': [{
        "id": None,
        "type": "coinbase",
        "inputs": [],
        "outputs": [{"address": "b95226e8fe7ca8163ee5c7acc5cb3d53d3b41bb14ef1a9b7d30f0d9c264f8e4e", "amount": 100}],
        "date": int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
        "block_index": 0,
        "signature": None
    }],
    'date': int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
    'nonce': '6756'
}]
MINE_PADDING = 4
# todo: scale difficulty over time?

def get_last_block_hash():
    return hash_block(BLOCKS[-1])


def get_blocks_content():
    return [b['content'] for b in BLOCKS]


def get_block_details(i):
    block_details = BLOCKS[i].copy()
    block_details['hash'] = hash_block(block_details)
    block_details['date'] = str(datetime.fromtimestamp(block_details['date'] / 1000))
    return block_details

def add_if_valid(block):
    # todo: validate block contains all required fields
    if not is_valid(block):
        logger.error(f"Block is not valid: {block}")
        return

    # Walidacja transakcji w bloku
    for tx in block['content']:
        if not isinstance(tx, dict) or 'id' not in tx or 'outputs' not in tx:
            logger.error(f"Invalid transaction in block: {tx}")
            return

    logger.debug(f"Adding block to chain: {block}")
    BLOCKS.append(block)


# todo: allow forks
def is_valid(block):
    return block['previous_hash'] == hash_block(BLOCKS[-1]) and is_mined(block)


def is_mined(block):
    return 'nonce' in block and bin(int(hash_block(block), 16))[2:].zfill(256).startswith(MINE_PADDING * '0')


def hash_block(block):
    """
    Oblicza hash bloku.
    """
    try:
        # Sprawdź, czy przetwarzasz transakcję zamiast bloku
        if 'content' not in block:
            transaction_string = json.dumps(block, sort_keys=True).encode()
            return hashlib.sha256(transaction_string).hexdigest()

        # Jeśli to blok, oblicz hash normalnie
        fields = (
            hash(block['previous_hash']) +
            hash(json.dumps(block['content'], sort_keys=True)) +
            hash(str(block['date'])) +
            hash(block['nonce'])
        )
        return hash(fields)
    except Exception as e:
        logger.error(f"Error hashing block: {e}")
        raise



def create_new_block(transactions):
    if not transactions:
        raise ValueError("Transaction list cannot be empty.")

    new_block = {
        "previous_hash": get_last_block_hash(),
        "content": transactions,
        "date": int(datetime.now().timestamp() * 1000),
        "nonce": None  # Ustawione podczas mining
    }
    return new_block

def calculate_balances():
    """
    Oblicza aktualne saldo każdego użytkownika na podstawie wszystkich transakcji w blockchainie.

    Returns:
        dict: Mapa adresów użytkowników do ich sald.
    """
    balances = {}
    for block in BLOCKS:
        for tx in block['content']:
            # Process outputs: Credit to recipient's address
            for output in tx.get('outputs', []):
                address = output["address"]
                amount = output["amount"]
                if address in balances:
                    balances[address] += amount
                else:
                    balances[address] = amount

            # Process inputs: Debit from sender's address
            for input_tx in tx.get('inputs', []):
                sender_address = input_tx.get("id")  # Sender's address stored in 'id'
                amount = input_tx.get("amount", 0)
                if sender_address in balances:
                    balances[sender_address] -= amount
                else:
                    balances[sender_address] = -amount
    return balances
