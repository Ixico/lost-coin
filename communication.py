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


# todo: get rid of globals one day


def handle_client(conn, node):
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
            data = data.decode('utf-8')
            message_digest = hash(data)
            data = json.loads(data)
            if TYPE_METADATA_FIELD not in data:
                logger.warn(f'Dropping data as it does not contain message type: {data}')
                continue
            if message_digest in RECEIVED_MESSAGES:
                logger.debug(f'Skipping message {data} since it already has been received.')
                continue
            RECEIVED_MESSAGES.append(message_digest)
            logger.debug(f'Received data from node {node}: {data}')
            broadcast(data)
            message_type = data[TYPE_METADATA_FIELD]
            del data[TYPE_METADATA_FIELD]
            HANDLER_FUNCTION(data, message_type)


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


# todo: refactor this
def broadcast(data_dict, data_type=None):
    if data_type is not None:
        data_dict[TYPE_METADATA_FIELD] = data_type
    logger.debug(f'Broadcasting to connections {list(CONNECTIONS.keys())} data: {data_dict}')
    send_and_delete_inactive(data_dict)


def send_and_delete_inactive(message: dict):
    inactive_nodes = []
    for node, conn in CONNECTIONS.items():
        try:
            message = json.dumps(message)
            RECEIVED_MESSAGES.append(hash(message))
            conn.sendall(message.encode('utf-8'))
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
