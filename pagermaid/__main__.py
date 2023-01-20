from sys import path, platform
from os import sep
from importlib import import_module

from pyrogram import idle
from pyrogram.errors import AuthKeyUnregistered

from pagermaid import bot, logs, working_dir
from pagermaid.hook import Hook
from pagermaid.modules import module_list, plugin_list
from pagermaid.single_utils import safe_remove
from pagermaid.utils import lang, process_exit
from pyromod.methods.sign_in_qrcode import start_client

path.insert(1, f"{working_dir}{sep}plugins")


async def main():
    logs.info(lang('platform') + platform + lang('platform_load'))

    try:
        await start_client(bot)
    except AuthKeyUnregistered:
        safe_remove("pagermaid.session")
        exit()

    me = await bot.get_me()
    if me.is_bot:
        safe_remove("pagermaid.session")
        exit()
    logs.info(f"{lang('save_id')} {me.first_name}({me.id})")

    for module_name in module_list:
        try:
            import_module(f"pagermaid.modules.{module_name}")
        except BaseException as exception:
            logs.info(f"{lang('module')} {module_name} {lang('error')}: {type(exception)}: {exception}")
    for plugin_name in plugin_list.copy():
        try:
            import_module(f"plugins.{plugin_name}")
        except BaseException as exception:
            logs.info(f"{lang('module')} {plugin_name} {lang('error')}: {exception}")
            plugin_list.remove(plugin_name)

    await process_exit(start=True, _client=bot)
    logs.info(lang('start'))
    await Hook.load_success_exec()
    await Hook.startup()

    await idle()
    await bot.stop()

bot.run(main())
