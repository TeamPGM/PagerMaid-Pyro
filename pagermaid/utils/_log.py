import logging
from logging.handlers import RotatingFileHandler

from coloredlogs import ColoredFormatter

from pagermaid.config import Config

logs = logging.getLogger("pagermaid")

logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))

file_handler = RotatingFileHandler(
    filename="data/pagermaid.log.txt",
    encoding="utf-8",
    maxBytes=50 * 1024 * 1024, # 50MB
    backupCount=1 # Only 1 backup to enable rotation
)
file_handler.setFormatter(logging.Formatter(logging_format))

logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    handlers=[logging_handler, file_handler],
)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG if Config.DEBUG else logging.CRITICAL)

pyro_logger = logging.getLogger("pyrogram")
pyro_logger.setLevel(logging.INFO if Config.DEBUG else logging.CRITICAL)

logs.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)
