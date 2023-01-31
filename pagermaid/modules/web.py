from pagermaid.config import Config
from pagermaid.hook import Hook
from pagermaid.services import bot


@Hook.on_startup()
async def init_web():
    if not Config.WEB_ENABLE:
        return
    import uvicorn
    from pagermaid.web import app, init_web

    init_web()
    server = uvicorn.Server(config=uvicorn.Config(app, host=Config.WEB_HOST, port=Config.WEB_PORT))
    bot.loop.create_task(server.serve())
