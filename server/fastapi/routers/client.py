from fastapi import APIRouter, Depends

from model.terminal_admin.terminal_model import TerminalRegisterRequest, TerminalStatusUpdate
from service.control.process_service import get_process_list
from service.control.website_service import get_rules_grouped_by_type
from service.terminal_admin.terminal_service import register_terminal, update_terminal_status

router = APIRouter()

# 终端注册接口
@router.post("/register")
def api_register_terminal(data: TerminalRegisterRequest):
    return register_terminal(data)

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