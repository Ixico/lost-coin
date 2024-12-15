import signal
import threading
import PySimpleGUI as sg
import block
import miner
import node
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
    Setup wallet: asks for user_id and password, and chooses or creates an identity.
    """
    layout = [
        [sg.Text("Enter your user ID:"), sg.InputText(key="user_id", size=(30, 1))],
        [sg.Text("Enter your password:"), sg.InputText(key="password", password_char="*", size=(30, 1))],
        [sg.Button("Submit"), sg.Button("Exit")]
    ]
    window = sg.Window("Wallet Setup", layout)

    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            shutdown()
            return None
        elif event == "Submit":
            user_id = values["user_id"]
            password = values["password"]
            if not user_id or not password:
                sg.popup("User ID and password are required.")
                continue

            try:
                if wallet.exists(user_id):
                    wallet.unlock(user_id, password)
                    sg.popup(f"Wallet for user {user_id} unlocked successfully.")
                else:
                    wallet.create(user_id, password)
                    sg.popup(f"New wallet for user {user_id} created successfully.")

                # Choose or create identity
                identities = wallet.get_identities(user_id)
                if identities:
                    identity_name = sg.popup_get_text(
                        "Available identities:\n" + "\n".join(identities) +
                        "\n\nEnter identity name to use or create a new one:"
                    )
                else:
                    identity_name = sg.popup_get_text("No identities found.\nEnter name to create a new identity:")

                if identity_name and identity_name not in identities:
                    wallet.create_identity(user_id, identity_name)
                    sg.popup(f"Identity {identity_name} created successfully.")

                if not identity_name:
                    sg.popup("No identity selected or created.")
                    return None

                sender_address = wallet.generate_address(user_id, identity_name)

                window.close()
                return user_id, identity_name, password, sender_address
            except Exception as e:
                sg.popup(f"Error: {str(e)}")
    return None


def blockchain_view(user_id, identity_name, password, sender_address):
    """
    Blockchain view showing user_id and user's address.
    """
    layout = [
        [sg.Text(f"User ID: {user_id}, Identity: {identity_name}")],
        [sg.Text("Your Address (SHA256):"), sg.InputText(sender_address, key="user_address", readonly=True)],
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
                    amount = float(amount)
                    transaction_data = node.create_transaction(
                        sender=sender_address,
                        recipient=recipient,
                        amount=amount,
                        user_id=user_id,
                        identity_name=identity_name,
                        password=password
                    )
                    sg.popup(f"Transaction created and added to mining queue!\nTransaction ID: {transaction_data['id']}")
                except Exception as e:
                    sg.popup(f"Error creating transaction: {str(e)}")
        elif event == "Refresh Balance":
            balances = block.calculate_balances()
            balance = balances.get(sender_address, 0)
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


# Step 1: Setup Wallet
user_data = setup_wallet()
if user_data is None:
    shutdown()
    exit()

user_id, identity_name, password, sender_address = user_data

# Step 2: Connect to Network
connection_data = connect_view()
if connection_data is None:
    shutdown()
    exit()

port, registration_port, is_miner = connection_data
node.create(int(port), int(registration_port) if registration_port else None, is_miner)

# Step 3: Miner Mode
if is_miner:
    sg.popup(f"Starting miner mode for user {user_id}.")
    threading.Thread(target=miner.start_mining).start()
    mining_view()

# Step 4: Blockchain View
blockchain_view(user_id, identity_name, password, sender_address)
shutdown()
