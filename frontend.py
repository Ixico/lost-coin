import signal
import threading
import PySimpleGUI as sg
import block
import miner
import node
import transaction
import wallet
from common import STOP_EVENT, shutdown, handle_sigint


def create_connect_view():
    return [
        [sg.Text("Port:"), sg.InputText(key="port", size=(20, 1))],
        [sg.Text("Registration Port:"), sg.InputText(key="registration_port", size=(20, 1))],
        [sg.Checkbox("Miner", key="miner")],
        [sg.Text("Miner's Address (if miner):"), sg.InputText(key="miner_address", size=(40, 1))],
        [sg.Button("Connect", key="connect")]
    ]


def create_blockchain_view():
    return [
        [sg.Text("Your Address:"), sg.InputText(key="user_address", size=(60, 1))],
        [sg.Button("Refresh Balance", key="refresh_balance")],
        [sg.Text("Your Balance:"), sg.Text("0", key="user_balance")],
        [sg.Text("Blockchain:")],
        [sg.Listbox(values=[], size=(60, 10), key="block_list", select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, enable_events=True)],
        [sg.Button("Publish New Transaction", key="publish_new_transaction")]
    ]


def create_mining_view():
    return [
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


def connect_view():
    layout = create_connect_view()
    window = sg.Window("Connect to Network", layout)
    miner_address = ""
    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "connect":
            port = values["port"]
            registration_port = values["registration_port"]
            is_miner = values["miner"]
            miner_address = values["miner_address"]
            window.close()
            return port, registration_port, is_miner, miner_address
    window.close()


def blockchain_view():
    layout = create_blockchain_view()
    window = sg.Window("Blockchain", layout)
    user_address = ""
    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "publish_new_transaction":
            recipient_address = sg.popup_get_text("Enter recipient's address:", "New Transaction")
            amount = sg.popup_get_text("Enter amount to send:", "New Transaction")
            identity_name = sg.popup_get_text("Enter your identity name (for signing):", "Identity")

            if not (recipient_address and amount and identity_name):
                sg.popup("Please provide all required information.")
                continue

            try:
                # Konwersja kwoty
                amount = float(amount)
                # Pobierz klucz prywatny użytkownika
                private_key = wallet.get_private_key(identity_name)
                # Wybierz odpowiednie UTXO
                inputs = transaction.select_inputs(user_address, amount)
                # Utwórz transakcję
                new_transaction = transaction.create_transfer_transaction(
                    sender_private_key=private_key,
                    sender_public_key=user_address,
                    recipient=recipient_address,
                    amount=amount,
                    inputs=inputs
                )
                # Podpisz transakcję
                new_transaction["signature"] = wallet.sign_transaction(new_transaction["id"], private_key)
                # Wyślij transakcję
                node.create_transaction(new_transaction)
                sg.popup("Transaction created and broadcasted successfully.")
            except Exception as e:
                sg.popup(f"Error: {str(e)}")
        elif event == "block_list":
            if window["block_list"].get_indexes():
                selected_index = window["block_list"].get_indexes()[0]
                show_block_details(selected_index)
        elif event == "refresh_balance":
            user_address = values["user_address"]
            if user_address:
                balance = transaction.calculate_balance(user_address)
                window["user_balance"].update(str(balance))
            else:
                sg.popup("Please enter your address.")
        window['block_list'].update(values=block.get_blocks_content())
    window.close()


def show_block_details(block_index):
    block_detail = block.get_block_details(block_index)
    sg.popup("Block Details", '\n\n'.join(f"{key}: {value}" for key, value in block_detail.items()))


def mining_view():
    layout = create_mining_view()
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
params = connect_view()
if params is None:
    shutdown()
    exit()

port, registration_port, is_miner, miner_address = params
node.create(to_int(port), to_int(registration_port), is_miner)

if is_miner:
    if not miner_address:
        sg.popup("Miner's address is required.")
        shutdown()
        exit()
    threading.Thread(target=miner.start_mining, args=(miner_address,)).start()
    mining_view()
else:
    blockchain_view()
shutdown()
