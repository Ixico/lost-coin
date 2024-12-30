import hashlib
from datetime import datetime

import json
from common import logger
from crypto import hash

BLOCKS = [{
    'previous_hash': 64 * '0',
    'content': [{
        "id": "1",
        "sender_address": None,
        "recipient_address": 'b95226e8fe7ca8163ee5c7acc5cb3d53d3b41bb14ef1a9b7d30f0d9c264f8e4e',
        "amount": 100,
        "public_key": None,
        "signature": None
    }],
    'date': int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
    'nonce': '21179738'
}]
MINE_PADDING = 6
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



def create_new_block(transaction):
    if not transaction:
        raise ValueError("Transaction list cannot be empty.")

    new_block = {
        "previous_hash": get_last_block_hash(),
        "content": transaction,
        "date": int(datetime.now().timestamp() * 1000),
        "nonce": None  # Ustawione podczas mining
    }
    return new_block

def calculate_balances():
    """
    Calculate balances for all addresses based on the blockchain content.

    Returns:
        dict: A dictionary mapping addresses to their balances.
    """
    balances = {}

    # Retrieve all block contents
    all_block_contents = get_blocks_content()

    # Iterate through each block's content
    for block_content in all_block_contents:
        for transaction in block_content:
            sender = transaction.get("sender_address")
            recipient = transaction.get("recipient_address")
            amount = float(transaction.get("amount", 0))

            # Deduct amount from sender's balance
            if sender:
                balances[sender] = balances.get(sender, 0) - amount

            # Add amount to recipient's balance
            if recipient:
                balances[recipient] = balances.get(recipient, 0) + amount

    return balances

def get_balance_for_address(address):
    """
    Get the balance of a specific address.

    Args:
        address (str): The address to check.

    Returns:
        float: The balance of the given address.
    """
    balances = calculate_balances()
    return balances.get(address, 0)
