import hashlib
import datetime
import os
import sys
import json
import uuid
from common import logger
from Crypto.PublicKey import RSA


from wallet import get_private_key, get_public_key
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

cur_path = os.path.dirname(__file__)

def generate_transaction_id():
    return str(uuid.uuid4())

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

def create_transfer_transaction(sender_address, recipient_address, amount, user_id, identity_name, password):
    """
        Creates a transfer transaction with the simplified structure.

        Args:
            sender_address (str): sender_address of the sender.
            recipient_address (str): Address of the recipient.
            amount (float): Amount to send.
            user_id (str): User ID of the sender, to unlock the wallet.
            identity_name (str): Identity name of the sender.
            password (str): Password to unlock the private key.

        Returns:
            dict: Transaction in JSON format.
        """
    # Load the private and public keys
    private_key = get_private_key(user_id, identity_name, password)
    public_key = get_public_key(user_id, identity_name)

    # Generate a unique ID (incremental)
    #todo: consider using a timestamp instead
    transaction_id = generate_transaction_id()

    transaction = {
        "id": transaction_id,
        "sender_address": sender_address,
        "recipient_address": recipient_address,
        "amount": amount,
        "public_key": public_key.hex(),
        "signature": None
    }

    # Generate transaction ID
    transaction_copy = transaction.copy()
    transaction_copy.pop("signature")
    transaction_json = json.dumps(transaction_copy, sort_keys=True).encode("utf-8")
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
        logger.debug(f"Transaction hash: {transaction_hash.hexdigest()}")
        pkcs1_15.new(RSA.import_key(public_key)).verify(transaction_hash, signature)
        print("[DEBUG] Signature verified successfully.")
    except Exception as e:
        raise ValueError(f"Signature verification failed: {e}")

    return transaction
