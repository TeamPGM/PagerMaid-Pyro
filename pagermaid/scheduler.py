import contextlib
import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pagermaid.single_utils import Message

scheduler = AsyncIOScheduler(timezone="Asia/ShangHai")


async def delete_message(message: Message) -> bool:
    with contextlib.suppress(Exception):
        await message.delete()
        return True
    return False


def add_delete_message_job(message: Message, delete_seconds: int = 60):
    scheduler.add_job(
        delete_message, "date",
        id=f"{message.chat.id}|{message.id}|delete_message",
        name=f"{message.chat.id}|{message.id}|delete_message",
        args=[message],
        run_date=datetime.datetime.now(pytz.timezone("Asia/Shanghai")) + datetime.timedelta(seconds=delete_seconds),
        replace_existing=True)
