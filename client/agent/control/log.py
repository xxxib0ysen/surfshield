import os
import threading
from datetime import datetime
from client.config import config
from client.gui.context import main_window_instance
from client.gui.intercept_info import record_website_block

log_lock = threading.Lock()
max_log_size_mb = 5


def log_block(protocol, host):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[BLOCK] {timestamp} {protocol.upper()} {host}"

    # 写入日志
    with log_lock:
        if os.path.exists(config.log_file_path):
            size_mb = os.path.getsize(config.log_file_path) / (1024 * 1024)
            if size_mb >= max_log_size_mb:
                with open(config.log_file_path, "w", encoding="utf-8") as f:
                    f.write("[LOG CLEARED DUE TO SIZE LIMIT]\n")

        with open(config.log_file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    # ✅ 统计拦截次数 + 刷新界面
    try:
        record_website_block()
    except Exception as e:
        print(f"[拦截统计失败] {e}")
