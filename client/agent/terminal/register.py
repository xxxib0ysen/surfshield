import os
import uuid
import platform
import socket

import psutil
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

# 获取唯一标识 UUID
def get_uuid():
    return str(uuid.uuid1())

# 获取公网 IP
def get_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "0.0.0.0"

# 获取本地局域网 IP
def get_local_ip():
    for iface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET and not snic.address.startswith("127."):
                return snic.address
    return "127.0.0.1"

# 获取 MAC 地址
def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2)).lower()

# 获取操作系统名称
def get_os_name():
    return platform.system()

# 获取操作系统版本号
def get_os_version():
    return platform.version()

# 判断是否为 64 位系统
def is_64bit():
    return int(platform.machine().endswith('64'))

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

