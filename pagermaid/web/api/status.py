import asyncio
from typing import Union

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from pagermaid.common.status import get_status
from pagermaid.common.system import run_eval
from pagermaid.utils import execute
from pagermaid.web.api.utils import authentication

route = APIRouter()


@route.get("/log", dependencies=[authentication()])
async def get_log(num: Union[int, str] = 100):
    try:
        num = int(num)
    except ValueError:
        num = 100

    async def streaming_logs():
        with open("data/pagermaid.log.txt", "r", encoding="utf-8") as f:
            for log in f.readlines()[-num:]:
                yield log
                await asyncio.sleep(0.02)

    return StreamingResponse(streaming_logs())


@route.get("/run_eval", dependencies=[authentication()])
async def run_cmd(cmd: str = ""):
    async def run_cmd_func():
        result = (await run_eval(cmd)).split("\n")
        for i in result:
            yield i + "\n"
            await asyncio.sleep(0.02)

    return StreamingResponse(run_cmd_func()) if cmd else "无效命令"


@route.get("/run_sh", dependencies=[authentication()])
async def run_sh(cmd: str = ""):
    async def run_sh_func():
        result = (await execute(cmd)).split("\n")
        for i in result:
            yield i + "\n"
            await asyncio.sleep(0.02)

    return StreamingResponse(run_sh_func()) if cmd else "无效命令"


@route.get("/status", response_class=JSONResponse, dependencies=[authentication()])
async def status():
    return (await get_status()).dict()
