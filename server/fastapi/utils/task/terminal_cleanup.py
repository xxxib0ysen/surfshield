from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from utils.connect import create_connection, redis_client


# 标记离线终端并清理 Redis 中的进程缓存
def mark_inactive_terminals():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        sql = """
            select id
            from sys_terminal
            where last_heartbeat is not null
              and last_heartbeat < now() - interval 1 minute
        """
        cursor.execute(sql)
        offline_terminals = cursor.fetchall()

        if not offline_terminals:
            return

        # 获取 id 列表
        terminal_ids = [row["id"] for row in offline_terminals]

        # 更新终端状态为离线
        placeholders = ','.join(['%s'] * len(terminal_ids))
        sql = f"update sys_terminal set status = 0 where id in ({placeholders})"
        cursor.execute(sql, terminal_ids)
        conn.commit()

        # 清除 Redis 中缓存的进程数据
        for row in offline_terminals:
            terminal_id = row["id"]
            redis_key = f"terminal:process:{terminal_id}"
            redis_client.delete(redis_key)
            print(f"已清除 Redis 缓存: {redis_key}")

    except Exception as e:
        print(f"离线终端处理失败: {e}")


scheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()},
    executors={"default": ThreadPoolExecutor(10)},
    job_defaults={"coalesce": False, "max_instances": 1},
    timezone="Asia/Shanghai"
)



# 初始化定时任务
def init_scheduler():
    print("初始化定时任务：离线终端检测")
    scheduler.add_job(
        mark_inactive_terminals,
        trigger="interval",
        seconds=60,
        id="offline_terminal_check",
        replace_existing=True
    )
    scheduler.start()
