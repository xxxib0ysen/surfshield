import json
from threading import Thread
from time import time,sleep
from urllib.parse import urlparse, parse_qs
from datetime import datetime

from client.agent.terminal.browser_parser import extract_all_browser_history
from client.agent.terminal.register import get_terminal_id
from client.config.config import redis_client

# 获取当前终端 ID
terminal_id = get_terminal_id()

last_ts = (time() + 11644473600) * 1_000_000


# 写入网页访问记录到 Redis
def record_web_visit(record):
    try:
        key = f"behavior:web:{terminal_id}"

        # 写入 Redis 列表，最多保留 20 条
        redis_client.lpush(key, json.dumps({
            "terminal_id": terminal_id,
            "title": record["title"],
            "url": record["url"],
            "visit_time": record["visit_time"],
            "browser": record["browser"]
        }))
        redis_client.ltrim(key, 0, 19)

        print(f"[访问记录] {record['browser']} | {record['title']} | {record['url']}")

    except Exception as e:
        print(f"[记录网页访问异常] {e}")

# 判断 URL 是否属于搜索引擎
def is_search_engine(url):
    try:
        netloc = urlparse(url).netloc.lower()

        parts = netloc.split(".")
        if len(parts) >= 2:
            domain = ".".join(parts[-2:])
        else:
            domain = netloc

        known_engines = [
            "baidu.com", "google.com", "bing.com", "so.com",
            "sogou.com", "yahoo.com", "yahoo.com.cn",
        ]

        return domain in known_engines
    except Exception:
        return False

# 从 URL 中提取关键词参数
def extract_keyword(url):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        for key in ["q", "wd", "query", "keyword", "p", "text"]:
            if key in query:
                return query[key][0]
    except:
        pass
    return None

# 写入搜索关键词记录到 Redis
def record_search_behavior(record):
    try:
        # 仅处理搜索引擎页面
        if not is_search_engine(record["url"]):
            return

        keyword = extract_keyword(record["url"])
        if not keyword:
            return

        key = f"behavior:search:{terminal_id}"
        redis_client.lpush(key, json.dumps({
            "terminal_id": terminal_id,
            "search_time": record["visit_time"],
            "engine": urlparse(record["url"]).netloc,
            "keyword": keyword
        }))
        redis_client.ltrim(key, 0, 19)

        print(f"[搜索记录] {keyword} | {record['url']}")

    except Exception as e:
        print(f"[记录搜索行为异常] {e}")

# 行为采集循环线程
def behavior_loop():
    global last_ts

    while True:
        try:
            # 提取所有浏览器中的新增历史记录
            records = extract_all_browser_history(last_ts)

            if not records:
                sleep(10)
                continue

            for record in records:
                timestamp = record["timestamp"]
                # 记录最新时间戳
                if timestamp > last_ts:
                    last_ts = timestamp

                # 写入网页访问记录
                record_web_visit(record)

                # 判断是否为搜索行为
                record_search_behavior(record)

        except Exception as e:
            print(f"[行为采集异常] {e}")

        sleep(10)


def start_behavior_capture():
    print("[行为采集] 启动成功，开始周期性轮询浏览器历史记录")
    Thread(target=behavior_loop, daemon=True).start()
