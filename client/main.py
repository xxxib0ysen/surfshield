import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from PyQt5.QtCore import QTimer
from client.agent.init import initialize_backend
from client.gui.splash import SplashWindow
import atexit
import signal
from client.agent.terminal.register import report_terminal_status
from threading import Thread
from agent.control.process_control import run_process_guard
from config import config
from PyQt5.QtWidgets import QApplication


# 确保日志目录存在
def ensure_log_dir():
    log_dir = os.path.dirname(config.log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

# 进程控制线程
def start_process_guard_loop():
    Thread(target=run_process_guard, daemon=True).start()


# 退出上报离线状态
def on_exit():
    report_terminal_status(0)

def main():
    print("客户端启动中...")
    ensure_log_dir()

    # 注册退出信号
    atexit.register(on_exit)
    signal.signal(signal.SIGINT, lambda sig, frame: exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: exit(0))

    app = QApplication(sys.argv)

    # 显示启动界面
    splash = SplashWindow()
    splash.show()

    QTimer.singleShot(100, lambda: initialize_backend(splash))

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
