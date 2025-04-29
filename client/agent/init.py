import sys
import time
from threading import Thread

import requests
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QMessageBox

from client.agent.control.intercept import start_network_intercept
from client.agent.control.process_control import run_process_guard
from client.agent.control.rule_sync import sync_rules
from client.config import config
from client.config.logger import logger

from client.agent.terminal.register import (
    startup_routine,
    report_terminal_status,
    register_terminal, collect_terminal_info, get_uuid, set_terminal_id)

from client.agent.terminal.process_monitor import start_process_report_loop, listen_for_commands
from client.agent.terminal.behavior import start_behavior_capture
from client.gui.invite import InviteCodeDialog, show_error_message, show_success_message
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
        # 1. 检测UUID
        splash.set_progress(5, "检测终端注册状态...")
        uuid_value = get_uuid()
        if not uuid_value:
            show_error_message("无法获取终端UUID，无法启动！")
            sys.exit(1)

        # 2. 发送注册检测
        info = collect_terminal_info()
        info["group_code"] = ""

        url = config.server_url.rstrip("/") + config.terminal_register_endpoint

        try:
            res = requests.post(url, json=info, timeout=5)
            result = res.json()

            if res.status_code != 200:
                show_error_message("服务器返回异常状态码，请联系管理员！")
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            logger.error(f"[连接服务器失败] {e}")
            show_error_message("无法连接服务器，请检查网络或联系管理员！")
            sys.exit(1)
        except Exception as e:
            logger.error(f"[注册异常] {e}")
            show_error_message("注册失败，发生未知错误！")
            sys.exit(1)

        data = result.get("data")

        if not data or not data.get("id"):
            # 没注册，弹邀请码
            splash.set_progress(10, "首次使用，请填写邀请码注册...")

            while True:
                dialog = InviteCodeDialog()
                if dialog.exec_() == QDialog.Accepted:
                    group_code = dialog.get_code()
                    if not group_code:
                        show_error_message("请输入邀请码！")
                        continue
                    try:
                        info["group_code"] = group_code
                        res = requests.post(url, json=info, timeout=5)
                        result = res.json()

                        if res.status_code != 200:
                            show_error_message("服务器返回异常，请联系管理员！")
                            continue

                        if result.get("code") == 200 and result["data"].get("id"):
                            terminal_id = result["data"]["id"]
                            set_terminal_id(terminal_id)
                            show_success_message("终端注册成功！正在继续加载...")
                            break
                        else:
                            show_error_message(f"注册失败：{result.get('message')}")
                    except requests.exceptions.RequestException as e:
                        logger.error(f"[注册请求异常] {e}")
                        show_error_message("无法连接服务器，请检查网络！")
                    except Exception as e:
                        logger.error(f"[注册未知异常] {e}")
                        show_error_message("注册失败，请联系管理员！")
                else:
                    logger.error("用户取消邀请码填写，退出。")
                    sys.exit(0)
        else:
            terminal_id = data["id"]
            set_terminal_id(terminal_id)
            splash.set_progress(20, "终端已注册，继续初始化...")

        # 3. 后续模块启动
        splash.set_progress(30, "加载终端信息...")
        startup_routine()

        splash.set_progress(60, "启动后台线程...")
        start_heartbeat_loop()
        start_rule_sync_loop()
        start_network_intercept()
        Thread(target=run_process_guard, daemon=True).start()
        start_process_report_loop_thread()
        start_command_listener()
        start_behavior_capture()

        splash.set_progress(100, "初始化完成，启动主界面...")
        QTimer.singleShot(500, splash.finish)

        from client.gui.context import main_window_instance
        main_window_instance = MainWindow()
        main_window_instance.show()

    except Exception as e:
        logger.error(f"[初始化失败] {e}")
        show_error_message(f"启动失败：{e}")
        sys.exit(1)
