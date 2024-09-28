import contextlib

import pagermaid.update
from pagermaid.config import Config as _Config
from pagermaid.utils import logs as _logs

module_dir = __path__[0]

if not _Config.API_ID or not _Config.API_HASH:
    _logs.warning("Api-ID or Api-HASH Not Found!")
    _Config.API_ID = _Config.DEFAULT_API_ID
    _Config.API_HASH = _Config.DEFAULT_API_HASH

with contextlib.suppress(ImportError):
    import uvloop  # noqa

    uvloop.install()
