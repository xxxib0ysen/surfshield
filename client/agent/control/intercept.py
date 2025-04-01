from threading import Thread
import pydivert
import re
from client.agent.control import rule_matcher
from client.agent.control.log import log_block

# 提取 HTTP 请求中的 Host 字段
def extract_host(payload):
    try:
        lines = payload.decode(errors="ignore").split("\r\n")
        for line in lines:
            if line.lower().startswith("host:"):
                return line.split(":",1)[1].strip()
    except:
        pass
    return None

# 启动 HTTP 拦截线程
def start_http_intercept():
    def http_loop():
        print("[HTTP] 拦截线程启动中...")
        with pydivert.WinDivert("tcp.DstPort == 80 and tcp.PayloadLength > 0") as w:
            for packet in w:
                if packet.is_outbound and packet.tcp and packet.payload:
                    host = extract_host(packet.payload)
                    if host:
                        # print("[DEBUG] 当前访问（HTTP）：", host)
                        if rule_matcher.is_blocked(host):
                            log_block("http", host)
                            continue  # 丢弃数据包
                w.send(packet)
    thread = Thread(target=http_loop, daemon=True)
    thread.start()

# 提取 TLS Client Hello 中的 SNI
def extract_sni(payload):
    try:
        if payload[0] == 0x16 and payload[5] == 0x01:
            # 跳过 TLS 记录层前 43 字节
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
    except:
        pass
    return None

# 启动 HTTPS 拦截线程
def start_https_intercept():
    def https_loop():
        print("[HTTPS] 拦截线程启动中...")
        with pydivert.WinDivert("tcp.DstPort == 443 and tcp.PayloadLength > 0") as w:
            for packet in w:
                if packet.is_outbound and packet.tcp and packet.payload:
                    sni = extract_sni(packet.payload)
                    if sni and rule_matcher.is_blocked(sni):
                        # print("[DEBUG] 当前访问（HTTPS）：", sni)

                        log_block("https", sni)
                        continue
                w.send(packet)
    thread = Thread(target=https_loop, daemon=True)
    thread.start()

# 启动
def start_network_intercept():
    start_http_intercept()
    start_https_intercept()