import re
from datetime import datetime

from utils.common import format_time_in_rows
from utils.connect import create_connection
from utils.log.log_decorator import log_operation, get_target_name
from utils.response import error_response, success_response
from utils.security import hash_password, verify_password
from utils.status_code import HTTP_CONFLICT, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_UNAUTHORIZED, \
    HTTP_INTERNAL_SERVER_ERROR

default_pwd = "surfshield"

# 查询管理员分页列表
@log_operation(module="用户列表", action="admin:list", is_query=True,template="{operator} 查询了用户列表")
def get_admin_list(page: int, size: int):
    offset = (page - 1) * size
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            count_sql = "select count(*) as total from sys_admin"
            cursor.execute(count_sql)
            total = cursor.fetchone()["total"]

            list_sql = """
                select admin_id, admin_name, role_id, description, status, createdon 
                from sys_admin where 1=1 
            """
            list_sql += " order by createdon desc limit %s offset %s"
            cursor.execute(list_sql, [size, offset])
            data = cursor.fetchall()
            data = format_time_in_rows(data, ['createdon'])
            return success_response(data={"total": total, "data": data})
    finally:
        conn.close()

# 新增管理员（默认禁用，默认密码）
@log_operation(module="用户列表", action="admin:add", template="{operator} 新增了用户 {admin}")
def add_admin(admin_name: str, role_id: int, description: str, status: int ):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from sys_admin where admin_name = %s", (admin_name,))

            if cursor.fetchone():
                return error_response("管理员名称已存在", code=HTTP_CONFLICT)
            cursor.execute("select 1 from sys_role where role_id = %s", (role_id,))

            if not cursor.fetchone():
                return error_response("角色不存在", code=HTTP_BAD_REQUEST)
            sql = """
                insert into sys_admin (admin_name, password, role_id, description, status, createdon, is_default_pwd)
                values (%s, %s, %s, %s, %s, %s, %s)
            """
            password = hash_password(default_pwd)
            createdon = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(sql, (admin_name, password, role_id, description, status, createdon, True))
        conn.commit()
        return success_response(message="管理员添加成功")
    finally:
        conn.close()

# 更新管理员角色与说明
@log_operation(module="用户列表", action="admin:edit", template="{operator} 编辑了 {admin}")
def update_admin(admin_id: int, role_id: int, description: str):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from sys_admin where admin_id = %s", (admin_id,))
            if not cursor.fetchone():
                return error_response("管理员不存在", code=HTTP_NOT_FOUND)

            cursor.execute("select 1 from sys_role where role_id = %s", (role_id,))
            if not cursor.fetchone():
                return error_response("角色不存在", code=HTTP_BAD_REQUEST)

            sql = "update sys_admin set role_id = %s, description = %s where admin_id = %s"
            cursor.execute(sql, (role_id, description, admin_id))
        conn.commit()
        return success_response(message="管理员信息更新成功")
    finally:
        conn.close()

# 修改管理员状态（启用/禁用）
@log_operation(module="用户列表", action="admin:disable",template="{operator} 将 {admin} 状态更改为 {status_text}")
def update_admin_status(admin_id: int, status: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from sys_admin where admin_id = %s", (admin_id,))
            if not cursor.fetchone():
                return error_response("管理员不存在", code=HTTP_NOT_FOUND)

            sql = "update sys_admin set status = %s where admin_id = %s"
            cursor.execute(sql, (status, admin_id))
        conn.commit()
        status_text = "启用" if status == 1 else "禁用"
        return success_response(
            message="状态更新成功",
            data={"description": status_text}

        )
    finally:
        conn.close()

# 修改密码
@log_operation(module="用户列表", action="admin:change_password", template="{operator} 修改了自身密码")
def change_password(admin_id: int, old_password: str, new_password: str):
    # 密码强度校验：6-12位，包含大小写字母和数字
    if not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{6,12}$', new_password):
        return error_response("新密码格式不符合要求，需为6-12位且包含数字、大小写字母", code=HTTP_BAD_REQUEST)

    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select password from sys_admin where admin_id = %s", (admin_id,))
            row = cursor.fetchone()
            if not row:
                return error_response("管理员不存在", code=HTTP_NOT_FOUND)

            if not verify_password(old_password, row["password"]):
                return error_response("旧密码不正确", code=HTTP_UNAUTHORIZED)

            new_hashed = hash_password(new_password)
            cursor.execute("update sys_admin set password = %s, is_default_pwd = false where admin_id = %s",
                           (new_hashed, admin_id))
        conn.commit()
        return success_response(message="密码修改成功")
    finally:
        conn.close()

# 重置管理员密码为默认
@log_operation(module="用户列表", action="admin:reset", template="{operator} 对 {admin} 执行了密码重置")
def reset_admin_password(admin_id: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from sys_admin where admin_id = %s", (admin_id,))
            if not cursor.fetchone():
                return error_response("管理员不存在", code=HTTP_NOT_FOUND)

            new_password = hash_password(default_pwd)
            sql = "update sys_admin set password = %s , is_default_pwd = true where admin_id = %s"
            cursor.execute(sql, (new_password, admin_id))

        conn.commit()
        return success_response(message="密码重置成功")
    except Exception as e:
        return error_response(f"密码重置失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)
    finally:
        conn.close()

# 删除管理员
@log_operation(module="用户列表", action="admin:delete",template="{operator} 删除了用户 {admin}")
def delete_admin(admin_id: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from sys_admin where admin_id = %s", (admin_id,))
            if not cursor.fetchone():
                return error_response("管理员不存在", code=HTTP_NOT_FOUND)

            sql = "delete from sys_admin where admin_id = %s"
            cursor.execute(sql, (admin_id,))
        conn.commit()
        return success_response(message="管理员删除成功")
    finally:
        conn.close()