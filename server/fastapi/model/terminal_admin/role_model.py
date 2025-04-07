from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 角色分页查询 - 请求
class RoleQuery(BaseModel):
    page: int
    page_size: int

# 角色分页查询 - 响应
class RoleInfo(BaseModel):
    role_id: int
    role_name: str
    status: int
    description: Optional[str] = None
    createdon: Optional[datetime] = None

class RoleListResponse(BaseModel):
    total: int
    items: List[RoleInfo]

# 新增角色
class RoleCreate(BaseModel):
    role_name: str
    description: Optional[str] = Field(None, description="说明")
    permissions: List[int] = Field(default=[], description="绑定的权限ID列表")
    status: int = Field(0, ge=0, le=1, description="状态：0禁用 1启用")

# 编辑角色
class RoleUpdate(BaseModel):
    role_id: int
    role_name: str
    description: Optional[str] = Field(None, description="说明")
    permissions: List[int] = Field(default=[], description="绑定的权限ID列表")

# 启用/禁用角色
class RoleStatusUpdate(BaseModel):
    role_id: int
    status: int = Field(..., ge=0, le=1, description="状态：0禁用 1启用")

# 删除角色
class RoleDelete(BaseModel):
    role_id: int
