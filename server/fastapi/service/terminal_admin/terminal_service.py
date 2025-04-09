from datetime import datetime

from utils.connect import create_connection
from utils.response import success_response, error_response
from utils.status_code import HTTP_OK, HTTP_BAD_REQUEST
from model.terminal_admin.terminal_model import TerminalQuery, TerminalMoveGroup

# 查询终端列表
def get_terminal_list(query: TerminalQuery):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        filters = []
        values = []

        # 筛选用户名
        if query.username:
            filters.append("username like %s" if query.fuzzy else "username = %s")
            values.append(f"%{query.username}%" if query.fuzzy else query.username)
        # 筛选计算机名
        if query.hostname:
            filters.append("hostname like %s" if query.fuzzy else "hostname = %s")
            values.append(f"%{query.hostname}%" if query.fuzzy else query.hostname)
        # 筛选IP地址
        if query.ip_address:
            filters.append("ip_address like %s" if query.fuzzy else "ip_address = %s")
            values.append(f"%{query.ip_address}%" if query.fuzzy else query.ip_address)
        # 筛选唯一标识符
        if query.uuid:
            filters.append("uuid like %s" if query.fuzzy else "uuid = %s")
            values.append(f"%{query.uuid}%" if query.fuzzy else query.uuid)
        # 筛选操作系统
        if query.os_name:
            filters.append("os_name like %s" if query.fuzzy else "os_name = %s")
            values.append(f"%{query.os_name}%" if query.fuzzy else query.os_name)
        # 筛选操作系统版本
        if query.os_version:
            filters.append("os_version like %s" if query.fuzzy else "os_version = %s")
            values.append(f"%{query.os_version}%" if query.fuzzy else query.os_version)
        # 筛选在线状态
        if query.status is not None:
            filters.append("status = %s")
            values.append(query.status)
        # 筛选分组
        if query.group_id:
            filters.append("group_id = %s")
            values.append(query.group_id)

        where_sql = " where " + " and ".join(filters) if filters else ""
        limit_sql = " limit %s offset %s"
        values.extend([query.page_size, (query.page - 1) * query.page_size])

        # 查询总数
        count_sql = f"select count(*) as total from sys_terminal {where_sql}"
        cursor.execute(count_sql, values[:-2])
        total = cursor.fetchone()["total"]

        # 查询数据列表
        data_sql = f"""
            select * from sys_terminal
            {where_sql}
            order by status desc, createdon desc
            {limit_sql}
        """
        cursor.execute(data_sql, values)
        rows = cursor.fetchall()

        return success_response(
            code=HTTP_OK,
            message="查询成功",
            data={"total": total, "data": rows}
        )
    except Exception as e:
        return error_response(
            code=HTTP_BAD_REQUEST,
            message=f"查询失败: {str(e)}"
        )


# 获取终端详情信息
def get_terminal_detail(terminal_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "select * from sys_terminal where id = %s"
        cursor.execute(sql, (terminal_id,))
        result = cursor.fetchone()

        if result:
            return success_response(
                code=HTTP_OK,
                message="获取成功",
                data=result
            )
        else:
            return error_response(
                code=HTTP_BAD_REQUEST,
                message="终端不存在"
            )
    except Exception as e:
        return error_response(
            code=HTTP_BAD_REQUEST,
            message=f"获取失败: {str(e)}"
        )


# 批量移动终端到指定分组
def move_terminal_to_group(data: TerminalMoveGroup):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        format_strings = ",".join(["%s"] * len(data.ids))
        sql = f"update sys_terminal set group_id = %s where id in ({format_strings})"
        cursor.execute(sql, [data.group_id] + data.ids)
        conn.commit()

        return success_response(
            code=HTTP_OK,
            message="移动成功"
        )
    except Exception as e:
        return error_response(
            code=HTTP_BAD_REQUEST,
            message=f"移动失败: {str(e)}"
        )

# 终端注册
def register_terminal(data):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # 查询 group_code 是否存在且启用
        sql = "select group_id from sys_group_code where group_code = %s and status = 1"
        cursor.execute(sql, (data.group_code,))
        result = cursor.fetchone()

        if not result:
            return error_response(
                code=HTTP_BAD_REQUEST,
                message="无效的邀请码，请联系管理员"
            )

        group_id = result["group_id"]

        # 检查是否存在相同 uuid 的终端
        sql = "select id, group_id, group_name from sys_terminal where uuid = %s"
        cursor.execute(sql, (data.uuid,))
        exist = cursor.fetchone()
        if exist:
            return success_response(
                code=HTTP_OK,
                message="终端已存在，跳过重复注册",
                data={
                    "terminal_id": exist["id"],
                    "group_id": exist["group_id"],
                    "group_name": exist["group_name"]
                }
            )

        # 获取分组名称
        sql = "select group_name from sys_group where group_id = %s"
        cursor.execute(sql, (group_id,))
        group = cursor.fetchone()
        group_name = group["group_name"] if group else "未知分组"

        # 插入终端信息
        sql = """
                    insert into sys_terminal (
                        username, hostname, uuid, ip_address, local_ip, mac_address,
                        os_name, os_version, is_64bit, install_time, status, createdon,
                        group_id, group_name
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, now(), %s, %s)
                """
        now = datetime.now()
        cursor.execute(sql, (
            data.username, data.hostname, data.uuid, data.ip_address, data.local_ip,
            data.mac_address, data.os_name, data.os_version, data.is_64bit, now,
            group_id, group_name
        ))
        conn.commit()
        terminal_id = cursor.lastrowid

        return success_response(
            code=HTTP_OK,
            message="终端注册成功",
            data={
                "terminal_id": terminal_id,
                "group_id": group_id,
                "group_name": group_name
            }
        )
    except Exception as e:
        return error_response(
            code=HTTP_BAD_REQUEST,
            message=f"注册失败: {str(e)}"
        )

# 更新终端在线状态
def update_terminal_status(terminal_id: int, status: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        if status == 1:
            # 在线：更新 last_login
            sql = "update sys_terminal set status = %s, last_login = now() where id = %s"
            cursor.execute(sql, (status, terminal_id))
        else:
            # 离线：不更新 last_login，只修改状态
            sql = "update sys_terminal set status = %s where id = %s"
            cursor.execute(sql, (status, terminal_id))

        conn.commit()
        return success_response(code=HTTP_OK, message="终端状态已更新")
    except Exception as e:
        return error_response(code=HTTP_BAD_REQUEST, message=f"更新失败: {str(e)}")
