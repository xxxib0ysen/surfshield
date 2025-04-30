from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 查询请求
class TerminalQuery(BaseModel):
    username: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    uuid: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    status: Optional[int] = None  # 1在线，0离线
    fuzzy: Optional[bool] = True
    page: int = 1
    page_size: int = 6

# 批量移动分组请求模型
class TerminalMoveGroup(BaseModel):
    ids: List[int] = Field(..., description="终端ID列表")
    group_id: int = Field(..., description="目标分组ID")

# 注册请求
class TerminalRegisterRequest(BaseModel):
    group_code: str
    username: str
    hostname: str
    uuid: str
    ip_address: str
    local_ip: str
    mac_address: str
    os_name: str
    os_version: str
    install_time: str
    is_64bit: int
# 检查注册请求模型
class TerminalCheckRequest(BaseModel):
    uuid: str

# 更新
class TerminalUpdateRequest(BaseModel):
    username: str
    hostname: str
    uuid: str
    ip_address: str
    local_ip: str
    mac_address: str
    os_name: str
    os_version: str
    install_time: str
    is_64bit: int

class TerminalStatusUpdate(BaseModel):
    terminal_id: int
    status: int  # 1=在线，0=离线


# 终端响应模型
class TerminalOut(BaseModel):
    id: int
    username: str
    hostname: str
    uuid: str
    ip_address: str
    local_ip: str
    mac_address: str
    os_name: str
    os_version: str
    is_64bit: int
    install_time: datetime
    status: int
    createdon: datetime
    last_login: Optional[datetime] = None
    group_id: int
    group_name: str
    group_path: str

    class Config:
        from_attributes = True
        populate_by_name = True

# 分页响应模型
class TerminalPageOut(BaseModel):
    total: int
    data: List[TerminalOut]


# 终端在线/离线数量响应
class TerminalStatusCount(BaseModel):
    online: int
    offline: int

# 操作系统分布项
class OSDistributionItem(BaseModel):
    name: str
    count: int

# 操作系统分布响应列表
class OSDistributionOut(BaseModel):
    data: List[OSDistributionItem]
