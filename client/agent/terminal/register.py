import os
import uuid
import platform
import socket
import winreg
from datetime import datetime

import psutil
import subprocess
import requests
from getpass import getuser

from client.config import config

# 本地存储终端 ID
terminal_id_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "terminal_id.txt")

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
                print("[调试] 未匹配安装时间格式：", date_str)
    except Exception as e:
        print(f"[调试] 获取安装时间失败: {e}")
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

# 提示用户输入组织邀请码
def ask_group_code():
    return input("请输入组织邀请码（由管理员提供）: ").strip()

# 注册终端
def register_terminal():
    # 已注册则跳过
    if os.path.exists(terminal_id_file):
        print("终端已注册，跳过注册流程。")
        return

    # 收集终端信息与邀请码
    group_code = ask_group_code()
    info = collect_terminal_info()
    info["group_code"] = group_code

    # 发送注册请求
    try:
        url = config.server_url + config.terminal_register_endpoint
        res = requests.post(url, json=info)
        result = res.json()
        if result.get("code") == 200:
            terminal_id = result["data"]["terminal_id"]
            with open(terminal_id_file, "w") as f:
                f.write(str(terminal_id))
            print(f"终端注册成功，ID: {terminal_id}")
        else:
            print(f"[注册失败] {result.get('message')}")
            print(f"[注册失败] 响应内容: {result}")
    except Exception as e:
        print(f"[异常] 无法连接服务器: {e}")

# 更新终端信息
def update_terminal_info():
    info = collect_terminal_info()
    try:
        url = config.server_url + "/client/update"
        res = requests.post(url, json=info)
        result = res.json()
        print(f"[更新] {result.get('message')}")
        print("[DEBUG] 上传终端信息：", info)

    except Exception as e:
        print(f"[异常] 更新失败: {e}")

# 上报终端状态
def report_terminal_status(status: int):
    if not os.path.exists(terminal_id_file):
        return
    try:
        with open(terminal_id_file, "r") as f:
            terminal_id = int(f.read().strip())
        url = config.server_url + "/client/status"
        res = requests.post(url, json={"terminal_id": terminal_id, "status": status})
        result = res.json()
        print(result.get("message"))
        print(f"[上报] terminal_id: {terminal_id}, status: {status}")
        print(f"[上报响应] {result}")
    except Exception as e:
        print(f"[异常] 上报状态失败: {e}")

def startup_routine():
    if os.path.exists(terminal_id_file):
        update_terminal_info()
    else:
        register_terminal()