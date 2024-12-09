import threading

import block
import communication
import miner
import transaction
import wallet


def handler_miner(data, message_type):
    # todo: validate transaction (especially its date)
    if message_type == 'transaction':
        miner.add(data)
    if message_type == 'block':
        block.add_if_valid(data)


def handler(data, message_type):
    if message_type == 'block':
        block.add_if_valid(data)


def create_transaction(sender, recipient, amount, node_id, identity_name, password):
    """
    Tworzy transakcję, podpisuje ją i dodaje do kolejki minera.

    Args:
        sender (str): Adres SHA256 nadawcy.
        recipient (str): Adres SHA256 odbiorcy.
        amount (float): Kwota do przesłania.
        node_id (str): Identyfikator węzła nadawcy.
        identity_name (str): Nazwa tożsamości nadawcy.
        password (str): Hasło do odblokowania klucza prywatnego.

    Returns:
        dict: Transakcja w formacie JSON.

    Raises:
        ValueError: Jeśli środki są niewystarczające lub transakcja jest nieprawidłowa.
    """
    # Wybierz wejścia (UTXO)
    inputs = transaction.select_inputs(sender, amount)

    # Stwórz transakcję
    transaction_data = transaction.create_transfer_transaction(
        node_id=node_id,
        identity_name=identity_name,
        recipient=recipient,
        amount=amount,
        inputs=inputs,
        password=password
    )

    # Dodaj transakcję do kolejki minera
    communication.broadcast(transaction_data, "transaction")




def create(port, registration_port, is_miner=False):
    if is_miner:
        communication.set_handler_function(handler_miner)
        threading.Thread(target=miner.start_mining).start()
    else:
        communication.set_handler_function(handler)
    threading.Thread(target=communication.listen, args=(port,)).start()
    if registration_port is not None:
        communication.connect(registration_port)
