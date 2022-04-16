import io
import sys
import traceback

from sys import exit
from platform import node
from getpass import getuser

from pyrogram import Client

from pagermaid import bot
from pagermaid.listener import listener
from pagermaid.utils import attach_log, execute, Message, lang


@listener(is_plugin=False, command="sh",
          level=99,
          description=lang('sh_des'),
          parameters=lang('sh_parameters'))
async def sh(_: Client, message: Message):
    """ Use the command-line from Telegram. """
    user = getuser()
    command = message.text[4:]
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
            await attach_log(bot, result, message.chat.id, "output.log", message.message_id)
            return

        await message.edit(
                            f"`{user}`@{hostname} ~"
                            f"\n> `#` {command}"
                            f"\n`{result}`"
                            )
    else:
        return


@listener(is_plugin=False, command="restart",
          level=75,
          description=lang('restart_des'))
async def restart(_: Client, message: Message):
    """ To re-execute PagerMaid. """
    if not message.text[0].isalpha():
        await message.edit(lang('restart_log'))
        exit(1)


@listener(is_plugin=False, command="eval",
          level=99,
          description=lang('eval_des'),
          parameters=lang('eval_parameters'))
async def sh_eval(_: Client, message: Message):
    """ Run python commands from Telegram. """
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await message.edit(lang('eval_need_dev'))
        return
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, message, bot)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = (
        "**>>>** ```{}``` \n```{}```".format(
            cmd,
            evaluation,
        )
    )
    if len(final_output) > 4096:
        await message.edit("**>>>** ```{}```".format(cmd))
        await attach_log(bot, evaluation, message.chat.id, "output.log", message.message_id)
    else:
        await message.edit(final_output)


async def aexec(code, event, client):
    exec(
        f"async def __aexec(e, client): "
        + "\n msg = message = e"
        + "\n reply = message.reply_to_message"
        + "\n chat = e.chat"
        + "".join(f"\n {x}" for x in code.split("\n")),
    )

    return await locals()["__aexec"](event, client)
