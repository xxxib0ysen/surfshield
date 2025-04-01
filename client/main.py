import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import time
from threading import Thread

from agent.control.intercept import start_network_intercept
from agent.control.rule_sync import sync_rules
from config import config

# 确保日志目录存在
def ensure_log_dir():
    log_dir = os.path.dirname(config.log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

# 启动规则同步线程
def start_rule_sync_loop():
    def loop():
        while True:
            sync_rules()
            time.sleep(config.sync_interval_minutes * 60)
    thread = Thread(target=loop, daemon=True)
    thread.start()

def main():
    print("客户端启动中...")
    ensure_log_dir()
    start_rule_sync_loop()
    start_network_intercept()

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
