import hashlib
import datetime
import json

from Crypto.PublicKey import RSA

from wallet import get_private_key, get_public_key
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def calculate_transaction_hash(transaction):
    """
    Calculates the hash of a transaction, including the public key.

    Args:
        transaction (dict): Transaction data.

    Returns:
        str: SHA256 hash of the transaction.
    """
    tx_copy = transaction.copy()
    tx_copy.pop("signature", None)  # Remove the signature before hashing
    tx_string = json.dumps(tx_copy, sort_keys=True).encode()
    return hashlib.sha256(tx_string).hexdigest()

def select_inputs(address, required_amount):
    """
    Selects UTXOs to satisfy the required amount.
    """
    from block import BLOCKS
    utxos = []
    selected_inputs = []
    total_amount = 0

    for block in BLOCKS:
        for tx in block.get('content', []):
            for output_index, output in enumerate(tx['outputs']):
                if output['address'] == address and not is_output_spent(tx['id'], output_index):
                    utxos.append({
                        'id': tx['id'],
                        'amount': output['amount'],
                        'output_index': output_index
                    })

    for utxo in utxos:
        selected_inputs.append({
            'id': utxo['id'],
            'amount': utxo['amount'],
            'output_index': utxo['output_index']
        })
        total_amount += utxo['amount']
        if total_amount >= required_amount:
            break

    if total_amount < required_amount:
        raise ValueError(f"Insufficient funds. Required: {required_amount}, Available: {total_amount}")

    return selected_inputs

def is_output_spent(tx_id, output_index):
    """
    Checks if a UTXO is already spent.
    """
    from block import BLOCKS
    for block in BLOCKS:
        for tx in block.get('content', []):
            for tx_input in tx.get('inputs', []):
                if tx_input['id'] == tx_id and tx_input['output_index'] == output_index:
                    return True
    return False

def create_transfer_transaction(user_id, identity_name, recipient, amount, inputs, password):
    """
    Creates a transfer transaction with the full public key included.

    Args:
        user_id (str): User ID of the sender.
        identity_name (str): Identity name of the sender.
        recipient (str): Address of the recipient.
        amount (float): Amount to send.
        inputs (list): List of transaction inputs.
        password (str): Password to unlock the private key.

    Returns:
        dict: Transaction in JSON format.
    """
    # Load the private and public keys
    private_key = get_private_key(user_id, identity_name, password)
    public_key = get_public_key(user_id, identity_name)

    transaction = {
        "id": None,
        "inputs": inputs,
        "outputs": [{"address": recipient, "amount": amount}],
        "public_key": public_key.hex(),  # Include full public key
        "signature": None
    }

    # Generate transaction ID
    transaction_json = json.dumps(transaction, sort_keys=True).encode("utf-8")
    transaction["id"] = hashlib.sha256(transaction_json).hexdigest()
    transaction.pop("signature")
    # Sign the transaction
    transaction_hash = SHA256.new(transaction_json)
    try:
        signature = pkcs1_15.new(private_key).sign(transaction_hash)
        transaction["signature"] = signature.hex()
        print(f"[DEBUG] Generated Signature: {transaction['signature']}")
    except Exception as e:
        raise ValueError(f"Failed to sign transaction: {e}")

    # Step 5: Verify the signature (Optional, to debug)
    try:
        print(transaction_json.decode())
        pkcs1_15.new(RSA.import_key(public_key)).verify(transaction_hash, signature)
        print("[DEBUG] Signature verified successfully.")
    except Exception as e:
        raise ValueError(f"Signature verification failed: {e}")

    return transaction