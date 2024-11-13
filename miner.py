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
def start_mining():
    while not STOP_EVENT.is_set():
        try:
            currently_mined = TRANSACTIONS[0]
            currently_mined['previous_hash'] = block.get_last_block_hash()
            logger.debug(f'Mining block {currently_mined}')
        except IndexError:
            time.sleep(1)
            continue
        while not STOP_EVENT.is_set():
            nonce = get_random_bytes(64).hex()
            currently_mined['nonce'] = nonce
            if block.is_mined(currently_mined):
                logger.info(f'Mined block: {currently_mined}')
                block.add_if_valid(currently_mined)
                communication.broadcast(currently_mined, 'block')
                TRANSACTIONS.popleft()
                break
