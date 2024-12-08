import datetime
import hashlib
import json
import crypto
def create_coinbase_transaction(recipient, amount, block_index):
    """
    Creates transaction coinbase, which creates money
    """
    transaction = {
        "id": None,
        "type": "coinbase",
        "inputs": [],
        "outputs": [{"address": recipient, "amount": amount}],
        "date": int(datetime.datetime.now().timestamp() * 1000),
        "block_index": block_index,
        "signature": None
    }
    transaction["id"] = calculate_transaction_hash(transaction)
    return transaction

def calculate_transaction_hash(transaction):
    """
    Calcules transaction hash
    """
    tx_copy = transaction.copy()
    tx_copy.pop("signature", None)  # Usuń podpis na czas hashowania
    tx_string = json.dumps(tx_copy, sort_keys=True).encode()
    return hashlib.sha256(tx_string).hexdigest()

def create_transfer_transaction(sender_private_key, sender_public_key, recipient, amount, inputs):
    """
    Creates standard transfer transaction
    """
    transaction = {
        "id": None,
        "type": "transfer",
        "inputs": inputs,
        "outputs": [
            {"address": recipient, "amount": amount},
            {"address": sender_public_key, "amount": sum(i["amount"] for i in inputs) - amount}  # Reszta
        ],
        "date": int(datetime.datetime.now().timestamp() * 1000),
        "signature": None
    }
    transaction["id"] = calculate_transaction_hash(transaction)
    #transaction["signature"] = sign(sender_private_key, transaction["id"])
    return transaction
