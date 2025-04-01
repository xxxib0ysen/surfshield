from typing import Any

# 成功响应
def success_response(data: Any = None, message: str = "请求成功", code: int = 200):
    return {
        "code": code,
        "message": message,
        "data": data
    }

# 错误响应
def error_response(message: str = "请求失败", code: int = 400, data: Any = None):
    return {
        "code": code,
        "message": message,
        "data": data
    }
