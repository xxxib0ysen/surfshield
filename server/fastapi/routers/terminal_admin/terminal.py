from typing import Optional, List

from fastapi import APIRouter, Body, Depends, Query

from model.terminal_admin.terminal_model import TerminalQuery, TerminalMoveGroup, TerminalStatusCount, \
    OSDistributionItem
from service.terminal_admin.terminal_service import get_terminal_list, get_terminal_detail, move_terminal_to_group, \
    get_terminal_columns, get_terminal_status_count, get_terminal_os_distribution

router = APIRouter()

# 查询终端列表
@router.get("/list")
def api_get_terminal_list(query: TerminalQuery = Depends(), group_id: Optional[str] = Query(None)):
    group_ids = [int(i) for i in group_id.split(",")] if group_id else None
    return get_terminal_list(query, group_id)

# 获取终端详情
@router.get("/detail/{terminal_id}")
def api_get_terminal_detail(terminal_id: int):
    return get_terminal_detail(terminal_id)

# 批量移动终端到分组
@router.post("/move_group")
def api_move_terminal_to_group(data: TerminalMoveGroup):
    return move_terminal_to_group(data)

# 自定义列
@router.get("/columns")
def api_get_terminal_columns():
    return get_terminal_columns()

# 获取终端状态统计（在线/离线）
@router.get("/status-count", response_model=TerminalStatusCount)
def get_terminal_status():
    return get_terminal_status_count()

# 获取终端操作系统分布
@router.get("/os-distribution", response_model=List[OSDistributionItem])
def get_terminal_os():
    return get_terminal_os_distribution()
