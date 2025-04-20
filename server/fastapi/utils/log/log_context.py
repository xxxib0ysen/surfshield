from contextvars import ContextVar
from fastapi import Depends, Request
from utils.auth import get_current_user

# 上下文变量定义
log_context_operator = ContextVar("log_operator", default=None)
log_context_ip = ContextVar("log_ip", default=None)

# 设置上下文
def set_log_context(operator: int, ip_address: str):
    log_context_operator.set(operator)
    log_context_ip.set(ip_address)

# 获取上下文
def get_log_context():
    return {
        "operator": log_context_operator.get(),
        "ip_address": log_context_ip.get()
    }

async def log_context_dependency(request: Request, current_user: dict = Depends(get_current_user)):
    operator = current_user["admin_id"]
    ip_address = request.client.host
    set_log_context(operator, ip_address)