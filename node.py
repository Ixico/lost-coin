import threading

import block
import communication
import miner
import transaction


def handle_mined_block(mined_block):
    block.add_if_valid(mined_block)
    communication.broadcast(mined_block, 'block')


def handler_miner(data, message_type):
    if message_type == 'transaction':
        miner.add(data)
    if message_type == 'block':
        block.add_if_valid(data)


def handler(data, message_type):
    if message_type == 'transaction':
        return
    if message_type == 'block':
        block.add_if_valid(data)


def create_transaction(content):
    communication.broadcast(transaction.create(content), 'transaction')


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
