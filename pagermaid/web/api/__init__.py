from fastapi import APIRouter

from pagermaid.web.api.utils import authentication
from pagermaid.web.api.bot_info import route as bot_info_route
from pagermaid.web.api.command_alias import route as command_alias_route
from pagermaid.web.api.ignore_groups import route as ignore_groups_route
from pagermaid.web.api.login import route as login_route
from pagermaid.web.api.plugin import route as plugin_route
from pagermaid.web.api.status import route as status_route

base_api_router = APIRouter(prefix="/pagermaid/api")

base_api_router.include_router(plugin_route)
base_api_router.include_router(bot_info_route)
base_api_router.include_router(status_route)
base_api_router.include_router(login_route)
base_api_router.include_router(command_alias_route)
base_api_router.include_router(ignore_groups_route)
