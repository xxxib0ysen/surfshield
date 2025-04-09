from fastapi import APIRouter, Depends

from model.terminal_admin.terminal_model import TerminalQuery, TerminalMoveGroup
from service.terminal_admin.terminal_service import get_terminal_list, get_terminal_detail, move_terminal_to_group

router = APIRouter()

# 分页查询终端列表
@router.get("/list")
def api_get_terminal_list(query: TerminalQuery = Depends(),):
    return get_terminal_list(query)

# 获取终端详情
@router.get("/detail/{terminal_id}")
def api_get_terminal_detail(terminal_id: int):
    return get_terminal_detail(terminal_id)

# 批量移动终端到分组
@router.post("/move_group")
def api_move_terminal_to_group(data: TerminalMoveGroup):
    return move_terminal_to_group(data)


