from threading import Thread
import pydivert
from client.agent.control import rule_matcher
from client.agent.control.log import log_block
from client.config.logger import logger
from client.gui.context import safe_update_module_status

# 全局拦截状态
intercept_status = {"http": False, "https": False}

# 更新网站拦截模块状态显示
def update_web_block_status():
    if intercept_status["http"] and intercept_status["https"]:
        safe_update_module_status("label_web_block", True, "网站拦截")
    else:
        safe_update_module_status("label_web_block", False, "网站拦截")

# 提取 HTTP 请求中的 Host 字段
def extract_host(payload):
    try:
        lines = payload.decode(errors="ignore").split("\r\n")
        for line in lines:
            if line.lower().startswith("host:"):
                return line.split(":", 1)[1].strip()
    except Exception as e:
        logger.error(f"[HTTP] 解析Host失败: {e}", exc_info=True)
    return None

# 启动 HTTP 拦截线程
def start_http_intercept():
    def loop():
        try:
            logger.info("[HTTP拦截] 启动中...")
            with pydivert.WinDivert("tcp.DstPort == 80 and tcp.PayloadLength > 0") as w:
                intercept_status["http"] = True
                update_web_block_status()
                for packet in w:
                    if packet.is_outbound and packet.tcp and packet.payload:
                        host = extract_host(packet.payload)
                        if host and rule_matcher.is_blocked(host):
                            log_block("http", host)
                            continue
                    w.send(packet)
        except Exception as e:
            logger.error(f"[HTTP拦截异常] {e}", exc_info=True)
            intercept_status["http"] = False
            update_web_block_status()
    Thread(target=loop, daemon=True).start()

# 提取 TLS Client Hello 中的 SNI 字段
def extract_sni(payload):
    try:
        if payload[0] == 0x16 and payload[5] == 0x01:
            session_id_len = payload[43]
            offset = 44 + session_id_len
            cipher_suites_len = int.from_bytes(payload[offset:offset+2], 'big')
            offset += 2 + cipher_suites_len
            compression_methods_len = payload[offset]
            offset += 1 + compression_methods_len
            extensions_len = int.from_bytes(payload[offset:offset+2], 'big')
            offset += 2
            end = offset + extensions_len

            while offset + 4 <= end:
                ext_type = int.from_bytes(payload[offset:offset+2], 'big')
                ext_len = int.from_bytes(payload[offset+2:offset+4], 'big')
                offset += 4
                if ext_type == 0x00:  # SNI 扩展
                    sni_data = payload[offset+5:offset+5+payload[offset+4]]
                    return sni_data.decode()
                offset += ext_len
    except Exception as e:
        logger.warning(f"[HTTPS] 提取SNI失败: {e}")
    return None

# 启动 HTTPS 拦截线程
def start_https_intercept():
    def loop():
        try:
            logger.info("[HTTPS拦截] 启动中...")
            with pydivert.WinDivert("tcp.DstPort == 443 and tcp.PayloadLength > 0") as w:
                intercept_status["https"] = True
                update_web_block_status()
                for packet in w:
                    if packet.is_outbound and packet.tcp and packet.payload:
                        sni = extract_sni(packet.payload)
                        if sni and rule_matcher.is_blocked(sni):
                            log_block("https", sni)
                            continue
                    w.send(packet)
        except Exception as e:
            logger.error(f"[HTTPS拦截异常] {e}", exc_info=True)
            intercept_status["https"] = False
            update_web_block_status()
    Thread(target=loop, daemon=True).start()


# 启动 HTTP + HTTPS 拦截
def start_network_intercept():
    start_http_intercept()
    start_https_intercept()
