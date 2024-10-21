import datetime
import json
import socket
import threading

from apscheduler.schedulers.background import BackgroundScheduler

from common import logger, STOP_EVENT, shutdown

HOST = "127.0.0.1"
TYPE_METADATA_FIELD = 'socket_metadata_message_type'
HEARTBEAT = 'socket_heartbeat'
CONNECTIONS = {}
scheduler = BackgroundScheduler()


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
                break
            data = json.loads(data.decode('utf-8'))
            # todo: drop messages that does not contain type metadata field
            if data[TYPE_METADATA_FIELD] == HEARTBEAT:
                continue
            logger.debug(f'Received data from node {node}: {data}')
            handler(data)


def listen(port, handler):
    register_actuator()
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
            threading.Thread(target=handle_client, args=(conn, node, handler)).start()


def connect(port):
    s = socket.socket()
    logger.info(f'Connecting to node {port}.')
    try:
        s.connect((HOST, port))
        CONNECTIONS[port] = s
    except ConnectionRefusedError:
        logger.critical(f"Connection to the node {port} refused.")
        shutdown(cleanup=lambda: scheduler.shutdown())


def broadcast(data_dict, data_type):
    data_dict[TYPE_METADATA_FIELD] = data_type
    logger.debug(f'Broadcasting to connections {list(CONNECTIONS.keys())} data: {data_dict}')
    send_and_delete_inactive(data_dict)


def check_connections():
    logger.debug(f'Checking active connections via heartbeat.')
    send_and_delete_inactive({TYPE_METADATA_FIELD: HEARTBEAT})
    check_net_connection()


def send_and_delete_inactive(message):
    inactive_nodes = []
    for node, conn in CONNECTIONS.items():
        try:
            conn.sendall(json.dumps(message).encode('utf-8'))
        except ConnectionResetError:
            logger.warn(f'Node {node} became inactive and will be deleted from connections.')
            inactive_nodes.append(node)
    for inactive_node in inactive_nodes:
        del CONNECTIONS[inactive_node]


def check_net_connection():
    if len(CONNECTIONS) == 0:
        logger.critical("No active connections, node is out of network!")
        shutdown(cleanup=lambda: scheduler.shutdown())


def register_actuator():
    job = scheduler.add_job(check_connections, 'interval', seconds=30)
    job.modify(next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=30))  # 30s initial delay
    scheduler.start()
