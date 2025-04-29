import sys
import time
from threading import Thread

from PyQt5.QtCore import QTimer

from client.agent.control.intercept import start_network_intercept
from client.agent.control.process_control import run_process_guard
from client.agent.control.rule_sync import sync_rules
from client.config.logger import logger

from client.agent.terminal.register import (
    startup_routine,
    report_terminal_status,
    get_terminal_id, register_terminal)

from client.agent.terminal.process_monitor import start_process_report_loop, listen_for_commands
from client.agent.terminal.behavior import start_behavior_capture
from client.gui.invite import InviteCodeDialog, show_error_message
from client.gui.window import MainWindow


# 启动规则同步线程
def start_rule_sync_loop():
    def loop():
        while True:
            sync_rules()
            time.sleep(10 * 60)  # 每10分钟同步一次
    Thread(target=loop, daemon=True).start()

# 启动心跳线程
def start_heartbeat_loop():
    def loop():
        while True:
            try:
                report_terminal_status(1)
            except Exception as e:
                logger.error(f"[心跳异常] {e}")
            time.sleep(30)
    Thread(target=loop, daemon=True).start()

# 进程采集上报线程
def start_process_report_loop_thread():
    Thread(target=start_process_report_loop, daemon=True).start()

# 终止进程监听线程
def start_command_listener():
    Thread(target=listen_for_commands, daemon=True).start()


# 初始化整个模块
def initialize_backend(splash):
    try:
        # 检测是否已注册
        splash.set_progress(10, "检测终端注册状态...")
        if not get_terminal_id():
            splash.set_progress(20, "首次启动，需要填写邀请码...")
            while True:
                dialog = InviteCodeDialog()
                if dialog.exec_() == InviteCodeDialog.Accepted:
                    group_code = dialog.get_code()
                    if group_code:
                        try:
                            register_terminal(group_code)
                            splash.set_progress(30, "注册成功，正在加载系统...")
                            break
                        except Exception:
                            show_error_message("邀请码错误，请重新输入！")
                            continue
                    else:
                        show_error_message("请输入邀请码！")
                else:
                    logger.error("用户取消了邀请码填写，退出。")
                    sys.exit(0)

        # 终端信息加载
        splash.set_progress(40, "加载终端信息...")
        startup_routine()

        # 上报在线状态
        splash.set_progress(50, "上报在线状态...")
        report_terminal_status(1)

        # 启动后台线程
        splash.set_progress(60, "启动后台线程...")
        start_heartbeat_loop()
        start_rule_sync_loop()
        start_network_intercept()
        Thread(target=run_process_guard, daemon=True).start()
        start_process_report_loop_thread()
        start_command_listener()
        start_behavior_capture()

        # 启动主界面
        splash.set_progress(100, "初始化完成，启动主界面...")

        QTimer.singleShot(500, splash.finish)

        from client.gui.context import main_window_instance
        main_window_instance = MainWindow()
        main_window_instance.show()

    except Exception as e:
        logger.error(f"[初始化失败] {e}")
        sys.exit(1)
