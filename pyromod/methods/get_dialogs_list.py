from datetime import timedelta

from pyrogram import Client

from pagermaid.common.cache import cache


@cache(ttl=timedelta(hours=1))
async def get_dialogs_list(client: Client):
    dialogs = []
    async for dialog in client.get_dialogs():
        dialogs.append(dialog)
    return dialogs
