import importlib
import pagermaid.config
import pagermaid.modules

from pagermaid import bot, logs, help_messages, all_permissions
from pagermaid.listener import listener
from pagermaid.utils import lang, Message


def reload_all():
    bot.dispatcher.remove_all_handlers()
    bot.job.remove_all_jobs()
    loaded_plugins = list(pagermaid.modules.plugin_list)
    loaded_plugins.extend(iter(pagermaid.modules.module_list))
    # init
    importlib.reload(pagermaid.modules)
    importlib.reload(pagermaid.config)
    help_messages.clear()
    all_permissions.clear()

    importlib.reload(pagermaid.modules)
    for module_name in pagermaid.modules.module_list:
        try:
            module = importlib.import_module(f"pagermaid.modules.{module_name}")
            if module_name in loaded_plugins:
                importlib.reload(module)
        except BaseException as exception:
            logs.info(f"{lang('module')} {module_name} {lang('error')}: {type(exception)}: {exception}")
    for plugin_name in pagermaid.modules.plugin_list:
        try:
            plugin = importlib.import_module(f"plugins.{plugin_name}")
            if plugin_name in loaded_plugins:
                importlib.reload(plugin)
        except BaseException as exception:
            logs.info(f"{lang('module')} {plugin_name} {lang('error')}: {exception}")
            pagermaid.modules.plugin_list.remove(plugin_name)


@listener(is_plugin=False, command="reload",
          need_admin=True,
          description=lang('reload_des'))
async def reload_plugins(message: Message):
    """ To reload plugins. """
    reload_all()
    await message.edit(lang("reload_ok"))
