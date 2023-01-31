from os.path import exists, sep
from sys import exit
from platform import node
from getpass import getuser

from pyrogram.enums import ParseMode

from pagermaid.common.system import run_eval
from pagermaid.listener import listener
from pagermaid.enums import Message
from pagermaid.utils import attach_log, execute, lang, upload_attachment


@listener(is_plugin=False, command="sh",
          need_admin=True,
          description=lang('sh_des'),
          parameters=lang('sh_parameters'))
async def sh(message: Message):
    """ Use the command-line from Telegram. """
    user = getuser()
    command = message.arguments
    hostname = node()

    if not command:
        await message.edit(lang('arg_error'))
        return

    message = await message.edit(
        f"`{user}`@{hostname} ~"
        f"\n> `$` {command}"
    )

    result = await execute(command)

    if result:
        if len(result) > 4096:
            await attach_log(result, message.chat.id, "output.log", message.id)
            return

        await message.edit(
            f"`{user}`@{hostname} ~"
            f"\n> `#` {command}"
            f"\n`{result}`"
        )
    else:
        return


@listener(is_plugin=False, command="restart",
          need_admin=True,
          description=lang('restart_des'))
async def restart(message: Message):
    """ To re-execute PagerMaid. """
    if not message.text[0].isalpha():
        await message.edit(lang('restart_log'))
        exit(0)


@listener(is_plugin=False, command="eval",
          need_admin=True,
          description=lang('eval_des'),
          parameters=lang('eval_parameters'))
async def sh_eval(message: Message):
    """ Run python commands from Telegram. """
    dev_mode = exists(f"data{sep}dev")
    try:
        assert dev_mode
        cmd = message.text.split(" ", maxsplit=1)[1]
    except (IndexError, AssertionError):
        return await message.edit(lang('eval_need_dev'))
    final_output = await run_eval(cmd, message)
    if len(final_output) > 4096:
        message = await message.edit(f"**>>>** `{cmd}`", parse_mode=ParseMode.MARKDOWN)
        await attach_log(final_output, message.chat.id, "output.log", message.id)
    else:
        await message.edit(final_output)


@listener(is_plugin=False, command="send_log",
          need_admin=True,
          description=lang("send_log_des"))
async def send_log(message: Message):
    """ Send log to a chat. """
    if not exists("pagermaid.log.txt"):
        return await message.edit(lang("send_log_not_found"))
    await upload_attachment("pagermaid.log.txt",
                            message.chat.id,
                            message.reply_to_message_id or message.reply_to_top_message_id,
                            thumb=f"pagermaid{sep}assets{sep}logo.jpg",
                            caption=lang("send_log_caption"))
    await message.safe_delete()
