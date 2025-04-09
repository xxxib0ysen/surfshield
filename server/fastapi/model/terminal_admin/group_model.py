from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 查询树结构响应模型
class GroupTree(BaseModel):
    group_id: int
    group_name: str
    parent_id: Optional[int]
    description: Optional[str]
    createdon: Optional[datetime]
    children: Optional[List['GroupTree']] = []

    class Config:
        orm_mode = True


# 新增/编辑分组请求模型
class GroupCreateUpdate(BaseModel):
    group_name: str = Field(..., description="分组名称")
    parent_id: Optional[int] = Field(default=0, description="父分组ID，顶级为 0")
    description: Optional[str] = Field(default="", description="备注说明")


# 查询单个分组响应模型
class GroupInfo(BaseModel):
    group_id: int
    group_name: str
    parent_id: Optional[int]
    description: Optional[str]
    createdon: datetime
