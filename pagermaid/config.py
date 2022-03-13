import os
from json import load as load_json
from yaml import load, FullLoader, safe_load
from shutil import copyfile
from distutils.util import strtobool


try:
    config = load(open(r"config.yml"), Loader=FullLoader)
except FileNotFoundError:
    print("The configuration file does not exist, and a new configuration file is being generated.")
    copyfile(f"{os.getcwd()}{os.sep}config.gen.yml", "config.yml")
    exit(1)


class Config(object):
    try:
        API_ID = int(os.environ.get("API_ID", config["api_id"]))
        API_HASH = os.environ.get("API_HASH", config["api_hash"])
        STRING_SESSION = os.environ.get("STRING_SESSION", None)
        DEBUG = strtobool(os.environ.get("DEBUG", config["debug"]))
        ERROR_REPORT = strtobool(os.environ.get("ERROR_REPORT", config["error_report"]))
        LANGUAGE = os.environ.get("LANGUAGE", config["application_language"])
        REGION = os.environ.get("REGION", config["application_region"])
        TTS = os.environ.get("TTS", config["application_tts"])
        LOG = strtobool(os.environ.get("LOG", config["log"]))
        LOG_ID = int(os.environ.get("LOG_ID", config["log_chatid"]))
        IPV6 = strtobool(os.environ.get("IPV6", config["ipv6"]))
        TIME_FORM = os.environ.get("TIME_FORM", config["time_form"])
        DATE_FORM = os.environ.get("DATE_FORM", config["date_form"])
        START_FORM = os.environ.get("START_FORM", config["start_form"])
        SILENT = strtobool(os.environ.get("SILENT", config["silent"]))
        try:
            with open(f"languages{os.sep}built-in{os.sep}{LANGUAGE}.yml", "r", encoding="utf-8") as f:
                lang_dict = safe_load(f)
        except Exception as e:
            print("Reading language YAML file failed")
            print(e)
            exit(1)
        try:
            with open(f"data{os.sep}alias.json", encoding="utf-8") as f:
                alias_dict = load_json(f)
        except Exception as e:
            print(f"Reading alias file failed：{e}")
            alias_dict = {}
    except ValueError as e:
        print(e)
        exit(1)
