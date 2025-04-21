from datetime import datetime
from typing import Optional, List

from utils.common import format_time_fields
from utils.connect import create_connection
from utils.log.log_decorator import log_operation
from utils.response import success_response, error_response
from utils.status_code import HTTP_OK, HTTP_BAD_REQUEST, HTTP_INTERNAL_SERVER_ERROR
from model.terminal_admin.terminal_model import TerminalQuery, TerminalMoveGroup

# 查询终端列表
@log_operation(module="终端列表", action="terminal:list", is_query=True, template="{operator} 查询了终端列表")
def get_terminal_list(query: TerminalQuery, group_ids: Optional[List[int]] = None):
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
        if group_ids:
            placeholders = ','.join(['%s'] * len(group_ids))
            filters.append(f"group_id in ({placeholders})")
            values.extend(group_ids)

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

        time_keys = ['install_time', 'createdon', 'last_login']
        rows = [format_time_fields(row, time_keys) for row in rows]

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
@log_operation(module="终端管理", action="terminal:detail", is_query=True, template="{operator} 查看了终端 {terminal} 的详情")
def get_terminal_detail(terminal_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "select * from sys_terminal where id = %s"
        cursor.execute(sql, (terminal_id,))
        result = cursor.fetchone()

        if result:
            result = format_time_fields(result, ['install_time', 'createdon', 'last_login'])
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
@log_operation(module="终端管理", action="terminal:move", template="{operator} 将多个终端移动至其他分组")
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

# 获取分组完整路径
def get_group_path(conn, group_id: int) -> str:
    cursor = conn.cursor()
    path = []
    while group_id:
        cursor.execute("select group_name, parent_id from sys_group where group_id = %s", (group_id,))
        row = cursor.fetchone()
        if not row:
            break
        path.insert(0, row["group_name"])
        group_id = row["parent_id"]
    return "/" + "/".join(path) if path else "/默认分组"

# 自定义列
def get_terminal_columns():
    try:
        columns = [
            {"prop": "username", "label": "用户名", "default": True},
            {"prop": "status", "label": "在线状态", "default": True},
            {"prop": "hostname", "label": "计算机名", "default": True},
            {"prop": "os_name", "label": "操作系统", "default": True},
            {"prop": "ip_address", "label": "IP", "default": True},
            {"prop": "os_version", "label": "操作系统版本", "default": False},
            {"prop": "install_time", "label": "操作系统安装时间", "default": False},
            {"prop": "uuid", "label": "唯一标识符", "default": False},
            {"prop": "local_ip", "label": "本地IP", "default": False},
            {"prop": "mac_address", "label": "MAC", "default": False},
            {"prop": "is_64bit", "label": "是否64位", "default": False},
            {"prop": "group_path", "label": "分组路径", "default": False},
            {"prop": "last_login", "label": "最后在线时间", "default": False},
        ]
        return success_response(code=HTTP_OK, message="获取成功", data=columns)
    except Exception as e:
        return error_response(code=HTTP_BAD_REQUEST, message=f"获取失败: {str(e)}")


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

        # 获取分组名称与路径
        sql = "select group_name from sys_group where group_id = %s"
        cursor.execute(sql, (group_id,))
        group = cursor.fetchone()
        group_name = group["group_name"] if group else "未知分组"
        group_path = get_group_path(conn, group_id)

        # 检查是否存在相同 uuid 的终端
        sql = "select id, group_id, group_name from sys_terminal where uuid = %s"
        cursor.execute(sql, (data.uuid,))
        if cursor.fetchone():
            return error_response(code=HTTP_BAD_REQUEST, message="终端已存在，禁止重复注册")

        install_time = None
        if getattr(data, "install_time", None):
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d, %H:%M:%S"]:
                try:
                    install_time = datetime.strptime(data.install_time, fmt)
                    break
                except:
                    continue
        if not install_time:
            install_time = datetime.now()

        # 插入新终端
        sql = """
                insert into sys_terminal (
                    username, hostname, uuid, ip_address, local_ip, mac_address,
                    os_name, os_version, is_64bit, install_time,
                    status, createdon, group_id, group_name, group_path
                ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, now(), %s, %s, %s)
            """
        cursor.execute(sql, (
            data.username, data.hostname, data.uuid, data.ip_address, data.local_ip,
            data.mac_address, data.os_name, data.os_version, data.is_64bit, install_time,
            group_id, group_name, group_path
        ))
        conn.commit()

        terminal_id = cursor.lastrowid
        return success_response(
            code=HTTP_OK,
            message="终端注册成功",
        )
    except Exception as e:
        return error_response(
            code=HTTP_BAD_REQUEST,
            message=f"注册失败: {str(e)}"
        )

# 更新
def update_terminal_info(data):
    try:
        if not data.uuid:
            return error_response(code=HTTP_BAD_REQUEST, message="缺少 uuid，无法更新")

        conn = create_connection()
        cursor = conn.cursor()

        # 检查是否存在该终端
        cursor.execute("select id from sys_terminal where uuid = %s", (data.uuid,))
        row = cursor.fetchone()
        if not row:
            return error_response(code=HTTP_BAD_REQUEST, message="终端不存在，无法更新")

        install_time = None
        if getattr(data, "install_time", None):
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d, %H:%M:%S"]:
                try:
                    install_time = datetime.strptime(data.install_time, fmt)
                    break
                except:
                    continue
        if not install_time:
            install_time = datetime.now()

        sql = """
            update sys_terminal set
                username = %s, hostname = %s, ip_address = %s, local_ip = %s,
                mac_address = %s, os_name = %s, os_version = %s,
                install_time = %s, is_64bit = %s, last_login = now()
            where uuid = %s
        """
        cursor.execute(sql, (
            data.username, data.hostname, data.ip_address, data.local_ip,
            data.mac_address, data.os_name, data.os_version, install_time,
            data.is_64bit, data.uuid
        ))
        conn.commit()

        return success_response(code=HTTP_OK, message="终端信息更新成功")
    except Exception as e:
        return error_response(code=HTTP_INTERNAL_SERVER_ERROR, message=f"更新失败：{str(e)}")

# 更新终端在线状态
def update_terminal_status(terminal_id: int, status: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        if status == 1:
            # 在线
            sql = "update sys_terminal set status = %s, last_login = now(),  last_heartbeat = now() where id = %s"
            cursor.execute(sql, (status, terminal_id))
        else:
            # 离线
            sql = "update sys_terminal set status = %s, last_heartbeat = now() where id = %s"
            cursor.execute(sql, (status, terminal_id))

        conn.commit()
        return success_response(code=HTTP_OK, message="终端状态已更新")
    except Exception as e:
        return error_response(code=HTTP_BAD_REQUEST, message=f"更新失败: {str(e)}")


# 终端状态统计
def get_terminal_status_count():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # 在线
        cursor.execute("select count(*) as count from sys_terminal where status = 1")
        online = cursor.fetchone()["count"]

        # 离线
        cursor.execute("select count(*) as count from sys_terminal where status = 0")
        offline = cursor.fetchone()["count"]

        return { "online": online, "offline": offline }
    except Exception as e:
        return error_response(message=f"获取终端状态统计失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)


# 查询终端操作系统分布
def get_terminal_os_distribution():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # 按操作系统名称统计数量
        sql = "select os_name as name, count(*) as count from sys_terminal group by os_name"
        cursor.execute(sql)
        rows = cursor.fetchall()

        return rows
    except Exception as e:
        return error_response(message=f"获取操作系统分布失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)
