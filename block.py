from datetime import datetime

from common import logger
from crypto import hash

BLOCKS = [{
    'previous_hash': 64 * '0',
    'content': 'COINBASE',
    'date': int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
    'nonce': 'd1ff6478faa875780d959dba441c8612c0be270df1bf5700d3573317422457a389ebd902a360fce7e9637767ace265a866e4a029d85906385c013b84f2a4f65d'
}]
MINE_PADDING = 17
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
    if is_valid(block):
        logger.debug(f'Adding block to chain: {block}')
        BLOCKS.append(block)


# todo: allow forks
def is_valid(block):
    return block['previous_hash'] == hash_block(BLOCKS[-1]) and is_mined(block)


def is_mined(block):
    return 'nonce' in block and bin(int(hash_block(block), 16))[2:].zfill(256).startswith(MINE_PADDING * '0')


def hash_block(block):
    fields = hash(block['previous_hash']) + hash(block['content']) + hash(str(block['date'])) + hash(block['nonce'])
    return hash(fields)
