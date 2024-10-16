import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import request
from requests.exceptions import ConnectionError
from waitress import serve
import logging

app = Flask(__name__)
scheduler = BackgroundScheduler()

NET_ADDRESS = '127.0.0.1'  # todo: figure out https
NODES = []
REGISTER_ENDPOINT = '/register'
ACTUATOR_ENDPOINT = '/actuator'


@app.post(REGISTER_ENDPOINT)
def register():
    port = request.json['port']
    NODES.append(port)
    print(f"Node {port} has been registered.")
    return '', 200


@app.get(ACTUATOR_ENDPOINT)
def actuator():
    return '', 200


def is_node_alive(node):
    try:
        return requests.get(prepare_url(node, ACTUATOR_ENDPOINT), timeout=5).status_code == 200
    except ConnectionError:
        return False


def track_nodes():
    global NODES
    NODES = [node for node in NODES if is_node_alive(node)]
    print(f"Connected nodes: {NODES}")
    if len(NODES) == 0:
        terminate_node("[ERROR] Connection to the net has been lost.")


def create(port, registration_port):
    logging.debug("Creating node")
    if registration_port is not None:
        response = requests.post(prepare_url(registration_port, REGISTER_ENDPOINT), json={'port': port}, timeout=5)
        if response.status_code != 200:
            terminate_node(f"Cannot connect to net. Node {registration_port} didn't respond.")  # todo: try-except ConnectionError
        NODES.append(registration_port)
        scheduler.add_job(track_nodes, 'interval', seconds=30)
        scheduler.start()
    serve(app, host=NET_ADDRESS, port=port)


def prepare_url(node, endpoint):
    return f"http://{NET_ADDRESS}:{node}{endpoint}"  # todo: figure out https


def terminate_node(reason):
    print(f"[CRITICAL ERROR] {reason}")
    scheduler.shutdown()  # todo: gracefully shutdown everything
    exit(-2)

