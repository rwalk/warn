from logging.handlers import RotatingFileHandler

class WARNLogger:

    @staticmethod
    def get_logstash_handler():
        handler = RotatingFileHandler("logs/warn.log", maxBytes=1000)
        return handler