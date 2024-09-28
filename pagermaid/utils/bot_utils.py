from asyncio import sleep
from datetime import datetime, timedelta
from os.path import exists
from typing import Optional, TYPE_CHECKING

from pagermaid.dependence import get_sudo_list
from pagermaid.services import bot
from . import logs
from ._path import safe_remove
from ..config import Config

if TYPE_CHECKING:
    from pagermaid.enums import Message
    from pyrogram import enums


async def attach_report(plaintext, file_name, reply_id=None, caption=None):
    """Attach plaintext as logs."""
    with open(file_name, "w+") as file:
        file.write(plaintext)
    try:
        await bot.send_document(
            "PagerMaid_Modify_bot",
            file_name,
            reply_to_message_id=reply_id,
            caption=caption,
        )
    except Exception:  # noqa
        return
    safe_remove(file_name)


async def attach_log(plaintext, chat_id, file_name, reply_id=None, caption=None):
    """Attach plaintext as logs."""
    with open(file_name, "w+", encoding="utf-8") as file:
        file.write(plaintext)
    await bot.send_document(
        chat_id, file_name, reply_to_message_id=reply_id, caption=caption
    )
    safe_remove(file_name)


async def upload_attachment(
    file_path, chat_id, reply_id, message_thread_id=None, caption=None, thumb=None
):
    """Uploads a local attachment file."""
    if not exists(file_path):
        return False
    try:
        await bot.send_document(
            chat_id,
            file_path,
            message_thread_id=message_thread_id,
            thumb=thumb,
            reply_to_message_id=reply_id,
            caption=caption,
        )
    except BaseException as exception:
        raise exception
    return True


async def edit_delete(
    message: "Message",
    text: str,
    time: int = 5,
    parse_mode: Optional["enums.ParseMode"] = None,
    disable_web_page_preview: bool = None,
):
    sudo_users = get_sudo_list()
    from_id = message.from_user.id if message.from_user else message.sender_chat.id
    if from_id in sudo_users:
        reply_to = message.reply_to_message
        event = (
            await reply_to.reply(
                text,
                disable_web_page_preview=disable_web_page_preview,
                parse_mode=parse_mode,
            )
            if reply_to
            else await message.reply(
                text,
                disable_web_page_preview=disable_web_page_preview,
                parse_mode=parse_mode,
            )
        )
    else:
        event = await message.edit(
            text,
            disable_web_page_preview=disable_web_page_preview,
            parse_mode=parse_mode,
        )
    await sleep(time)
    return await event.delete()


async def log(message: str, notice: bool = False):
    logs.info(message.replace("`", '"'))
    if not Config.LOG:
        return
    try:
        await bot.send_message(
            Config.LOG_ID,
            message,
            schedule_date=(datetime.now() + timedelta(seconds=3)) if notice else None,
        )
    except Exception:
        Config.LOG = False
        Config.LOG_ID = "me"
