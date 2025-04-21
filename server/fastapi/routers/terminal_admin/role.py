from fastapi import APIRouter, Depends
from model.terminal_admin.role_model import *
from service.terminal_admin import role_service
from utils.check_perm import check_permission
from utils.log.log_context import log_context_dependency

router = APIRouter()

# 获取所有角色列表
@router.get("/list")
def get_all_roles(_=Depends(log_context_dependency),
    _p=Depends(check_permission("role:list"))):
    return role_service.get_all_roles()

# 单个角色详情
@router.get("/detail")
def get_role_detail(role_id: int, _=Depends(log_context_dependency),
    _p=Depends(check_permission("role:list"))):
    return role_service.get_role_detail(role_id=role_id)

# 新增角色
@router.post("/add")
def add_role(data: RoleCreate, _=Depends(log_context_dependency),
    _p=Depends(check_permission("role:add"))):
    return role_service.add_role(
        role_name=data.role_name,
        description=data.description,
        status=data.status,
        permissions=data.permissions
    )

# 编辑角色
@router.post("/update")
def update_role(data: RoleUpdate, _=Depends(log_context_dependency),
    _p=Depends(check_permission("role:edit"))):
    return role_service.update_role(
        role_id=data.role_id,
        role_name=data.role_name,
        description=data.description,
        permissions=data.permissions
    )

# 修改角色状态
@router.post("/status")
def update_role_status(data: RoleStatusUpdate, _=Depends(log_context_dependency),
    _p=Depends(check_permission("role:disable"))):
    return role_service.update_role_status(
        role_id=data.role_id,
        status=data.status
    )

# 删除角色
@router.post("/delete")
def delete_role(data: RoleDelete, _=Depends(log_context_dependency),
    _p=Depends(check_permission("role:delete"))):
    return role_service.delete_role(data.role_id)
