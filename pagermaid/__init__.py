import contextlib
import sys

from typing import Callable, Awaitable, Set, Dict

from coloredlogs import ColoredFormatter
from datetime import datetime, timezone
from logging import getLogger, StreamHandler, CRITICAL, INFO, basicConfig, DEBUG, Formatter, FileHandler
from os import getcwd

from pagermaid.config import Config
from pagermaid.scheduler import scheduler
import pyromod.listen
from pyrogram import Client

pgm_version = "1.2.8"
CMD_LIST = {}
module_dir = __path__[0]
working_dir = getcwd()
# solve same process
read_context = {}
help_messages = {}
hook_functions: Dict[str, Set[Callable[[], Awaitable[None]]]] = {
    "startup": set(), "shutdown": set(), "command_pre": set(), "command_post": set(), "process_error": set(), }
all_permissions = []

logs = getLogger(__name__)
logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
logging_handler = StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))
root_logger = getLogger()
root_logger.setLevel(DEBUG if Config.DEBUG else CRITICAL)
root_logger.addHandler(logging_handler)
pyro_logger = getLogger("pyrogram")
pyro_logger.setLevel(CRITICAL)
pyro_logger.addHandler(logging_handler)
file_handler = FileHandler(filename="pagermaid.log.txt", mode="w", encoding="utf-8")
file_handler.setFormatter(Formatter(logging_format))
root_logger.addHandler(file_handler)
basicConfig(level=DEBUG if Config.DEBUG else INFO)
logs.setLevel(DEBUG if Config.DEBUG else INFO)

# easy check
if not Config.API_ID:
    logs.error("Api-ID Not Found!")
    sys.exit(1)
elif not Config.API_HASH:
    logs.error("Api-Hash Not Found!")
    sys.exit(1)

start_time = datetime.now(timezone.utc)

with contextlib.suppress(ImportError):
    import uvloop  # noqa
    uvloop.install()

if not scheduler.running:
    scheduler.start()
bot = Client("pagermaid",
             session_string=Config.STRING_SESSION,
             api_id=Config.API_ID,
             api_hash=Config.API_HASH,
             ipv6=Config.IPV6,
             proxy=Config.PROXY)
bot.job = scheduler


async def log(message):
    logs.info(
        message.replace('`', '\"')
    )
    if not Config.LOG:
        return
    try:
        await bot.send_message(
                Config.LOG_ID,
                message
        )
    except Exception:
        Config.LOG = False
        Config.LOG_ID = "me"
