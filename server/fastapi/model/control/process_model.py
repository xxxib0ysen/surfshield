from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional

# 添加
class AddSingleProcessRequest(BaseModel):
    process_name: str
    status: int = Field(0, ge=0, le=1, description="规则状态，0=禁用，1=启用")

# 删除
class DeleteSingleProcessRequest(BaseModel):
    id: int

# 批量添加
class AddProcessRequest(BaseModel):
    process_list: List[str]
    status: int = Field(0, ge=0, le=1, description="规则状态，0=禁用，1=启用")

# 批量删除
class DeleteProcessRequest(BaseModel):
    ids: List[int]

# 启用/禁用
class ToggleProcessStatusRequest(BaseModel):
    id: int
    status: int = Field(..., ge=0, le=1, description="规则状态，0=禁用，1=启用")

# 响应 获取列表
class ProcessRuleItem(BaseModel):
    id: int
    process_name: str
    status: int
    create_time: str
