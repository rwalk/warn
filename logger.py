from logging.handlers import RotatingFileHandler
import sys
import os

class WARNLogger:

    @staticmethod
    def get_logstash_handler():
        handler = RotatingFileHandler("/var/log/warn/warn.log", maxBytes=1000)
        return handler