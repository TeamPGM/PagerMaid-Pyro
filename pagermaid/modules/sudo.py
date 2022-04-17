from pyrogram import Client

from pagermaid.single_utils import sqlite
from pagermaid.listener import listener
from pagermaid.group_manager import add_permission_for_group, Permission, remove_permission_for_group, \
    add_user_to_group, remove_user_from_group, add_permission_for_user, remove_permission_for_user, \
    permissions
from pagermaid.utils import lang, Message, edit_delete, _status_sudo
from pagermaid.single_utils import get_sudo_list


def from_msg_get_sudo_id(message: Message) -> int:
    reply = message.reply_to_message
    if reply:
        return reply.from_user.id if reply.from_user else reply.sender_chat.id
    else:
        return message.chat.id


@listener(is_plugin=False, outgoing=True, command="sudo",
          need_admin=True,
          parameters="{on|off|add|remove|gaddp|gaddu|gdelp|gdelu|glist|uaddp|udelp|list}",
          description=lang('sudo_des'))
async def sudo_change(client: Client, message: Message):
    """ To enable or disable sudo of your userbot. """
    input_str = message.arguments
    sudo = get_sudo_list()
    if input_str == "on":
        if _status_sudo():
            return await edit_delete(message, lang('sudo_has_enabled'))
        sqlite["sudo_enable"] = True
        text = f"__{lang('sudo_enable')}__\n"
        if len(sudo) != 0:
            return await message.edit(
                text,
            )
        text += f"**{lang('sudo_no_sudo')}**"
        return await message.edit(
            text,
        )
    elif input_str == "off":
        if _status_sudo():
            del sqlite["sudo_enable"]
            text = f"__{lang('sudo_disable')}__\n"
            if len(sudo) != 0:
                return await message.edit(
                    text,
                )
            text += f"**{lang('sudo_no_sudo')}**"
            return await message.edit(
                text,
            )
        await edit_delete(message, lang('sudo_has_disabled'))
    elif input_str == "add":
        from_id = from_msg_get_sudo_id(message)
        if from_id in sudo:
            return await edit_delete(message, f"__{lang('sudo_add')}__")
        sudo.append(from_id)
        sqlite["sudo_list"] = sudo
        add_user_to_group(str(from_id), "default")  # 添加到默认组
        if from_id > 0:
            await message.edit(f"__{lang('sudo_add')}__")
        else:
            await message.edit(f"__{lang('sudo_add_chat')}__")
    elif input_str == "remove":
        from_id = from_msg_get_sudo_id(message)
        if from_id not in sudo:
            return await edit_delete(message, f"__{lang('sudo_no')}__")
        sudo.remove(from_id)
        sqlite["sudo_list"] = sudo
        if from_id > 0:
            await message.edit(f"__{lang('sudo_remove')}__")
        else:
            await message.edit(f"__{lang('sudo_remove_chat')}__")
    elif input_str == "list":
        if len(sudo) == 0:
            return await edit_delete(message, f"__{lang('sudo_no_one')}__")
        text = f"**{lang('sudo_list')}**\n\n"
        for i in sudo:
            try:
                if i > 0:
                    user = await client.get_users(i)
                    text += f"• {user.mention()} - {' '.join(permissions.get_roles_for_user(str(i)))}\n"
                else:
                    chat = await client.get_chat(i)
                    text += f"• {chat.title} - {' '.join(permissions.get_roles_for_user(str(i)))}\n"
                for j in permissions.get_permissions_for_user(str(i)):
                    text += f"    • {'-' if j[2] == 'ejection' else ''}{j[1]}\n"
            except:
                text += f"• `{i}` - {' '.join(permissions.get_roles_for_user(str(i)))}\n"
        await message.edit(text)
    elif len(message.parameter) > 0:
        if len(message.parameter) == 2:
            from_id = from_msg_get_sudo_id(message)
            if message.parameter[0] == "glist":
                data = permissions.get_permissions_for_user(str(message.parameter[1]))
                if data:
                    text = f"**{message.parameter[1]} {lang('sudo_group_list')}**\n\n"
                    for i in data:
                        text += f"  • `{'-' if i[2] == 'ejection' else ''}{i[1]}`\n"
                    return await message.edit(text)
                else:
                    return await edit_delete(message, f"__{lang('sudo_group_list')}__")
            if from_id not in sudo:
                return await edit_delete(message, f"__{lang('sudo_no')}__")
            elif message.parameter[0] == "gaddu":
                add_user_to_group(str(from_id), message.parameter[1])
                return await message.edit(lang("sudo_group_add_user"))
            elif message.parameter[0] == "gdelu":
                remove_user_from_group(str(from_id), message.parameter[1])
                return await message.edit(lang("sudo_group_del_user"))
            elif message.parameter[0] == "uaddp":
                add_permission_for_user(str(from_id), Permission(message.parameter[1]))
                return await message.edit(lang("sudo_user_add_per"))
            elif message.parameter[0] == "udelp":
                remove_permission_for_user(str(from_id), Permission(message.parameter[1]))
                return await message.edit(lang("sudo_user_del_per"))
            else:
                return await edit_delete(message, lang('arg_error'))
        if len(message.parameter) == 3:
            if message.parameter[0] == "gaddp":
                add_permission_for_group(message.parameter[1], Permission(message.parameter[2]))
                return await message.edit(lang("sudo_group_add_per"))
            elif message.parameter[0] == "gdelp":
                remove_permission_for_group(message.parameter[1], Permission(message.parameter[2]))
                return await message.edit(lang("sudo_group_del_per"))
            else:
                return await edit_delete(message, lang('arg_error'))
        else:
            await edit_delete(message, lang('arg_error'))
    else:
        await edit_delete(message, lang('arg_error'))
