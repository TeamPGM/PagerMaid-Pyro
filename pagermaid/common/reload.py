import contextlib
import importlib
import os

import pagermaid.config
import pagermaid.modules
from pagermaid import read_context, bot, help_messages, all_permissions, hook_functions, logs
from pagermaid.common.plugin import plugin_manager
from pagermaid.hook import Hook
from pagermaid.utils import lang


async def reload_all():
    read_context.clear()
    bot.dispatcher.remove_all_handlers()
    bot.job.remove_all_jobs()
    with contextlib.suppress(RuntimeError):
        bot.cancel_all_listener()
    loaded_plugins = list(pagermaid.modules.plugin_list)
    loaded_plugins.extend(iter(pagermaid.modules.module_list))
    # init
    importlib.reload(pagermaid.modules)
    importlib.reload(pagermaid.config)
    help_messages.clear()
    all_permissions.clear()
    for functions in hook_functions.values():
        functions.clear()  # noqa: clear all hooks

    for module_name in pagermaid.modules.module_list:
        try:
            module = importlib.import_module(f"pagermaid.modules.{module_name}")
            if module_name in loaded_plugins:
                importlib.reload(module)
        except BaseException as exception:
            logs.info(f"{lang('module')} {module_name} {lang('error')}: {type(exception)}: {exception}")
    for plugin_name in pagermaid.modules.plugin_list.copy():
        try:
            plugin = importlib.import_module(f"plugins.{plugin_name}")
            if plugin_name in loaded_plugins and os.path.exists(plugin.__file__):
                importlib.reload(plugin)
        except BaseException as exception:
            logs.info(f"{lang('module')} {plugin_name} {lang('error')}: {exception}")
            pagermaid.modules.plugin_list.remove(plugin_name)
    plugin_manager.load_local_plugins()
    plugin_manager.save_local_version_map()
    await Hook.load_success_exec()
