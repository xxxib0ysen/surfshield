from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from utils.connect import create_connection

# 标记离线终端
def mark_inactive_terminals():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = """
            update sys_terminal
            set status = 0
            where last_heartbeat is not null
              and last_heartbeat < now() - interval 1 minute
        """
        cursor.execute(sql)
        conn.commit()
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
    scheduler.add_job(
        mark_inactive_terminals,
        trigger="interval",
        seconds=60,
        id="offline_terminal_check",
        replace_existing=True
    )
    scheduler.start()