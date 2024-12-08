from collections import deque
import communication
from common import STOP_EVENT, logger
import block
from Crypto.Random import get_random_bytes
import time

TRANSACTIONS = deque()


def get_content():
    return [x['content'] for x in TRANSACTIONS]


def add(transaction):
    logger.debug(f'Adding transaction to mine: {transaction}')
    TRANSACTIONS.append(transaction)


# todo: enclosing multiple transactions into one block
def start_mining(miner_address):
    while not STOP_EVENT.is_set():
        try:
            transactions = list(TRANSACTIONS)
            new_block = block.create_new_block(transactions, miner_address)
            logger.debug(f'Mining block: {new_block}')
        except IndexError:
            time.sleep(1)
            continue

        # Proces mining
        while not STOP_EVENT.is_set():
            nonce = get_random_bytes(64).hex()
            new_block['nonce'] = nonce
            if block.is_mined(new_block):
                logger.info(f'Mined block: {new_block}')
                block.add_if_valid(new_block)
                communication.broadcast(new_block, 'block')
                TRANSACTIONS.clear()
                break
