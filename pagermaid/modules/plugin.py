"""PagerMaid module to manage plugins."""

import contextlib
from os import remove, path, sep
from os.path import exists
from re import search, I
from shutil import copyfile, move

from pyrogram.types import LinkPreviewOptions

from pagermaid.common.plugin import plugin_remote_manager, plugin_manager
from pagermaid.common.reload import reload_all
from pagermaid.enums import Message
from pagermaid.listener import listener
from pagermaid.static import working_dir
from pagermaid.utils import lang
from pagermaid.utils.bot_utils import log, upload_attachment


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


@listener(
    is_plugin=False,
    outgoing=True,
    command="apt",
    need_admin=True,
    diagnostics=False,
    description=lang("apt_des"),
    parameters=lang("apt_parameters"),
)
async def plugin(message: Message):
    if len(message.parameter) == 0:
        await message.edit(lang("arg_error"))
        return
    reply = message.reply_to_message
    plugin_directory = f"{working_dir}{sep}plugins{sep}"
    if message.parameter[0] == "install":
        if len(message.parameter) == 1:
            file_path = await plugin_manager.download_from_message(message)
            if file_path is None:
                await message.edit(lang("apt_no_py"))
                return
            plugin_name = path.basename(file_path)[:-3]
            plugin_manager.remove_plugin(plugin_name)
            move_plugin(file_path)
            await message.edit(
                f"<b>{lang('apt_name')}</b>\n\n"
                f"{lang('apt_plugin')} "
                f"{plugin_name} {lang('apt_installed')}"
            )
            await log(f"{lang('apt_install_success')} {plugin_name}.")
            await reload_all()
        elif len(message.parameter) >= 2:
            await plugin_manager.load_remote_plugins()
            process_list = message.parameter
            message = await message.edit(lang("apt_processing"))
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
                text += lang("apt_install_success") + " : %s\n" % ", ".join(
                    success_list
                )
            if len(failed_list) > 0:
                text += lang("apt_not_found") + " %s\n" % ", ".join(failed_list)
            if len(no_need_list) > 0:
                text += lang("apt_no_update") + " %s\n" % ", ".join(no_need_list)
            await log(text)
            restart = len(success_list) > 0
            await message.edit(text)
            if restart:
                await reload_all()
        else:
            await message.edit(lang("arg_error"))
    elif message.parameter[0] == "remove":
        if len(message.parameter) == 2:
            if plugin_manager.remove_plugin(message.parameter[1]):
                await message.edit(
                    f"{lang('apt_remove_success')} {message.parameter[1]}"
                )
                await log(f"{lang('apt_remove')} {message.parameter[1]}.")
                await reload_all()
            elif "/" in message.parameter[1]:
                await message.edit(lang("arg_error"))
            else:
                await message.edit(lang("apt_not_exist"))
        else:
            await message.edit(lang("arg_error"))
    elif message.parameter[0] == "status":
        if len(message.parameter) == 1:
            (
                active_plugins,
                disabled_plugins,
                inactive_plugins,
            ) = plugin_manager.get_plugins_status()
            active_plugins_string = ", ".join(active_plugins)
            inactive_plugins_string = ", ".join([i.name for i in inactive_plugins])
            disabled_plugins_string = ", ".join([i.name for i in disabled_plugins])
            if len(active_plugins) == 0:
                active_plugins_string = f"`{lang('apt_no_running_plugins')}`"
            if len(inactive_plugins) == 0:
                inactive_plugins_string = f"`{lang('apt_no_load_failed_plugins')}`"
            if len(disabled_plugins) == 0:
                disabled_plugins_string = f"`{lang('apt_no_disabled_plugins')}`"
            output = (
                f"**{lang('apt_plugin_list')}**\n"
                f"{lang('apt_plugin_running')}: {active_plugins_string}\n"
                f"{lang('apt_plugin_disabled')}: {disabled_plugins_string}\n"
                f"{lang('apt_plugin_failed')}: {inactive_plugins_string}"
            )
            await message.edit(output)
        else:
            await message.edit(lang("arg_error"))
    elif message.parameter[0] == "enable":
        if len(message.parameter) == 2:
            if plugin_manager.enable_plugin(message.parameter[1]):
                await message.edit(
                    f"{lang('apt_plugin')} {message.parameter[1]} {lang('apt_enable')}"
                )
                await log(f"{lang('apt_enable')} {message.parameter[1]}.")
                await reload_all()
            else:
                await message.edit(lang("apt_not_exist"))
        else:
            await message.edit(lang("arg_error"))
    elif message.parameter[0] == "disable":
        if len(message.parameter) == 2:
            if plugin_manager.disable_plugin(message.parameter[1]):
                await message.edit(
                    f"{lang('apt_plugin')} {message.parameter[1]} {lang('apt_disable')}"
                )
                await log(f"{lang('apt_disable')} {message.parameter[1]}.")
                await reload_all()
            else:
                await message.edit(lang("apt_not_exist"))
        else:
            await message.edit(lang("arg_error"))
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
                try:
                    await message.edit(lang("apt_uploading"))
                    await upload_attachment(
                        file_name,
                        message.chat.id,
                        reply_id,
                        message_thread_id=message.message_thread_id,
                        thumb=f"pagermaid{sep}assets{sep}logo.jpg",
                        caption=f"<b>{lang('apt_name')}</b>\n\n"
                        f"PagerMaid-Pyro {message.parameter[1]} plugin.",
                    )
                    await message.safe_delete()
                finally:
                    remove(file_name)
            else:
                await message.edit(lang("apt_not_exist"))
        else:
            await message.edit(lang("arg_error"))
    elif message.parameter[0] == "update":
        if not exists(f"{plugin_directory}version.json"):
            await message.edit(lang("apt_why_not_install_a_plugin"))
            return
        await plugin_manager.load_remote_plugins()
        updated_plugins = [
            i.name for i in await plugin_manager.update_all_remote_plugin() if i
        ]
        if len(updated_plugins) == 0:
            await message.edit(
                f"<b>{lang('apt_name')}</b>\n\n"
                + lang("apt_loading_from_online_but_nothing_need_to_update")
            )
        else:
            message = await message.edit(lang("apt_loading_from_online_and_updating"))
            await message.edit(
                f"<b>{lang('apt_name')}</b>\n\n"
                + lang("apt_reading_list")
                + "\n"
                + "、".join(updated_plugins)
            )
            await reload_all()
    elif message.parameter[0] == "search":
        if len(message.parameter) == 1:
            await message.edit(lang("apt_search_no_name"))
        elif len(message.parameter) == 2:
            await plugin_manager.load_remote_plugins()
            search_result = []
            plugin_name = message.parameter[1]
            for i in plugin_manager.remote_plugins:
                if search(plugin_name, i.name, I):
                    search_result.append(f"`{i.name}` / `{i.version}`\n  {i.des_short}")
            if len(search_result) == 0:
                await message.edit(lang("apt_search_not_found"))
            else:
                await message.edit(
                    f"{lang('apt_search_result_hint')}:\n\n"
                    + "\n\n".join(search_result)
                )
        else:
            await message.edit(lang("arg_error"))
    elif message.parameter[0] == "show":
        if len(message.parameter) == 1:
            await message.edit(lang("apt_search_no_name"))
        elif len(message.parameter) == 2:
            await plugin_manager.load_remote_plugins()
            search_result = ""
            plugin_name = message.parameter[1]
            for i in plugin_manager.remote_plugins:
                if plugin_name == i.name:
                    if i.supported:
                        search_support = lang("apt_search_supporting")
                    else:
                        search_support = lang("apt_search_not_supporting")
                    search_result = (
                        f"{lang('apt_plugin_name')}:`{i.name}`\n"
                        f"{lang('apt_plugin_ver')}:`Ver  {i.version}`\n"
                        f"{lang('apt_plugin_section')}:`{i.section}`\n"
                        f"{lang('apt_plugin_maintainer')}:`{i.maintainer}`\n"
                        f"{lang('apt_plugin_size')}:`{i.size}`\n"
                        f"{lang('apt_plugin_support')}:{search_support}\n"
                        f"{lang('apt_plugin_des_short')}:{i.des_short}"
                    )
                    break
            if search_result == "":
                await message.edit(lang("apt_search_not_found"))
            else:
                await message.edit(search_result)
    elif message.parameter[0] == "list":
        await plugin_manager.load_remote_plugins()
        plugins = sorted(plugin_manager.remote_plugins, key=lambda x: x.name)

        if not plugins:
            await message.edit(lang("apt_search_not_found"))
            return

        active, disabled, inactive = plugin_manager.get_plugins_status()
        active_set = set(active)
        inactive_set = set(p.name for p in disabled)
        disabled_set = set(p.name for p in inactive)

        page = 1
        if len(message.parameter) > 1:
            try:
                page = int(message.parameter[1])
            except ValueError:
                await message.edit(lang("arg_error"))
                return

        page_size = 15
        total_pages = (len(plugins) + page_size - 1) // page_size

        if not 1 <= page <= total_pages:
            page = 1

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        plugins_to_show = plugins[start_index:end_index]

        text = f"**{lang('apt_plugin_list')} ({page}/{total_pages})**\n\n<blockquote expandable>"
        for p in plugins_to_show:
            status_icon = "⚪️"
            if p.name in active_set:
                status_icon = "🟢"
            elif p.name in disabled_set:
                status_icon = "🔘"
            elif p.name in inactive_set:
                status_icon = "🔴"

            text += f"{status_icon} `{p.name}`\n  `·` {p.des_short}\n"

        text += f"\n🟢: {lang('apt_plugin_running')}, 🔘: {lang('apt_disable')},  🔴: {lang('apt_plugin_failed')}, ⚪️: {lang('apt_plugin_not_installed')}.\n"
        text += f"</blockquote>\n{lang('apt_plugin_list_des')}"
        await message.edit(text)
    elif message.parameter[0] == "export":
        if not exists(f"{plugin_directory}version.json"):
            await message.edit(lang("apt_why_not_install_a_plugin"))
            return
        message = await message.edit(lang("stats_loading"))
        list_plugin = []
        for key, value in plugin_manager.version_map.items():
            if not value:
                continue
            list_plugin.append(key)
        if len(list_plugin) == 0:
            await message.edit(lang("apt_why_not_install_a_plugin"))
        else:
            await message.edit(",apt install " + " ".join(list_plugin))
    else:
        await message.edit(lang("arg_error"))


