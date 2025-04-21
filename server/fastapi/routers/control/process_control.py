from fastapi import APIRouter, Depends
from model.control.process_model import *
from service.control.process_service import *
from utils.auth import get_current_user
from utils.check_perm import check_permission
from utils.log.log_context import log_context_dependency

router = APIRouter()

# 添加单个
@router.post("/add_single")
async def add_single(req: AddSingleProcessRequest, _=Depends(log_context_dependency),
    _p=Depends(check_permission("process_rule:add"))):
    return add_single_process(req.process_name, status=req.status)

# 批量添加
@router.post("/add_batch")
async def add_batch(req: AddProcessRequest, _=Depends(log_context_dependency),
    _p=Depends(check_permission("process_rule:add"))):
    return add_batch_process(req.process_list, status=req.status)

# 删除单个
@router.post("/delete_single")
async def delete_single(req: DeleteSingleProcessRequest, _=Depends(log_context_dependency),
    _p=Depends(check_permission("process_rule:delete"))):
    return delete_single_process(req.id)

# 批量删除
@router.post("/delete_batch")
async def delete_batch(req: DeleteProcessRequest, _=Depends(log_context_dependency),
    _p=Depends(check_permission("process_rule:delete"))):
    return delete_batch_process(req.ids)

# 启用/禁用
@router.post("/toggle")
async def toggle_status(req: ToggleProcessStatusRequest, _=Depends(log_context_dependency),
    _p=Depends(check_permission("process_rule:toggle"))):
    return toggle_process_status(req.id, req.status)

# 获取全部规则列表
@router.get("/list")
async def list_rules(_=Depends(log_context_dependency),
    _p=Depends(check_permission("process_rule:list"))):
    return get_process_list()
