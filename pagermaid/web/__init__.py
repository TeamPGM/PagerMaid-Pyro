from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from pagermaid.config import Config
from pagermaid.web.api import base_api_router
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
app: FastAPI = FastAPI()


def init_web():
    app.include_router(base_api_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.WEB_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=RedirectResponse)
    async def index():
        return "/admin"

    @app.get("/admin", response_class=HTMLResponse)
    async def admin():
        return admin_app.render(
            site_title="PagerMaid-Pyro 后台管理",
            site_icon=icon_path,
            requestAdaptor=requestAdaptor,
            responseAdaptor=responseAdaptor,
        )

    @app.get("/login", response_class=HTMLResponse)
    async def login():
        return login_page.render(
            site_title="登录 | PagerMaid-Pyro 后台管理",
            site_icon=icon_path,
        )
