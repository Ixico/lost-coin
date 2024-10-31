import block
import communication
import threading

import miner
from common import STOP_EVENT


def handle_mined_block(mined_block):
    # todo: won't work correctly with more than one miner
    block.add(mined_block)
    communication.broadcast(mined_block, 'mined_block')


def handler_miner(data, message_type):
    if message_type == 'block' and block.is_valid(data):
        miner.add(data)
    if message_type == 'mined_block':
        if block.is_valid(data) and block.is_mined(data):
            block.add(data)


def handler(data, message_type):
    if message_type == 'block':
        return
    if message_type == 'mined_block':
        if block.is_valid(data) and block.is_mined(data):
            block.add(data)


def create_block(content):
    communication.broadcast(block.create(content), 'block')


def create(port, registration_port, is_miner=False):
    if is_miner:
        communication.set_handler_function(handler_miner)
        miner.set_handler_function(handle_mined_block)
        threading.Thread(target=miner.start_mining).start()
    else:
        communication.set_handler_function(handler)
    threading.Thread(target=communication.listen, args=(port,)).start()
    if registration_port is not None:
        communication.connect(registration_port)
