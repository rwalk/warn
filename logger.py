from logging.handlers import RotatingFileHandler
import logging

class WARNLogger:

    @staticmethod
    def get_logstash_handler():
        formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
        handler = RotatingFileHandler("/var/log/warn/warn.log", maxBytes=10000000, backupCount=5)
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        return handler