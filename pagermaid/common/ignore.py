import json

from pyrogram.enums import ChatType

from pagermaid import bot
from pagermaid.sub_utils import Sub

ignore_groups_manager = Sub("ignore_groups")


async def get_group_list():
    try:
        return [
            json.loads(str(dialog.chat))
            for dialog in await bot.get_dialogs_list()
            if (
                dialog.chat
                and dialog.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]
            )
        ]
    except BaseException:
        return []
