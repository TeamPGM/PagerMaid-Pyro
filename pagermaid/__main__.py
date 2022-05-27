from sys import path, platform
from os import sep
from importlib import import_module

from pyrogram import idle

from pagermaid import bot, logs, working_dir
from pagermaid.modules import module_list, plugin_list
from pagermaid.utils import lang

path.insert(1, f"{working_dir}{sep}plugins")


async def main():
    logs.info(lang('platform') + platform + lang('platform_load'))

    await bot.start()

    for module_name in module_list:
        try:
            import_module("pagermaid.modules." + module_name)
        except BaseException as exception:
            logs.info(f"{lang('module')} {module_name} {lang('error')}: {type(exception)}: {exception}")
    for plugin_name in plugin_list:
        try:
            import_module("plugins." + plugin_name)
        except BaseException as exception:
            logs.info(f"{lang('module')} {plugin_name} {lang('error')}: {exception}")
            plugin_list.remove(plugin_name)

    logs.info(lang('start'))
    await idle()
    await bot.stop()

bot.run(main())
