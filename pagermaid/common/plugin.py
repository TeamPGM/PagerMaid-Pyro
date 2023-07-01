import contextlib
import json
import os
from pathlib import Path
from typing import Optional, List, Tuple

from pydantic import BaseModel

from pagermaid import Config
from pagermaid.enums import Message
from pagermaid.common.cache import cache
from pagermaid.modules import plugin_list as active_plugins
from pagermaid.utils import client

plugins_path = Path("plugins")


class LocalPlugin(BaseModel):
    name: str
    status: bool
    installed: bool = False
    version: Optional[float]

    @property
    def normal_path(self) -> Path:
        return plugins_path / f"{self.name}.py"

    @property
    def disabled_path(self) -> Path:
        return plugins_path / f"{self.name}.py.disabled"

    @property
    def load_status(self) -> bool:
        """插件加载状态"""
        return self.name in active_plugins

    def remove(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove(self.normal_path)
        with contextlib.suppress(FileNotFoundError):
            os.remove(self.disabled_path)

    def enable(self) -> bool:
        try:
            os.rename(self.disabled_path, self.normal_path)
            return True
        except Exception:
            return False

    def disable(self) -> bool:
        try:
            os.rename(self.normal_path, self.disabled_path)
            return True
        except Exception:
            return False


class RemotePlugin(LocalPlugin):
    section: str
    maintainer: str
    size: str
    supported: bool
    des: str
    ...

    async def install(self) -> bool:
        html = await client.get(f"{Config.GIT_SOURCE}{self.name}/main.py")
        if html.status_code == 200:
            self.remove()
            with open(plugins_path / f"{self.name}.py", mode="wb") as f:
                f.write(html.text.encode("utf-8"))
            return True
        return False


class PluginManager:
    def __init__(self):
        self.version_map = {}
        self.remote_version_map = {}
        self.plugins: List[LocalPlugin] = []
        self.remote_plugins: List[RemotePlugin] = []

    def load_local_version_map(self):
        if not os.path.exists(plugins_path / "version.json"):
            return
        with open(plugins_path / "version.json", "r", encoding="utf-8") as f:
            self.version_map = json.load(f)

    def save_local_version_map(self):
        with open(plugins_path / "version.json", "w", encoding="utf-8") as f:
            json.dump(self.version_map, f, indent=4)

    def get_local_version(self, name: str) -> Optional[float]:
        data = self.version_map.get(name)
        return float(data) if data else None

    def set_local_version(self, name: str, version: float) -> None:
        self.version_map[name] = version
        self.save_local_version_map()

    def get_plugin_install_status(self, name: str) -> bool:
        return name in self.version_map

    @staticmethod
    def get_plugin_load_status(name: str) -> bool:
        return bool(os.path.exists(plugins_path / f"{name}.py"))

    def remove_plugin(self, name: str) -> bool:
        if plugin := self.get_local_plugin(name):
            plugin.remove()
            if name in self.version_map:
                self.version_map.pop(name)
                self.save_local_version_map()
            return True
        return False

    def enable_plugin(self, name: str) -> bool:
        return plugin.enable() if (plugin := self.get_local_plugin(name)) else False

    def disable_plugin(self, name: str) -> bool:
        return plugin.disable() if (plugin := self.get_local_plugin(name)) else False

    def load_local_plugins(self) -> List[LocalPlugin]:
        self.load_local_version_map()
        self.plugins = []
        for plugin in os.listdir("plugins"):
            if plugin.endswith(".py") or plugin.endswith(".py.disabled"):
                plugin = (
                    plugin[:-12] if plugin.endswith(".py.disabled") else plugin[:-3]
                )
                self.plugins.append(
                    LocalPlugin(
                        name=plugin,
                        installed=self.get_plugin_install_status(plugin),
                        status=self.get_plugin_load_status(plugin),
                        version=self.get_local_version(plugin),
                    )
                )
        return self.plugins

    def get_local_plugin(self, name: str) -> LocalPlugin:
        return next(filter(lambda x: x.name == name, self.plugins), None)

    async def __load_remote_plugins(self) -> List[RemotePlugin]:
        plugin_list = await client.get(f"{Config.GIT_SOURCE}list.json")
        plugin_list = plugin_list.json()["list"]
        plugins = [
            RemotePlugin(
                **plugin,
                status=False,
            )
            for plugin in plugin_list
        ]
        self.remote_plugins = plugins
        self.remote_version_map = {plugin.name: plugin.version for plugin in plugins}
        return plugins

    @cache()
    async def _load_remote_plugins(self) -> List[RemotePlugin]:
        return await self.__load_remote_plugins()

    async def load_remote_plugins(self) -> List[RemotePlugin]:
        plugin_list = await self._load_remote_plugins()
        for i in plugin_list:
            i.status = self.get_plugin_load_status(i.name)
        return plugin_list

    def get_remote_plugin(self, name: str) -> RemotePlugin:
        return next(filter(lambda x: x.name == name, self.remote_plugins), None)

    def plugin_need_update(self, name: str) -> bool:
        if local_version := self.get_local_version(name):
            if local_version == 0.0:
                return False
            if remote_version := self.remote_version_map.get(name):
                return local_version < remote_version
        return False

    async def install_remote_plugin(self, name: str) -> bool:
        if plugin := self.get_remote_plugin(name):
            if await plugin.install():
                self.set_local_version(name, plugin.version)
                return True
        return False

    async def update_remote_plugin(self, name: str) -> bool:
        if self.plugin_need_update(name):
            return await self.install_remote_plugin(name)
        return False

    async def update_all_remote_plugin(self) -> List[RemotePlugin]:
        updated_plugins = []
        for i in self.remote_plugins:
            if await self.update_remote_plugin(i.name):
                updated_plugins.append(i)
        return updated_plugins

    @staticmethod
    async def download_from_message(message: Message) -> str:
        """Download a plugin from a message"""
        reply = message.reply_to_message
        file_path = None
        if (
            reply
            and reply.document
            and reply.document.file_name
            and reply.document.file_name.endswith(".py")
        ):
            file_path = await message.reply_to_message.download()
        elif (
            message.document
            and message.document.file_name
            and message.document.file_name.endswith(".py")
        ):
            file_path = await message.download()
        return file_path

    def get_plugins_status(
        self,
    ) -> Tuple[List[LocalPlugin], List[LocalPlugin], List[LocalPlugin]]:
        """Get plugins status"""
        all_local_plugins = self.plugins
        disabled_plugins = []
        inactive_plugins = []
        for plugin in all_local_plugins:
            if not plugin.status:
                inactive_plugins.append(plugin)
            elif not plugin.load_status:
                disabled_plugins.append(plugin)
        return active_plugins, disabled_plugins, inactive_plugins


plugin_manager = PluginManager()
