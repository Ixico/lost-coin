import hashlib
import json
import datetime

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