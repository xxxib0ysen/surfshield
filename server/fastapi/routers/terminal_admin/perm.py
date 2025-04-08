from fastapi import APIRouter

from model.terminal_admin.perm_model import RolePermissionUpdate
from service.terminal_admin.perm_service import get_all_permissions, get_permission_ids_by_role, \
    update_role_permissions, get_permissions_grouped_by_module

router = APIRouter()


# 获取权限列表
@router.get("/list")
def permission_list():
    return get_all_permissions()

# 模块分组的权限列表
@router.get("/grouped")
def get_grouped_permissions():
    return get_permissions_grouped_by_module()


# 获取指定角色绑定的权限
@router.get("/role/{role_id}")
def role_permission_list(role_id: int):
    return get_permission_ids_by_role(role_id)

# 绑定权限到角色
@router.post("/bind")
def bind_permissions(data: RolePermissionUpdate):
    return update_role_permissions(data.role_id, data.perm_ids)
