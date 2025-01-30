# server/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os


class ServerLogger:
    def __init__(self):
        self.logger = logging.getLogger("ServerLogger")
        self._setup_logger()

    def _setup_logger(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')

        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # File handlers
        file_handler = RotatingFileHandler(
            'logs/server.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)
