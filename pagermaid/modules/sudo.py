from pyrogram import Client

from pagermaid import sqlite
from pagermaid.listener import listener
from pagermaid.utils import alias_command, lang, Message, _get_sudo_list, edit_delete, edit_or_reply, _status_sudo


@listener(is_plugin=False, outgoing=True, command=alias_command("sudo"),
          parameters="{on|off|add|remove|list}",
          description=lang('sudo_des'))
async def sudo_change(client: Client, message: Message):
    """ To enable or disable sudo of your userbot. """
    input_str = message.arguments
    sudo = _get_sudo_list()
    if input_str == "on":
        if _status_sudo():
            return await edit_delete(message, lang('sudo_has_enabled'))
        sqlite["sudo_enable"] = True
        text = f"__{lang('sudo_enable')}__\n"
        if len(sudo) != 0:
            return await edit_or_reply(
                message,
                text,
            )
        text += f"**{lang('sudo_no_sudo')}**"
        return await edit_or_reply(
            message,
            text,
        )
    elif input_str == "off":
        if _status_sudo():
            del sqlite["sudo_enable"]
            text = f"__{lang('sudo_disable')}__\n"
            if len(sudo) != 0:
                return await edit_or_reply(
                    message,
                    text,
                )
            text += f"**{lang('sudo_no_sudo')}**"
            return await edit_or_reply(
                message,
                text,
            )
        await edit_delete(message, lang('sudo_has_disabled'))
    elif input_str == "add":
        reply = message.reply_to_message
        if reply:
            from_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
            if from_id in sudo:
                return await edit_delete(message, f"__{lang('sudo_add')}__")
            sudo.append(from_id)
            sqlite["sudo_list"] = sudo
            await edit_or_reply(message, f"__{lang('sudo_add')}__")
        else:
            await edit_delete(message, f"__{lang('sudo_reply')}__")
    elif input_str == "remove":
        reply = message.reply_to_message
        if reply:
            from_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
            if from_id not in sudo:
                return await edit_delete(message, f"__{lang('sudo_no')}__")
            sudo.remove(from_id)
            sqlite["sudo_list"] = sudo
            await edit_or_reply(message, f"__{lang('sudo_remove')}__")
        else:
            await edit_delete(message, f"__{lang('sudo_reply')}__")
    elif input_str == "list":
        if len(sudo) == 0:
            return await edit_delete(message, f"__{lang('sudo_no_one')}__")
        text = f"**{lang('sudo_list')}**\n\n"
        for i in sudo:
            try:
                user = await client.get_users(i)
                text += f"• {user.mention()}\n"
            except:
                text += f"• `{i}`\n"
        return await edit_or_reply(
            message,
            text,
        )
    else:
        await edit_delete(message, lang('arg_error'))
