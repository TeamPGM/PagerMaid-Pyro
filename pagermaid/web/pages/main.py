from amis import App, PageSchema, Tpl, Page, Flex

from pagermaid.web.html import get_footer, get_github_logo
from pagermaid.web.pages.command_alias import page as command_alias_page
from pagermaid.web.pages.ignore_groups import page as ignore_groups_page
from pagermaid.web.pages.home_page import page as home_page
from pagermaid.web.pages.plugin_local_manage import page as plugin_local_manage_page
from pagermaid.web.pages.plugin_remote_manage import page as plugin_remote_manage_page

github_logo = Tpl(
    className="w-full",
    tpl=get_github_logo(),
)
header = Flex(
    className="w-full", justify="flex-end", alignItems="flex-end", items=[github_logo]
)
admin_app = App(
    brandName="pagermaid",
    logo="https://xtaolabs.com/pagermaid-logo.png",
    header=header,
    pages=[
        {
            "children": [
                home_page,
                PageSchema(
                    label="Bot 设置",
                    icon="fa fa-wrench",
                    children=[command_alias_page, ignore_groups_page],
                ),
                PageSchema(
                    label="插件管理",
                    icon="fa fa-cube",
                    children=[plugin_local_manage_page, plugin_remote_manage_page],
                ),
            ]
        }
    ],
    footer=get_footer(),
)
blank_page = Page(title="PagerMaid-Pyro 404", body="404")
