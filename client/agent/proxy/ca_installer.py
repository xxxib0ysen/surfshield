import os
import subprocess
from client.config.config import get_runtime_path
from client.config.logger import logger

def is_cert_installed(cert_cn="mitmproxy"):
    try:
        result = subprocess.run(["certutil", "-store", "root"], capture_output=True, text=True)
        return cert_cn.lower() in result.stdout.lower()
    except Exception as e:
        logger.warning(f"[CA] 查询系统证书失败: {e}")
        return False

def install_ca():
    try:
        mitm_path = get_runtime_path("mitmproxy-ca-cert.pem")

        if not os.path.exists(mitm_path):
            logger.error("[CA] 缺少 mitmproxy-ca-cert.pem")
            return

        if is_cert_installed("mitmproxy"):
            logger.info("[CA] 已安装 mitmproxy 根证书")
            return

        subprocess.run(["certutil", "-addstore", "root", mitm_path], check=False)
        logger.info("[CA] mitmproxy 根证书已安装")
    except Exception as e:
        logger.error(f"[CA] 安装根证书失败: {e}", exc_info=True)
