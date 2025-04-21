import json
from datetime import datetime
from utils.connect import redis_client, create_connection
from utils.common import format_time_in_rows
from utils.log.log_decorator import log_operation


# 根据用户名模糊查询（为空表示查询所有在线终端）
def get_terminal_ids_by_username(username: str = None):
    try:
        # 获取 Redis 中所有在线终端
        keys = redis_client.keys("terminal:heartbeat:*")
        print("[调试] Redis 在线终端键列表:", keys)
        terminal_ids = [int(key.split(":")[-1]) for key in keys]
        print("[调试] 在线 terminal_ids:", terminal_ids)

        if not terminal_ids:
            return []

        conn = create_connection()
        cursor = conn.cursor()

        if username is not None and username.strip() != "":
            sql = f"""
                select id from sys_terminal
                where id in ({','.join(['%s'] * len(terminal_ids))})
                  and username like %s
            """
            cursor.execute(sql, terminal_ids + [f"%{username}%"])
        else:
            sql = f"""
                select id from sys_terminal
                where id in ({','.join(['%s'] * len(terminal_ids))})
            """
            cursor.execute(sql, terminal_ids)

        rows = cursor.fetchall()
        return [row["id"] for row in rows]

    except Exception as e:
        print(f"[Redis 在线终端查询失败] {e}")
        return []

# 获取用户名
def map_terminal_ids_to_usernames(terminal_ids: list[str]) -> dict:
    try:
        if not terminal_ids:
            return {}
        conn = create_connection()
        cursor = conn.cursor()
        sql = f"select id, username from sys_terminal where id in ({','.join(['%s']*len(terminal_ids))})"
        cursor.execute(sql, terminal_ids)
        rows = cursor.fetchall()
        return {row["id"]: row["username"] for row in rows}
    except Exception as e:
        print(f"[用户名映射失败] {e}")
        return {}

# 获取网页访问记录
@log_operation(module="行为管控", action="behavior:web", is_query=True, template="{operator} 查询了网页访问记录")
def get_web_behavior_service(username: str):
    result = []

    terminal_ids = get_terminal_ids_by_username(username)
    tid_to_user = map_terminal_ids_to_usernames(terminal_ids)

    for tid in terminal_ids:
        key = f"behavior:web:{tid}"
        raw_list = redis_client.lrange(key, 0, 19)
        parsed = [json.loads(item) for item in raw_list]
        for item in parsed:
            item["username"] = tid_to_user.get(tid, "未知终端")
        result.extend(parsed)

    # 格式化时间
    result = format_time_in_rows(result, ["visit_time"])

    # 按时间排序
    result.sort(key=lambda x: x["visit_time"], reverse=True)
    return result

# 获取搜索关键词记录
@log_operation(module="行为管控", action="behavior:search", is_query=True, template="{operator} 查询了搜索关键词记录")
def get_search_behavior_service(username: str):
    result = []

    terminal_ids = get_terminal_ids_by_username(username)
    tid_to_user = map_terminal_ids_to_usernames(terminal_ids)

    for tid in terminal_ids:
        key = f"behavior:search:{tid}"
        raw_list = redis_client.lrange(key, 0, 19)
        parsed = [json.loads(item) for item in raw_list]
        for item in parsed:
            item["username"] = tid_to_user.get(tid, "未知终端")
        result.extend(parsed)

    # 格式化时间
    result = format_time_in_rows(result, ["search_time"])

    # 按时间排序
    result.sort(key=lambda x: x["search_time"], reverse=True)
    return result

# 获取所有在线终端用户名
def get_online_username():
    try:
        keys = redis_client.keys("terminal:heartbeat:*")
        if not keys:
            return []

        terminal_ids = [int(key.split(":")[-1]) for key in keys]
        if not terminal_ids:
            return []

        conn = create_connection()
        cursor = conn.cursor()
        sql = f"""
            select distinct username
            from sys_terminal
            where id in ({','.join(['%s'] * len(terminal_ids))})
        """
        cursor.execute(sql, terminal_ids)
        rows = cursor.fetchall()

        # 排序后返回
        result = [row["username"] for row in rows]
        result.sort()
        return result

    except Exception as e:
        print(f"[Redis 在线终端获取失败] {e}")
        return []