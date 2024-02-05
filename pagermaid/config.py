import os
import sys
from json import load as load_json
from pathlib import Path
from shutil import copyfile
from typing import Dict

from yaml import load, FullLoader, safe_load

CONFIG_PATH = Path("data/config.yml")


def strtobool(val, default=False):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    if val is None:
        return default
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        print("[Degrade] invalid truth value %r" % (val,))
        return default


try:
    config: Dict = load(open(CONFIG_PATH, encoding="utf-8"), Loader=FullLoader)
except FileNotFoundError:
    print(
        "The configuration file does not exist, and a new configuration file is being generated."
    )
    copyfile(f"{os.getcwd()}{os.sep}config.gen.yml", CONFIG_PATH)
    sys.exit(1)


class Config:
    try:
        DEFAULT_API_ID = 21724
        DEFAULT_API_HASH = "3e0cb5efcd52300aec5994fdfc5bdc16"
        try:
            API_ID = int(os.environ.get("API_ID", config["api_id"]))
            API_HASH = os.environ.get("API_HASH", config["api_hash"])
        except (ValueError, KeyError):
            print("[Error] API_ID or API_HASH is invalid, use the default value.")
            # TGX
            API_ID = DEFAULT_API_ID
            API_HASH = DEFAULT_API_HASH
        QRCODE_LOGIN = strtobool(
            os.environ.get("QRCODE_LOGIN", config.get("qrcode_login", "false"))
        )
        WEB_LOGIN = strtobool(
            os.environ.get("WEB_LOGIN", config.get("web_login", "false"))
        )
        STRING_SESSION = os.environ.get("STRING_SESSION")
        DEBUG = strtobool(os.environ.get("PGM_DEBUG", config["debug"]))
        ERROR_REPORT = strtobool(
            os.environ.get("PGM_ERROR_REPORT", config["error_report"]), True
        )
        LANGUAGE = os.environ.get("PGM_LANGUAGE", config["application_language"])
        REGION = os.environ.get("PGM_REGION", config["application_region"])
        TIME_ZONE = os.environ.get(
            "PGM_TIME_ZONE", config.get("timezone", "Asia/Shanghai")
        )
        TTS = os.environ.get("PGM_TTS", config["application_tts"])
        LOG = strtobool(os.environ.get("PGM_LOG", config["log"]))
        LOG_ID = os.environ.get("PGM_LOG_ID", config["log_chatid"])
        IPV6 = strtobool(os.environ.get("PGM_IPV6", config["ipv6"]))
        ALLOW_ANALYTIC = strtobool(
            os.environ.get("PGM_ALLOW_ANALYTIC", config["allow_analytic"]), True
        )
        SENTRY_API = os.environ.get("SENTRY_API", config.get("sentry_api", ""))
        if not SENTRY_API:
            SENTRY_API = "https://79584904859c93d48dbc71d73e76a51a@o416616.ingest.sentry.io/4506478732443653"
        MIXPANEL_API = os.environ.get("MIXPANEL_API", config.get("mixpanel_api"))
        if not MIXPANEL_API:
            MIXPANEL_API = "c79162511383b0fa1e9c062a2a86c855"
        TIME_FORM = os.environ.get("PGM_TIME_FORM", config["time_form"])
        DATE_FORM = os.environ.get("PGM_DATE_FORM", config["date_form"])
        START_FORM = os.environ.get("PGM_START_FORM", config["start_form"])
        SILENT = strtobool(os.environ.get("PGM_PGM_SILENT", config["silent"]), True)
        PROXY_ADDRESS = os.environ.get("PGM_PROXY_ADDRESS", config["proxy_addr"])
        PROXY_PORT = os.environ.get("PGM_PROXY_PORT", config["proxy_port"])
        PROXY_HTTP_ADDRESS = os.environ.get(
            "PGM_PROXY_HTTP_ADDRESS", config["http_addr"]
        )
        PROXY_HTTP_PORT = os.environ.get("PGM_PROXY_HTTP_PORT", config["http_port"])
        PROXY = None
        if PROXY_ADDRESS and PROXY_PORT:
            PROXY = dict(scheme="socks5", hostname=PROXY_ADDRESS, port=int(PROXY_PORT))
        elif PROXY_HTTP_ADDRESS and PROXY_HTTP_PORT:
            PROXY = dict(
                scheme="http", hostname=PROXY_HTTP_ADDRESS, port=int(PROXY_HTTP_PORT)
            )
        GIT_SOURCE = os.environ.get("PGM_GIT_SOURCE", config["git_source"])
        GIT_SOURCE = GIT_SOURCE.replace(
            "TeamPGM/PagerMaid_Plugins/", "TeamPGM/PagerMaid_Plugins_Pyro/"
        )
        try:
            with open(
                f"languages{os.sep}built-in{os.sep}en.yml",
                "r",
                encoding="utf-8",
            ) as f:
                lang_default_dict = safe_load(f)
            with open(
                f"languages{os.sep}built-in{os.sep}{LANGUAGE}.yml",
                "r",
                encoding="utf-8",
            ) as f:
                lang_dict = safe_load(f)
        except Exception as e:
            print(
                "[Degrade] Reading language YAML file failed, try to use the english language file."
            )
            print(e)
            try:
                with open(
                    f"languages{os.sep}built-in{os.sep}en.yml",
                    "r",
                    encoding="utf-8",
                ) as f:
                    lang_dict = safe_load(f)
            except Exception as e:
                print("[Error] Reading English language YAML file failed.")
                print(e)
                sys.exit(1)
        try:
            with open(f"data{os.sep}alias.json", encoding="utf-8") as f:
                alias_dict = load_json(f)
        except Exception as e:
            alias_dict = {}
        web_interface = config.get("web_interface", {})
        WEB_ENABLE = strtobool(
            os.environ.get("WEB_ENABLE", web_interface.get("enable", "False"))
        )
        WEB_SECRET_KEY = os.environ.get(
            "WEB_SECRET_KEY", web_interface.get("secret_key", "secret_key")
        )
        WEB_HOST = os.environ.get("WEB_HOST", web_interface.get("host", "127.0.0.1"))
        WEB_PORT = int(os.environ.get("WEB_PORT", web_interface.get("port", 3333)))
        WEB_ORIGINS = web_interface.get("origins", ["*"])
        USE_PB = strtobool(os.environ.get("PGM_USE_PB", config.get("use_pb")), True)
    except ValueError as e:
        print(e)
        sys.exit(1)
