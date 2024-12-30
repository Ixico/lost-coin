from collections import deque
from datetime import datetime
from Crypto.Random import get_random_bytes
from common import STOP_EVENT, logger

import block
import time
import json
import communication
import node

TRANSACTIONS = deque()


def get_content():
    """
    Pobiera listę transakcji w kolejce minera.
    """
    try:
        return [json.dumps(tx, indent=4) for tx in TRANSACTIONS]
    except Exception as e:
        logger.error(f"Error getting mining queue content: {e}")
        return []


def add(transaction):
    """
    Adds a transaction to the mining queue after validation.
    """
    if node.validate_transaction(transaction):
        logger.debug(f'Adding valid transaction to mine: {transaction}')
        TRANSACTIONS.append(transaction)
    else:
        logger.error(f"Invalid transaction rejected: {transaction}")


def start_mining():
    while not STOP_EVENT.is_set():
        try:
            # Get the first transaction from the queue
            currently_mined = TRANSACTIONS.popleft()
            if not node.validate_transaction(currently_mined):
                logger.error(f"Invalid transaction removed from mining queue: {currently_mined}")
                continue  # Skip invalid transactions

            logger.debug(f"Mining transaction: {currently_mined}")

            # Create a block for mining
            new_block = {
                "previous_hash": block.get_last_block_hash(),
                "content": [currently_mined],
                "date": int(datetime.now().timestamp() * 1000),
                "nonce": None
            }

            while not STOP_EVENT.is_set():
                nonce = get_random_bytes(64).hex()
                new_block['nonce'] = nonce
                if block.is_mined(new_block):
                    logger.info(f"Mined block successfully: {new_block}")
                    block.add_if_valid(new_block)
                    communication.broadcast(new_block, 'block')
                    break
        except IndexError:
            # The queue is empty
            logger.debug("No transactions to mine, waiting...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Error during mining: {e}")
