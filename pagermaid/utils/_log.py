import logging

from coloredlogs import ColoredFormatter

from pagermaid.config import Config

logs = logging.getLogger("pagermaid")

logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))

file_handler = logging.FileHandler(
    filename="data/pagermaid.log.txt", mode="w", encoding="utf-8"
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
