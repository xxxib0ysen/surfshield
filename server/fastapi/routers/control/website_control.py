from fastapi import APIRouter, Depends
from model.control.website_model import *
from service.control.website_service import*
from utils.auth import get_current_user

router = APIRouter()

# 获取所有网站类型
@router.get("/type")
def list_website_types(current_user: dict=Depends(get_current_user)):
    return get_website_type()

# 添加网站类型
@router.post("/type/add")
def create_website_type(body: WebsiteTypeAddRequest, current_user: dict=Depends(get_current_user)):
    return add_type(body)

# 删除网站类型
@router.post("/type/delete")
def remove_website_type(body: WebsiteTypeDeleteRequest, current_user: dict=Depends(get_current_user)):
    return delete_website_type(body.type_id)

# 修改网站类型状态
@router.post("/type/updateStatus")
def change_type_status(body: WebsiteTypeUpdateStatusRequest, current_user: dict=Depends(get_current_user)):
    return update_type_status(body.type_id, body.status)

# 添加网站规则（支持多个）
@router.post("/add")
def create_website_rule(body: WebsiteRuleAddRequest, current_user: dict=Depends(get_current_user)):
    return add_website_rule(body)

# 删除网站规则
@router.post("/delete")
def remove_website_rule(body: WebsiteRuleDeleteRequest, current_user: dict=Depends(get_current_user)):
    return delete_website_rule(body.website_id)

# 修改规则启用状态
@router.post("/updateStatus")
def change_rule_status(body: WebsiteRuleUpdateStatusRequest, current_user: dict=Depends(get_current_user)):
    return update_website_status(body.website_id, body.status)

# 获取所有规则，按类型分组
@router.get("/listGrouped")
def list_grouped_rules(current_user: dict=Depends(get_current_user)):
    return get_rules_grouped_by_type()