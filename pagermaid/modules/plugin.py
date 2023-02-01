""" PagerMaid module to manage plugins. """

import contextlib
import json
from glob import glob
from os import remove, chdir, path, sep
from os.path import exists
from re import search, I
from shutil import copyfile, move

from pagermaid import log, working_dir, Config
from pagermaid.common.plugin import plugin_manager
from pagermaid.common.reload import reload_all
from pagermaid.listener import listener
from pagermaid.modules import plugin_list as active_plugins, __list_plugins
from pagermaid.utils import upload_attachment, lang, Message, client


def remove_plugin(name):
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    with contextlib.suppress(FileNotFoundError):
        remove(f"{plugin_directory}{name}.py")
    with contextlib.suppress(FileNotFoundError):
        remove(f"{plugin_directory}{name}.py.disabled")


def move_plugin(file_path):
    name = path.basename(file_path)[:-3]
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    remove_plugin(name)
    move(file_path, plugin_directory)


def update_version(plugin_name, version):
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
        version_json = json.load(f)
        version_json[plugin_name] = version
    with open(f"{plugin_directory}version.json", 'w') as f:
        json.dump(version_json, f)


@listener(is_plugin=False, outgoing=True, command="apt",
          need_admin=True,
          diagnostics=False,
          description=lang('apt_des'),
          parameters=lang('apt_parameters'))
