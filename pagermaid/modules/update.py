from sys import executable

from pyrogram import Client

from pagermaid.listener import listener
from pagermaid.utils import lang, execute, Message, alias_command


@listener(is_plugin=False, outgoing=True, command=alias_command("update"),
          level=75,
          description=lang('update_des'),
          parameters="<true/debug>")
async def update(_: Client, message: Message):
    if len(message.parameter) > 0:
        await execute('git reset --hard HEAD')
    await execute('git pull')
    await execute(f"{executable} -m pip install -r requirements.txt --upgrade")
    await execute(f"{executable} -m pip install -r requirements.txt")
    await message.edit(lang('update_success'))
    exit(1)
