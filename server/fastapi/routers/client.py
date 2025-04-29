from fastapi import APIRouter, Depends

from model.monitor.process_monitor_model import ProcessReport, KillProcessRequest
from model.terminal_admin.terminal_model import TerminalRegisterRequest, TerminalStatusUpdate, TerminalUpdateRequest
from service.control.process_service import get_process_list
from service.control.website_service import get_rules_grouped_by_type
from service.monitor.process_monitor_service import save_process_to_redis, send_kill_command
from service.terminal_admin.terminal_service import register_terminal, update_terminal_status, update_terminal_info
from utils.response import success_response, error_response
from utils.status_code import HTTP_OK, HTTP_BAD_REQUEST

router = APIRouter()

# 终端注册接口
@router.post("/register")
def api_register_terminal(data: TerminalRegisterRequest):
    if not data.uuid or data.uuid.strip() == "":
        return error_response(
            code=HTTP_BAD_REQUEST,
            message="缺少终端唯一标识符 uuid"
        )
    return register_terminal(data)

# 终端信息更新接口
@router.post("/update")
def api_update_terminal(data: TerminalUpdateRequest):
    return update_terminal_info(data)

@router.post("/status")
def api_terminal_status(data: TerminalStatusUpdate):
    return update_terminal_status(data.terminal_id, data.status)

# 获取进程全部规则列表
@router.get("/process/list")
async def list_rules():
    return get_process_list()

# 网站拦截：获取所有规则，按类型分组
@router.get("/website_control/listGrouped")
def list_grouped_rules():
    return get_rules_grouped_by_type()

# 客户端上报进程数据
@router.post("/process-report")
def report_process(data: ProcessReport):
    return save_process_to_redis(data.terminal_id, [item.dict() for item in data.process_list])

