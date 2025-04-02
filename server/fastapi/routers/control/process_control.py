from fastapi import APIRouter
from model.control.process_model import *
from service.control.process_service import *

router = APIRouter()

# 添加单个
@router.post("/add_single")
async def add_single(req: AddSingleProcessRequest):
    return add_single_process(req.process_name)

# 批量添加
@router.post("/add_batch")
async def add_batch(req: AddProcessRequest):
    return add_batch_process(req.process_list)

# 删除单个
@router.post("/delete_single")
async def delete_single(req: DeleteSingleProcessRequest):
    return delete_single_process(req.id)

# 批量删除
@router.post("/delete_batch")
async def delete_batch(req: DeleteProcessRequest):
    return delete_batch_process(req.ids)

# 启用/禁用
@router.post("/toggle")
async def toggle_status(req: ToggleProcessStatusRequest):
    return toggle_process_status(req.id, req.status)

# 获取全部规则列表
@router.get("/list")
async def list_rules():
    return get_process_list()
