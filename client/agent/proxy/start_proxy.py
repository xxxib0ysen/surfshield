import os
import subprocess
import time

from client.agent.proxy.ca_installer import install_ca
from client.config.config import get_runtime_path
from client.config.logger import logger

def start_proxy():
    """
    启动 mitmproxy 拦截脚本
    """
    install_ca()
    mitm_exe_path = get_runtime_path("mitmproxy.exe")
    script_path = get_runtime_path("block_domain.py")
    logger.info(f"[DEBUG] mitmproxy 路径为：{mitm_exe_path}")
    logger.info(f"[DEBUG] 拦截脚本路径为：{script_path}")
    if not os.path.exists(mitm_exe_path):
        logger.error("[MITM]  mitmproxy.exe 文件不存在，无法启动")
        return

    if not os.path.exists(script_path):
        logger.error("[MITM]  block_domain.py 文件不存在，无法启动")
        return

    try:
        # 启动 mitmproxy 进程，捕捉 stdout 和 stderr
        process = subprocess.Popen([
            mitm_exe_path,
            "-s", script_path,
            "--listen-port", "8888",
            "--ssl-insecure",
            "--set", "block_global=false"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logger.info("[MITM]  mitmproxy 启动中...")

        # 等待 2 秒看看是否启动失败
        time.sleep(2)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            logger.error(f"[MITM]  启动失败，退出码：{process.returncode}")
            logger.error(f"[MITM] stderr 输出：{stderr.decode(errors='ignore')}")
        else:
            logger.info("[MITM] ✅ mitmproxy 已成功启动并监听 8888 端口")
            return True
    except Exception as e:
        logger.error(f"[MITM]  启动 mitmproxy 失败：{e}", exc_info=True)
        return False