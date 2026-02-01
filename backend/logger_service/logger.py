import logging
import uuid
import contextvars
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from colorlog import ColoredFormatter
import os

request_id_ctx = contextvars.ContextVar("request_id", default=None)
client_ip_ctx = contextvars.ContextVar("client_ip", default=None)

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get() or str(uuid.uuid4())
        record.client_ip = client_ip_ctx.get() or "unknown"
        return True

def setup_logger():
    base_log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(base_log_dir, exist_ok=True)
    log_file_path = os.path.join(base_log_dir, "app.log")

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    json_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(client_ip)s"
    )

    console_formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s %(asctime)s %(name)s %(message)s [%(request_id)s %(client_ip)s]",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(json_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    context_filter = ContextFilter()
    file_handler.addFilter(context_filter)
    console_handler.addFilter(context_filter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
