from fastapi import APIRouter, Depends, Path

from model.terminal_admin.group_model import GroupCreateUpdate
from service.terminal_admin.group_service import get_group_tree_service, get_group_detail_service, add_group_service, \
    update_group_service, delete_group_service

router = APIRouter()

# 获取分组树结构
@router.get("/tree")
def get_group_tree():
    return get_group_tree_service()

# 获取分组详情
@router.get("/list/{group_id}")
def get_group_detail(group_id: int = Path(..., description="分组ID")):
    return get_group_detail_service(group_id)

# 新增分组
@router.post("/add")
def add_group(group: GroupCreateUpdate):
    return add_group_service(group)

# 编辑分组
@router.put("/edit/{group_id}")
def update_group(group_id: int, group: GroupCreateUpdate):
    return update_group_service(group_id, group)

# 删除分组
@router.delete("/delete/{group_id}")
def delete_group(group_id: int):
    return delete_group_service(group_id)
