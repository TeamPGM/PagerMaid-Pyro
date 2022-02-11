from sys import executable

from pyrogram import Client

from pagermaid.listener import listener
from pagermaid.utils import lang, execute, Message, alias_command, edit_or_reply


@listener(is_plugin=False, outgoing=True, command=alias_command("update"),
          description=lang('update_des'),
          parameters="<true/debug>")
async def update(client: Client, message: Message):
    if len(message.parameter) > 0:
        await execute('git reset --hard HEAD')
    await execute('git pull')
    await execute(f"{executable} -m pip install -r requirements.txt --upgrade")
    await execute(f"{executable} -m pip install -r requirements.txt")
    await edit_or_reply(message, lang('update_success'))
    exit(1)
