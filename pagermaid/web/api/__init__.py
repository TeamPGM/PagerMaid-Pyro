from fastapi import APIRouter

from pagermaid.web.api.utils import authentication
from pagermaid.web.api.bot_info import route as bot_info_route
from pagermaid.web.api.command_alias import route as command_alias_route
from pagermaid.web.api.ignore_groups import route as ignore_groups_route
from pagermaid.web.api.login import route as login_route
from pagermaid.web.api.plugin import route as plugin_route
from pagermaid.web.api.status import route as status_route
from pagermaid.web.api.web_login import (
    route as web_login_route,
    html_route as web_login_html_route,
)

__all__ = ["authentication", "base_api_router", "base_html_router"]

base_api_router = APIRouter(prefix="/pagermaid/api")
base_html_router = APIRouter()

base_api_router.include_router(plugin_route)
base_api_router.include_router(bot_info_route)
base_api_router.include_router(status_route)
base_api_router.include_router(login_route)
base_api_router.include_router(command_alias_route)
base_api_router.include_router(ignore_groups_route)
base_api_router.include_router(web_login_route)
base_html_router.include_router(web_login_html_route)
