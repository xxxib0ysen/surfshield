from fastapi import APIRouter, Depends, Path

from model.terminal_admin.group_model import GroupCreateUpdate
from service.terminal_admin.group_service import get_group_tree_service, get_group_detail_service, add_group_service, \
    update_group_service, delete_group_service, get_group_with_user_tree_service
from utils.check_perm import check_permission
from utils.log.log_context import log_context_dependency

router = APIRouter()

# 获取分组树结构
@router.get("/tree")
def get_group_tree(_=Depends(log_context_dependency), _p=Depends(check_permission("group:tree"))):
    return get_group_tree_service()

# 获取分组详情
@router.get("/list/{group_id}")
def get_group_detail(group_id: int = Path(..., description="分组ID"), _p=Depends(check_permission("group:detail"))):
    return get_group_detail_service(group_id)

# 新增分组
@router.post("/add")
def add_group(group: GroupCreateUpdate, _=Depends(log_context_dependency),
    _p=Depends(check_permission("group:add"))):
    return add_group_service(group)

# 编辑分组
@router.put("/edit/{group_id}")
def update_group(group_id: int, group: GroupCreateUpdate,_=Depends(log_context_dependency),
    _p=Depends(check_permission("group:edit"))):
    return update_group_service(group_id, group)

# 删除分组
@router.delete("/delete/{group_id}")
def delete_group(group_id: int, _=Depends(log_context_dependency),
    _p=Depends(check_permission("group:delete"))):
    return delete_group_service(group_id)

@router.get("/user-tree")
def get_group_with_user_tree(_=Depends(log_context_dependency)):
    return get_group_with_user_tree_service()
