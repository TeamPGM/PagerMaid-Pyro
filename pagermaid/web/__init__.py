import asyncio

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from pagermaid.config import Config
from pagermaid.utils import logs
from pagermaid.web.api import base_api_router, base_html_router
from pagermaid.web.pages import admin_app, login_page

requestAdaptor = """
requestAdaptor(api) {
    api.headers["token"] = localStorage.getItem("token");
    return api;
},
"""
responseAdaptor = """
responseAdaptor(api, payload, query, request, response) {
    if (response.data.detail == '登录验证失败或已失效，请重新登录') {
        window.location.href = '/login'
        window.localStorage.clear()
        window.sessionStorage.clear()
        window.alert('登录验证失败或已失效，请重新登录')
    }
    return payload
},
"""
icon_path = "https://xtaolabs.com/pagermaid-logo.png"


class Web:
    def __init__(self):
        self.app: FastAPI = FastAPI()
        self.web_server = None
        self.web_server_task = None
        self.bot_main_task = None

    def init_web(self):
        self.app.include_router(base_api_router)
        self.app.include_router(base_html_router)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=Config.WEB_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/", response_class=RedirectResponse)
        async def index():
            return "/admin"

        @self.app.get("/admin", response_class=HTMLResponse)
        async def admin():
            return admin_app.render(
                site_title="PagerMaid-Pyro 后台管理",
                site_icon=icon_path,
                requestAdaptor=requestAdaptor,
                responseAdaptor=responseAdaptor,
            )

        @self.app.get("/login", response_class=HTMLResponse)
        async def login():
            return login_page.render(
                site_title="登录 | PagerMaid-Pyro 后台管理",
                site_icon=icon_path,
            )

    async def start(self):
        if not Config.WEB_ENABLE:
            return
        if not Config.WEB_SECRET_KEY:
            logs.warning("未设置 WEB_SECRET_KEY ，请勿将 PagerMaid-Pyro 暴露在公网")
        import uvicorn

        self.init_web()
        self.web_server = uvicorn.Server(
            config=uvicorn.Config(
                self.app, host=Config.WEB_HOST, port=Config.WEB_PORT, log_config=None
            )
        )
        server_config = self.web_server.config
        server_config.setup_event_loop()
        if not server_config.loaded:
            server_config.load()
        self.web_server.lifespan = server_config.lifespan_class(server_config)
        try:
            await self.web_server.startup()
        except OSError as e:
            if e.errno == 10048:
                logs.error("Web Server 端口被占用：%s", e)
            logs.error("Web Server 启动失败，正在退出")
            raise SystemExit from None

        if self.web_server.should_exit:
            logs.error("Web Server 启动失败，正在退出")
            raise SystemExit from None
        logs.info("Web Server 启动成功")
        self.web_server_task = asyncio.create_task(self.web_server.main_loop())

    def stop(self):
        if self.web_server_task:
            self.web_server_task.cancel()
        if self.bot_main_task:
            self.bot_main_task.cancel()


web = Web()
