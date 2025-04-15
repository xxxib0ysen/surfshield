from fastapi import APIRouter, Query
from typing import Optional
from service.monitor.process_monitor_service import get_process_from_redis

router = APIRouter()

# 获取进程信息
@router.get("/process_monitor")
def query_process_list(terminal_id: Optional[int] = Query(None, description="终端ID，留空获取全部")):
    return get_process_from_redis(terminal_id)
