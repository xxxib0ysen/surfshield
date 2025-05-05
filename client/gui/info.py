from datetime import datetime, date

import requests
from PyQt5.QtCore import QTimer, QDateTime

from client.agent.terminal.register import get_terminal_id, get_local_ip, get_username
from client.config.config import redis_client, server_url
from client.config.logger import logger

program_start_time = datetime.now().date()

#   界面终端基础信息
def bind_terminal_info(main_window):
    try:
        terminal_id = get_terminal_id() or "未知"
        username = get_username() or "未知"
        ip_address = get_local_ip() or "0.0.0.0"

        main_window.label_terminal_id.setText(f"终端ID: {terminal_id}")
        main_window.label_username.setText(f"用户名: {username}")
        main_window.label_ip.setText(f"IP: {ip_address}")

        main_window.terminal_id = terminal_id
        main_window.username = username
        main_window.ip_address = ip_address

    except Exception as e:
        logger.error(f"[错误] 绑定终端信息失败: {e}")


def bind_runtime_info(main_window):
    try:
        # 启动定时器：每秒刷新时间
        timer_time = QTimer(main_window)
        timer_time.timeout.connect(lambda: update_current_time(main_window))
        timer_time.start(1000)

        # 启动定时器：每60秒检查Redis、服务器连接状态
        timer_status = QTimer(main_window)
        timer_status.timeout.connect(lambda: update_connection_status(main_window))
        timer_status.start(60000)

        # 启动定时器：每60秒刷新运行天数（跨天自动更新）
        timer_run_days = QTimer(main_window)
        timer_run_days.timeout.connect(lambda: update_run_days(main_window))
        timer_run_days.start(60000)

        # 初始化
        update_current_time(main_window)
        update_connection_status(main_window)
        update_run_days(main_window)

        main_window.timer_time = timer_time
        main_window.timer_status = timer_status
        main_window.timer_run_days = timer_run_days

    except Exception as e:
        logger.error(f"[错误] 绑定运行信息失败: {e}")

# 当前时间
def update_current_time(main_window):
    current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
    main_window.label_time.setText(f"当前时间：{current_time}")

# 检测 Redis 和 服务器连接状态
def update_connection_status(main_window):
    # Redis连接
    try:
        redis_ok = redis_client.ping()
    except Exception:
        redis_ok = False

    if redis_ok:
        main_window.label_redis_status.setText("正常")
        main_window.label_redis_status.setStyleSheet("color: green; font-weight: bold;")
    else:
        main_window.label_redis_status.setText("异常")
        main_window.label_redis_status.setStyleSheet("color: red; font-weight: bold;")

    # 服务器连接
    try:
        resp = requests.get(server_url.rstrip("/") + "/api/ping", timeout=5)
        server_ok = (resp.status_code == 200)
    except Exception:
        server_ok = False

    if server_ok:
        main_window.label_server_status.setText("正常")
        main_window.label_server_status.setStyleSheet("color: green; font-weight: bold;")
    else:
        main_window.label_server_status.setText("异常")
        main_window.label_server_status.setStyleSheet("color: red; font-weight: bold;")

# 刷新运行天数
def update_run_days(main_window):
    try:
        today = datetime.now().date()
        days = (today - program_start_time).days + 1  # 包括当天
        main_window.label_run_days.setText(f"运行天数：{days}天")
    except Exception as e:
        logger.error(f"[错误] 更新运行天数失败: {e}")