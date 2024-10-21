import json
import socket
import threading

from common import logger, CommonException, STOP_EVENT, shutdown

HOST = "127.0.0.1"
TYPE_METADATA_FIELD = 'socket_metadata_message_type'
CONNECTIONS = {}


def handle_client(conn, node, handler):
    with conn:
        conn.settimeout(2)
        while not STOP_EVENT.is_set():
            try:
                data = conn.recv(1024)
            except ConnectionResetError:  # unexpected disconnection
                data = None
            except socket.timeout:
                continue
            if not data:
                logger.warn(f'Node {node} disconnected.')
                del CONNECTIONS[node]
                check_net_connection()
                break
            data = json.loads(data.decode('utf-8'))
            logger.debug(f'Received data from node {node}: {data}')
            handler(data)
    print("HANDLE CLIENT FINISHED")

#todo debug threads
def listen(port, handler):
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

            state = threading.Thread(target=handle_client, args=(conn, node, handler))
            state.start()
            state.join()


def connect(port):
    s = socket.socket()
    logger.info(f'Connecting to node {port}.')
    try:
        s.connect((HOST, port))
        CONNECTIONS[port] = s
    except ConnectionRefusedError:
        logger.critical(f"Connection to the node {port} refused.")
        raise CommonException()


def broadcast(data_dict, data_type):
    data_dict[TYPE_METADATA_FIELD] = data_type
    logger.debug(f'Broadcasting to connections {list(CONNECTIONS.keys())} data: {data_dict}')
    inactive_nodes = []
    for node, conn in CONNECTIONS.items():
        try:
            conn.sendall(json.dumps(data_dict).encode('utf-8'))
        except ConnectionResetError:
            logger.warn(f'Node {node} became inactive and will be deleted from connections.')
            inactive_nodes.append(node)
    for inactive_node in inactive_nodes:
        del CONNECTIONS[inactive_node]
    check_net_connection()


def check_net_connection():
    if len(CONNECTIONS) == 0:
        logger.critical("No active connections, node is out of network!")
        shutdown()
