import logging
import threading


def setup_logger():
    log = logging.getLogger('MyApp')
    log.setLevel(logging.DEBUG)

    log_format = '%(asctime)s [%(levelname)s] %(module)s: %(message)s'
    date_format = '%H:%M:%S'
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)
    return log


logger = setup_logger()

STOP_EVENT = threading.Event()


def shutdown():
    STOP_EVENT.set()
    for thread in threading.enumerate():
        if thread is not threading.current_thread():
            thread.join()
    exit()


class CommonException(Exception):
    pass