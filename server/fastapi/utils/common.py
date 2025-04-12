import re
from datetime import datetime
import hashlib
from fastapi import Request

from utils.connect import create_connection


# 验证请求参数是否完整
def validate_params(required_params: list, data: dict):
    missing = [param for param in required_params if param not in data]
    return missing


# 密码哈希加密
def hash_pwd(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# 分页辅助函数
def paginate_query(page: int, page_size: int):
    page = max(1, page)
    page_size = min(100, max(1, page_size))
    offset = (page - 1) * page_size
    return offset, page_size

# 格式化时间
def format_time_fields(obj: dict, fields: list[str]) -> dict:
    for key in fields:
        if key in obj and isinstance(obj[key], datetime):
            obj[key] = obj[key].strftime('%Y-%m-%d %H:%M:%S')
    return obj
def format_time_in_rows(rows: list[dict], fields: list[str]) -> list[dict]:
    return [format_time_fields(row, fields) for row in rows]


# 验证 URL 是否符合格式（支持通配符）
def validate_url(url: str) -> bool:
    domain_regex = r'^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'
    return re.fullmatch(domain_regex, url) is not None

import re

# 校验是否为合法进程关键词（进程名或关键词）
def is_valid_process_keyword(name: str) -> bool:
    # 排除完整路径（如 C:\xxx\xxx.exe 或 /usr/bin/xxx）
    if "\\" in name or "/" in name or re.match(r"^[a-zA-Z]:\\", name):
        return False
    if not re.fullmatch(r"[a-zA-Z0-9_\-\.]+", name):
        return False
    return True


# 获取客户端 IP
def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.client.host
