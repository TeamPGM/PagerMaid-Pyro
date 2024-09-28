import re


def get_version():
    with open("pagermaid/version.py", "r", encoding="utf-8") as f:
        if version_match := re.search(r'pgm_version = "(.*?)"', f.read()):
            return version_match[1]
        raise FileNotFoundError


if __name__ == "__main__":
    print(get_version())
