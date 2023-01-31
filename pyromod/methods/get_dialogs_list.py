from datetime import timedelta

from pyrogram import Client
from pyrogram.enums import ChatType

from pagermaid.common.cache import cache


@cache(ttl=timedelta(hours=1))
async def get_dialogs_list(client: Client):
    dialogs = []
    async for dialog in client.get_dialogs():
        dialogs.append(dialog)
        if dialog.chat.type == ChatType.SUPERGROUP:
            break
    return dialogs
