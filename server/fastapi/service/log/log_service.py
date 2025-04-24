import json
from fastapi import HTTPException

from model.log.log_model import OperationLogQuery, BehaviorLogQuery
from utils.common import format_time_in_rows
from utils.connect import create_connection
from utils.log.log_decorator import log_operation
from utils.response import success_response, error_response
from utils.status_code import HTTP_OK, HTTP_INTERNAL_SERVER_ERROR


# 格式化描述
def format_detail_description(row: dict) -> dict:
    try:
        detail_obj = json.loads(row.get("detail", "{}"))
        if isinstance(detail_obj, dict) and "description" in detail_obj:
            row["detail"] = detail_obj["description"]
    except Exception:
        pass
    return row


# 查询系统操作日志
@log_operation(module="系统操作日志",action="log:operation:list",is_query=True,template="{operator} 查询了系统操作日志")
def get_operation_log_list(query: OperationLogQuery):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        filters = ["is_deleted = 0"]  # 默认仅查询未删除
        values = []

        # 管理员名模糊搜索
        if query.admin_name and query.admin_name.strip():
            filters.append("admin_name like %s")
            values.append(f"%{query.admin_name.strip()}%")

        # 模块筛选
        if query.module:
            filters.append("module = %s")
            values.append(query.module)

        # 时间范围筛选
        if query.start_date:
            filters.append("date(created_at) >= %s")
            values.append(query.start_date)
        if query.end_date:
            filters.append("date(created_at) <= %s")
            values.append(query.end_date)

        where_clause = " and ".join(filters)
        offset = (query.page - 1) * query.page_size

        # 查询总数
        count_sql = f"""
            select count(*) as count
            from log_operation l
            left join sys_admin a on l.admin_id = a.admin_id
            where {where_clause}
        """
        cursor.execute(count_sql, values)
        total = cursor.fetchone()["count"]

        # 查询分页数据
        list_sql = f"""
            select l.id, l.created_at, l.admin_id, a.admin_name, l.ip_address, l.module, l.action, l.detail
            from log_operation l
            left join sys_admin a on l.admin_id = a.admin_id
            where {where_clause}
            order by l.created_at desc
            limit %s offset %s
        """

        cursor.execute(list_sql, values + [query.page_size, offset])
        rows = cursor.fetchall()
        rows = format_time_in_rows(rows, ['created_at'])
        rows = [format_detail_description(row) for row in rows]

        return success_response(
            message="查询成功",
            data={"total": total, "data": rows}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取模块
def get_module_list_service():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # 查询所有非空模块并去重
        sql = "select distinct module from log_operation where module is not null and module != ''"
        cursor.execute(sql)
        rows = cursor.fetchall()
        modules = [row["module"] for row in rows]

        return success_response(data=modules, code=HTTP_OK)
    except Exception as e:
        return error_response(message=f"获取模块列表失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)


# 分页查询终端管控日志
@log_operation(module="终端管控日志", action="behavior:query", is_query=True, template="{operator} 查询了终端管控日志")
def get_behavior_log_list(query: BehaviorLogQuery):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        filters = []
        values = []

        # ✅ 分组筛选：递归获取该组及其子组下所有终端 ID
        if query.group_id is not None:
            cursor.execute("select group_id, parent_id from sys_group")
            all_groups = cursor.fetchall()

            # 递归获取所有子分组 ID
            def get_all_subgroups(gid, groups):
                result = [gid]
                for g in groups:
                    if g['parent_id'] == gid:
                        result.extend(get_all_subgroups(g['group_id'], groups))
                return result

            group_ids = get_all_subgroups(query.group_id, all_groups)
            cursor.execute(f"select id from sys_terminal where group_id in ({','.join(['%s'] * len(group_ids))})", group_ids)
            terminal_rows = cursor.fetchall()
            terminal_ids = [row["id"] for row in terminal_rows]

            if terminal_ids:
                placeholders = ','.join(['%s'] * len(terminal_ids))
                filters.append(f"b.terminal_id in ({placeholders})")
                values.extend(terminal_ids)
            else:
                filters.append("1 = 0")  # 返回空结果

        # ✅ 用户名模糊匹配
        if query.username:
            filters.append("t.username like %s")
            values.append(f"%{query.username.strip()}%")

        # ✅ 行为类型
        if query.behavior_type:
            filters.append("b.behavior_type = %s")
            values.append(query.behavior_type)

        # ✅ 时间范围
        if query.start_date:
            filters.append("b.event_time >= %s")
            values.append(query.start_date)
        if query.end_date:
            filters.append("b.event_time <= %s")
            values.append(query.end_date)

        # ✅ 拼接 where 子句
        where_clause = " and ".join(filters)
        where_clause = f"where {where_clause}" if where_clause else ""

        # ✅ 查询总数
        count_sql = f"""
            select count(*) as total
            from log_behavior b
            join sys_terminal t on b.terminal_id = t.id
            {where_clause}
        """
        cursor.execute(count_sql, values)
        total = cursor.fetchone()["total"]

        # ✅ 查询数据
        offset = (query.page - 1) * query.page_size
        sql = f"""
            select b.id, b.event_time, t.username, b.ip_address,
                   b.behavior_type, b.detail
            from log_behavior b
            join sys_terminal t on b.terminal_id = t.id
            {where_clause}
            order by b.event_time desc
            limit %s offset %s
        """
        cursor.execute(sql, values + [query.page_size, offset])
        rows = cursor.fetchall()

        from utils.common import format_time_in_rows
        rows = format_time_in_rows(rows, ["event_time"])

        return success_response(data={"total": total, "list": rows}, code=HTTP_OK)

    except Exception as e:
        return error_response(message=f"获取终端行为日志失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)
