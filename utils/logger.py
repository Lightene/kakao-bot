import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logger():
    logger = logging.getLogger("ServerLogger")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handlers = [
        logging.FileHandler('logs/server.log'),
        logging.FileHandler('logs/error.log'),
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
