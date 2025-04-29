import json
import os
from datetime import datetime, date
from PyQt5.QtCore import QTimer

# 本地存储文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(DATA_DIR, exist_ok=True)

INTERCEPT_INFO_PATH = os.path.join(DATA_DIR, "intercept_info.json")

# 默认结构
default_info = {
    "total_website_block": 0,
    "total_process_block": 0,
    "today_website_block": 0,
    "today_process_block": 0,
    "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
    "last_web_rule_sync": "--",
    "web_rule_count": 0,
    "last_process_rule_sync": "--",
    "process_rule_count": 0
}

# 读取拦截数据
def load_intercept_info():
    try:
        if os.path.exists(INTERCEPT_INFO_PATH):
            with open(INTERCEPT_INFO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[错误] 读取拦截信息失败: {e}")
    return default_info.copy()

# 保存拦截数据
def save_intercept_info(info):
    try:
        with open(INTERCEPT_INFO_PATH, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[错误] 保存拦截信息失败: {e}")

# 初始化
def bind_intercept_info(main_window):
    main_window.intercept_info = load_intercept_info()

    timer = QTimer(main_window)
    timer.timeout.connect(lambda: reset_today_if_needed(main_window))
    timer.start(60000)  # 每60秒检查一次

    # 页面初始刷新
    refresh_block_ui(main_window)
    refresh_rule_ui(main_window)

    main_window.timer_intercept_check = timer

# 刷新拦截次数到界面
def refresh_block_ui(main_window):
    info = main_window.intercept_info
    today_total = info.get("today_website_block", 0) + info.get("today_process_block", 0)
    total = info.get("total_website_block", 0) + info.get("total_process_block", 0)

    main_window.label_today_block.setText(f"今日拦截次数：{today_total}")
    main_window.label_total_block.setText(f"总共拦截次数：{total}")

# 刷新规则数量到界面
def refresh_rule_ui(main_window):
    info = main_window.intercept_info
    main_window.label_web_rule.setText(
        f"网站规则：{info.get('web_rule_count', 0)}条，最后同步：{info.get('last_web_rule_sync', '--')}")
    main_window.label_process_rule.setText(
        f"进程规则：{info.get('process_rule_count', 0)}条，最后同步：{info.get('last_process_rule_sync', '--')}")

# 每次网站拦截调用
def record_website_block(main_window):
    info = main_window.intercept_info

    reset_today_if_needed(main_window)

    info["today_website_block"] = info.get("today_website_block", 0) + 1
    info["total_website_block"] = info.get("total_website_block", 0) + 1

    save_intercept_info(info)
    refresh_block_ui(main_window)

# 每次进程拦截调用
def record_process_block(main_window):
    info = main_window.intercept_info

    reset_today_if_needed(main_window)

    info["today_process_block"] = info.get("today_process_block", 0) + 1
    info["total_process_block"] = info.get("total_process_block", 0) + 1

    save_intercept_info(info)
    refresh_block_ui(main_window)

# 每次规则同步后调用
def update_rule_info(main_window, web_rule_count=None, process_rule_count=None):
    info = main_window.intercept_info

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if web_rule_count is not None:
        info["web_rule_count"] = web_rule_count
        info["last_web_rule_sync"] = now

    if process_rule_count is not None:
        info["process_rule_count"] = process_rule_count
        info["last_process_rule_sync"] = now

    save_intercept_info(info)
    refresh_rule_ui(main_window)

# 清空今日数据
def reset_today_if_needed(main_window):
    info = main_window.intercept_info
    last_reset = info.get("last_reset_date")

    if last_reset != datetime.now().strftime("%Y-%m-%d"):
        info["today_website_block"] = 0
        info["today_process_block"] = 0
        info["last_reset_date"] = datetime.now().strftime("%Y-%m-%d")
        save_intercept_info(info)
        refresh_block_ui(main_window)