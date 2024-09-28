from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pagermaid.config import Config
from pagermaid.version import pgm_version_code
from pagermaid.web.api.utils import create_token


class UserModel(BaseModel):
    password: Optional[str] = None


route = APIRouter()


@route.post("/login", response_class=JSONResponse)
async def login(user: UserModel):
    if not Config.WEB_SECRET_KEY or user.password == Config.WEB_SECRET_KEY:
        token = create_token()
        data = {
            "status": 0,
            "msg": "登录成功",
            "data": {"version": pgm_version_code, "token": token},
        }
        response = JSONResponse(content=data)
        response.set_cookie(key="token_ck", value=token, expires=1800)
        return response
    return {"status": -100, "msg": "登录失败，请重新输入密钥"}
