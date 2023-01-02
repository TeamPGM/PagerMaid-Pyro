import contextlib

from typing import Callable, Awaitable, Set, Dict

import pyrogram.types
from coloredlogs import ColoredFormatter
from datetime import datetime, timezone
from logging import getLogger, StreamHandler, CRITICAL, INFO, basicConfig, DEBUG, Formatter, FileHandler
from os import getcwd

from pagermaid.config import Config
from pagermaid.scheduler import scheduler
import pyromod.listen
from pyrogram import Client

from pyromod.listen.temp_fix import temp_fix

pgm_version = "1.2.21"
CMD_LIST = {}
module_dir = __path__[0]
working_dir = getcwd()
# solve same process
read_context = {}
help_messages = {}
hook_functions: Dict[str, Set[Callable[[], Awaitable[None]]]] = {
    "startup": set(), "shutdown": set(), "command_pre": set(), "command_post": set(), "process_error": set(),
    "load_plugins_finished": set(),
}
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

if not Config.API_ID or not Config.API_HASH:
    logs.warning("Api-ID or Api-HASH Not Found!")
    Config.API_ID = Config.DEFAULT_API_ID
    Config.API_HASH = Config.DEFAULT_API_HASH

start_time = datetime.now(timezone.utc)

with contextlib.suppress(ImportError):
    import uvloop  # noqa
    uvloop.install()

if not scheduler.running:
    scheduler.start()
bot = Client(
    "pagermaid",
    session_string=Config.STRING_SESSION,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    ipv6=Config.IPV6,
    proxy=Config.PROXY,
    app_version=f"PagerMaid {pgm_version}",
)
# temp fix topics group
setattr(pyrogram.types.Message, "old_parse", getattr(pyrogram.types.Message, "_parse"))
setattr(pyrogram.types.Message, "_parse", temp_fix)
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
