from pagermaid import logs
from pagermaid.config import Config
from pagermaid.hook import Hook
from pagermaid.services import bot


@Hook.on_startup()
async def init_web():
    if not Config.WEB_ENABLE:
        return
    if not Config.WEB_SECRET_KEY:
        logs.warning("未设置 WEB_SECRET_KEY ，请勿将 PagerMaid-Pyro 暴露在公网")
    import uvicorn
    from pagermaid.web import app, init_web

    init_web()
    server = uvicorn.Server(config=uvicorn.Config(app, host=Config.WEB_HOST, port=Config.WEB_PORT))
    bot.loop.create_task(server.serve())
