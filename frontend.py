import signal
import threading
import PySimpleGUI as sg
import block
import miner
import node
import transaction
import wallet
from common import STOP_EVENT, shutdown, handle_sigint


def connect_view():
    """
    Widok dla konfiguracji połączenia węzła z obsługą trybu minera.
    """
    layout = [
        [sg.Text("Enter the port to host this node:"), sg.InputText(key="port", size=(20, 1))],
        [sg.Text("Enter the registration port (optional):"), sg.InputText(key="registration_port", size=(20, 1))],
        [sg.Checkbox("Enable Miner Mode", key="miner")],
        [sg.Button("Connect"), sg.Button("Exit")]
    ]
    window = sg.Window("Node Connection Setup", layout)

    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            shutdown()
            break
        elif event == "Connect":
            port = values["port"]
            registration_port = values["registration_port"]
            is_miner = values["miner"]

            if not port:
                sg.popup("Port is required to start the node.")
                continue

            window.close()
            return port, registration_port, is_miner
    window.close()
    return None



def setup_wallet():
    """
    Konfiguracja portfela: tworzenie lub odblokowywanie portfela.
    """
    # Prompt o hasło
    layout = [
        [sg.Text("Enter your wallet password:")],
        [sg.InputText(key="password", password_char="*")],
        [sg.Button("Submit"), sg.Button("Exit")]
    ]
    window = sg.Window("Wallet Setup", layout)
    password = None
    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            shutdown()
            break
        elif event == "Submit":
            password = values["password"]
            if password:
                window.close()
                break
            else:
                sg.popup("Password cannot be empty.")
    if not password:
        return None, None

    # Konfiguracja portfela
    node_id = sg.popup_get_text("Enter node identifier (e.g., 'node1'):", "Node Registration")
    if not node_id:
        sg.popup("Node identifier is required.")
        return None, None

    try:
        if wallet.exists(node_id):
            wallet.unlock(node_id, password)
            sg.popup(f"Wallet for node {node_id} unlocked successfully.")
        else:
            wallet.create(node_id, password)
            sg.popup(f"New wallet for node {node_id} created successfully.")
    except Exception as e:
        sg.popup(f"Error: {str(e)}")
        return None, None

    # Wyświetl dostępne tożsamości lub stwórz nową
    identities = wallet.get_identities(node_id)
    if identities:
        identity_name = sg.popup_get_text("Available identities:\n" + "\n".join(identities) +
                                          "\n\nEnter identity name to use or create a new one:")
    else:
        identity_name = sg.popup_get_text("No identities found.\nEnter name to create a new identity:")

    if identity_name and identity_name not in identities:
        wallet.create_identity(node_id, identity_name)
        sg.popup(f"Identity {identity_name} created successfully.")

    return node_id, identity_name, password


def blockchain_view(node_id, identity_name):
    """
    Widok blockchaina z wyświetlaniem SHA256 klucza publicznego.
    """
    # Generuj adres użytkownika (SHA256 klucza publicznego)
    user_address = wallet.generate_address(node_id, identity_name)

    layout = [
        [sg.Text(f"Node: {node_id}, Identity: {identity_name}")],
        [sg.Text("Your Address (SHA256):"), sg.InputText(user_address, key="user_address", readonly=True)],
        [sg.Text("Your Balance:"), sg.Text("0", key="user_balance")],
        [sg.Text("Blockchain:")],
        [sg.Listbox(values=[], size=(60, 10), key="block_list", select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, enable_events=True)],
        [sg.Button("Publish Transaction"), sg.Button("Refresh Balance"), sg.Button("Exit")]
    ]
    window = sg.Window("Blockchain Node", layout)
    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        elif event == "Publish Transaction":
            recipient = sg.popup_get_text("Enter recipient's SHA256 address:")
            amount = sg.popup_get_text("Enter amount to send:")
            if recipient and amount:
                try:
                    # Tworzenie i podpisywanie transakcji
                    amount = float(amount)
                    inputs = transaction.select_inputs(user_address, amount)
                    transaction_data = transaction.create_transfer_transaction(
                        node_id=node_id,
                        identity_name=identity_name,
                        recipient=recipient,
                        amount=amount,
                        inputs=inputs,
                        password=password
                    )
                    sg.popup(f"Transaction created and signed successfully!\nTransaction ID: {transaction_data['id']}")
                except Exception as e:
                    sg.popup(f"Error creating transaction: {str(e)}")
        elif event == "Refresh Balance":
            # Obliczanie aktualnego salda
            balances = block.calculate_balances()
            balance = balances.get(user_address, 0)
            window["user_balance"].update(str(balance))
        window["block_list"].update(values=block.get_blocks_content())
    window.close()


def mining_view():
    layout = [
        [sg.Text("Mining Queue:")],
        [sg.Listbox(
            values=[],
            size=(60, 10),
            key="mining_queue",
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=False,
            highlight_background_color='yellow',
            highlight_text_color='black'
        )],
    ]
    window = sg.Window("Mining", layout)
    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED:
            break
        window["mining_queue"].update(values=miner.get_content(), set_to_index=[0])
    window.close()


def to_int(x):
    return int(x) if x else None


signal.signal(signal.SIGINT, handle_sigint)

node_data = setup_wallet()
if node_data is None:
    shutdown()
    exit()

node_id, identity_name, password = node_data

result = connect_view()
if result is None:
    shutdown()
    exit()

port, registration_port, is_miner = result

node.create(to_int(port), to_int(registration_port), is_miner)

if is_miner:
    sg.popup(f"Starting miner mode for node {node_id}.")
    threading.Thread(target=miner.start_mining).start()
    mining_view()  # Uruchamia widok minera

blockchain_view(node_id, identity_name)
shutdown()

