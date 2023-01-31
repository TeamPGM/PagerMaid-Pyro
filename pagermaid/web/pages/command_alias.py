from amis import Form, InputSubForm, InputText, Static, Alert, PageSchema, Page

main_form = Form(
    title='命令别名',
    initApi='get:/pagermaid/api/command_alias',
    api='post:/pagermaid/api/command_alias',
    submitText='保存',
    body=[
        InputSubForm(
            name='items',
            label='已设置的命令别名',
            multiple=True,
            btnLabel='${alias} >> ${command}',
            draggable=True,
            addable=True,
            removable=True,
            addButtonText='添加命令别名',
            showErrorMsg=False,
            form=Form(
                title='命令别名',
                body=[
                    InputText(name='alias', label='命令别名', required=True),
                    InputText(name='command', label='原命令', required=True),
                ]
            )
        )
    ]
)

test_form = Form(
    title='测试',
    api='get:/pagermaid/api/test_command_alias?message=${message}',
    submitText='测试',
    body=[
        InputText(name='message', label='测试消息（无需输入逗号前缀）', required=True),
        Static(className='text-red-600', name='new_msg', label='命令别名修改后消息',
               visibleOn="typeof data.new_msg !== 'undefined'")
    ]
)

tips = Alert(level='info')

page = PageSchema(
    url='/bot_config/command_alias',
    icon='fa fa-link', label='命令别名',
    schema=Page(
        title='',
        body=[tips, main_form, test_form]
    )
)
