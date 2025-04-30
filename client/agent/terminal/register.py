import json
import os
import sys
import uuid
import platform
import socket
import winreg
from datetime import datetime

import subprocess
import requests
from getpass import getuser

from PyQt5.QtWidgets import QApplication, QMessageBox

from client.config import config
from client.config.config import redis_client
from client.config.logger import logger
from client.gui.invite import InviteCodeDialog

_terminal_id = None

def set_terminal_id(id_value):
    global _terminal_id
    _terminal_id = id_value
    from client.config.logger import logger
    logger.info(f"[终端ID设置成功] terminal_id = {_terminal_id}")

def get_terminal_id():
    return _terminal_id

# 获取当前用户名
def get_username():
    return getuser()

# 获取计算机名
def get_hostname():
    return platform.node()

# 获取唯一标识
def get_uuid():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography"
        )
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        return value
    except Exception as e:
        return None

# 获取公网 IP（通过在线服务）
def get_ip_address():
    try:
        return requests.get("https://api.ipify.org", timeout=3).text
    except:
        return "0.0.0.0"

# 获取局域网（本地）IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# 获取 MAC 地址
def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2)).lower()

# 获取操作系统名称
def get_os_name():
    try:
        output = subprocess.check_output("systeminfo", shell=True, encoding="gbk", errors="ignore")
        for line in output.splitlines():
            if "OS 名称" in line or "OS Name" in line:
                return line.split(":", 1)[1].strip()
    except Exception as e:
        print(f"获取操作系统名称失败: {e}")
    return "未知操作系统"

# 获取操作系统版本号
def get_os_version():
    return platform.version()

# 判断是否为 64 位系统
def is_64bit():
    return int(platform.machine().endswith('64'))

# 获取操作系统安装时间
def get_install_time():
    try:
        output = subprocess.check_output('systeminfo', shell=True, encoding='gbk', errors='ignore')
        for line in output.splitlines():
            if "初始安装日期" in line or "Original Install Date" in line:
                date_str = line.split(":", 1)[1].strip()
                known_formats = [
                    "%Y/%m/%d, %H:%M:%S",
                    "%m/%d/%Y, %I:%M:%S %p",
                    "%Y-%m-%d %H:%M:%S"
                ]
                for fmt in known_formats:
                    try:
                        return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        continue
                logger.error("[调试] 未匹配安装时间格式：", date_str)
    except Exception as e:
        logger.error(f"[调试] 获取安装时间失败: {e}")
    return None


# 采集终端完整信息
def collect_terminal_info():
    return {
        "username": get_username(),
        "hostname": get_hostname(),
        "uuid": get_uuid(),
        "ip_address": get_ip_address(),
        "local_ip": get_local_ip(),
        "mac_address": get_mac_address(),
        "os_name": get_os_name(),
        "os_version": get_os_version(),
        "install_time": get_install_time() or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_64bit": is_64bit()
    }

# 组织邀请码
def ask_group_code():
    app = QApplication.instance() or QApplication([])
    dialog = InviteCodeDialog()
    if dialog.exec_() == dialog.Accepted:
        return dialog.get_code()
    else:
        logger.error("[注册模块] 用户取消了邀请码填写，程序退出。")
        exit(0)

# 注册终端
def register_terminal(group_code: str) -> int | None:
    try:
        info = collect_terminal_info()
        info["group_code"] = group_code
        url = config.server_url.rstrip("/") + config.terminal_register_endpoint

        res = requests.post(url, json=info, timeout=5)
        if res.status_code != 200:
            logger.error(f"[注册失败] 服务器返回码异常 {res.status_code}")
            return None

        result = res.json()
        logger.info(f"[注册返回] {result}")

        if result.get("code") == 200 and result.get("data", {}).get("id"):
            return result["data"]["id"]
        else:
            logger.error(f"[注册失败] {result.get('message')}")
            return None
    except Exception as e:
        logger.error(f"[注册异常] {e}")
        return None

# 更新终端信息
def update_terminal_info():
    info = collect_terminal_info()
    try:
        url = config.server_url + "/api/client/update"
        res = requests.post(url, json=info)
        result = res.json()
        logger.info(f"[更新] {result.get('message')}")
        logger.info("[DEBUG] 上传终端信息：", info)

    except Exception as e:
        logger.error(f"[异常] 更新失败: {e}")

# 上报终端状态
def report_terminal_status(terminal_id: int, status: int):
    try:
        url = config.server_url.rstrip("/") + "/api/client/status"
        res = requests.post(url, json={"terminal_id": terminal_id, "status": status}, timeout=5)
        result = res.json()
        logger.info(f"[上报终端状态] {result.get('message')}")
        if status == 1:
            redis_client.set(f"terminal:heartbeat:{terminal_id}", "1", ex=90)
        else:
            redis_client.delete(f"terminal:heartbeat:{terminal_id}")
    except Exception as e:
        logger.error(f"[异常] 上报状态失败: {e}")

def startup_routine():
    try:
        update_terminal_info()
    except Exception as e:
        logger.error(f"[启动异常] {e}")
        sys.exit(1)

