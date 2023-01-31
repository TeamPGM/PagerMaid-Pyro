from amis import Page, PageSchema, Html, Property, Service, Flex, ActionType, LevelEnum, Divider, Log, Alert, Form, \
    Dialog, Select, Group, InputText, DisplayModeEnum, Horizontal

from pagermaid.config import Config
from pagermaid.web.html import get_logo

logo = Html(html=get_logo())
select_log_num = Select(
    label='日志数量',
    name='log_num',
    value=100,
    options=[
        {
            'label': 100,
            'value': 100
        },
        {
            'label': 200,
            'value': 200
        },
        {
            'label': 300,
            'value': 300
        },
        {
            'label': 400,
            'value': 400
        },
        {
            'label': 500,
            'value': 500
        }
    ]
)

log_page = Log(
    autoScroll=True,
    placeholder='暂无日志数据...',
    operation=['stop', 'showLineNumber', 'filter'],
    source={
        'method': 'get',
        'url': '/pagermaid/api/log?num=${log_num | raw}',
        'headers': {
            'token': Config.WEB_SECRET_KEY
        }
    }
)

cmd_input = Form(
    mode=DisplayModeEnum.horizontal,
    horizontal=Horizontal(left=0),
    wrapWithPanel=False,
    body=[
        InputText(name='command', required=True, clearable=True, addOn=ActionType.Dialog(
            label='执行',
            level=LevelEnum.primary,
            dialog=Dialog(
                title='命令执行结果',
                size='xl',
                body=Log(
                    autoScroll=True,
                    placeholder='执行命令中，请稍候...',
                    operation=['stop', 'showLineNumber', 'filter'],
                    source={
                        'method': 'get',
                        'url': '/pagermaid/api/run_sh?cmd=${command | raw}',
                        'headers': {
                            'token': Config.WEB_SECRET_KEY
                        }
                    }),
            )
        ))
    ]
)
eval_input = Form(
    mode=DisplayModeEnum.horizontal,
    horizontal=Horizontal(left=0),
    wrapWithPanel=False,
    body=[
        InputText(name='command', required=True, clearable=True, addOn=ActionType.Dialog(
            label='执行',
            level=LevelEnum.primary,
            dialog=Dialog(
                title='命令执行结果',
                size='xl',
                body=Log(
                    autoScroll=True,
                    placeholder='执行命令中，请稍候...',
                    operation=['stop', 'showLineNumber', 'filter'],
                    source={
                        'method': 'get',
                        'url': '/pagermaid/api/run_eval?cmd=${command | raw}',
                        'headers': {
                            'token': Config.WEB_SECRET_KEY
                        }
                    }),
            )
        ))
    ]
)

operation_button = Flex(justify='center', items=[
    ActionType.Ajax(
        label='更新',
        api='/pagermaid/api/bot_update',
        confirmText='该操作会更新 PagerMaid-Pyro ，请在更新完成后手动重启，请确认执行该操作',
        level=LevelEnum.info
    ),
    ActionType.Ajax(
        label='重启',
        className='m-l',
        api='/pagermaid/api/bot_restart',
        confirmText='该操作会重启 PagerMaid-Pyro ，请耐心等待重启',
        level=LevelEnum.danger
    ),
    ActionType.Dialog(
        label='日志',
        className='m-l',
        level=LevelEnum.primary,
        dialog=Dialog(title='查看日志',
                      size='xl',
                      actions=[],
                      body=[
                          Alert(level=LevelEnum.info,
                                body='查看最近最多500条日志，不会自动刷新，需要手动点击两次"暂停键"来进行刷新。'),
                          Form(
                              body=[Group(body=[select_log_num]), log_page]
                          )])
    ),
    ActionType.Dialog(
        label='shell',
        className='m-l',
        level=LevelEnum.warning,
        dialog=Dialog(title='shell',
                      size='lg',
                      actions=[],
                      body=[cmd_input])
    ),
    ActionType.Dialog(
        label='eval',
        className='m-l',
        level=LevelEnum.warning,
        dialog=Dialog(title='eval',
                      size='lg',
                      actions=[],
                      body=[eval_input])
    )
])

status = Service(
    api='/pagermaid/api/status',
    body=Property(
        title='运行信息',
        column=2,
        items=[
            Property.Item(
                label='Bot 运行时间',
                content='${run_time}'
            ),
            Property.Item(
                label='CPU占用率',
                content='${cpu_percent}'
            ),
            Property.Item(
                label='RAM占用率',
                content='${ram_percent}'
            ),
            Property.Item(
                label='SWAP占用率',
                content='${swap_percent}',
                span=2
            ),
        ]
    )
)

page_detail = Page(title='', body=[logo, operation_button, Divider(), status])
page = PageSchema(url='/home', label='首页', icon='fa fa-home', isDefaultPage=True, schema=page_detail)
