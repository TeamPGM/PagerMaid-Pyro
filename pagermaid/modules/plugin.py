""" PagerMaid module to manage plugins. """

import json
from re import search, I
from os import remove, rename, chdir, path, sep
from os.path import exists
from shutil import copyfile, move
from glob import glob

from pyrogram import Client

from pagermaid import log, working_dir
from pagermaid.listener import listener
from pagermaid.utils import upload_attachment, lang, alias_command, client, Message, edit_or_reply
from pagermaid.modules import plugin_list as active_plugins, __list_plugins


def remove_plugin(name):
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    try:
        remove(f"{plugin_directory}{name}.py")
    except FileNotFoundError:
        pass
    try:
        remove(f"{plugin_directory}{name}.py.disabled")
    except FileNotFoundError:
        pass


def move_plugin(file_path):
    name = path.basename(file_path)[:-3]
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    remove_plugin(name)
    move(file_path, plugin_directory)


@listener(is_plugin=False, outgoing=True, command=alias_command('apt'), diagnostics=False,
          description=lang('apt_des'),
          parameters=lang('apt_parameters'))
async def plugin(__: Client, context: Message):
    if len(context.parameter) == 0:
        await edit_or_reply(context, lang('arg_error'))
        return
    reply = context.reply_to_message
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    if context.parameter[0] == "install":
        if len(context.parameter) == 1:
            await edit_or_reply(context, lang('apt_processing'))
            if reply:
                file_path = await reply.download()
            else:
                file_path = await context.download()
            if file_path is None or not file_path.endswith('.py'):
                await edit_or_reply(context, lang('apt_no_py'))
                try:
                    remove(str(file_path))
                except FileNotFoundError:
                    pass
                return
            move_plugin(file_path)
            result = await edit_or_reply(context,
                                         f"{lang('apt_plugin')} "
                                         f"{path.basename(file_path)[:-3]} {lang('apt_installed')},"
                                         f"{lang('apt_reboot')}")
            await log(f"{lang('apt_install_success')} {path.basename(file_path)[:-3]}.")
            exit(1)
        else:
            await edit_or_reply(context, lang('arg_error'))
    elif context.parameter[0] == "remove":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py"):
                remove(f"{plugin_directory}{context.parameter[1]}.py")
                result = await edit_or_reply(context,
                                             f"{lang('apt_remove_success')} {context.parameter[1]}, {lang('apt_reboot')} ")
                await log(f"{lang('apt_remove')} {context.parameter[1]}.")
                exit(1)
            elif exists(f"{plugin_directory}{context.parameter[1]}.py.disabled"):
                remove(f"{plugin_directory}{context.parameter[1]}.py.disabled")
                await edit_or_reply(context, f"{lang('apt_removed_plugins')} {context.parameter[1]}.")
                await log(f"{lang('apt_removed_plugins')} {context.parameter[1]}.")
            elif "/" in context.parameter[1]:
                await edit_or_reply(context, lang('arg_error'))
            else:
                await edit_or_reply(context, lang('apt_not_exist'))
        else:
            await edit_or_reply(context, lang('arg_error'))
    elif context.parameter[0] == "status":
        if len(context.parameter) == 1:
            inactive_plugins = sorted(__list_plugins())
            disabled_plugins = []
            if not len(inactive_plugins) == 0:
                for target_plugin in active_plugins:
                    inactive_plugins.remove(target_plugin)
            chdir(f"plugins{sep}")
            for target_plugin in glob(f"*.py.disabled"):
                disabled_plugins += [f"{target_plugin[:-12]}"]
            chdir(f"..{sep}")
            active_plugins_string = ""
            inactive_plugins_string = ""
            disabled_plugins_string = ""
            for target_plugin in active_plugins:
                active_plugins_string += f"{target_plugin}, "
            active_plugins_string = active_plugins_string[:-2]
            for target_plugin in inactive_plugins:
                inactive_plugins_string += f"{target_plugin}, "
            inactive_plugins_string = inactive_plugins_string[:-2]
            for target_plugin in disabled_plugins:
                disabled_plugins_string += f"{target_plugin}, "
            disabled_plugins_string = disabled_plugins_string[:-2]
            if len(active_plugins) == 0:
                active_plugins_string = f"`{lang('apt_no_running_plugins')}`"
            if len(inactive_plugins) == 0:
                inactive_plugins_string = f"`{lang('apt_no_load_falied_plugins')}`"
            if len(disabled_plugins) == 0:
                disabled_plugins_string = f"`{lang('apt_no_disabled_plugins')}`"
            output = f"**{lang('apt_plugin_list')}**\n" \
                     f"{lang('apt_plugin_running')}: {active_plugins_string}\n" \
                     f"{lang('apt_plugin_disabled')}: {disabled_plugins_string}\n" \
                     f"{lang('apt_plugin_failed')}: {inactive_plugins_string}"
            await edit_or_reply(context, output)
        else:
            await edit_or_reply(context, lang('arg_error'))
    elif context.parameter[0] == "enable":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py.disabled"):
                rename(f"{plugin_directory}{context.parameter[1]}.py.disabled",
                       f"{plugin_directory}{context.parameter[1]}.py")
                result = await edit_or_reply(context,
                                             f"{lang('apt_plugin')} {context.parameter[1]} {lang('apt_enable')},{lang('apt_reboot')}")
                await log(f"{lang('apt_enable')} {context.parameter[1]}.")
                exit(1)
            else:
                await edit_or_reply(context, lang('apt_not_exist'))
        else:
            await edit_or_reply(context, lang('arg_error'))
    elif context.parameter[0] == "disable":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py") is True:
                rename(f"{plugin_directory}{context.parameter[1]}.py",
                       f"{plugin_directory}{context.parameter[1]}.py.disabled")
                result = await edit_or_reply(context,
                                             f"{lang('apt_plugin')} {context.parameter[1]} {lang('apt_disable')},{lang('apt_reboot')}")
                await log(f"{lang('apt_disable')} {context.parameter[1]}.")
                exit(1)
            else:
                await edit_or_reply(context, lang('apt_not_exist'))
        else:
            await edit_or_reply(context, lang('arg_error'))
    elif context.parameter[0] == "upload":
        if len(context.parameter) == 2:
            file_name = f"{context.parameter[1]}.py"
            reply_id = None
            if reply:
                reply_id = reply.message_id
            if exists(f"{plugin_directory}{file_name}"):
                copyfile(f"{plugin_directory}{file_name}", file_name)
            elif exists(f"{plugin_directory}{file_name}.disabled"):
                copyfile(f"{plugin_directory}{file_name}.disabled", file_name)
            if exists(file_name):
                context = await edit_or_reply(context, lang('apt_uploading'))
                await upload_attachment(file_name,
                                        context.chat.id, reply_id,
                                        caption=f"PagerMaid-Pyro {context.parameter[1]} plugin.")
                remove(file_name)
                await context.delete()
            else:
                await edit_or_reply(context, lang('apt_not_exist'))
        else:
            await edit_or_reply(context, lang('arg_error'))
    else:
        await edit_or_reply(context, lang('arg_error'))
