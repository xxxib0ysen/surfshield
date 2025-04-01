from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# 添加网站类型
class WebsiteTypeAddRequest(BaseModel):
    type_name: str = Field(..., description="网站类型名称")
    status: Optional[int] = Field(0, description="类型启用状态，默认禁用")

# 删除网站类型
class WebsiteTypeDeleteRequest(BaseModel):
    type_id: int

# 修改网站类型状态
class WebsiteTypeUpdateStatusRequest(BaseModel):
    type_id: int
    status: int

# 添加网站规则
class WebsiteRuleAddRequest(BaseModel):
    website_url: str
    type_id: int
    status: Optional[int] = Field(0, description="规则状态，默认禁用")

# 删除网站规则
class WebsiteRuleDeleteRequest(BaseModel):
    website_id: int

# 启用/禁用规则
class WebsiteRuleUpdateStatusRequest(BaseModel):
    website_id: int
    status: int

# 网站类型响应
class WebsiteTypeResponse(BaseModel):
    type_id: int
    type_name: str
    status: int
    createdon: datetime
    last_modified: Optional[datetime]

# 网站规则响应
class WebsiteRuleResponse(BaseModel):
    website_id: int
    website_url: str
    type_name: str
    status: int
    createdon: datetime

# 单条规则项
class WebsiteRuleItem(BaseModel):
    website_id: int
    website_url: str
    status: int
    createdon: datetime

# 分组响应
class WebsiteRuleGroupByType(BaseModel):
    type_id: int
    type_name: str
    type_status: int
    rules: List[WebsiteRuleItem]
