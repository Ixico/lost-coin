import hashlib
import json
from datetime import datetime

from anytree import Node, RenderTree, AsciiStyle
from anytree.search import findall, find

from common import logger
from crypto import hash

GENESIS = Node(name='genesis', body={
    'previous_hash': 64 * '0',
    'content': [{
        "id": "1",
        "sender_address": None,
        "recipient_address": 'c52155717762ff290836cb04895390ac69518c222c68554ccfd4a324a5cc4aed',
        "amount": 100,
        "public_key": None,
        "signature": None
    }],
    'date': int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
    'nonce': '866648'
})

MINE_PADDING = 6
# todo: scale difficulty over time?

def get_last_block_hash():
    leaves = findall(GENESIS, filter_=lambda node: node.is_leaf)
    last_block = max(leaves, key=lambda node: node.depth).body
    return hash_block(last_block)


def is_in_blokchain_with_id(block_id):
    return find(GENESIS, filter_=lambda node: node.body['content'][0]['id'] == block_id) is not None



def get_blocks_content():
    leaves = findall(GENESIS, filter_=lambda node: node.is_leaf)
    last_block = max(leaves, key=lambda node: node.depth)
    return [b.body['content'] for b in last_block.ancestors + (last_block,)]


def add_if_valid(block):
    if not is_mined(block):
        logger.error(f"Block is not mined: {block}")
        return
    leaf = find(GENESIS, filter_=lambda node: hash_block(node.body) == block['previous_hash'])
    if leaf is None:
        logger.error(f"Block with hash {block['previous_hash']} not found in blokchain.")
        return
    logger.debug(f"Adding block to chain: {block}")
    Node(name=hash_block(block), parent=leaf, body=block)
    print(RenderTree(GENESIS, style=AsciiStyle()).by_attr())


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
