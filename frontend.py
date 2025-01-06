import signal
import threading
import PySimpleGUI as sg
import block
import miner
import node
import wallet
from anytree.search import findall

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


from anytree.search import findall  # Dodaj ten import


def blockchain_view(user_id, identity_name, password, sender_address):
    """
    Blockchain view showing user_id, user's address, and block hashes with transaction details.
    """
    layout = [
        [sg.Text(f"User ID: {user_id}, Identity: {identity_name}", expand_x=True)],
        [sg.Text("Your Address (SHA256):"),
         sg.InputText(sender_address, key="user_address", readonly=True, expand_x=True)],
        [sg.Text("Your Balance:"), sg.Text("0", key="user_balance", expand_x=True)],
        [sg.Text("Blockchain (Block Hashes and Transactions):", expand_x=True)],
        [sg.Listbox(
            values=[],
            size=(80, 20),  # Ustawienia początkowego rozmiaru komponentu
            key="block_list",
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            expand_x=True,
            expand_y=True,
            enable_events=True
        )],
        [sg.Button("Publish Transaction"), sg.Button("Refresh Balance"), sg.Button("Exit")]
    ]
    window = sg.Window(
        "Blockchain Node",
        layout,
        resizable=True,  # Allow window resizing
        finalize=True,  # Needed to use expand options effectively
    )
    # Ensure resizing behavior works
    window['block_list'].expand(expand_x=True, expand_y=True)

    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        elif event == "Publish Transaction":
            recipient_address = sg.popup_get_text("Enter recipient's SHA256 address:")
            amount = sg.popup_get_text("Enter amount to send:")
            if recipient_address and amount:
                try:
                    amount = float(amount)
                    node.create_transaction(
                        sender_address=sender_address,
                        recipient_address=recipient_address,
                        amount=amount,
                        user_id=user_id,
                        identity_name=identity_name,
                        password=password
                    )
                    sg.popup("Transaction created and added to mining queue!")
                except Exception as e:
                    sg.popup(f"Error creating transaction: {str(e)}")
        elif event == "Refresh Balance":
            try:
                balance = block.get_balance_for_address(sender_address)
                window["user_balance"].update(str(balance))
            except Exception as e:
                sg.popup(f"Error refreshing balance: {str(e)}")

        # Fetch hashes and transaction data for display
        transactions = []
        leaves = findall(block.GENESIS, filter_=lambda node: node.is_leaf)
        for leaf in leaves:
            current = leaf
            while current is not None:
                block_hash = block.hash_block(current.body)
                transactions.append(f"Block: {block_hash}")
                for tx in current.body['content']:
                    transactions.append(f"  Transaction: {tx}")
                current = current.parent

        # Reverse to show blocks in chronological order
        transactions.reverse()
        window["block_list"].update(values=transactions)
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
