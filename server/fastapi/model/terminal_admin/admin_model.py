from pydantic import BaseModel
from typing import Optional, List

class AdminBase(BaseModel):
    admin_name: str
    role_id: int
    description: Optional[str]

# 创建管理员
class AdminCreate(AdminBase):
    status: int = 0  # 默认禁用

# 编辑管理员
class AdminUpdate(BaseModel):
    role_id: int
    description: Optional[str]

# 修改启用状态
class AdminStatusUpdate(BaseModel):
    status: int  # 0-禁用, 1-启用

# 修改密码
class AdminChangePassword(BaseModel):
    old_password: str
    new_password: str

# 查询参数模型
class AdminListQuery(BaseModel):
    page: int = 1
    size: int = 6

# 管理员信息响应模型
class AdminInfo(BaseModel):
    admin_id: int
    admin_name: str
    role_id: int
    description: Optional[str]
    status: int
    createdon: str

# 分页返回列表
class AdminListResponse(BaseModel):
    total: int
    data: List[AdminInfo]
