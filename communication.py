import json
import socket
import threading

from common import logger, STOP_EVENT, shutdown
from crypto import hash

HOST = "127.0.0.1"
TYPE_METADATA_FIELD = 'socket_metadata_message_type'
CONNECTIONS = {}
RECEIVED_MESSAGES = []
HANDLER_FUNCTION = lambda x, y: None



def handle_client(conn, node):
    """
    Obsługuje połączenie z klientem, przetwarzając odbierane wiadomości JSON.
    """
    buffer = ""
    with conn:
        conn.settimeout(2)
        while not STOP_EVENT.is_set():
            try:
                data = conn.recv(1024)
            except (ConnectionResetError, ConnectionAbortedError):  # unexpected disconnection
                data = None
            except socket.timeout:
                continue

            if not data:
                logger.warn(f'Node {node} disconnected.')
                delete_node(node)
                break

            buffer += data.decode('utf-8')

            # Przetwarzanie pełnych wiadomości z bufora
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                try:
                    message_digest = hash(message)
                    data = json.loads(message)

                    if TYPE_METADATA_FIELD not in data:
                        logger.warn(f'Dropping data as it does not contain message type: {data}')
                        continue

                    if message_digest in RECEIVED_MESSAGES:
                        logger.debug(f'Skipping message {data} since it already has been received.')
                        continue

                    RECEIVED_MESSAGES.append(message_digest)
                    logger.debug(f'Received data from node {node}: {data}')
                    message_type = data.pop(TYPE_METADATA_FIELD)
                    broadcast(data, message_type, node)
                    HANDLER_FUNCTION(data, message_type)

                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON from node {node}: {e}")



def listen(port):
    with socket.socket() as s:
        s.bind((HOST, port))
        s.listen()
        s.settimeout(2)  # timeout is required to check STOP_EVENT flag from time to time
        logger.info(f'Creating socket on port {port}, waiting for connection...')
        while not STOP_EVENT.is_set():
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue
            node = addr[1]
            CONNECTIONS[node] = conn
            logger.info(f'Node {node} connected.')
            threading.Thread(target=handle_client, args=(conn, node)).start()


def connect(port):
    s = socket.socket()
    logger.info(f'Connecting to node {port}.')
    try:
        s.connect((HOST, port))
        CONNECTIONS[port] = s
        threading.Thread(target=handle_client, args=(s, port)).start()
    except ConnectionRefusedError:
        logger.critical(f"Connection to the node {port} refused.")
        shutdown()


def broadcast(data_dict: dict, data_type, omit_node=None):
    data = data_dict.copy()
    data[TYPE_METADATA_FIELD] = data_type
    message = json.dumps(data) + "\n"  # Dodanie separatora
    logger.debug(f'Broadcasting to connections {list(CONNECTIONS.keys())} data: {data}, omitting node: {omit_node}')
    send_and_delete_inactive(message, omit_node)


def send_and_delete_inactive(message: str, omit_node=None):
    inactive_nodes = []
    RECEIVED_MESSAGES.append(hash(message))
    message = message.encode('utf-8')
    for node, conn in CONNECTIONS.items():
        try:
            if node == omit_node:
                continue
            conn.sendall(message)
        except ConnectionResetError:
            logger.warn(f'Node {node} became inactive and will be deleted from connections.')
            inactive_nodes.append(node)
    for inactive_node in inactive_nodes:
        delete_node(inactive_node)


def set_handler_function(handler):
    global HANDLER_FUNCTION
    HANDLER_FUNCTION = handler


def delete_node(node):
    del CONNECTIONS[node]
    if len(CONNECTIONS) == 0:
        logger.critical("No active connections, node is out of network!")
        shutdown()
