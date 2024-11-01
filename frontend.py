import PySimpleGUI as sg

# Initial blocks for demonstration
blocks = ["Block 1", "Block 2", "Block 3"]  # Sample blocks


def create_connect_view():
    """Creates the layout for the connect view."""
    return [
        [sg.Text("Port:")],
        [sg.InputText(key="port", size=(20, 1))],
        [sg.Text("Registration Port:")],
        [sg.InputText(key="registration_port", size=(20, 1))],
        [sg.Checkbox("Miner", key="miner")],
        [sg.Button("Connect", key="connect")]
    ]


def create_blockchain_view():
    """Creates the layout for the blockchain view."""
    return [
        [sg.Text("Blockchain:")],
        [sg.Listbox(values=blocks, size=(40, 10), key="block_list")],
        [sg.Button("Publish New Block", key="publish_new_block")]
    ]


def connect_view():
    """Manages the connect view."""
    layout = create_connect_view()
    window = sg.Window("Connect to Network", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:  # Exit if the user closes the window
            break
        elif event == "connect":  # Connect button clicked
            port = values["port"]
            registration_port = values["registration_port"]
            is_miner = values["miner"]
            print(f"Connecting with Port: {port}, Registration Port: {registration_port}, Miner: {is_miner}")

            window.close()  # Close the current window
            blockchain_view()  # Switch to blockchain view

    window.close()


def blockchain_view():
    """Manages the blockchain view."""
    global blocks  # Use global variable to access and modify blocks
    layout = create_blockchain_view()
    window = sg.Window("Blockchain", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:  # Exit if the user closes the window
            break
        elif event == "publish_new_block":  # Publish new block button clicked
            print("Publishing a new block...")
            new_block = f"Block {len(blocks) + 1}"  # Generate a new block string
            blocks.append(new_block)  # Add new block to the list
            window["block_list"].update(values=blocks)  # Update the Listbox with new blocks

    window.close()


# Start with the connect view
connect_view()
