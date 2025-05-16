from pagermaid.dependence import get_sudo_list, status_sudo, sqlite
from pagermaid.enums import Client, Message
from pagermaid.enums.command import CommandHandler
from pagermaid.group_manager import (
    add_permission_for_group,
    Permission,
    remove_permission_for_group,
    add_user_to_group,
    remove_user_from_group,
    add_permission_for_user,
    remove_permission_for_user,
    permissions,
    rename_group,
)
from pagermaid.listener import listener
from pagermaid.utils import lang
from pagermaid.utils.bot_utils import edit_delete


def from_msg_get_sudo_id(message: Message) -> int:
    if reply := message.reply_to_message:
        return reply.from_user.id if reply.from_user else reply.sender_chat.id
    else:
        return message.chat.id


@listener(
    is_plugin=False,
    command="sudo",
    need_admin=True,
    parameters="{on|off|add|remove|gaddp|gaddu|gdelp|gdelu|glist|grename|uaddp|udelp|list}",
    description=lang("sudo_des"),
)
async def sudo_change(message: Message):
    """To enable or disable sudo of your userbot."""
    await edit_delete(message, lang("arg_error"))


sudo_change: "CommandHandler"


@sudo_change.sub_command(
    is_plugin=False,
    command="on",
    need_admin=True,
)
async def sudo_on(message: Message):
    sudo = get_sudo_list()
    if status_sudo():
        return await edit_delete(message, lang("sudo_has_enabled"))
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


@sudo_change.sub_command(
    is_plugin=False,
    command="off",
    need_admin=True,
)
async def sudo_off(message: Message):
    sudo = get_sudo_list()
    if status_sudo():
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
    await edit_delete(message, lang("sudo_has_disabled"))


@sudo_change.sub_command(
    is_plugin=False,
    command="add",
    need_admin=True,
)
async def sudo_add(message: Message):
    sudo = get_sudo_list()
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


@sudo_change.sub_command(
    is_plugin=False,
    command="remove",
    need_admin=True,
)
async def sudo_remove(message: Message):
    sudo = get_sudo_list()
    from_id = from_msg_get_sudo_id(message)
    if from_id not in sudo:
        return await edit_delete(message, f"__{lang('sudo_no')}__")
    sudo.remove(from_id)
    sqlite["sudo_list"] = sudo
    if from_id > 0:
        await message.edit(f"__{lang('sudo_remove')}__")
    else:
        await message.edit(f"__{lang('sudo_remove_chat')}__")


@sudo_change.sub_command(
    is_plugin=False,
    command="list",
    need_admin=True,
)
async def sudo_list(client: Client, message: Message):
    sudo = get_sudo_list()
    if len(sudo) == 0:
        return await edit_delete(message, f"__{lang('sudo_no_one')}__")
    text = f"**{lang('sudo_list')}**\n\n"
    for i in sudo.copy():
        try:
            if i > 0:
                user = await client.get_users(i)
                if user.is_deleted:
                    sudo.remove(i)
                    sqlite["sudo_list"] = sudo
                    continue
                text += f"• {user.mention()} - {' '.join(permissions.get_roles_for_user(str(i)))}\n"
            else:
                chat = await client.get_chat(i)
                text += f"• {chat.title} - {' '.join(permissions.get_roles_for_user(str(i)))}\n"
            for j in permissions.get_permissions_for_user(str(i)):
                text += f"    • {'-' if j[2] == 'ejection' else ''}{j[1]}\n"
        except Exception:
            text += f"• `{i}` - {' '.join(permissions.get_roles_for_user(str(i)))}\n"
    await message.edit(text)


def check_parameter_length(length: int, check_permission: bool):
    def decorator(func):
        async def wrapper(message: Message):
            if len(message.parameter) != length:
                return await edit_delete(message, lang("arg_error"))
            if check_permission:
                sudo = get_sudo_list()
                from_id = from_msg_get_sudo_id(message)
                if from_id not in sudo:
                    return await edit_delete(message, f"__{lang('sudo_no')}__")

            return await func(message)

        return wrapper

    return decorator


@sudo_change.sub_command(
    is_plugin=False,
    command="glist",
    need_admin=True,
)
@check_parameter_length(2, False)
async def sudo_glist(message: Message):
    if not (data := permissions.get_permissions_for_user(str(message.parameter[1]))):
        return await edit_delete(message, f"__{lang('sudo_group_list')}__")
    text = f"**{message.parameter[1]} {lang('sudo_group_list')}**\n\n"
    for i in data:
        text += f"  • `{'-' if i[2] == 'ejection' else ''}{i[1]}`\n"
    return await message.edit(text)


@sudo_change.sub_command(
    is_plugin=False,
    command="gaddu",
    need_admin=True,
)
@check_parameter_length(2, True)
async def sudo_gaddu(message: Message):
    from_id = from_msg_get_sudo_id(message)
    add_user_to_group(str(from_id), message.parameter[1])
    return await message.edit(lang("sudo_group_add_user"))


@sudo_change.sub_command(
    is_plugin=False,
    command="gdelu",
    need_admin=True,
)
@check_parameter_length(2, True)
async def sudo_gdelu(message: Message):
    from_id = from_msg_get_sudo_id(message)
    remove_user_from_group(str(from_id), message.parameter[1])
    return await message.edit(lang("sudo_group_del_user"))


@sudo_change.sub_command(
    is_plugin=False,
    command="uaddp",
    need_admin=True,
)
@check_parameter_length(2, True)
async def sudo_uaddp(message: Message):
    from_id = from_msg_get_sudo_id(message)
    add_permission_for_user(str(from_id), Permission(message.parameter[1]))
    return await message.edit(lang("sudo_user_add_per"))


@sudo_change.sub_command(
    is_plugin=False,
    command="udelp",
    need_admin=True,
)
@check_parameter_length(2, True)
async def sudo_udelp(message: Message):
    from_id = from_msg_get_sudo_id(message)
    remove_permission_for_user(str(from_id), Permission(message.parameter[1]))
    return await message.edit(lang("sudo_user_del_per"))


@sudo_change.sub_command(
    is_plugin=False,
    command="gaddp",
    need_admin=True,
)
@check_parameter_length(3, False)
async def sudo_gaddp(message: Message):
    add_permission_for_group(message.parameter[1], Permission(message.parameter[2]))
    return await message.edit(lang("sudo_group_add_per"))


@sudo_change.sub_command(
    is_plugin=False,
    command="gdelp",
    need_admin=True,
)
@check_parameter_length(3, False)
async def sudo_gdelp(message: Message):
    remove_permission_for_group(message.parameter[1], Permission(message.parameter[2]))
    return await message.edit(lang("sudo_group_del_per"))


@sudo_change.sub_command(
    is_plugin=False,
    command="grename",
    need_admin=True,
)
@check_parameter_length(3, False)
async def sudo_grename(message: Message):
    old_name = message.parameter[1]
    new_name = message.parameter[2]
    rename_group(old_name, new_name)
    await message.edit(lang("sudo_group_rename_per"))