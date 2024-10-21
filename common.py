import datetime
import logging
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_STOPPED as SCHEDULER_STATE_STOPPED


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

SCHEDULERS = []


# todo: handle sigint (it doesn't work now)

def handle_sigint(signum, frame):
    shutdown()


def proceed_shutdown():
    for scheduler in SCHEDULERS:
        if scheduler.state != SCHEDULER_STATE_STOPPED:
            scheduler.shutdown()
    STOP_EVENT.set()
    for thread in threading.enumerate():
        if thread is not threading.current_thread():
            thread.join()
    exit()


def shutdown():
    threading.Thread(target=proceed_shutdown).start()


def register_scheduler(job_function, interval, initial_delay):
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(job_function, 'interval', seconds=interval)
    job.modify(next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=initial_delay))
    SCHEDULERS.append(scheduler)
    scheduler.start()


class CommonException(Exception):
    pass
