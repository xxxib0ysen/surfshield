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


# 分页返回模型
class OperationLogListPayload(BaseModel):
    total: int
    data: List[OperationLogItem]

class OperationLogListResponse(BaseModel):
    code: int
    message: str
    data: OperationLogListPayload
