import json
import os
from datetime import datetime, date
from PyQt5.QtCore import QTimer

from client.config import config

# 拦截信息存储路径
INTERCEPT_PATH = config.intercept_info_path
os.makedirs(os.path.dirname(INTERCEPT_PATH), exist_ok=True)

# 默认结构
default_info = {
    "today_website_block": 0,
    "today_process_block": 0,
    "total_website_block": 0,
    "total_process_block": 0,
    "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
    "web_rule_count": 0,
    "last_web_rule_sync": "--",
    "process_rule_count": 0,
    "last_process_rule_sync": "--"
}

# 读取
def load_info():
    try:
        if os.path.exists(INTERCEPT_PATH):
            with open(INTERCEPT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return default_info.copy()

# 保存
def save_info(info):
    with open(INTERCEPT_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)

# 每天自动重置
def reset_if_needed(info):
    today = datetime.now().strftime("%Y-%m-%d")
    if info.get("last_reset_date") != today:
        info["today_website_block"] = 0
        info["today_process_block"] = 0
        info["last_reset_date"] = today
        save_info(info)

# 绑定界面与定时器
def bind_intercept_info(main_window):
    main_window.intercept_info = load_info()
    reset_if_needed(main_window.intercept_info)
    refresh_all_ui(main_window)

    # 定时器检查是否换天
    timer = QTimer(main_window)
    timer.timeout.connect(lambda: refresh_all_ui(main_window))
    timer.start(60000)
    main_window.timer_intercept_check = timer

# 页面 UI 刷新
def refresh_all_ui(main_window):
    info = main_window.intercept_info
    reset_if_needed(info)

    today_total = info["today_website_block"] + info["today_process_block"]
    total = info["total_website_block"] + info["total_process_block"]

    main_window.label_today_block.setText(f"今日拦截次数：{today_total}")
    main_window.label_total_block.setText(f"总共拦截次数：{total}")
    main_window.label_web_rule.setText(f"网站规则：{info['web_rule_count']}条，最后同步：{info['last_web_rule_sync']}")
    main_window.label_process_rule.setText(f"进程规则：{info['process_rule_count']}条，最后同步：{info['last_process_rule_sync']}")

# 网站拦截统计
def record_website_block():
    from client.gui.context import main_window_instance
    if not main_window_instance:
        return
    info = main_window_instance.intercept_info
    reset_if_needed(info)
    info["today_website_block"] += 1
    info["total_website_block"] += 1
    save_info(info)
    refresh_all_ui(main_window_instance)

# 进程拦截统计
def record_process_block():
    from client.gui.context import main_window_instance
    if not main_window_instance:
        return
    info = main_window_instance.intercept_info
    reset_if_needed(info)
    info["today_process_block"] += 1
    info["total_process_block"] += 1
    save_info(info)
    refresh_all_ui(main_window_instance)

# 规则同步后调用
def update_rule_sync(web_rule_count=None, process_rule_count=None, sync_time=None):
    from client.gui.context import main_window_instance
    if not main_window_instance:
        return
    info = main_window_instance.intercept_info
    if sync_time is None:
        sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if web_rule_count is not None:
        info["web_rule_count"] = web_rule_count
        info["last_web_rule_sync"] = sync_time
    if process_rule_count is not None:
        info["process_rule_count"] = process_rule_count
        info["last_process_rule_sync"] = sync_time
    save_info(info)
    refresh_all_ui(main_window_instance)
