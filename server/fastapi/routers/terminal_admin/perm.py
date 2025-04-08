from fastapi import APIRouter, Depends

from model.terminal_admin.perm_model import RolePermissionUpdate
from service.terminal_admin.perm_service import get_all_permissions, get_permission_ids_by_role, \
    update_role_permissions, get_permissions_grouped_by_module
from utils.check_perm import check_permission

router = APIRouter()


# 获取权限列表
@router.get("/list")
def permission_list(_=Depends(check_permission("permission:list"))):
    return get_all_permissions()

# 获取某角色的权限 ID 列表
@router.get("/role/{role_id}")
def role_permission_list(role_id: int, _=Depends(check_permission("role:list"))):
    return get_permission_ids_by_role(role_id)

# 模块分组的权限列表
@router.get("/grouped")
def get_grouped_permissions(_=Depends(check_permission("permission:list"))):
    return get_permissions_grouped_by_module()

# 绑定权限到角色
@router.post("/bind")
def bind_permissions(data: RolePermissionUpdate,_=Depends(check_permission("role:bind_permission"))):
    return update_role_permissions(data.role_id, data.perm_ids)
