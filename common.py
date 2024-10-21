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


# todo: handle sigint (it doesn't work now)

def handle_sigint(signum, frame):
    print('hi')
    shutdown()


def proceed_shutdown(cleanup):
    cleanup()
    STOP_EVENT.set()
    for thread in threading.enumerate():
        if thread is not threading.current_thread():
            thread.join()
    exit()


def shutdown(cleanup):
    threading.Thread(target=proceed_shutdown, args=(cleanup,)).start()


class CommonException(Exception):
    pass
