import sys
import os


sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from client.logs.logger import logger
import atexit
import signal
import time
from client.agent.terminal.process_monitor import start_process_report_loop, listen_for_commands
from client.agent.terminal.register import report_terminal_status, startup_routine
from client.agent.terminal.behavior import start_behavior_capture
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


# 心跳线程（每 30 秒上报一次在线）
def start_heartbeat_loop():
    def heartbeat_loop():
        while True:
            try:
                report_terminal_status(1)  # 在线状态
            except Exception as e:
                logger.error(f"[上报异常] {e}")
            time.sleep(30)

    Thread(target=heartbeat_loop, daemon=True).start()


# 退出上报离线状态
def on_exit():
    report_terminal_status(0)


# 进程采集上报线程
def start_process_report_loop_thread():
    Thread(target=start_process_report_loop, daemon=True).start()


# 终止进程监听
def start_command_listener():
    Thread(target=listen_for_commands, daemon=True).start()


def main():
    print("客户端启动中...")
    ensure_log_dir()

    # 注册退出信号
    atexit.register(on_exit)
    signal.signal(signal.SIGINT, lambda sig, frame: exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: exit(0))

    startup_routine()
    report_terminal_status(1)  # status=1 表示上线
    start_heartbeat_loop()

    # 规则同步
    start_rule_sync_loop()
    # 网络拦截
    start_network_intercept()
    # 进程控制策略
    start_process_guard_loop()
    # 采集用户进程
    start_process_report_loop_thread()
    # 终止进程
    start_command_listener()
    # 启动行为采集线程
    start_behavior_capture()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.error("[退出] 收到中断信号，正在退出客户端...")
    except Exception as e:
        logger.error(f"[异常退出] {e}")
    finally:
        report_terminal_status(0)


if __name__ == "__main__":
    main()
