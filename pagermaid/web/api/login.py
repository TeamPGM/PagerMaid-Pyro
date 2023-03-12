from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pagermaid import pgm_version_code
from pagermaid.web.api.utils import create_token
from pagermaid.config import Config


class UserModel(BaseModel):
    password: str


route = APIRouter()


@route.post("/login", response_class=JSONResponse)
async def login(user: UserModel):
    if user.password != Config.WEB_SECRET_KEY:
        return {"status": -100, "msg": "登录失败，请重新输入密钥"}
    token = create_token()
    return {
        "status": 0,
        "msg": "登录成功",
        "data": {"version": pgm_version_code, "token": token},
    }
