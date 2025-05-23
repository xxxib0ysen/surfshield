import json
from threading import Thread
from time import time,sleep
from urllib.parse import urlparse, parse_qs

from client.agent.terminal.browser_parser import extract_all_browser_history
from client.agent.terminal.register import get_terminal_id
from client.config.config import redis_client
from client.config.logger import logger

last_ts = (time() + 11644473600) * 1_000_000
last_search_keywords = {}

# 写入网页访问记录到 Redis
def record_web_visit(record):
    try:
        terminal_id = get_terminal_id()
        if not terminal_id:
            logger.warning("[行为采集] 终端 ID 获取失败，跳过网页访问写入")
            return
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

        logger.info(f"[访问记录] {record['browser']} | {record['title']} | {record['url']}")

    except Exception as e:
        logger.error(f"[记录网页访问异常] {e}")

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
        terminal_id = get_terminal_id()
        if not terminal_id:
            logger.warning("[行为采集] 终端 ID 获取失败，跳过搜索关键词写入")
            return
        # 仅处理搜索引擎页面
        if not is_search_engine(record["url"]):
            return

        keyword = extract_keyword(record["url"])
        if not keyword:
            return

        now_ts = time()
        if now_ts - last_search_keywords.get(keyword, 0) < 60:
            return  # 距离上次相同关键词不足60秒，跳过
        last_search_keywords[keyword] = now_ts

        key = f"behavior:search:{terminal_id}"
        redis_client.lpush(key, json.dumps({
            "terminal_id": terminal_id,
            "search_time": record["visit_time"],
            "engine": urlparse(record["url"]).netloc,
            "keyword": keyword
        }))
        redis_client.ltrim(key, 0, 19)

        logger.info(f"[搜索记录] {keyword} | {record['url']}")

    except Exception as e:
        logger.error(f"[记录搜索行为异常] {e}")

# 行为采集循环线程
def behavior_loop():
    global last_ts
    logger.info(f"[行为采集模块] 启动线程成功，初始时间戳：{last_ts}")
    logger.info(f"[行为采集模块] 当前终端 ID 为：{get_terminal_id()}")
    while True:
        try:
            # 提取所有浏览器中的新增历史记录
            records = extract_all_browser_history(last_ts)

            if not records:
                sleep(5)
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
            logger.error(f"[行为采集异常] {e}")

        sleep(10)


def start_behavior_capture():
    logger.info("[行为采集] 启动成功，开始周期性轮询浏览器历史记录")
    Thread(target=behavior_loop, daemon=True).start()
