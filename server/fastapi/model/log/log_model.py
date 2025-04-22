from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# 分页查询参数模型
class OperationLogQuery(BaseModel):
    page: int = Field(1, description="页码")
    page_size: int = Field(6, description="每页条数")
    admin_name: Optional[str] = None
    module: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class BehaviorLogQuery(BaseModel):
    page: int = Field(1)
    page_size: int = Field(10)
    username: Optional[str] = None
    behavior_type: Optional[str] = None
    group_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    group_ids: Optional[List[int]] = None

# 日志记录单条返回模型
class OperationLogItem(BaseModel):
    id: int
    created_at: str
    admin_id: int
    admin_name: Optional[str] = None
    ip_address: str
    module: str
    action: str
    detail: str

class BehaviorLogItem(BaseModel):
    id: int
    event_time: str
    username: Optional[str] = None
    ip_address: str
    behavior_type: str
    detail: str

# 分页返回模型
class OperationLogListPayload(BaseModel):
    total: int
    data: List[OperationLogItem]

class OperationLogListResponse(BaseModel):
    code: int
    message: str
    data: OperationLogListPayload

class BehaviorLogListPayload(BaseModel):
    total: int  # 总条数
    list: List[BehaviorLogItem]
