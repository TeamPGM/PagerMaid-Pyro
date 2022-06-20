from sys import executable, exit

from pagermaid.listener import listener
from pagermaid.utils import lang, execute, Message, alias_command


@listener(is_plugin=False, outgoing=True, command=alias_command("update"),
          need_admin=True,
          description=lang('update_des'),
          parameters="<true/debug>")
async def update(message: Message):
    await execute('git fetch --all')
    if len(message.parameter) > 0:
        await execute('git reset --hard origin/master')
    await execute('git pull --all')
    await execute(f"{executable} -m pip install --upgrade -r requirements.txt")
    await execute(f"{executable} -m pip install -r requirements.txt")
    await message.edit(lang('update_success'))
    exit(0)
