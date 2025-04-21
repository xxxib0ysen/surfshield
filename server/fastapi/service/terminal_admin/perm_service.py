from utils.connect import create_connection
from utils.log.log_decorator import log_operation
from utils.response import success_response, error_response
from utils.status_code import *


# 查询所有权限列表
def get_all_permissions():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "select * from sys_permission"
        cursor.execute(sql)
        result = cursor.fetchall()
        return success_response(data=result, code=HTTP_OK)
    except Exception as e:
        return error_response(message=f"查询权限列表失败: {str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)

# 按模块分组返回权限列表
def get_permissions_grouped_by_module():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "select module, perm_id, perm_name from sys_permission order by module"
        cursor.execute(sql)
        rows = cursor.fetchall()

        grouped = {}
        for row in rows:
            module = row["module"]
            if module not in grouped:
                grouped[module] = []
            grouped[module].append({
                "id": row["perm_id"],
                "name": row["perm_name"]
            })

        return success_response(data=grouped)
    except Exception as e:
        return error_response(message=f"分组获取权限失败: {str(e)}")

# 查询角色绑定的权限 ID 列表
def get_permission_ids_by_role(role_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "select perm_id from sys_role_permission where role_id = %s"
        cursor.execute(sql, (role_id,))
        rows = cursor.fetchall()
        perm_ids = [row["perm_id"] for row in rows]
        return success_response(data=perm_ids, code=HTTP_OK)
    except Exception as e:
        return error_response(message=f"查询角色权限失败: {str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)

# 更新角色权限
@log_operation(module="角色权限列表", action="role:bind_permission", template="{operator} 更新了角色 {role} 的权限绑定")
def update_role_permissions(role_id: int, perm_ids: list):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # 删除原权限
        delete_sql = "delete from sys_role_permission where role_id = %s"
        cursor.execute(delete_sql, (role_id,))

        # 插入新权限
        insert_sql = "insert into sys_role_permission (role_id, perm_id) values (%s, %s)"
        for perm_id in perm_ids:
            cursor.execute(insert_sql, (role_id, perm_id))

        conn.commit()
        return success_response(message="权限绑定成功", code=HTTP_OK)
    except Exception as e:
        conn.rollback()
        return error_response(message=f"权限绑定失败: {str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)
