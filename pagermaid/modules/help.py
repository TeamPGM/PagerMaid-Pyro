""" The help module. """

from os import listdir

from pyrogram.enums import ParseMode

from pagermaid import help_messages, Config
from pagermaid.common.alias import AliasManager
from pagermaid.config import CONFIG_PATH
from pagermaid.group_manager import enforce_permission
from pagermaid.common.reload import reload_all
from pagermaid.utils import lang, Message, from_self, from_msg_get_sudo_uid
from pagermaid.listener import listener


@listener(
    is_plugin=False,
    command="help",
    description=lang("help_des"),
    parameters=f"<{lang('command')}>",
)
async def help_command(message: Message):
    """The help new command,"""
    if message.arguments:
        if message.arguments in help_messages:
            if from_self(message) or enforce_permission(
                from_msg_get_sudo_uid(message),
                help_messages[message.arguments]["permission"],
            ):
                await message.edit(f"{help_messages[message.arguments]['use']}")
            else:
                await message.edit(lang("help_no_permission"))
        else:
            await message.edit(lang("arg_error"))
    else:
        result = f"**{lang('help_list')}: \n**"
        support_commands = [
            "username",
            "name",
            "pfp",
            "bio",
            "rmpfp",
            "profile",
            "block",
            "unblock",
            "ghost",
            "deny",
            "convert",
            "caption",
            "ocr",
            "highlight",
            "time",
            "translate",
            "tts",
            "google",
            "animate",
            "teletype",
            "widen",
            "owo",
            "flip",
            "rng",
            "aaa",
            "tuxsay",
            "coin",
            "help",
            "lang",
            "alias",
            "id",
            "uslog",
            "log",
            "re",
            "leave",
            "hitokoto",
            "apt",
            "prune",
            "selfprune",
            "yourprune",
            "del",
            "genqr",
            "parseqr",
            "sb",
            "sysinfo",
            "status",
            "stats",
            "speedtest",
            "connection",
            "pingdc",
            "ping",
            "topcloud",
            "s",
            "sticker",
            "sh",
            "restart",
            "trace",
            "chat",
            "update",
        ]
        for command in sorted(help_messages, reverse=False):
            if str(command) in support_commands:
                continue
            if from_self(message) or enforce_permission(
                from_msg_get_sudo_uid(message), help_messages[command]["permission"]
            ):
                result += f"`{command}`, "
        if result == f"**{lang('help_list')}: \n**":
            """The help raw command,"""
            for command in sorted(help_messages, reverse=False):
                if from_self(message) or enforce_permission(
                    from_msg_get_sudo_uid(message), help_messages[command]["permission"]
                ):
                    result += f"`{command}`, "
        await message.edit(
            result[:-2]
            + f"\n**{lang('help_send')} \",help <{lang('command')}>\" {lang('help_see')}**\n"
            f"[{lang('help_source')}](https://t.me/PagerMaid_Modify) "
            f"[{lang('help_plugin')}](https://index.xtaolabs.com/) "
            f"[{lang('help_module')}](https://wiki.xtaolabs.com/)",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


@listener(
    is_plugin=False,
    command="help_raw",
    description=lang("help_des"),
    parameters=f"<{lang('command')}>",
)
async def help_raw_command(message: Message):
    """The help raw command,"""
    if message.arguments:
        if message.arguments in help_messages:
            if from_self(message) or enforce_permission(
                from_msg_get_sudo_uid(message),
                help_messages[message.arguments]["permission"],
            ):
                await message.edit(f"{help_messages[message.arguments]['use']}")
            else:
                await message.edit(lang("help_no_permission"))
        else:
            await message.edit(lang("arg_error"))
    else:
        result = f"**{lang('help_list')}: \n**"
        for command in sorted(help_messages, reverse=False):
            if from_self(message) or enforce_permission(
                from_msg_get_sudo_uid(message), help_messages[command]["permission"]
            ):
                result += f"`{command}`, "
        await message.edit(
            f"""{result[:-2]}\n**{lang('help_send')} ",help <{lang('command')}>" {lang('help_see')}** [{lang('help_source')}](https://t.me/PagerMaid_Modify)""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


@listener(
    is_plugin=False, command="lang", need_admin=True, description=lang("lang_des")
)
async def lang_change(message: Message):
    to_lang = message.arguments
    from_lang = Config.LANGUAGE
    dir_, dir__ = listdir("languages/built-in"), []
    for i in dir_:
        if i.find("yml") != -1:
            dir__.append(i[:-4])
    file = CONFIG_PATH.read_text()
    if to_lang in dir__:
        file = file.replace(
            f'application_language: "{from_lang}"', f'application_language: "{to_lang}"'
        )
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(file)
        await message.edit(f"{lang('lang_change_to')} {to_lang}, {lang('lang_reboot')}")
        await reload_all()
    else:
        await message.edit(
            f'{lang("lang_current_lang")} {Config.LANGUAGE}\n\n'
            f'{lang("lang_all_lang")}{"，".join(dir__)}'
        )


@listener(
    is_plugin=False,
    outgoing=True,
    command="alias",
    disallow_alias=True,
    need_admin=True,
    description=lang("alias_des"),
    parameters="{list|del|set} <source> <to>",
)
async def alias_commands(message: Message):
    alias_manager = AliasManager()
    if len(message.parameter) == 0:
        await message.edit(lang("arg_error"))
    elif len(message.parameter) == 1:
        if alias_manager.alias_list:
            await message.edit(
                lang("alias_list") + "\n\n" + alias_manager.get_all_alias_text()
            )
        else:
            await message.edit(lang("alias_no"))
    elif len(message.parameter) == 2:
        source_command = message.parameter[1]
        try:
            alias_manager.delete_alias(source_command)
            await message.edit(lang("alias_success"))
            await reload_all()
        except KeyError:
            await message.edit(lang("alias_no_exist"))
            return
    elif len(message.parameter) == 3:
        source_command = message.parameter[1]
        to_command = message.parameter[2]
        if to_command in help_messages:
            await message.edit(lang("alias_exist"))
            return
        alias_manager.add_alias(source_command, to_command)
        await message.edit(lang("alias_success"))
        await reload_all()
