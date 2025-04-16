import json

import time
from urllib.parse import urlparse, parse_qs
from datetime import datetime

import win32gui
import win32process
import psutil
from threading import Thread
import re
from client.agent.terminal.register import get_terminal_id
from client.config.config import redis_client

terminal_id = get_terminal_id()


# 获取当前浏览器窗口标题
def get_active_browser_title():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        browser_names = ['chrome', 'msedge', 'firefox']

        if any(b in proc.name().lower() for b in browser_names):
            title = win32gui.GetWindowText(hwnd)
            return title.strip()
    except Exception as e:
        print(f"[行为采集] 获取浏览器窗口标题失败: {e}")
    return None


# 记录网站访问行为
def record_website_visit(url: str):
    try:
        title = get_active_browser_title() or urlparse(url).netloc
        data = {
            "terminal_id": terminal_id,
            "title": title,
            "url": url,
            "visit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        key = f"behavior:web:{terminal_id}"
        redis_client.lpush(key, json.dumps(data))
        redis_client.ltrim(key, 0, 19)
        print(f"[记录网页访问] 网站名称: {title} | 网址: {url} | 时间: {data['visit_time']}")
    except Exception as e:
        print(f"[行为采集] 记录网页访问失败: {e}")


# 提取关键词参数
def extract_search_keyword(url: str):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        for param in ['q', 'wd', 'query', 'keyword']:
            if param in query:
                return query[param][0]
    except Exception as e:
        print(f"[行为采集] 提取搜索关键词失败: {e}")
    return None


# 记录搜索关键词行为
def record_search_behavior(url: str):
    try:
        keyword = extract_search_keyword(url)
        if not keyword:
            return

        engine = urlparse(url).netloc
        data = {
            "terminal_id": terminal_id,
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": engine,
            "keyword": keyword
        }
        key = f"behavior:search:{terminal_id}"
        redis_client.lpush(key, json.dumps(data))
        redis_client.ltrim(key, 0, 19)
        print(f"[记录搜索行为] 关键词: {keyword} | 搜索引擎: {engine} | 时间: {data['search_time']}")

    except Exception as e:
        print(f"[行为采集] 记录搜索失败: {e}")


# 抓包记录网页访问与搜索行为
def start_behavior_capture():
    try:
        from pydivert import WinDivert

        def capture_loop():
            print("[行为采集] 网络行为监听已启动...")
            try:
                with WinDivert("outbound and tcp.DstPort == 80 or tcp.DstPort == 443") as w:
                    for packet in w:
                        try:
                            url = None

                            # HTTP 请求，获取 Host
                            if hasattr(packet, "http") and packet.http.host:
                                host = packet.http.host
                                if re.match(r"^([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}$", host):
                                    url = f"http://{host}"

                            # HTTPS 请求，获取 SNI
                            elif hasattr(packet, "sni"):
                                sni = packet.sni
                                if re.match(r"^([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}$", sni):
                                    url = f"https://{sni}"

                            if url:
                                record_website_visit(url)
                                record_search_behavior(url)

                        except Exception as inner:
                            print(f"[行为采集异常] 单个包处理失败: {inner}")

            except Exception as e:
                print(f"[行为采集启动失败] {e}")

        Thread(target=capture_loop, daemon=True).start()

    except ImportError:
        print("[行为采集] 缺少 pydivert，请确保已安装驱动及依赖。")
