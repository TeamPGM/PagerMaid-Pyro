""" PagerMaid module to manage plugins. """
import json
from re import search, I
from os import remove, rename, chdir, path, sep
from os.path import exists
from shutil import copyfile, move
from glob import glob

from pyrogram import Client

from pagermaid import log, working_dir, Config
from pagermaid.listener import listener
from pagermaid.utils import upload_attachment, lang, alias_command, Message, client
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


async def download(name):
    html = await client.get(f'{Config.GIT_SOURCE}{name}.py')
    with open(f'plugins{sep}{name}.py', mode='wb') as f:
        f.write(html.text.encode('utf-8'))
    return f'plugins{sep}{name}.py'


def update_version(plugin_name, version):
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
        version_json = json.load(f)
        version_json[plugin_name] = version
    with open(f"{plugin_directory}version.json", 'w') as f:
        json.dump(version_json, f)


@listener(is_plugin=False, outgoing=True, command=alias_command('apt'),
          diagnostics=False,
          description=lang('apt_des'),
          parameters=lang('apt_parameters'))
async def plugin(__: Client, context: Message):
    if len(context.parameter) == 0:
        await context.edit(lang('arg_error'))
        return
    reply = context.reply_to_message
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    if context.parameter[0] == "install":
        if len(context.parameter) == 1:
            await context.edit(lang('apt_processing'))
            if reply:
                file_path = await reply.download()
            else:
                file_path = await context.download()
            if file_path is None or not file_path.endswith('.py'):
                await context.edit(lang('apt_no_py'))
                try:
                    remove(str(file_path))
                except FileNotFoundError:
                    pass
                return
            move_plugin(file_path)
            await context.edit(f"<b>{lang('apt_name')}</b>\n\n"
                               f"{lang('apt_plugin')} "
                               f"{path.basename(file_path)[:-3]} {lang('apt_installed')},"
                               f"{lang('apt_reboot')}")
            await log(f"{lang('apt_install_success')} {path.basename(file_path)[:-3]}.")
            exit(1)
        elif len(context.parameter) >= 2:
            await context.edit(lang('apt_processing'))
            process_list = context.parameter
            del process_list[0]
            success_list = []
            failed_list = []
            noneed_list = []
            plugin_list = await client.get(f"{Config.GIT_SOURCE}list.json")
            plugin_list = plugin_list.json()["list"]
            for i in process_list:
                if exists(f"{plugin_directory}version.json"):
                    with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                        version_json = json.load(f)
                    try:
                        plugin_version = version_json[i]
                    except:
                        plugin_version = 0
                else:
                    temp_dict = {}
                    with open(f"{plugin_directory}version.json", 'w') as f:
                        json.dump(temp_dict, f)
                    plugin_version = 0
                temp = True
                for x in plugin_list:
                    if x["name"] == i:
                        if (float(x["version"]) - float(plugin_version)) <= 0:
                            noneed_list.append(i)
                            temp = False
                            break
                        else:
                            remove_plugin(i)
                            await download(i)
                            update_version(i, x["version"])
                            success_list.append(i)
                            temp = False
                            break
                if temp:
                    failed_list.append(i)
            message = f"<b>{lang('apt_name')}</b>\n\n"
            if len(success_list) > 0:
                message += lang('apt_install_success') + " : %s\n" % ", ".join(success_list)
            if len(failed_list) > 0:
                message += lang('apt_not_found') + " %s\n" % ", ".join(failed_list)
            if len(noneed_list) > 0:
                message += lang('apt_no_update') + " %s\n" % ", ".join(noneed_list)
            await log(message)
            restart = len(success_list) > 0
            if restart:
                message += lang('apt_reboot')
            await context.edit(message)
            if restart:
                exit(1)
        else:
            await context.edit(lang('arg_error'))
    elif context.parameter[0] == "remove":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py"):
                remove(f"{plugin_directory}{context.parameter[1]}.py")
                result = await context.edit(
                                             f"{lang('apt_remove_success')} {context.parameter[1]}, {lang('apt_reboot')} ")
                await log(f"{lang('apt_remove')} {context.parameter[1]}.")
                exit(1)
            elif exists(f"{plugin_directory}{context.parameter[1]}.py.disabled"):
                remove(f"{plugin_directory}{context.parameter[1]}.py.disabled")
                await context.edit(f"{lang('apt_removed_plugins')} {context.parameter[1]}.")
                await log(f"{lang('apt_removed_plugins')} {context.parameter[1]}.")
            elif "/" in context.parameter[1]:
                await context.edit(lang('arg_error'))
            else:
                await context.edit(lang('apt_not_exist'))
        else:
            await context.edit(lang('arg_error'))
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
            await context.edit(output)
        else:
            await context.edit(lang('arg_error'))
    elif context.parameter[0] == "enable":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py.disabled"):
                rename(f"{plugin_directory}{context.parameter[1]}.py.disabled",
                       f"{plugin_directory}{context.parameter[1]}.py")
                result = await context.edit(
                                             f"{lang('apt_plugin')} {context.parameter[1]} {lang('apt_enable')},{lang('apt_reboot')}")
                await log(f"{lang('apt_enable')} {context.parameter[1]}.")
                exit(1)
            else:
                await context.edit(lang('apt_not_exist'))
        else:
            await context.edit(lang('arg_error'))
    elif context.parameter[0] == "disable":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py") is True:
                rename(f"{plugin_directory}{context.parameter[1]}.py",
                       f"{plugin_directory}{context.parameter[1]}.py.disabled")
                result = await context.edit(
                                             f"{lang('apt_plugin')} {context.parameter[1]} {lang('apt_disable')},{lang('apt_reboot')}")
                await log(f"{lang('apt_disable')} {context.parameter[1]}.")
                exit(1)
            else:
                await context.edit(lang('apt_not_exist'))
        else:
            await context.edit(lang('arg_error'))
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
                await context.edit(lang('apt_uploading'))
                await upload_attachment(file_name,
                                        context.chat.id, reply_id,
                                        thumb=f"pagermaid{sep}assets{sep}logo.jpg",
                                        caption=f"<b>{lang('apt_name')}</b>\n\n"
                                                f"PagerMaid-Pyro {context.parameter[1]} plugin.")
                remove(file_name)
                await context.safe_delete()
            else:
                await context.edit(lang('apt_not_exist'))
        else:
            await context.edit(lang('arg_error'))
    elif context.parameter[0] == "update":
        unneed_update = lang('apt_no_update')
        need_update = f"\n{lang('apt_updated')}:"
        need_update_list = []
        if not exists(f"{plugin_directory}version.json"):
            await context.edit(lang('apt_why_not_install_a_plugin'))
            return
        with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
            version_json = json.load(f)
        plugin_list = await client.get(f"{Config.GIT_SOURCE}list.json")
        plugin_online = plugin_list.json()["list"]
        for key, value in version_json.items():
            if value == "0.0":
                continue
            for i in plugin_online:
                if key == i["name"]:
                    if (float(i["version"]) - float(value)) <= 0:
                        unneed_update += "\n`" + key + "`:Ver  " + value
                    else:
                        need_update_list.extend([key])
                        need_update += "\n`" + key + "`:Ver  " + value + " --> Ver  " + i['version']
                    continue
        if unneed_update == f"{lang('apt_no_update')}:":
            unneed_update = ""
        if need_update == f"\n{lang('apt_updated')}:":
            need_update = ""
        if not unneed_update and not need_update:
            await context.edit(lang("apt_why_not_install_a_plugin"))
        else:
            if len(need_update_list) == 0:
                await context.edit(f"<b>{lang('apt_name')}</b>\n\n" +
                                   lang("apt_loading_from_online_but_nothing_need_to_update"))
            else:
                print(6)
                await context.edit(lang("apt_loading_from_online_and_updating"))
                plugin_directory = f"{working_dir}{sep}plugins{sep}"
                for i in need_update_list:
                    remove_plugin(i)
                    await download(i)
                    with open(f"{plugin_directory}version.json", "r", encoding="utf-8") as f:
                        version_json = json.load(f)
                    for m in plugin_online:
                        if m["name"] == i:
                            version_json[i] = m["version"]
                    with open(f"{plugin_directory}version.json", "w") as f:
                        json.dump(version_json, f)
                await context.edit(f"<b>{lang('apt_name')}</b>\n\n" + lang("apt_reading_list") + need_update)
                exit(1)
    elif context.parameter[0] == "search":
        if len(context.parameter) == 1:
            await context.edit(lang("apt_search_no_name"))
        elif len(context.parameter) == 2:
            search_result = []
            plugin_name = context.parameter[1]
            plugin_list = await client.get(f"{Config.GIT_SOURCE}list.json")
            plugin_online = plugin_list.json()["list"]
            for i in plugin_online:
                if search(plugin_name, i["name"], I):
                    search_result.extend(['`' + i['name'] + '` / `' + i['version'] + '`\n  ' + i['des-short']])
            if len(search_result) == 0:
                await context.edit(lang("apt_search_not_found"))
            else:
                await context.edit(f"{lang('apt_search_result_hint')}:\n\n" + '\n\n'.join(search_result))
        else:
            await context.edit(lang('arg_error'))
    elif context.parameter[0] == "show":
        if len(context.parameter) == 1:
            await context.edit(lang("apt_search_no_name"))
        elif len(context.parameter) == 2:
            search_result = ""
            plugin_name = context.parameter[1]
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
                await context.edit(lang("apt_search_not_found"))
            else:
                await context.edit(search_result)
    elif context.parameter[0] == "export":
        if not exists(f"{plugin_directory}version.json"):
            await context.edit(lang("apt_why_not_install_a_plugin"))
            return
        await context.edit(lang("stats_loading"))
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
            await context.edit(lang("apt_why_not_install_a_plugin"))
        else:
            await context.edit(",apt install " + " ".join(list_plugin))
    else:
        await context.edit(lang("arg_error"))
