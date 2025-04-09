import atexit
import signal
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from client.agent.terminal.register import report_terminal_status, register_terminal
import time
from threading import Thread

from agent.control.intercept import start_network_intercept
from agent.control.rule_sync import sync_rules
from agent.control.process_control import run_process_guard
from config import config


# 确保日志目录存在
def ensure_log_dir():
    log_dir = os.path.dirname(config.log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

# 规则同步线程
def start_rule_sync_loop():
    def loop():
        while True:
            sync_rules()
            time.sleep(config.sync_interval_minutes * 60)
    thread = Thread(target=loop, daemon=True)
    thread.start()

# 进程控制线程
def start_process_guard_loop():
    Thread(target=run_process_guard, daemon=True).start()

# 客户端退出时回调，标记为离线
def on_exit():
    report_terminal_status(0)  # status=0 表示离线

def main():
    print("客户端启动中...")
    ensure_log_dir()

    # 注册终端（首次）+ 上报在线状态
    register_terminal()
    report_terminal_status(1)  # status=1 表示上线

    # 注册退出信号
    atexit.register(on_exit)
    signal.signal(signal.SIGINT, lambda sig, frame: exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: exit(0))

    # 规则同步
    start_rule_sync_loop()
    # 网络拦截
    start_network_intercept()
    # 进程守护
    start_process_guard_loop()

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
