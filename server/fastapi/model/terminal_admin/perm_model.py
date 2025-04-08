from pydantic import BaseModel
from typing import List, Optional

# 权限项模型
class PermissionItem(BaseModel):
    perm_id: int
    perm_code: str
    perm_name: str
    module: str
    description: Optional[str] = None

# 保存角色权限请求模型
class RolePermissionUpdate(BaseModel):
    role_id: int
    perm_ids: List[int]

class PermissionListResponse(BaseModel):
    code: int
    message: str
    data: List[PermissionItem]
