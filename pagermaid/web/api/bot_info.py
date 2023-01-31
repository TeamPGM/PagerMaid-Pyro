import os
import signal

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from pagermaid.web.api.utils import authentication
from pagermaid.common.update import update

route = APIRouter()


@route.post('/bot_update', response_class=JSONResponse, dependencies=[authentication()])
async def bot_update():
    await update()
    return {
        "status": 0,
        "msg":    "更新成功，请重启 PagerMaid-Pyro 以应用更新。"
    }


@route.post('/bot_restart', response_class=JSONResponse, dependencies=[authentication()])
async def bot_restart():
    os.kill(os.getpid(), signal.SIGINT)
    return {}
