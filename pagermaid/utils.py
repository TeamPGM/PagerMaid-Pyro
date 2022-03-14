import subprocess
from importlib.util import find_spec
from os.path import exists
from typing import Optional

import httpx
from os import remove
from sys import executable
from asyncio import create_subprocess_shell, sleep
from asyncio.subprocess import PIPE

from pyrogram import filters
from pagermaid.config import Config
from pagermaid import bot
from pagermaid.single_utils import _status_sudo, get_sudo_list, Message


def lang(text: str) -> str:
    """ i18n """
    result = Config.lang_dict.get(text, text)
    return result


def alias_command(command: str) -> str:
    """ alias """
    return Config.alias_dict.get(command, command)


async def attach_report(plaintext, file_name, reply_id=None, caption=None):
    """ Attach plaintext as logs. """
    file = open(file_name, "w+")
    file.write(plaintext)
    file.close()
    try:
        await bot.send_document(
            "PagerMaid_Modify_bot",
            file_name,
            reply_to_message_id=reply_id,
            caption=caption
        )
    except:
        return
    remove(file_name)


async def attach_log(plaintext, chat_id, file_name, reply_id=None, caption=None):
    """ Attach plaintext as logs. """
    file = open(file_name, "w+")
    file.write(plaintext)
    file.close()
    await bot.send_document(
        chat_id,
        file_name,
        reply_to_message_id=reply_id,
        caption=caption
    )
    remove(file_name)


async def upload_attachment(file_path, chat_id, reply_id, caption=None, preview=None, document=None):
    """ Uploads a local attachment file. """
    if not exists(file_path):
        return False
    try:
        await bot.send_document(
            chat_id,
            file_path,
            reply_to_message_id=reply_id,
            caption=caption
        )
    except BaseException as exception:
        raise exception
    return True


async def execute(command, pass_error=True):
    """ Executes command and returns output, with the option of enabling stderr. """
    executor = await create_subprocess_shell(
        command,
        stdout=PIPE,
        stderr=PIPE,
        stdin=PIPE
    )

    stdout, stderr = await executor.communicate()
    if pass_error:
        try:
            result = str(stdout.decode().strip()) \
                     + str(stderr.decode().strip())
        except UnicodeDecodeError:
            result = str(stdout.decode('gbk').strip()) \
                     + str(stderr.decode('gbk').strip())
    else:
        try:
            result = str(stdout.decode().strip())
        except UnicodeDecodeError:
            result = str(stdout.decode('gbk').strip())
    return result


def pip_install(package: str, version: Optional[str] = "", alias: Optional[str] = "") -> bool:
    """ Auto install extra pypi packages """
    if not alias:
        # when import name is not provided, use package name
        alias = package
    if find_spec(alias) is None:
        subprocess.call([executable, "-m", "pip", "install", f"{package}{version}"])
        if find_spec(package) is None:
            return False
    return True


async def edit_delete(message: Message,
                      text: str,
                      time: int = 5,
                      parse_mode: Optional[str] = object,
                      disable_web_page_preview: bool = None):
    sudo_users = get_sudo_list()
    from_id = message.from_user.id if message.from_user else message.sender_chat.id
    if from_id in sudo_users:
        reply_to = message.reply_to_message
        event = (
            await reply_to.reply(text, disable_web_page_preview=disable_web_page_preview, parse_mode=parse_mode)
            if reply_to
            else await message.reply(
                text, disable_web_page_preview=disable_web_page_preview, parse_mode=parse_mode
            )
        )
    else:
        event = await message.edit(
            text, disable_web_page_preview=disable_web_page_preview, parse_mode=parse_mode
        )
    await sleep(time)
    return await event.delete()


def if_sudo(message: Message):
    if not _status_sudo():
        return False
    try:
        from_id = message.from_user.id if message.from_user else message.sender_chat.id
        return from_id in get_sudo_list()
    except Exception as e:
        return False


""" Init httpx client """
# 使用自定义 UA
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
}
client = httpx.AsyncClient(timeout=10.0, headers=headers)
sudo_filter = filters.create(lambda _, __, message: if_sudo(message))
