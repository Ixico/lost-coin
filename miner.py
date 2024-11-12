import queue

import communication
from common import STOP_EVENT, logger
import block
from Crypto.Random import get_random_bytes

TRANSACTIONS = queue.Queue()


def add(transaction):
    logger.debug(f'Adding transaction to mine: {transaction}')
    TRANSACTIONS.put(transaction)


# todo: enclosing multiple transactions into one block
def start_mining():
    while not STOP_EVENT.is_set():
        try:
            transaction = TRANSACTIONS.get(timeout=2)
            transaction['previous_hash'] = block.get_last_block_hash()
            logger.debug(f'Mining block {transaction}')
        except queue.Empty:
            continue
        while not STOP_EVENT.is_set():
            nonce = get_random_bytes(64).hex()
            transaction['nonce'] = nonce
            if block.is_mined(transaction):
                logger.info(f'Mined block: {transaction}')
                block.add_if_valid(transaction)
                communication.broadcast(transaction, 'block')
                break
