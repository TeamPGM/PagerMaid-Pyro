from fastapi import APIRouter
from starlette.responses import JSONResponse

from pagermaid.common.ignore import ignore_groups_manager, get_group_list
from pagermaid.web.api import authentication

route = APIRouter()


@route.get("/get_ignore_group_list", response_class=JSONResponse, dependencies=[authentication()])
async def get_ignore_group_list():
    try:
        groups = []
        for data in await get_group_list():
            data["status"] = ignore_groups_manager.check_id(data["id"])
            groups.append(data)
        return {
            'status': 0,
            'msg':    'ok',
            'data':   {
                'groups': groups
            }
        }
    except BaseException:
        return {
            'status': -100,
            'msg':    '获取群组列表失败'
        }


@route.post('/set_ignore_group_status', response_class=JSONResponse, dependencies=[authentication()])
async def set_ignore_group_status(data: dict):
    cid: int = data.get('id')
    status: bool = data.get('status')
    if status:
        ignore_groups_manager.add_id(cid)
    else:
        ignore_groups_manager.del_id(cid)
    return {'status': 0, 'msg': f'成功{"忽略" if status else "取消忽略"} {cid}'}


@route.post('/clear_ignore_group', response_class=JSONResponse, dependencies=[authentication()])
async def clear_ignore_group():
    ignore_groups_manager.clear_subs()
    return {'status': 0, 'msg': '成功清空忽略列表'}
