from pathlib import Path

html_base_path = Path(__file__).parent


def get_html(path: Path) -> str:
    """获取 HTML 模板。"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_logo() -> str:
    """获取 logo。"""
    return get_html(html_base_path / "logo.html")


def get_github_logo() -> str:
    """获取 github logo。"""
    return get_html(html_base_path / "github_logo.html")


def get_footer() -> str:
    """获取 footer。"""
    return get_html(html_base_path / "footer.html")
