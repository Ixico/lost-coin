import communication
import threading
from common import STOP_EVENT


def handler(message):
    pass


def create(port, registration_port):
    communication.set_handler_function(handler)
    thread = threading.Thread(target=communication.listen, args=(port,))
    thread.start()
    if registration_port is not None:
        communication.connect(registration_port)
    while not STOP_EVENT.is_set():
        pass

