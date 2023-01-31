from amis import InputText, Switch, Card, Tpl, CardsCRUD, PageSchema, Page, Button

card = Card(
    header=Card.Header(
        title='$name',
        description='$des',
        avatarText='$name',
        avatarTextClassName='overflow-hidden'
    ),
    actions=[],
    toolbar=[
        Switch(
            name='enable',
            value='${status}',
            onText='已安装',
            offText='未安装',
            onEvent={
                'change': {
                    'actions': {
                        'actionType': 'ajax',
                        'args': {
                            'api': {
                                'url': '/pagermaid/api/set_remote_plugin_status',
                                'method': 'post'
                            },
                            'messages': {
                                'success': '成功${IF(event.data.value, "安装", "卸载")}了 ${name}',
                                'failed': '操作失败'
                            },
                            'status': '${event.data.value}',
                            'plugin': '${name}'
                        }
                    }
                }
            }
        )
    ]
)
cards_curd = CardsCRUD(
    mode='cards',
    title='',
    syncLocation=False,
    api='/pagermaid/api/get_remote_plugins',
    loadDataOnce=True,
    source='${rows | filter:name:match:keywords_name | filter:des:match:keywords_description}',
    filter={
        'body': [
            InputText(name='keywords_name', label='插件名'),
            InputText(name='keywords_description', label='插件描述')
        ]
    },
    perPage=12,
    autoJumpToTopOnPagerChange=True,
    placeholder='暂无插件信息',
    footerToolbar=['switch-per-page', 'pagination'],
    columnsCount=3,
    card=card
)
page = PageSchema(
    url='/plugins/remote',
    icon='fa fa-cloud-download',
    label='插件仓库',
    schema=Page(title='插件仓库', body=cards_curd)
)
