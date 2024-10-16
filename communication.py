import json
import socket
import threading

from common import logger, CommonException

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
TYPE_METADATA_FIELD = 'socket_metadata_message_type'
CONNECTIONS = {}


def handle_client(conn, node, handler):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                logger.warn(f'Node {node} disconnected.')
                del CONNECTIONS[node]
                if len(CONNECTIONS) == 0:
                    logger.error("No active connections, node is out of network!")
                break
            data = json.loads(data.decode('utf-8'))
            logger.debug(f'Received data from node {node}: {data}')
            handler(data)
    # todo: terminate program (maybe I need some threads register)


def listen(port, handler):
    with socket.socket() as s:
        s.bind((HOST, port))
        s.listen()
        logger.info(f'Creating socket on port {port}, waiting for connection...')
        while True:
            conn, addr = s.accept()
            node = addr[1]
            CONNECTIONS[node] = conn
            logger.info(f'Node {node} connected.')
            threading.Thread(target=handle_client, args=(conn, node, handler)).start()
    # todo: gracefully shutdown server socket (with is useless since I will never get out of while loop)


def connect(port):
    s = socket.socket()
    logger.info(f'Connecting to node {port}.')
    try:
        s.connect((HOST, port))
        CONNECTIONS[port] = s
    except ConnectionRefusedError:
        logger.error(f"Connection to the node {port} refused.")
        raise CommonException()
# todo WHAT IF SERVER DISAPPEARS - TEST AGAIN

def broadcast(data_dict, data_type):
    data_dict[TYPE_METADATA_FIELD] = data_type
    logger.debug(f'Broadcasting to connections {list(CONNECTIONS.keys())} data: {data_dict}')
    for conn in CONNECTIONS.values():
        conn.sendall(json.dumps(data_dict).encode('utf-8'))
