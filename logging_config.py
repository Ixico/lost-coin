import logging

logger = logging.getLogger('MyApp')
logger.setLevel(logging.DEBUG)

log_format = '%(asctime)s [%(levelname)s] %(module)s: %(message)s'
date_format = '%H:%M:%S'
formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