@listener(
    is_plugin=False,
    outgoing=True,
    command="apt_source",
    need_admin=True,
    description=lang("apt_source_des"),
    parameters=lang("apt_source_parameters"),
)
async def apt_source(message: Message):
    if len(message.parameter) == 0:
        remotes = plugin_remote_manager.get_remotes()
        if len(remotes) == 0:
            await message.edit(lang("apt_source_not_found"))
            return
        await message.edit(
            f"{lang('apt_source_header')}\n\n" + "\n".join([i.text for i in remotes]),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    elif len(message.parameter) == 2:
        url = message.parameter[1]
        if not url.endswith("/"):
            url += "/"
        if message.parameter[0] == "add":
            try:
                status = await plugin_manager.fetch_remote_url(url)
            except Exception:
                status = False
            if status:
                if plugin_remote_manager.add_remote(url):
                    await message.edit(lang("apt_source_add_success"))
                    await plugin_manager.load_remote_plugins(enable_cache=False)
                else:
                    await message.edit(lang("apt_source_add_failed"))
            else:
                await message.edit(lang("apt_source_add_invalid"))
        elif message.parameter[0] == "del":
            if plugin_remote_manager.remove_remote(url):
                await message.edit(lang("apt_source_del_success"))
                await plugin_manager.load_remote_plugins(enable_cache=False)
            else:
                await message.edit(lang("apt_source_del_failed"))
        else:
            await message.edit(lang("arg_error"))
    else:
        await message.edit(lang("arg_error"))
