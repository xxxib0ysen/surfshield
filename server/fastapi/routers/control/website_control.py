from fastapi import APIRouter
from typing import List
from model.control.website_model import *
from service.control.website_service import *

router = APIRouter()

# 网站类型管理接口
# -------------

# 获取网站类型列表
@router.get("/type", response_model=List[WebsiteTypeOut])
def list_types():
    return get_website_type()

# 添加网站类型
@router.post("/type/add")
def add_type_api(data: WebsiteTypeCreate):
    return add_type(data)

# 删除网站类型
@router.post("/type/delete")
def delete_type_api(data: WebsiteTypeDelete):
    return delete_website_type(data.type_id)

# 修改网站类型启用/禁用状态
@router.post("/type/updateStatus")
def update_type_status_api(data: WebsiteTypeUpdateStatus):
    return update_type_status(data.type_id, data.status)


# 网站规则管理接口
# -------------

# 获取所有网站规则
@router.get("/list", response_model=List[WebsiteRuleOut])
def list_rules():
    return get_website_rule()

# 获取按网站类型分组的规则
@router.get("/grouped", response_model=WebsiteRuleGroupedResponse)
def list_rules_grouped():
    return get_website_rule_grouped()

# 添加网站规则
@router.post("/add")
def add_rule_api(data: WebsiteRuleCreate):
    return add_website_rule(data)

# 删除网站规则
@router.post("/delete")
def delete_rule_api(data: WebsiteRuleDelete):
    return delete_website_rule(data.website_id)

# 修改网站规则启用/禁用状态
@router.post("/updateStatus")
def update_rule_status_api(data: WebsiteRuleUpdateStatus):
    return update_website_status(data.website_id, data.status)
