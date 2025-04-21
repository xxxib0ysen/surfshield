from functools import wraps
from utils.log.log import write_log
from utils.log.log_context import get_log_context
from utils.connect import create_connection

# 通用名称提取器
def get_target_name(table: str, field: str, id_field: str, id_value: int) -> str:
    if not id_value:
        return f"{table}[null]"
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = f"select {field} from {table} where {id_field} = %s"
        cursor.execute(sql, (id_value,))
        row = cursor.fetchone()
        return row[field] if row else f"{table}[{id_value}]"
    except:
        return f"{table}[{id_value}]"

# 操作日志装饰器
def log_operation(module: str, action: str, is_query: bool = False, template: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("日志触发...")
            context = get_log_context()
            operator_id = context.get("operator")
            ip_address = context.get("ip_address", "unknown")
            print(f"操作人ID: {operator_id}, IP地址: {ip_address}")
            detail = {}
            if is_query:
                detail["params"] = {
                    k: (v.dict() if hasattr(v, "dict") else v)
                    for k, v in kwargs.items()
                    if k not in ("operator", "ip_address")
                }
                detail["description"] = f"{module}：查询操作"

            result = func(*args, **kwargs)

            if isinstance(result, dict) and result.get("code") == 200:
                print("结果：", result)
                try:
                    if template:
                        operator_name = get_target_name("sys_admin", "admin_name", "admin_id", operator_id)
                        context_data = {"operator": operator_name}

                        # 支持常用实体名
                        target_map = {
                            "admin": ("sys_admin", "admin_name", "admin_id"),
                            "role": ("sys_role", "role_name", "role_id"),
                            "group": ("sys_group", "group_name", "group_id"),
                            "terminal": ("sys_terminal", "username", "id"),
                        }

                        for key, (table, field, id_field) in target_map.items():
                            if f"{{{key}}}" in template:
                                target_id = kwargs.get(id_field)
                                context_data[key] = get_target_name(table, field, id_field, target_id)

                        if "description" in result.get("data", {}):
                            status_text = result["data"].get("description", "")
                            context_data["status_text"] = status_text
                        if "process_list" in result.get("data", {}):
                            context_data["process_list"] = "、".join(result["data"]["process_list"][:5])
                        if "rule_names" in result.get("data", {}):
                            context_data["rule_names"] = result["data"]["rule_names"]
                        detail["description"] = template.format(**context_data)


                    write_log(
                        admin_id=operator_id,
                        ip_address=ip_address,
                        module=module,
                        action=action,
                        detail=detail
                    )
                except Exception as e:
                    print(f"[日志处理失败] {e}")
            return result
        return wrapper
    return decorator
