""" PagerMaid module for different ways to avoid users. """

from pagermaid import log
from pagermaid.single_utils import sqlite
from pagermaid.utils import lang
from pagermaid.enums import Client, Message
from pagermaid.listener import listener


@listener(is_plugin=False, outgoing=True, command="ghost",
          description=lang('ghost_des'),
          parameters="<true|false|status>")
async def ghost(client: Client, message: Message):
    """ Toggles ghosting of a user. """
    if len(message.parameter) != 1:
        await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        return
    myself = await client.get_me()
    self_user_id = myself.id
    if message.parameter[0] == "true":
        if message.chat.id == self_user_id:
            return await message.edit(lang('ghost_e_mark'))
        sqlite[f"ghosted.chat_id.{str(message.chat.id)}"] = True
        await message.safe_delete()
        await log(f"{lang('ghost_set_f')} ChatID {str(message.chat.id)} {lang('ghost_set_l')}")
    elif message.parameter[0] == "false":
        if message.chat.id == self_user_id:
            await message.edit(lang('ghost_e_mark'))
            return
        try:
            del sqlite[f"ghosted.chat_id.{str(message.chat.id)}"]
        except KeyError:
            return await message.edit(lang('ghost_e_noexist'))
        await message.safe_delete()
        await log(f"{lang('ghost_set_f')} ChatID {str(message.chat.id)} {lang('ghost_cancel')}")
    elif message.parameter[0] == "status":
        if sqlite.get(f"ghosted.chat_id.{str(message.chat.id)}", None):
            await message.edit(lang('ghost_e_exist'))
        else:
            await message.edit(lang('ghost_e_noexist'))
    else:
        await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")


@listener(is_plugin=False, outgoing=True, command="deny",
          need_admin=True,
          description=lang('deny_des'),
          parameters="<true|false|status>")
async def deny(client: Client, message: Message):
    """ Toggles denying of a user. """
    if len(message.parameter) != 1:
        await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        return
    myself = await client.get_me()
    self_user_id = myself.id
    if message.parameter[0] == "true":
        if message.chat.id == self_user_id:
            return await message.edit(lang('ghost_e_mark'))
        sqlite[f"denied.chat_id.{str(message.chat.id)}"] = True
        await message.safe_delete()
        await log(f"ChatID {str(message.chat.id)} {lang('deny_set')}")
    elif message.parameter[0] == "false":
        if message.chat.id == self_user_id:
            await message.edit(lang('ghost_e_mark'))
            return
        try:
            del sqlite[f"denied.chat_id.{str(message.chat.id)}"]
        except KeyError:
            return await message.edit(lang('deny_e_noexist'))
        await message.safe_delete()
        await log(f"ChatID {str(message.chat.id)} {lang('deny_cancel')}")
    elif message.parameter[0] == "status":
        if sqlite.get(f"denied.chat_id.{str(message.chat.id)}", None):
            await message.edit(lang('deny_e_exist'))
        else:
            await message.edit(lang('deny_e_noexist'))
    else:
        await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")


@listener(is_plugin=False, incoming=True, outgoing=False, ignore_edited=True)
async def set_read_acknowledgement(client: Client, message: Message):
    """ Event handler to infinitely read ghosted messages. """
    if sqlite.get(f"ghosted.chat_id.{str(message.chat.id)}", None):
        await client.read_chat_history(message.chat.id)


@listener(is_plugin=False, incoming=True, outgoing=False, ignore_edited=True)
async def message_removal(message: Message):
    """ Event handler to infinitely delete denied messages. """
    if sqlite.get(f"denied.chat_id.{str(message.chat.id)}", None):
        await message.safe_delete()
