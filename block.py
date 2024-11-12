from dataclasses import dataclass
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from crypto import hash
from common import logger

BLOCKS = [{
    'previous_hash': 64 * '0',
    'content': 'COINBASE',
    'nonce': 128 * '0'
}]
MINE_PADDING = 12


def get_blocks():
    return [b['content'] for b in BLOCKS]


def add_if_valid(block):
    if is_valid(block):
        logger.debug(f'Adding block to chain: {block}')
        BLOCKS.append(block)


# todo: allow forks
def is_valid(block):
    return block['previous_hash'] == hash_block(BLOCKS[-1]) and is_mined(block)


def is_mined(block):
    return 'nonce' in block and bin(int(hash_block(block), 16))[2:].zfill(256).startswith(MINE_PADDING * '0')


def hash_block(block):
    return hash(block['previous_hash'] + hash(block['content'] + block['nonce']))

# def mine():
#     while True:
#         nonce = get_random_bytes(32)
#         digest = SHA256.new(nonce).hexdigest()
#         binary_digest = bin(int(digest, 24))[2:].zfill(256)
#         if binary_digest.startswith(16 * '0'):
#             return binary_digest
