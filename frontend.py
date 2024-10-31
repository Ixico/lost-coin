import PySimpleGUI as sg
import block, node
from common import STOP_EVENT

blocks = block.get_blocks()
mining_queue = []  # Queue of blocks waiting to be mined
currently_mined_block = ""  # Placeholder for the block currently being mined
import threading


def create_connect_view():
    """Creates the layout for the connect view."""
    return [
        [sg.Text("Port:"), sg.InputText(key="port", size=(20, 1))],
        [sg.Text("Registration Port:"), sg.InputText(key="registration_port", size=(20, 1))],
        [sg.Checkbox("Miner", key="miner")],
        [sg.Button("Connect", key="connect")]
    ]


def create_blockchain_tab():
    """Creates the layout for the blockchain tab."""
    return [
        [sg.Text("Blockchain:")],
        [sg.Listbox(values=blocks, size=(40, 10), key="block_list")],
        [sg.Button("Publish New Block", key="publish_new_block")]
    ]


def create_mining_tab(is_miner):
    """Creates the layout for the mining tab, showing 'Mining is disabled' if user is not a miner."""
    if is_miner:
        # Layout for miners: show mining queue and controls
        mining_layout = [
            [sg.Text("Mining Queue:")],
            [sg.Multiline(
                "\n".join(mining_queue),
                size=(40, 5),
                key="mining_queue_display",
                disabled=True,  # Makes the queue display-only
                autoscroll=True,
                no_scrollbar=True
            )],
            [sg.Text("Currently Mined Block:"), sg.Text("", size=(30, 1), key="current_mined_block")],
            [sg.Button("Start Mining", key="start_mining")]
        ]
    else:
        # Layout for non-miners: show 'Mining is disabled' message
        mining_layout = [[sg.Text("Mining is disabled", font=("Helvetica", 12), text_color="red")]]

    return mining_layout


def create_blockchain_view(is_miner):
    """Creates the layout for the blockchain view with tabs."""
    blockchain_tab = create_blockchain_tab()
    mining_tab = create_mining_tab(is_miner)

    tab_group_layout = [
        [sg.Tab("Blockchain", blockchain_tab, key="blockchain_tab")],
        [sg.Tab("Mining", mining_tab, key="mining_tab")]
    ]

    layout = [[sg.TabGroup(tab_group_layout, key="tab_group")]]
    return layout


def connect_view():
    """Manages the connect view."""
    layout = create_connect_view()
    window = sg.Window("Connect to Network", layout)

    while not STOP_EVENT.is_set():
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:  # Exit if the user closes the window
            break
        elif event == "connect":  # Connect button clicked
            port = values["port"]
            registration_port = values["registration_port"]
            is_miner = values["miner"]
            print(f"Connecting with Port: {port}, Registration Port: {registration_port}, Miner: {is_miner}")

            window.close()  # Close the current window
            return port, registration_port, is_miner

    window.close()


def blockchain_view(is_miner):
    """Manages the blockchain view with blockchain and mining tabs."""
    global blocks, mining_queue, currently_mined_block  # Access global variables

    layout = create_blockchain_view(is_miner)
    window = sg.Window("Blockchain", layout)

    while not STOP_EVENT.is_set():
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:  # Exit if the user closes the window
            break
        elif event == "publish_new_block":  # Publish new block button clicked
            # Ask for content with a popup
            block_content = sg.popup_get_text("Enter content for the new block:", "New Block Content")
            if block_content:  # Proceed only if the user entered some content
                node.create_block(block_content)
            else:
                print("New block creation cancelled or empty content provided.")

        elif event == "start_mining" and is_miner:  # Start mining button clicked (only for miners)
            if mining_queue:  # Check if there are blocks to mine
                currently_mined_block = mining_queue.pop(0)  # Get the next block to mine
                window["mining_queue_display"].update("\n".join(mining_queue))  # Update mining queue display
                window["current_mined_block"].update(value=currently_mined_block)  # Display currently mined block
                print(f"Started mining: {currently_mined_block}")
            else:
                print("No blocks in the queue to mine.")

        # Refresh blockchain display
        window['block_list'].update(values=block.get_blocks())

    window.close()

def to_int(x):
    return int(x) if x else None

# Start with the connect view
port, registration_port, is_miner = connect_view()
# threading.Thread(target=node.create, args=(to_int(port), to_int(registration_port), is_miner)).start()
node.create(to_int(port), to_int(registration_port), is_miner)
blockchain_view(is_miner)
