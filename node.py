import threading
import json
import block
from block import BLOCKS
import communication
import miner
import transaction
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from common import logger


def validate_transaction(transaction):
    """
    Validates a transaction by verifying its signature.

    Args:
        transaction (dict): The transaction to validate.

    Returns:
        bool: True if the transaction is valid, False otherwise.
    """
    try:

        if any(tx['id'] == transaction['id'] for tx in miner.TRANSACTIONS):
            logger.error("Duplicate transaction ID in mempool.")
            return False

            # Check for duplicate transaction ID in blockchain
        for block in BLOCKS:
            if any(tx['id'] == transaction['id'] for tx in block['content']):
                logger.error("Duplicate transaction ID in blockchain.")
                return False

        # Step 1: Extract public key
        public_key_hex = transaction.get("public_key")
        if not public_key_hex:
            logger.error("Transaction validation failed: Missing public key.")
            return False

        # Decode the public key
        public_key = RSA.import_key(bytes.fromhex(public_key_hex))
        logger.debug(f"Decoded public key: {public_key.export_key().decode()}")

        # Step 2: Remove 'signature' field for hash computation
        transaction_copy = transaction.copy()
        signature_hex = transaction_copy.pop("signature")

        if not signature_hex:
            logger.error("Transaction validation failed: Missing signature.")
            return False
        signature = bytes.fromhex(signature_hex)

        logger.debug(f"Signature: {signature_hex}")

        # Step 3: Recreate the transaction hash
        transaction_json = json.dumps(transaction_copy, sort_keys=True).encode("utf-8")
        transaction_hash = SHA256.new(transaction_json)

        #ogger.debug(f"Recreated transaction JSON: {transaction_json.decode()}")
        #logger.debug(f"Recreated transaction hash: {transaction_hash.hexdigest()}")

        # Step 4: Verify the signature
        pkcs1_15.new(public_key).verify(transaction_hash, signature)
        logger.info("Transaction signature successfully verified.")
        return True

    except ValueError as ve:
        logger.error(f"Transaction validation failed: {ve}")
    except Exception as e:
        logger.error(f"Transaction validation failed: {e}")

    return False


def handler_miner(data, message_type):
    """
    Handles miner-related incoming messages.
    """
    if message_type == 'transaction':
        logger.debug(f"Received transaction for validation: {data}")
        if validate_transaction(data):
            miner.add(data)
        else:
            logger.error("Invalid transaction received and rejected.")
    if message_type == 'block':
        block.add_if_valid(data)

def handler(data, message_type):
    """
    Handles general incoming messages.
    """
    if message_type == 'block':
        block.add_if_valid(data)

def create_transaction(sender_address, recipient_address, amount, user_id, identity_name, password):
    """
    Creates a transaction, signs it, and broadcasts it to the network.

    Args:
        sender (str): SHA256 address of the sender.
        recipient (str): SHA256 address of the recipient.
        amount (float): Amount to transfer.
        user_id (str): User ID of the sender.
        identity_name (str): Identity name of the sender.
        password (str): Password to unlock the private key.

    Returns:
        dict: Signed transaction in JSON format.
    """
    # Create the transaction
    transaction_data = transaction.create_transfer_transaction(
        sender_address=sender_address,
        recipient_address=recipient_address,
        amount=amount,
        user_id=user_id,
        identity_name=identity_name,
        password=password
    )

    # Broadcast the transaction to the network (skip validation here)
    communication.broadcast(transaction_data, "transaction")

    # Return the transaction for confirmation
    return transaction_data

def create(port, registration_port, is_miner=False):
    """
    Starts the node and its communication handlers.
    """
    if is_miner:
        communication.set_handler_function(handler_miner)
        threading.Thread(target=miner.start_mining).start()
    else:
        communication.set_handler_function(handler)
    threading.Thread(target=communication.listen, args=(port,)).start()
    if registration_port is not None:
        communication.connect(registration_port)
