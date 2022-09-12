import os
from json import load as load_json
import sys
from yaml import load, FullLoader, safe_load
from shutil import copyfile


def strtobool(val, default=False):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        print("[Degrade] invalid truth value %r" % (val,))
        return default


try:
    config = load(open(r"config.yml", encoding="utf-8"), Loader=FullLoader)
except FileNotFoundError:
    print("The configuration file does not exist, and a new configuration file is being generated.")
    copyfile(f"{os.getcwd()}{os.sep}config.gen.yml", "config.yml")
    sys.exit(1)


class Config:
    try:
        API_ID = int(os.environ.get("API_ID", config["api_id"]))
        API_HASH = os.environ.get("API_HASH", config["api_hash"])
        STRING_SESSION = os.environ.get("STRING_SESSION")
        DEBUG = strtobool(os.environ.get("PGM_DEBUG", config["debug"]))
        ERROR_REPORT = strtobool(os.environ.get("PGM_ERROR_REPORT", config["error_report"]), True)
        LANGUAGE = os.environ.get("PGM_LANGUAGE", config["application_language"])
        REGION = os.environ.get("PGM_REGION", config["application_region"])
        TTS = os.environ.get("PGM_TTS", config["application_tts"])
        LOG = strtobool(os.environ.get("PGM_LOG", config["log"]))
        LOG_ID = int(os.environ.get("PGM_LOG_ID", config["log_chatid"]))
        IPV6 = strtobool(os.environ.get("PGM_IPV6", config["ipv6"]))
        ALLOW_ANALYTIC = strtobool(os.environ.get("PGM_ALLOW_ANALYTIC", config["allow_analytic"]), True)
        SENTRY_API = "https://0785960e63e04279a694d0486d47d9ea@o1342815.ingest.sentry.io/6617119"
        MIXPANEL_API = "c79162511383b0fa1e9c062a2a86c855"
        TIME_FORM = os.environ.get("PGM_TIME_FORM", config["time_form"])
        DATE_FORM = os.environ.get("PGM_DATE_FORM", config["date_form"])
        START_FORM = os.environ.get("PGM_START_FORM", config["start_form"])
        SILENT = strtobool(os.environ.get("PGM_PGM_SILENT", config["silent"]), True)
        PROXY_ADDRESS = os.environ.get("PGM_PROXY_ADDRESS", config["proxy_addr"])
        PROXY_PORT = os.environ.get("PGM_PROXY_PORT", config["proxy_port"])
        PROXY = None
        if PROXY_ADDRESS and PROXY_PORT:
            PROXY = dict(
                scheme="socks5",
                hostname=PROXY_ADDRESS,
                port=int(PROXY_PORT)
            )
        GIT_SOURCE = os.environ.get("PGM_GIT_SOURCE", config["git_source"])
        GIT_SOURCE = GIT_SOURCE.replace("TeamPGM/PagerMaid_Plugins/", "TeamPGM/PagerMaid_Plugins_Pyro/")
        try:
            with open(f"languages{os.sep}built-in{os.sep}{LANGUAGE}.yml", "r", encoding="utf-8") as f:
                lang_dict = safe_load(f)
        except Exception as e:
            print("[Degrade] Reading language YAML file failed, try to use the english language file.")
            print(e)
            try:
                with open(f"languages{os.sep}built-in{os.sep}{LANGUAGE}.yml", "r", encoding="utf-8") as f:
                    lang_dict = safe_load(f)
            except Exception as e:
                print("[Error] Reading English language YAML file failed.")
                print(e)
                sys.exit(1)
        try:
            with open(f"data{os.sep}alias.json", encoding="utf-8") as f:
                alias_dict = load_json(f)
        except Exception as e:
            print(f"[Degrade] Reading alias file failed：{e}")
            alias_dict = {}
    except ValueError as e:
        print(e)
        sys.exit(1)
