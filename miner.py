from collections import deque
from datetime import datetime
import json
import communication
from common import STOP_EVENT, logger
import block
from Crypto.Random import get_random_bytes
import time

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
    Dodaje transakcję do kolejki transakcji.
    """
    logger.debug(f'Adding transaction to mine: {transaction}')
    TRANSACTIONS.append(transaction)


def start_mining():
    while not STOP_EVENT.is_set():
        try:
            # Pobierz pierwszą transakcję z kolejki
            currently_mined = TRANSACTIONS.popleft()
            logger.debug(f"Mining transaction: {currently_mined}")

            # Stwórz blok na podstawie transakcji
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
            # Kolejka jest pusta
            logger.debug("No transactions to mine, waiting...")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error during mining: {e}")
