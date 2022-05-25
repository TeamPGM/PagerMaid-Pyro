from coloredlogs import ColoredFormatter
from logging import getLogger, StreamHandler, CRITICAL, INFO, basicConfig
from datetime import datetime
from os import getcwd
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pagermaid.config import Config
import pyromod.listen
from pyrogram import Client
import sys

pgm_version = "1.0.1"
CMD_LIST = {}
module_dir = __path__[0]
working_dir = getcwd()
# solve same process
read_context = {}
help_messages = {}
all_permissions = []
scheduler = AsyncIOScheduler()
if not scheduler.running:
    scheduler.configure(timezone="Asia/ShangHai")
    scheduler.start()
logs = getLogger(__name__)
logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
logging_handler = StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))
root_logger = getLogger()
root_logger.setLevel(CRITICAL)
root_logger.addHandler(logging_handler)
basicConfig(level=INFO)
logs.setLevel(INFO)

# easy check
if not Config.API_ID:
    logs.error("Api-ID Not Found!")
    sys.exit(1)
elif not Config.API_HASH:
    logs.error("Api-Hash Not Found!")
    sys.exit(1)
elif not Config.STRING_SESSION:
    logs.error("Api-Hash Not Found!")
    sys.exit(1)

start_time = datetime.utcnow()
bot = Client("pagermaid", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION, ipv6=Config.IPV6, proxy=Config.PROXY)


async def log(message):
    logs.info(
        message.replace('`', '\"')
    )
    if not Config.LOG:
        return
    await bot.send_message(
            Config.LOG_ID,
            message
    )
