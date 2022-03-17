""" The help module. """
from pyrogram import Client

from json import dump as json_dump
from os import listdir, sep
from pagermaid import help_messages, Config
from pagermaid.utils import lang, Message, alias_command
from pagermaid.listener import listener


@listener(is_plugin=False, command=alias_command("help"),
          description=lang('help_des'),
          parameters=f"<{lang('command')}>")
async def help_command(client: Client, message: Message):
    """ The help new command,"""
    support_commands = ['username', 'name', 'pfp', 'bio', 'rmpfp',
                        'profile', 'block', 'unblock', 'ghost', 'deny', 'convert',
                        'caption', 'ocr', 'highlight', 'time', 'translate',
                        'tts', 'google', 'animate',
                        'teletype', 'widen', 'owo', 'flip',
                        'rng', 'aaa', 'tuxsay', 'coin', 'help',
                        'lang', 'alias', 'id', 'uslog', 'log',
                        're', 'leave', 'hitokoto', 'apt', 'prune', 'selfprune',
                        'yourprune', 'del', 'genqr', 'parseqr',
                        'sb', 'sysinfo', 'status',
                        'stats', 'speedtest', 'connection',
                        'pingdc', 'ping', 'topcloud',
                        's', 'sticker', 'sh', 'restart',
                        'trace', 'chat', 'update']
    if message.arguments:
        if message.arguments in help_messages:
            await message.edit(str(help_messages[message.arguments]))
        else:
            await message.edit(lang('arg_error'))
    else:
        result = f"**{lang('help_list')}: \n**"
        for command in sorted(help_messages, reverse=False):
            if str(command) in support_commands:
                continue
            result += "`" + str(command)
            result += "`, "
        if result == f"**{lang('help_list')}: \n**":
            """ The help raw command,"""
            for command in sorted(help_messages, reverse=False):
                result += "`" + str(command)
                result += "`, "
        await message.edit(result[
                           :-2] + f"\n**{lang('help_send')} \",help <{lang('command')}>\" {lang('help_see')}**\n"
                                  f"[{lang('help_source')}](https://t.me/PagerMaid_Modify) "
                                  f"[{lang('help_plugin')}](https://index.xtaolabs.com/) "
                                  f"[{lang('help_module')}](https://wiki.xtaolabs.com/)",
                           disable_web_page_preview=True)


@listener(is_plugin=False, command=alias_command("help_raw"),
          description=lang('help_des'),
          parameters=f"<{lang('command')}>")
async def help_raw_command(client: Client, message: Message):
    """ The help raw command,"""
    if message.arguments:
        if message.arguments in help_messages:
            await message.edit(str(help_messages[message.arguments]))
        else:
            await message.edit(lang('arg_error'))
    else:
        result = f"**{lang('help_list')}: \n**"
        for command in sorted(help_messages, reverse=False):
            result += "`" + str(command)
            result += "`, "
        await message.edit(result[:-2] + f"\n**{lang('help_send')} \",help <{lang('command')}>\" {lang('help_see')}** "
                                         f"[{lang('help_source')}](https://t.me/PagerMaid_Modify)",
                           disable_web_page_preview=True)


@listener(is_plugin=False, command=alias_command("lang"),
          description=lang('lang_des'))
async def lang_change(client: Client, message: Message):
    to_lang = message.arguments
    from_lang = Config.LANGUAGE
    dir_, dir__ = listdir('languages/built-in'), []
    for i in dir_:
        if not i.find('yml') == -1:
            dir__.append(i[:-4])
    with open('config.yml') as f:
        file = f.read()
    if to_lang in dir__:
        file = file.replace(f'application_language: "{from_lang}"', f'application_language: "{to_lang}"')
        with open('config.yml', 'w') as f:
            f.write(file)
        await message.edit(f"{lang('lang_change_to')} {to_lang}, {lang('lang_reboot')}")
        exit(1)
    else:
        await message.edit(f'{lang("lang_current_lang")} {Config.LANGUAGE}\n\n'
                           f'{lang("lang_all_lang")}{"，".join(dir__)}')


@listener(is_plugin=False, outgoing=True, command="alias",
          description=lang('alias_des'),
          parameters='{list|del|set} <source> <to>')
async def alias_commands(client: Client, message: Message):
    source_commands = []
    to_commands = []
    texts = []
    for key, value in Config.alias_dict.items():
        source_commands.append(key)
        to_commands.append(value)
    if len(message.parameter) == 0:
        await message.edit(lang('arg_error'))
        return
    elif len(message.parameter) == 1:
        if not len(source_commands) == 0:
            for i in range(0, len(source_commands)):
                texts.append(f'`{source_commands[i]}` --> `{to_commands[i]}`')
            await message.edit(lang('alias_list') + '\n\n' + '\n'.join(texts))
        else:
            await message.edit(lang('alias_no'))
    elif len(message.parameter) == 2:
        source_command = message.parameter[1]
        try:
            del Config.alias_dict[source_command]
            with open(f"data{sep}alias.json", 'w') as f:
                json_dump(Config.alias_dict, f)
            await message.edit(lang('alias_success'))
            exit(1)
        except KeyError:
            await message.edit(lang('alias_no_exist'))
            return
    elif len(message.parameter) == 3:
        source_command = message.parameter[1]
        to_command = message.parameter[2]
        if to_command in help_messages:
            await message.edit(lang('alias_exist'))
            return
        Config.alias_dict[source_command] = to_command
        with open(f"data{sep}alias.json", 'w') as f:
            json_dump(Config.alias_dict, f)
        await message.edit(lang('alias_success'))
        exit(1)
