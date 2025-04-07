from fastapi import APIRouter, Depends
from model.terminal_admin.admin_model import *
from service.terminal_admin import admin_service
from utils.auth import get_current_user

router = APIRouter()

@router.get("/list", summary="分页查询管理员列表")
def get_admin_list(query: AdminListQuery = Depends()):
    return admin_service.get_admin_list(
        page=query.page,
        size=query.size
    )

@router.post("/add", summary="新增管理员")
def add_admin(admin: AdminCreate):
    return admin_service.add_admin(
        admin_name=admin.admin_name,
        role_id=admin.role_id,
        description=admin.description,
        status=admin.status
    )

@router.put("/update/{admin_id}", summary="编辑管理员信息")
def update_admin(admin_id: int, admin: AdminUpdate):
    return admin_service.update_admin(
        admin_id=admin_id,
        role_id=admin.role_id,
        description=admin.description
    )

@router.put("/status/{admin_id}", summary="修改管理员状态")
def change_admin_status(admin_id: int, status: AdminStatusUpdate):
    return admin_service.update_admin_status(
        admin_id=admin_id,
        status=status.status
    )

@router.put("/reset_password/{admin_id}", summary="重置管理员密码")
def reset_password(admin_id: int):
    return admin_service.reset_admin_password(admin_id)

@router.put("/change_password", summary="修改密码")
def change_password(pwd: AdminChangePassword, current_user: dict = Depends(get_current_user)):
    return admin_service.change_password(
        admin_id=current_user["admin_id"],
        old_password=pwd.old_password,
        new_password=pwd.new_password
    )

@router.delete("/delete/{admin_id}", summary="删除管理员")
def delete_admin(admin_id: int):
    return admin_service.delete_admin(admin_id)
