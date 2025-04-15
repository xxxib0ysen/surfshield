from pydantic import BaseModel, Field
from typing import List, Optional

# 单条进程数据模型
class ProcessItem(BaseModel):
    username: str
    process_name: str
    pid: int
    status: int
    is_network: int
    remote_ip: Optional[str] = ""
    remote_port: Optional[int] = 0
    network_status: Optional[str] = ""
    description: Optional[str] = ""
    start_time: str
    update_time: str

# 请求模型
class ProcessReport(BaseModel):
    terminal_id: int
    process_list: List[ProcessItem]

class ProcessInfo(BaseModel):
    terminal_id: int
    username: str
    process_name: str
    pid: int
    status: int
    is_network: int
    remote_ip: Optional[str] = ""
    remote_port: Optional[int] = 0
    network_status: Optional[str] = ""
    description: Optional[str] = ""
    start_time: str
    update_time: str

class KillProcessRequest(BaseModel):
    terminal_id: int = Field(..., description="终端 ID")
    pid: int = Field(..., description="进程 PID")