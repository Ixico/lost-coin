import queue
from common import STOP_EVENT, logger
import block
from Crypto.Random import get_random_bytes

BLOCKS = queue.Queue()
HANDLER = lambda x: None


def set_handler_function(handler):
    global HANDLER
    HANDLER = handler


def add(b):
    logger.debug(f'Adding block to mine: {b}')
    BLOCKS.put(b)


def start_mining():
    while not STOP_EVENT.is_set():
        try:
            b = BLOCKS.get(timeout=2)
            logger.debug(f'Mining block {b}')
        except queue.Empty:
            continue
        while not STOP_EVENT.is_set():
            nonce = get_random_bytes(64).hex()
            b['nonce'] = nonce
            if block.is_mined(b):
                logger.info(f'Mined block: {b}')
                HANDLER(b)
                break
