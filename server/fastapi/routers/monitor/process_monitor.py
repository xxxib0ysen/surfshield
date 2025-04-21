from fastapi import APIRouter, Query, Depends
from typing import Optional

from model.monitor.process_monitor_model import KillProcessRequest
from service.monitor.process_monitor_service import get_process_from_redis, send_kill_command
from utils.check_perm import check_permission
from utils.log.log_context import log_context_dependency
from utils.response import success_response, error_response
from utils.status_code import HTTP_OK, HTTP_BAD_REQUEST

router = APIRouter()

# 获取进程信息
@router.get("/process_monitor")
def query_process_list(terminal_id: Optional[int] = Query(None, description="终端ID，留空获取全部"),
                       _=Depends(log_context_dependency), _p=Depends(check_permission("process:list"))
):
    return get_process_from_redis(terminal_id)

@router.post("/kill_process", summary="远程终止终端进程")
def kill_process(req: KillProcessRequest, _=Depends(log_context_dependency),
    _p=Depends(check_permission("process:kill"))):
    try:
        success = send_kill_command(req.terminal_id, req.pid)
        if success:
            return success_response(message="终止进程指令已下发", code=HTTP_OK)
        else:
            return error_response(message="指令发送失败或终端不在线", code=HTTP_BAD_REQUEST)
    except Exception as e:
        return error_response(message=f"服务异常：{str(e)}", code=HTTP_BAD_REQUEST)