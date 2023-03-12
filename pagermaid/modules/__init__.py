""" PagerMaid module and plugin init. """

from os.path import dirname, basename, isfile, exists
from os import getcwd, makedirs, sep
from glob import glob
from pagermaid import logs
from pagermaid.utils import lang


def __list_modules():
    module_paths = glob(f"{dirname(__file__)}{sep}*.py")
    return [
        basename(file)[:-3]
        for file in module_paths
        if isfile(file) and file.endswith(".py") and not file.endswith("__init__.py")
    ]


def __list_plugins():
    plugin_paths = glob(f"{getcwd()}{sep}plugins" + f"{sep}*.py")
    if not exists(f"{getcwd()}{sep}plugins"):
        makedirs(f"{getcwd()}{sep}plugins")
    return [
        basename(file)[:-3]
        for file in plugin_paths
        if isfile(file) and file.endswith(".py") and not file.endswith("__init__.py")
    ]


module_list_string = "".join(f"{module}, " for module in sorted(__list_modules()))

module_list_string = module_list_string[:-2]

plugin_list_string = "".join(f"{plugin}, " for plugin in sorted(__list_plugins()))

plugin_list_string = plugin_list_string[:-2]

module_list = sorted(__list_modules())
plugin_list = sorted(__list_plugins())
logs.info(f"{lang('modules_init_loading_modules')}: {module_list_string}")
if len(plugin_list) > 0:
    logs.info(f"{lang('modules_init_loading_plugins')}: {plugin_list_string}")
__all__ = __list_modules() + ["module_list"] + __list_plugins() + ["plugin_list"]
