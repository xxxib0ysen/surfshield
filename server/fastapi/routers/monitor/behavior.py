from typing import Optional, List

from fastapi import APIRouter, Query, Depends

from service.monitor.behavior_service import get_web_behavior_service, get_search_behavior_service, get_online_username
from utils.check_perm import check_permission
from utils.connect import redis_client
from utils.log.log_context import log_context_dependency
from utils.response import success_response, error_response

import json

router = APIRouter()

# 获取网页访问记录
@router.get("/web")
def get_web_behavior(username: Optional[str] = Query(None), _=Depends(log_context_dependency),
    _p=Depends(check_permission("behavior:web"))):
    try:
        data = get_web_behavior_service(username)
        return success_response(data=data)
    except Exception as e:
        return error_response(f"获取网页访问记录失败：{e}")

# 获取搜索关键词记录
@router.get("/search")
def get_search_behavior(username: Optional[str] = Query(None), _=Depends(log_context_dependency),
    _p=Depends(check_permission("behavior:search"))):
    try:
        data = get_search_behavior_service(username)
        return success_response(data=data)
    except Exception as e:
        return error_response(f"获取搜索行为失败：{e}")


# 获取所有在线终端用户
@router.get("/userlist")
def get_user_list():
    try:
        data = get_online_username()
        return success_response(data=data)
    except Exception as e:
        return error_response(f"获取在线终端用户失败：{e}")