async def plugin(message: Message):
    if len(message.parameter) == 0:
        await message.edit(lang('arg_error'))
        return
    reply = message.reply_to_message
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    if message.parameter[0] == "install":
        if len(message.parameter) == 1:
            message = await message.edit(lang('apt_processing'))
            file_path = None
            with contextlib.suppress(Exception):
                if reply:
                    file_path = await reply.download()
                else:
                    file_path = await message.download()
            if file_path is None or not file_path.endswith('.py'):
                await message.edit(lang('apt_no_py'))
                try:
                    remove(str(file_path))
                except FileNotFoundError:
                    pass
                return
            move_plugin(file_path)
            await message.edit(f"<b>{lang('apt_name')}</b>\n\n"
                               f"{lang('apt_plugin')} "
                               f"{path.basename(file_path)[:-3]} {lang('apt_installed')}")
            await log(f"{lang('apt_install_success')} {path.basename(file_path)[:-3]}.")
            await reload_all()
        elif len(message.parameter) >= 2:
            await plugin_manager.load_remote_plugins()
            process_list = message.parameter
            message = await message.edit(lang('apt_processing'))
            del process_list[0]
            success_list = []
            failed_list = []
            no_need_list = []
            for i in process_list:
                if plugin_manager.get_remote_plugin(i):
                    local_temp = plugin_manager.get_local_plugin(i)
                    if local_temp and not plugin_manager.plugin_need_update(i):
                        no_need_list.append(i)
                    else:
                        try:
                            if await plugin_manager.install_remote_plugin(i):
                                success_list.append(i)
                            else:
                                failed_list.append(i)
                        except Exception:
                            failed_list.append(i)
                else:
                    failed_list.append(i)
            text = f"<b>{lang('apt_name')}</b>\n\n"
            if len(success_list) > 0:
                text += lang('apt_install_success') + " : %s\n" % ", ".join(success_list)
            if len(failed_list) > 0:
                text += lang('apt_not_found') + " %s\n" % ", ".join(failed_list)
            if len(no_need_list) > 0:
                text += lang('apt_no_update') + " %s\n" % ", ".join(no_need_list)
            await log(text)
            restart = len(success_list) > 0
            await message.edit(text)
            if restart:
                await reload_all()
        else:
            await message.edit(lang('arg_error'))
    elif message.parameter[0] == "remove":
        if len(message.parameter) == 2:
            if plugin_manager.remove_plugin(message.parameter[1]):
                await message.edit(f"{lang('apt_remove_success')} {message.parameter[1]}")
                await log(f"{lang('apt_remove')} {message.parameter[1]}.")
                await reload_all()
            elif "/" in message.parameter[1]:
                await message.edit(lang('arg_error'))
            else:
                await message.edit(lang('apt_not_exist'))
        else:
            await message.edit(lang('arg_error'))
    elif message.parameter[0] == "status":
        if len(message.parameter) == 1:
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
                inactive_plugins_string = f"`{lang('apt_no_load_failed_plugins')}`"
            if len(disabled_plugins) == 0:
                disabled_plugins_string = f"`{lang('apt_no_disabled_plugins')}`"
            output = f"**{lang('apt_plugin_list')}**\n" \
                     f"{lang('apt_plugin_running')}: {active_plugins_string}\n" \
                     f"{lang('apt_plugin_disabled')}: {disabled_plugins_string}\n" \
                     f"{lang('apt_plugin_failed')}: {inactive_plugins_string}"
            await message.edit(output)
        else:
            await message.edit(lang('arg_error'))
    elif message.parameter[0] == "enable":
        if len(message.parameter) == 2:
            if plugin_manager.enable_plugin(message.parameter[1]):
                await message.edit(f"{lang('apt_plugin')} {message.parameter[1]} "
                                   f"{lang('apt_enable')}")
                await log(f"{lang('apt_enable')} {message.parameter[1]}.")
                await reload_all()
            else:
                await message.edit(lang('apt_not_exist'))
        else:
            await message.edit(lang('arg_error'))
    elif message.parameter[0] == "disable":
        if len(message.parameter) == 2:
            if plugin_manager.disable_plugin(message.parameter[1]):
                await message.edit(f"{lang('apt_plugin')} {message.parameter[1]} "
                                   f"{lang('apt_disable')}")
                await log(f"{lang('apt_disable')} {message.parameter[1]}.")
                await reload_all()
            else:
                await message.edit(lang('apt_not_exist'))
        else:
            await message.edit(lang('arg_error'))
    elif message.parameter[0] == "upload":
        if len(message.parameter) == 2:
            file_name = f"{message.parameter[1]}.py"
            reply_id = None
            if reply:
                reply_id = reply.id
            if exists(f"{plugin_directory}{file_name}"):
                copyfile(f"{plugin_directory}{file_name}", file_name)
            elif exists(f"{plugin_directory}{file_name}.disabled"):
                copyfile(f"{plugin_directory}{file_name}.disabled", file_name)
            if exists(file_name):
                await message.edit(lang('apt_uploading'))
                await upload_attachment(file_name,
                                        message.chat.id, reply_id,
                                        thumb=f"pagermaid{sep}assets{sep}logo.jpg",
                                        caption=f"<b>{lang('apt_name')}</b>\n\n"
                                                f"PagerMaid-Pyro {message.parameter[1]} plugin.")
                remove(file_name)
                await message.safe_delete()
            else:
                await message.edit(lang('apt_not_exist'))
        else:
            await message.edit(lang('arg_error'))
    elif message.parameter[0] == "update":
        if not exists(f"{plugin_directory}version.json"):
            await message.edit(lang('apt_why_not_install_a_plugin'))
            return
        await plugin_manager.load_remote_plugins()
        updated_plugins = [i.name for i in await plugin_manager.update_all_remote_plugin() if i]
        if len(updated_plugins) == 0:
            await message.edit(f"<b>{lang('apt_name')}</b>\n\n" +
                               lang("apt_loading_from_online_but_nothing_need_to_update"))
        else:
            message = await message.edit(lang("apt_loading_from_online_and_updating"))
            await message.edit(
                f"<b>{lang('apt_name')}</b>\n\n" + lang("apt_reading_list") + "\n\n" + "、".join(updated_plugins)
            )
            await reload_all()
    elif message.parameter[0] == "search":
        if len(message.parameter) == 1:
            await message.edit(lang("apt_search_no_name"))
        elif len(message.parameter) == 2:
            search_result = []
            plugin_name = message.parameter[1]
            plugin_list = await client.get(f"{Config.GIT_SOURCE}list.json")
            plugin_online = plugin_list.json()["list"]
            for i in plugin_online:
                if search(plugin_name, i["name"], I):
                    search_result.extend(['`' + i['name'] + '` / `' + i['version'] + '`\n  ' + i['des-short']])
            if len(search_result) == 0:
                await message.edit(lang("apt_search_not_found"))
            else:
                await message.edit(f"{lang('apt_search_result_hint')}:\n\n" + '\n\n'.join(search_result))
        else:
            await message.edit(lang('arg_error'))
    elif message.parameter[0] == "show":
        if len(message.parameter) == 1:
            await message.edit(lang("apt_search_no_name"))
        elif len(message.parameter) == 2:
            search_result = ""
            plugin_name = message.parameter[1]
            plugin_list = await client.get(f"{Config.GIT_SOURCE}list.json")
            plugin_online = plugin_list.json()["list"]
            for i in plugin_online:
                if plugin_name == i["name"]:
                    if i["supported"]:
                        search_support = lang("apt_search_supporting")
                    else:
                        search_support = lang("apt_search_not_supporting")
                    search_result = f"{lang('apt_plugin_name')}:`{i['name']}`\n" \
                                    f"{lang('apt_plugin_ver')}:`Ver  {i['version']}`\n" \
                                    f"{lang('apt_plugin_section')}:`{i['section']}`\n" \
                                    f"{lang('apt_plugin_maintainer')}:`{i['maintainer']}`\n" \
                                    f"{lang('apt_plugin_size')}:`{i['size']}`\n" \
                                    f"{lang('apt_plugin_support')}:{search_support}\n" \
                                    f"{lang('apt_plugin_des_short')}:{i['des-short']}\n\n" \
                                    f"{i['des']}"
                    break
            if search_result == '':
                await message.edit(lang("apt_search_not_found"))
            else:
                await message.edit(search_result)
    elif message.parameter[0] == "export":
        if not exists(f"{plugin_directory}version.json"):
            await message.edit(lang("apt_why_not_install_a_plugin"))
            return
        message = await message.edit(lang("stats_loading"))
        list_plugin = []
        with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
            version_json = json.load(f)
        plugin_list = await client.get(f"{Config.GIT_SOURCE}list.json")
        plugin_online = plugin_list.json()["list"]
        for key, value in version_json.items():
            if value == "0.0":
                continue
            for i in plugin_online:
                if key == i["name"]:
                    list_plugin.append(key)
                    break
        if len(list_plugin) == 0:
            await message.edit(lang("apt_why_not_install_a_plugin"))
        else:
            await message.edit(",apt install " + " ".join(list_plugin))
    else:
        await message.edit(lang("arg_error"))
