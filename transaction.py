import hashlib
import datetime
import json
from wallet import get_private_key
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
def calculate_transaction_hash(transaction):
    """
    Calculates transaction hash
    """
    tx_copy = transaction.copy()
    tx_copy.pop("signature", None)  # Usuń podpis na czas hashowania
    tx_string = json.dumps(tx_copy, sort_keys=True).encode()
    return hashlib.sha256(tx_string).hexdigest()

def select_inputs(address, required_amount):
    """
    Wybiera odpowiednie wejścia (UTXO), aby zaspokoić żądaną kwotę.
    """
    from block import BLOCKS  # Przenieś import do wnętrza funkcji
    utxos = []  # Lista dostępnych UTXO
    selected_inputs = []
    total_amount = 0

    # Iteruj przez blockchain w poszukiwaniu UTXO dla danego adresu
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
        raise ValueError("Insufficient funds.")

    return selected_inputs

def is_output_spent(tx_id, output_index):
    """
    Sprawdza, czy dany UTXO został wydany w kolejnych transakcjach.
    """
    from block import BLOCKS  # Przenieś import do wnętrza funkcji
    for block in BLOCKS:
        for tx in block.get('content', []):
            for tx_input in tx.get('inputs', []):
                if tx_input['id'] == tx_id and tx_input['output_index'] == output_index:
                    return True
    return False



def create_transfer_transaction(node_id, identity_name, recipient, amount, inputs, password):
    """
    Tworzy transakcję transferu środków.

    Args:
        node_id (str): Identyfikator węzła nadawcy.
        identity_name (str): Nazwa tożsamości nadawcy.
        recipient (str): Adres odbiorcy.
        amount (float): Kwota do wysłania.
        inputs (list): Lista wejść transakcji.

    Returns:
        dict: Transakcja w formacie JSON.
    """
    # Załaduj klucz prywatny (odblokowany)
    private_key = get_private_key(node_id, identity_name, password)

    transaction = {
        "id": None,
        "type": "transfer",
        "inputs": inputs,
        "outputs": [
            {"address": recipient, "amount": amount}
        ],
        "date": int(datetime.datetime.now().timestamp() * 1000),
        "block_index": None,
        "signature": None
    }

    # Generowanie ID transakcji
    transaction_json = json.dumps(transaction, sort_keys=True).encode("utf-8")
    transaction["id"] = hashlib.sha256(transaction_json).hexdigest()

    # Podpisanie transakcji
    transaction_hash = SHA256.new(transaction_json)
    transaction["signature"] = pkcs1_15.new(private_key).sign(transaction_hash).hex()

    return transaction