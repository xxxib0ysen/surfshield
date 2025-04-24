import json
from datetime import datetime
from utils.connect import create_connection, redis_client


# 同步 Redis 中终端进程
def sync_process_behavior_from_redis():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        keys = redis_client.keys("terminal:process:*")
        if not keys:
            print("[行为同步] 无进程数据可同步。")
            return

        sync_count = 0

        for key in keys:
            terminal_id = int(key.split(":")[-1])
            raw = redis_client.get(key)
            if not raw:
                continue

            process_list = json.loads(raw)

            # 查询终端公网 IP
            cursor.execute("select ip_address from sys_terminal where id = %s", (terminal_id,))
            row = cursor.fetchone()
            terminal_ip = row["ip_address"] if row else ""

            for p in process_list:
                if not all(k in p for k in ("process_name", "pid", "start_time")):
                    continue

                # 去重
                cursor.execute("""
                    select id from log_process
                    where terminal_id = %s and process_name = %s and pid = %s and start_time = %s
                """, (
                    terminal_id,
                    p["process_name"],
                    p["pid"],
                    p["start_time"]
                ))
                exists = cursor.fetchone()
                if exists:
                    continue

                # 插入 log_process
                cursor.execute("""
                    insert into log_process (
                        terminal_id, process_name, pid, status,
                        is_network, remote_ip, remote_port, network_status,
                        description, start_time
                    )
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    terminal_id,
                    p["process_name"],
                    p["pid"],
                    p["status"],
                    p.get("is_network", 0),
                    p.get("remote_ip"),
                    p.get("remote_port"),
                    p.get("network_status"),
                    p.get("description", ""),
                    p["start_time"]
                ))

                ref_id = cursor.lastrowid

                # 插入 log_behavior
                detail = f"运行进程：{p['process_name']} (PID={p['pid']})"
                cursor.execute("""
                    insert into log_behavior (
                        event_time, terminal_id, ip_address, behavior_type, detail, ref_id
                    )
                    values (%s, %s, %s, %s, %s, %s)
                """, (
                    p["start_time"],
                    terminal_id,
                    terminal_ip,
                    "进程运行",
                    detail,
                    ref_id
                ))

                sync_count += 1

        conn.commit()
        print(f"[行为同步] 进程日志同步完成，共写入 {sync_count} 条行为。")

    except Exception as e:
        print(f"[行为同步] 同步进程数据失败：{e}")

# 同步 Redis 中网页访问行为
def sync_web_behavior_from_redis():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        keys = redis_client.keys("behavior:web:*")
        if not keys:
            print("[行为同步] 无网页访问记录可同步。")
            return

        sync_count = 0

        for key in keys:
            terminal_id = int(key.split(":")[-1])
            raw = redis_client.lrange(key, 0, 19)
            if not raw:
                continue

            web_list = [json.loads(item) for item in raw]

            # 查找终端公网 IP
            cursor.execute("select ip_address from sys_terminal where id = %s", (terminal_id,))
            row = cursor.fetchone()
            terminal_ip = row["ip_address"] if row else ""

            for w in web_list:
                if not all(k in w for k in ("url", "visit_time", "browser")):
                    continue

                # 去重
                cursor.execute("""
                    select id from log_web
                    where terminal_id = %s and url = %s and visit_time = %s
                """, (
                    terminal_id,
                    w["url"],
                    w["visit_time"]
                ))
                if cursor.fetchone():
                    continue

                # 插入 log_web
                cursor.execute("""
                    insert into log_web (
                        terminal_id, ip_address, url, browser, visit_time
                    ) values (%s, %s, %s, %s, %s)
                """, (
                    terminal_id,
                    terminal_ip,
                    w["url"],
                    w["browser"],
                    w["visit_time"]
                ))

                ref_id = cursor.lastrowid

                # 插入 log_behavior 主表
                detail = f"访问网址：{w['url']}"
                cursor.execute("""
                    insert into log_behavior (
                        event_time, terminal_id, ip_address, behavior_type, detail, ref_id
                    ) values (%s, %s, %s, %s, %s, %s)
                """, (
                    w["visit_time"],
                    terminal_id,
                    terminal_ip,
                    "网站访问",
                    detail,
                    ref_id
                ))

                sync_count += 1

        conn.commit()
        print(f"[行为同步] 网页访问记录同步完成，共写入 {sync_count} 条行为。")

    except Exception as e:
        print(f"[行为同步] 同步网页行为失败：{e}")

# 同步 Redis 中搜索关键词行为
def sync_search_behavior_from_redis():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        keys = redis_client.keys("behavior:search:*")
        if not keys:
            print("[行为同步] 无搜索记录可同步。")
            return

        sync_count = 0

        for key in keys:
            terminal_id = int(key.split(":")[-1])
            raw = redis_client.lrange(key, 0, 19)
            if not raw:
                continue

            search_list = [json.loads(item) for item in raw]

            # 查找终端公网 IP
            cursor.execute("select ip_address from sys_terminal where id = %s", (terminal_id,))
            row = cursor.fetchone()
            terminal_ip = row["ip_address"] if row else ""

            for s in search_list:
                if not all(k in s for k in ("engine", "keyword", "search_time")):
                    continue

                # 去重
                cursor.execute("""
                    select id from log_search
                    where terminal_id = %s and keyword = %s and search_time = %s
                """, (
                    terminal_id,
                    s["keyword"],
                    s["search_time"]
                ))
                if cursor.fetchone():
                    continue

                # 插入 log_search
                cursor.execute("""
                    insert into log_search (
                        terminal_id, ip_address, engine, keyword, search_time
                    ) values (%s, %s, %s, %s, %s)
                """, (
                    terminal_id,
                    terminal_ip,
                    s["engine"],
                    s["keyword"],
                    s["search_time"]
                ))

                ref_id = cursor.lastrowid

                # 插入 log_behavior
                detail = f"使用 {s['engine']} 搜索：{s['keyword']}"
                cursor.execute("""
                    insert into log_behavior (
                        event_time, terminal_id, ip_address, behavior_type, detail, ref_id
                    ) values (%s, %s, %s, %s, %s, %s)
                """, (
                    s["search_time"],
                    terminal_id,
                    terminal_ip,
                    "搜索行为",
                    detail,
                    ref_id
                ))

                sync_count += 1

        conn.commit()
        print(f"[行为同步] 搜索记录同步完成，共写入 {sync_count} 条行为。")

    except Exception as e:
        print(f"[行为同步] 同步搜索记录失败：{e}")
