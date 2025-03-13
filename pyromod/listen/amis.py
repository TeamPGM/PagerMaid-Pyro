from pathlib import Path

import amis
from jinja2 import Environment, FileSystemLoader

from pyromod.utils import patchable, patch

env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))


@patch(amis.Page)
class Page(amis.Page):
    @patchable
    def render(
        self,
        template_name: str = "",
        locale: str = "zh_CN",
        cdn: str = "https://unpkg.com",
        version: str = "latest",
        site_title: str = "Amis",
        site_icon: str = "",
        theme: str = "default",
        routerModel: str = "createHashHistory",
        requestAdaptor: str = "",
        responseAdaptor: str = "",
    ) -> str:
        """渲染html模板"""
        if theme == "default":
            theme_css = "sdk.css"
            theme_name = "cxd"
        else:
            theme_css = f"{theme}.css"
            theme_name = theme
        template_name = template_name or self.__default_template_path__
        return env.get_template(template_name).render(
            **{
                "AmisSchemaJson": self.to_json(),
                "locale": locale,
                "cdn": cdn,
                "version": version,
                "site_title": site_title,
                "site_icon": site_icon,
                "theme_css": theme_css,
                "theme_name": theme_name,
                "routerModel": routerModel,
                "requestAdaptor": requestAdaptor,
                "responseAdaptor": responseAdaptor,
            }
        )
