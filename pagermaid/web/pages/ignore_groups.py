from amis import (
    InputText,
    Switch,
    Card,
    CardsCRUD,
    PageSchema,
    Page,
)

card = Card(
    header=Card.Header(
        title="$title",
        description="$id",
        avatarText="$title",
        avatarTextClassName="overflow-hidden",
    ),
    actions=[],
    toolbar=[
        Switch(
            name="enable",
            value="${status}",
            onText="已忽略",
            offText="未忽略",
            onEvent={
                "change": {
                    "actions": [
                        {
                            "actionType": "ajax",
                            "args": {
                                "api": {
                                    "url": "/pagermaid/api/set_ignore_group_status",
                                    "method": "post",
                                    "dataType": "json",
                                    "data": {
                                        "id": "${id}",
                                        "status": "${IF(event.data.value, 1, 0)}",
                                    },
                                },
                                "onSuccess": {
                                    "type": "tpl",
                                    "tpl": "${payload.msg}",  # 使用返回的 msg 字段作为成功消息
                                },
                                "onError": {
                                    "type": "tpl",
                                    "tpl": "操作失败",
                                },
                                "status": "${event.data.value}",
                                "id": "${id}",
                            },
                        },
                    ]
                }
            },
        )
    ],
)
cards_curd = CardsCRUD(
    mode="cards",
    title="",
    syncLocation=False,
    api="/pagermaid/api/get_ignore_group_list",
    loadDataOnce=True,
    source="${groups | filter:title:match:keywords_name}",
    filter={"body": [InputText(name="keywords_name", label="群组名")]},
    perPage=12,
    autoJumpToTopOnPagerChange=True,
    placeholder="群组列表为空",
    footerToolbar=["switch-per-page", "pagination"],
    columnsCount=3,
    card=card,
)
page = PageSchema(
    url="/bot_config/ignore_groups",
    icon="fa fa-ban",
    label="忽略群组",
    schema=Page(
        title="忽略群组",
        subTitle="忽略后，Bot 不再响应指定群组的消息（群组列表将会缓存一小时）",
        body=cards_curd,
    ),
)
