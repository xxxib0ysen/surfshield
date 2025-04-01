import os
import threading
from datetime import datetime
from client.config import config

log_lock = threading.Lock()

max_log_size_mb = 5

# 拦截日志
def log_block(protocol, host):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[BLOCK] {timestamp} {protocol.upper()} {host}"

    print(line)

    with log_lock:
        # 判断是否超过最大大小
        if os.path.exists(config.log_file_path):
            size_mb = os.path.getsize(config.log_file_path) / (1024 * 1024)
            if size_mb >= max_log_size_mb:
                # 清空文件内容
                with open(config.log_file_path, "w", encoding="utf-8") as f:
                    f.write("[LOG CLEARED DUE TO SIZE LIMIT]\n")

        with open(config.log_file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")