import signal

import PySimpleGUI as sg

import block
import miner
import node
from common import STOP_EVENT, shutdown, handle_sigint


def create_connect_view():
    return [
        [sg.Text("Port:"), sg.InputText(key="port", size=(20, 1))],
        [sg.Text("Registration Port:"), sg.InputText(key="registration_port", size=(20, 1))],
        [sg.Checkbox("Miner", key="miner")],
        [sg.Button("Connect", key="connect")]
    ]


def create_blockchain_view():
    return [
        [sg.Text("Blockchain:")],
        [sg.Listbox(values=[], size=(40, 10), key="block_list", select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, enable_events=True)],
        [sg.Button("Publish New Transaction", key="publish_new_transaction")]
    ]


def create_mining_view():
    return [
        [sg.Text("Mining Queue:")],
        [sg.Listbox(
            values=[],
            size=(40, 10),
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
    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "connect":
            port = values["port"]
            registration_port = values["registration_port"]
            is_miner = values["miner"]
            window.close()
            return port, registration_port, is_miner
    window.close()


def blockchain_view():
    layout = create_blockchain_view()
    window = sg.Window("Blockchain", layout)
    while not STOP_EVENT.is_set():
        event, values = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "publish_new_transaction":
            block_content = sg.popup_get_text("Enter content for the new transaction:", "New Transaction Content")
            if block_content:
                node.create_transaction(block_content)
        elif event == "block_list":
            selected_index = window["block_list"].get_indexes()[0]
            show_block_details(selected_index)
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
node.create(to_int(params[0]), to_int(params[1]), params[2])
if params[2]:
    mining_view()
else:
    blockchain_view()
shutdown()
