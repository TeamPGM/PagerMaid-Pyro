import datetime
import functools
import inspect
from typing import Any, Dict, Optional

from pydantic import BaseModel


class Cache(BaseModel):
    value: Any
    time: Optional[datetime.datetime]


def cache(ttl=datetime.timedelta(minutes=15)):
    def wrap(func):
        cache_data: Dict[str, Cache] = {}

        @functools.wraps(func)
        async def wrapped(*args, **kw):
            nonlocal cache_data
            bound = inspect.signature(func).bind(*args, **kw)
            bound.apply_defaults()
            ins_key = "|".join([f"{k}_{v}" for k, v in bound.arguments.items()])
            data: Cache = cache_data.get(ins_key, Cache(value=None, time=None))
            now = datetime.datetime.now()
            if (not data.time) or ((now - data.time) > ttl):
                try:
                    data.value = await func(*args, **kw)
                    data.time = datetime.datetime.now()
                    cache_data[ins_key] = data
                except Exception as e:
                    raise e
            return data.value

        return wrapped

    return wrap
