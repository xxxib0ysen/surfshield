import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import atexit
import signal
import requests

from threading import Thread
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from config import config
from client.config.logger import logger
from client.agent.init import initialize_backend
from client.gui.splash import SplashWindow
from client.gui.invite import show_error_message, InviteCodeDialog
from client.agent.terminal.register import report_terminal_status, get_terminal_id, set_terminal_id, get_uuid

# 确保日志目录存在
def ensure_log_dir():
    log_dir = os.path.dirname(config.log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

# 退出上报离线状态
def on_exit():
    terminal_id = get_terminal_id()
    if terminal_id:
        report_terminal_status(terminal_id, 0)

def main():
    print("客户端启动中...")
    ensure_log_dir()

    # 注册退出信号
    atexit.register(on_exit)
    signal.signal(signal.SIGINT, lambda sig, frame: exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: exit(0))

    app = QApplication(sys.argv)

    # 检查注册状态
    try:
        uuid_value = get_uuid()
        if not uuid_value:
            show_error_message("无法获取终端UUID，程序无法启动")
            sys.exit(1)

        url = config.server_url.rstrip("/") + "/api/client/check-register"
        res = requests.post(url, json={"uuid": uuid_value}, timeout=5)
        res.raise_for_status()
        result = res.json()

        data = result.get("data")

        if isinstance(data, dict) and data.get("id"):
            terminal_id = data["id"]
            # 已注册
            set_terminal_id(terminal_id)
            logger.info(f"[启动阶段] 成功拿到终端ID: {terminal_id}")
            splash = SplashWindow()
            splash.show()
            QTimer.singleShot(100, lambda: initialize_backend(splash))

        else:
            # 未注册，需要邀请码
            dialog = InviteCodeDialog()
            if dialog.exec_() == InviteCodeDialog.Accepted:
                terminal_id = get_terminal_id()
                if not terminal_id:
                    show_error_message("注册失败，终端ID未设置")
                    sys.exit(1)
                logger.info(f"[邀请码注册成功] 终端ID: {terminal_id}")
                splash = SplashWindow()
                splash.show()
                QTimer.singleShot(100, lambda: initialize_backend(splash))
            else:
                print("用户取消，退出程序")
                sys.exit(0)

    except Exception as e:
        show_error_message(f"连接服务器异常: {e}")
        sys.exit(1)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
