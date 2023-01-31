import datetime
from typing import Optional

from fastapi import Header, HTTPException, Depends
from jose import jwt

from pagermaid.config import Config

ALGORITHM = 'HS256'
TOKEN_EXPIRE_MINUTES = 30


def authentication():
    def inner(token: Optional[str] = Header(...)):
        try:
            jwt.decode(token, Config.WEB_SECRET_KEY, algorithms=ALGORITHM)
        except (jwt.JWTError, jwt.ExpiredSignatureError, AttributeError):
            raise HTTPException(status_code=400, detail='登录验证失败或已失效，请重新登录')

    return Depends(inner)


def create_token():
    data = {
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(data, Config.WEB_SECRET_KEY, algorithm=ALGORITHM)
