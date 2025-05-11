import sys
import time
from threading import Thread

from PyQt5.QtCore import QCoreApplication, QTimer

from client.agent.control.intercept import start_network_intercept
from client.agent.control.process_control import run_process_guard
from client.agent.control.rule_sync import sync_rules, global_rules
from client.agent.proxy.pac_generator import generate_pac_file
from client.agent.proxy.proxy_config import set_pac_config, is_pac_config_correct
from client.agent.terminal.behavior import start_behavior_capture
from client.agent.terminal.process_monitor import start_process_report_loop, listen_for_commands
from client.agent.terminal.register import get_terminal_id, report_terminal_status, startup_routine
from client.config.logger import logger
from client.gui.invite import show_error_message



# 进度条
def smooth_progress(splash, start: int, end: int, duration_ms: int = 500):
    steps = end - start
    if steps <= 0:
        return
    interval = duration_ms / steps  # 每步耗时

    for value in range(start, end):
        splash.set_progress(value, f"初始化中... {value}%")
        QCoreApplication.processEvents()
        time.sleep(interval / 1000)

def run_in_thread(target_func):
    t = Thread(target=target_func, daemon=True)
    t.start()

# 启动规则同步
def start_rule_sync_loop():
    def loop():
        while True:
            try:
                sync_rules()
            except Exception as e:
                logger.error(f"[规则同步异常] {e}")
            time.sleep(600)  # 每10分钟同步
    run_in_thread(loop)

# 启动心跳上报
def start_heartbeat_loop():
    def loop():
        while True:
            try:
                terminal_id = get_terminal_id()
                if terminal_id:
                    report_terminal_status(terminal_id, 1)
                else:
                    logger.warning("[心跳异常] 未获取终端ID")
            except Exception as e:
                logger.error(f"[心跳异常] {e}")
            time.sleep(30)
    run_in_thread(loop)

# 初始化后端
def initialize_backend(splash):
    logger.info(f"[初始化阶段] 当前终端ID: {get_terminal_id()}")
    try:
        # 上传终端信息
        splash.set_progress(0, "上传终端信息...")
        smooth_progress(splash, 0, 10, duration_ms=600)
        try:
            startup_routine()
        except Exception as e:
            logger.error(f"[上传终端信息异常] {e}")

        # 启动心跳
        splash.set_progress(10, "启动心跳线程...")
        smooth_progress(splash, 10, 20, duration_ms=400)
        start_heartbeat_loop()

        # 启动规则同步
        splash.set_progress(20, "启动规则同步...")
        smooth_progress(splash, 20, 30, duration_ms=400)
        start_rule_sync_loop()

        # 启动网络拦截
        splash.set_progress(30, "启动网络拦截模块...")
        smooth_progress(splash, 30, 45, duration_ms=600)
        pac_path = generate_pac_file(global_rules)
        if pac_path:
            if not is_pac_config_correct(pac_path):
                logger.warning("[PAC] 系统未正确设置 AutoConfigURL，正在修复...")
                set_pac_config(pac_path)
            else:
                logger.info("[PAC] 系统 AutoConfigURL 检测通过")

        run_in_thread(start_network_intercept)

        # 启动进程守护
        splash.set_progress(45, "启动进程守护模块...")
        smooth_progress(splash, 45, 60, duration_ms=600)
        run_in_thread(run_process_guard)

        # 启动进程采集
        splash.set_progress(60, "启动进程监控模块...")
        smooth_progress(splash, 60, 75, duration_ms=600)
        run_in_thread(start_process_report_loop)

        # 启动命令监听
        splash.set_progress(75, "启动命令监听模块...")
        smooth_progress(splash, 75, 85, duration_ms=400)
        terminal_id = get_terminal_id()
        run_in_thread(lambda: listen_for_commands(terminal_id))

        # 启动行为采集
        splash.set_progress(85, "启动行为采集模块...")
        smooth_progress(splash, 85, 95, duration_ms=400)
        run_in_thread(start_behavior_capture)

        # 准备主界面
        splash.set_progress(95, "加载主界面...")
        smooth_progress(splash, 95, 100, duration_ms=500)

        def show_main_window():
            from client.gui.intercept_info import refresh_all_ui, load_info
            try:
                splash.finish()
                import client.gui.context as ctx
                from client.gui.window import MainWindow
                ctx.main_window_instance = MainWindow()
                ctx.main_window_instance.intercept_info = load_info()
                ctx.main_window_instance.show()
                QTimer.singleShot(300, lambda: refresh_all_ui(ctx.main_window_instance))
                QTimer.singleShot(500, sync_rules)
                logger.info("[主界面] 已成功打开")
            except Exception as e:
                logger.error(f"[主界面启动失败] {e}")
                show_error_message(f"启动主界面失败：{e}")
                sys.exit(1)

        QTimer.singleShot(200, show_main_window)

    except Exception as e:
        logger.error(f"[初始化失败] {e}")
        show_error_message(f"启动失败：{e}")
        sys.exit(1)