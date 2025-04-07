from fastapi import APIRouter, Depends
from model.terminal_admin.role_model import *
from service.terminal_admin import role_service

router = APIRouter()

# 查询角色分页列表
@router.get("/list")
def get_role_list(page: int = 1, size: int = 6):
    return role_service.get_role_list(page, size)

# 新增角色
@router.post("/add")
def add_role(data: RoleCreate):
    return role_service.add_role(
        role_name=data.role_name,
        description=data.description,
        permissions=data.permissions
    )

# 编辑角色
@router.post("/update")
def update_role(data: RoleUpdate):
    return role_service.update_role(
        role_id=data.role_id,
        role_name=data.role_name,
        description=data.description,
        permissions=data.permissions
    )

# 修改角色状态
@router.post("/status")
def update_role_status(data: RoleStatusUpdate):
    return role_service.update_role_status(
        role_id=data.role_id,
        status=data.status
    )

# 删除角色
@router.post("/delete")
def delete_role(data: RoleDelete):
    return role_service.delete_role(data.role_id)
