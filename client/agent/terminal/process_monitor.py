import psutil
import time
import requests
from datetime import datetime
import os
import win32api
from client.agent.terminal.register import get_terminal_id
from client.config import config

terminal_id = get_terminal_id()
report_url = config.server_url.rstrip("/") + "/client/process-report"

# 获取进程描述信息
def get_process_description(exe_path: str) -> str:
    try:
        if not exe_path or not os.path.exists(exe_path):
            return ""
        info = win32api.GetFileVersionInfo(exe_path, "\\")  # type: ignore
        desc = win32api.VerQueryValue(info, 'StringFileInfo\\040904b0\\FileDescription')  # type: ignore
        return desc
    except Exception:
        return ""

# 获取联网信息
def get_network_info(p: psutil.Process) -> tuple:
    try:
        conns = p.connections(kind='inet')
        if conns:
            conn = conns[0]
            remote_ip = conn.raddr.ip if conn.raddr else ""
            remote_port = conn.raddr.port if (conn.raddr and isinstance(conn.raddr.port, int)) else 0
            return 1, remote_ip, remote_port, conn.status
        return 0, "", 0, ""
    except Exception:
        return 0, "", 0, ""

# 判断是否为用户进程
def is_user_process(p: psutil.Process) -> bool:
    try:
        username = p.username()
        if not username or username.lower() in ["system", "local service", "network service"]:
            return False
        return True
    except:
        return False

# 采集所有用户进程
def collect_process_info():
    process_list = []
    for p in psutil.process_iter():
        try:
            if not is_user_process(p):
                continue

            exe_path = p.exe()
            is_network, remote_ip, remote_port, net_status = get_network_info(p)

            process = {
                "terminal_id": terminal_id,
                "username": p.username(),
                "process_name": p.name(),
                "pid": p.pid,
                "status": 1 if p.status() == psutil.STATUS_RUNNING else 0,
                "is_network": is_network,
                "remote_ip": remote_ip,
                "remote_port": remote_port,
                "network_status": net_status,
                "description": get_process_description(exe_path),
                "start_time": datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            process_list.append(process)

        except Exception:
            continue

    return process_list

# 上报至服务端
def report_process():
    try:
        payload = {
            "terminal_id": terminal_id,
            "process_list": collect_process_info()
        }
        response = requests.post(report_url, json=payload, timeout=30)
        if response.status_code == 200:
            print("[进程上报] 成功")
        else:
            print("[进程上报] 失败", response.text)
    except Exception as e:
        print(f"[进程上报] 异常：{e}")

# 进程采集循环
def start_process_report_loop():
    print("[进程采集] 启动进程采集上报线程...")
    while True:
        report_process()
        time.sleep(5)
