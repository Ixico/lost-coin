from datetime import datetime

import communication
from block import GENESIS
from block import hash_block

previous_hash = hash_block(GENESIS.body)

b = {
    'previous_hash': previous_hash,
    'content': [{
        "id": "15",
        "sender_address": None,
        "recipient_address": '0cd2457089759e54e6fb3dd16e5b565d59b438a653b948a74eb2a678fee46a8f',
        "amount": 50,
        "public_key": None,
        "signature": None
    }],
    'date': int(datetime(2024, 11, 1, 0, 0, 0).timestamp() * 1000),
    'nonce': 'dad1421b21463ee99c94f0709b405b533ab9b4650dad0d5411b6bbbf6be51802f06544a21faf51bd63d9dc0bb1cbac0bdbfc315d629c60e0853a6c4363833078'
}

communication.connect(50001)
communication.broadcast(b, 'block')
