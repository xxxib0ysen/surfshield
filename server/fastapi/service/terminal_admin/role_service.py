from datetime import datetime

from service.terminal_admin.perm_service import get_permission_ids_by_role, update_role_permissions
from utils.connect import create_connection
from utils.response import error_response, success_response
from utils.status_code import HTTP_CONFLICT, HTTP_NOT_FOUND

# 获取所有角色
def get_all_roles():
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                            select role_id, role_name, status, description, createdon 
                            from sys_role
                            order by createdon desc
                        """
            cursor.execute(sql)
            data = cursor.fetchall()
            return success_response(data=data)
    finally:
        conn.close()

# 获取角色详情
def get_role_detail(role_id: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                select role_id, role_name, status, description, createdon 
                from sys_role where role_id = %s
            """
            cursor.execute(sql, (role_id,))
            row = cursor.fetchone()
            if not row:
                return error_response("角色不存在", code=HTTP_NOT_FOUND)

            # 查询权限列表
            perm_res = get_permission_ids_by_role(role_id)
            row["permissions"] = perm_res["data"] if perm_res["code"] == 200 else []

        return success_response(data=row)
    finally:
        conn.close()

# 新增角色
def add_role(role_name: str, description: str, permissions: list, status: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from sys_role where role_name = %s", (role_name,))
            if cursor.fetchone():
                return error_response("角色名称已存在", code=HTTP_CONFLICT)

            sql = """
                insert into sys_role (role_name, status, description, createdon)
                values (%s, %s, %s, %s)
            """
            createdon = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(sql, (role_name, status, description, createdon))

        conn.commit()
        return success_response(message="角色添加成功")
    finally:
        conn.close()

# 编辑角色
def update_role(role_id: int, role_name: str, description: str, permissions: list):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from sys_role where role_id = %s", (role_id,))
            if not cursor.fetchone():
                return error_response("角色不存在", code=HTTP_NOT_FOUND)

            sql = "update sys_role set role_name = %s, description = %s where role_id = %s"
            cursor.execute(sql, (role_name, description, role_id))

            # 权限绑定
            update_res = update_role_permissions(role_id, permissions)
            if update_res["code"] != 200:
                conn.rollback()
                return update_res

        conn.commit()
        return success_response(message="角色信息更新成功")
    finally:
        conn.close()

# 修改角色状态（启用/禁用）
def update_role_status(role_id: int, status: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from sys_role where role_id = %s", (role_id,))
            if not cursor.fetchone():
                return error_response("角色不存在", code=HTTP_NOT_FOUND)

            sql = "update sys_role set status = %s where role_id = %s"
            cursor.execute(sql, (status, role_id))
        conn.commit()
        return success_response(message="状态更新成功")
    finally:
        conn.close()

# 删除角色
def delete_role(role_id: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            # 判断是否有管理员绑定该角色
            cursor.execute("select 1 from sys_admin where role_id = %s", (role_id,))
            if cursor.fetchone():
                return error_response("有管理员绑定该角色，无法删除", code=HTTP_CONFLICT)

            cursor.execute("select 1 from sys_role where role_id = %s", (role_id,))
            if not cursor.fetchone():
                return error_response("角色不存在", code=HTTP_NOT_FOUND)

            cursor.execute("delete from sys_role where role_id = %s", (role_id,))
            # 删除权限绑定
            cursor.execute("delete from sys_role_permission where role_id = %s", (role_id,))
        conn.commit()
        return success_response(message="角色删除成功")
    finally:
        conn.close()


