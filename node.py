from apscheduler.schedulers.background import BackgroundScheduler

import communication
import threading

scheduler = BackgroundScheduler()


def handler(message):
    pass


def create(port, registration_port):
    thread = threading.Thread(target=communication.listen, args=(port, handler))
    thread.start()
    if registration_port is not None:
        communication.connect(registration_port)
    thread.join()
