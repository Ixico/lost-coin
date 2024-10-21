import communication
import threading
from common import STOP_EVENT


def handler(message):
    pass


def create(port, registration_port):
    thread = threading.Thread(target=communication.listen, args=(port, handler))
    thread.start()
    if registration_port is not None:
        communication.connect(registration_port)
    while not STOP_EVENT.is_set():
        pass

