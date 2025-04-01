from pydantic import BaseModel, Field, constr
from typing import Optional, Dict, List
from datetime import datetime

# 请求模型
# -------

# 添加网站类型
class WebsiteTypeCreate(BaseModel):
    type_name: constr(strip_whitespace=True, min_length=1, max_length=50) = Field(..., description="网站类型名称")
    status: Optional[int] = Field(0, ge=0, le=1, description="类型状态，默认禁用")

# 更新网站类型启用状态
class WebsiteTypeUpdateStatus(BaseModel):
    type_id: int
    status: int = Field(..., ge=0, le=1, description="类型状态（0=禁用，1=启用）")

# 删除网站类型
class WebsiteTypeDelete(BaseModel):
    type_id: int

# 添加网站规则（支持批量）
class WebsiteRuleCreate(BaseModel):
    website_url: constr(strip_whitespace=True, min_length=1, max_length=1000) = Field(...,
                                                                                      description="支持多个网址，换行分隔")
    type_id: int
    status: Optional[int] = Field(0, ge=0, le=1, description="规则状态，默认禁用")

# 删除某条规则
class WebsiteRuleDelete(BaseModel):
    website_id: int

# 更新某条规则的启用状态
class WebsiteRuleUpdateStatus(BaseModel):
    website_id: int
    status: int = Field(..., ge=0, le=1, description="0=禁用，1=启用")


# 响应模型
# -------

# 获取网站类型
class WebsiteTypeOut(BaseModel):
    type_id: int
    type_name: str
    status: int
    createdon: datetime
    last_modified: Optional[datetime] = None

# 获取网站规则
class WebsiteRuleOut(BaseModel):
    website_id: int
    website_url: str
    type_name: str
    status: int
    createdon: datetime

# 分组响应结构：{ type_name: [WebsiteRuleOut, ...] }
class WebsiteRuleGroupedResponse(BaseModel):
    __root__: Dict[str, List[WebsiteRuleOut]]