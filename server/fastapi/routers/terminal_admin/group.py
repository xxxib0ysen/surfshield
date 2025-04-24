from fastapi import APIRouter, Depends, Path

from model.terminal_admin.group_model import GroupCreateUpdate, InviteCreate, InviteUpdate
from service.terminal_admin.group_service import get_group_tree_service, get_group_detail_service, add_group_service, \
    update_group_service, delete_group_service, get_group_with_user_tree_service, add_invite_service, \
    get_invite_list_service, update_invite_service, delete_invite_service
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

@router.get("/invite/list", summary="获取邀请码列表", dependencies=[Depends(check_permission("group:invite:list"))])
def get_invite_list():
    return get_invite_list_service()


@router.post("/invite/add", summary="新增邀请码", dependencies=[Depends(check_permission("group:invite:add"))])
def add_invite(data: InviteCreate):
    return add_invite_service(data)


@router.put("/invite/edit/{id}", summary="编辑邀请码", dependencies=[Depends(check_permission("group:invite:edit"))])
def edit_invite(id: int, data: InviteUpdate):
    return update_invite_service(id, data)


@router.delete("/invite/delete/{id}", summary="删除邀请码", dependencies=[Depends(check_permission("group:invite:delete"))])
def delete_invite(id: int):
    return delete_invite_service(id)