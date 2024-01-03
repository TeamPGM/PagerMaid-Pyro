from fastapi import APIRouter
from fastapi.responses import JSONResponse

from pagermaid.common.plugin import plugin_manager
from pagermaid.common.reload import reload_all
from pagermaid.web.api.utils import authentication

route = APIRouter()


@route.get(
    "/get_local_plugins", response_class=JSONResponse, dependencies=[authentication()]
)
async def get_local_plugins():
    plugins = [i.dict() for i in plugin_manager.plugins]
    plugins.sort(key=lambda x: x["name"])
    return {"status": 0, "msg": "ok", "data": {"rows": plugins, "total": len(plugins)}}


@route.post(
    "/set_local_plugin_status",
    response_class=JSONResponse,
    dependencies=[authentication()],
)
async def set_local_plugin_status(data: dict):
    module_name: str = data.get("plugin")
    status: bool = data.get("status")
    if not (plugin := plugin_manager.get_local_plugin(module_name)):
        return {"status": -100, "msg": f"插件 {module_name} 不存在"}
    if status:
        plugin.enable()
    else:
        plugin.disable()
    await reload_all()
    return {"status": 0, "msg": f'成功{"开启" if status else "关闭"} {module_name}'}


@route.post(
    "/remove_local_plugin", response_class=JSONResponse, dependencies=[authentication()]
)
async def remove_local_plugin(data: dict):
    module_name: str = data.get("plugin")
    if not (plugin := plugin_manager.get_local_plugin(module_name)):
        return {"status": -100, "msg": f"插件 {module_name} 不存在"}
    plugin_manager.remove_plugin(plugin.name)
    await reload_all()
    return {"status": 0, "msg": f"成功卸载 {module_name}"}


@route.get(
    "/get_remote_plugins", response_class=JSONResponse, dependencies=[authentication()]
)
async def get_remote_plugins():
    await plugin_manager.load_remote_plugins()
    plugins = [i.dict() for i in plugin_manager.remote_plugins]
    plugins.sort(key=lambda x: x["name"])
    return {"status": 0, "msg": "ok", "data": {"rows": plugins, "total": len(plugins)}}


@route.post(
    "/set_remote_plugin_status",
    response_class=JSONResponse,
    dependencies=[authentication()],
)
async def set_remote_plugin_status(data: dict):
    module_name: str = data.get("plugin")
    status: bool = data.get("status")
    if not plugin_manager.get_remote_plugin(module_name):
        return {"status": 1, "msg": f"插件 {module_name} 不存在"}
    if status:
        await plugin_manager.install_remote_plugin(module_name)
    else:
        plugin_manager.remove_plugin(module_name)
    await reload_all()
    return {"status": 0, "msg": f'成功{"安装" if status else "卸载"} {module_name}'}
